"""
Pose Search Module — Semantic Search for OpenPose ControlNet Conditioning.

Refactored from openpose_test.py. Provides:
  - load_pose_index(): Load pre-built FAISS index or build at startup
  - retrieve_pose(): Query index and return matching skeleton image
  - build_model(): Load Nomic embedding model

Dependencies:
  - sentence-transformers (Nomic model)
  - datasets (HuggingFace)
  - faiss
  - Pillow
"""

import os
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from datasets import load_dataset, load_from_disk
import torch

# Global state (loaded once at server startup)
_model = None
_dataset_with_embeddings = None
_model_initialized = False

DATASET_NAME = "raulc0399/open_pose_controlnet"
# Resolve path relative to ml_pipeline directory (where this file is)
SAVE_DIR = os.path.join(os.path.dirname(__file__), "open_pose_controlnet_dataset")
INDEX_PATH = os.path.join(SAVE_DIR, "index.faiss")


def build_model(device: str = None):
    """Load Nomic embedding model. Called once at server startup."""
    global _model, _model_initialized
    
    if _model_initialized:
        return _model
    
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"[Pose Search] Loading Nomic embedding model on device: {device}")
    _model = SentenceTransformer(
        "nomic-ai/nomic-embed-text-v1.5",
        device=device,
        trust_remote_code=True,
        truncate_dim=256  # Truncate 768D → 256D vectors
    )
    _model_initialized = True
    print("[Pose Search] Model loaded successfully")
    return _model


def load_pose_index(hf_token: str = None):
    """
    Load or build FAISS index for pose semantic search.
    
    On first run (or if dataset missing): Downloads HF dataset, builds index, saves to disk.
    On subsequent runs: Loads pre-built index from disk.
    
    Args:
        hf_token (str): HuggingFace token. Required for first-time download.
    
    Returns:
        Dataset with loaded FAISS index
    """
    global _dataset_with_embeddings
    
    if _dataset_with_embeddings is not None:
        return _dataset_with_embeddings
    
    model = build_model()
    
    if not os.path.exists(SAVE_DIR):
        print(f"[Pose Search] Dataset not found at {SAVE_DIR}. Downloading from HuggingFace...")
        
        if not hf_token:
            raise ValueError(
                f"First-time setup requires HUGGING_FACE_HUB_TOKEN env var. "
                f"Get token from https://huggingface.co/settings/tokens or use existing local dataset at {SAVE_DIR}"
            )
        
        # Authenticate with HF
        from huggingface_hub import login
        login(hf_token)
        
        # Download dataset
        os.makedirs(SAVE_DIR, exist_ok=True)
        ds = load_dataset(DATASET_NAME, split="train")
        
        # Keep only necessary columns to save space
        if "id" not in ds.column_names:
            ds = ds.add_column("id", range(len(ds)))
        cols_to_keep = ["id", "conditioning_image", "text"]
        cols_to_remove = [col for col in ds.column_names if col not in cols_to_keep]
        ds = ds.remove_columns(cols_to_remove)
        
        # Generate embeddings for all text descriptions
        print("[Pose Search] Generating embeddings (this may take a minute)...")
        def generate_embeddings(batch):
            prefixed_texts = ["search_document: " + text for text in batch["text"]]
            return {"embeddings": model.encode(prefixed_texts).tolist()}
        
        ds_with_embeddings = ds.map(generate_embeddings, batched=True, batch_size=32)
        
        # Build and save FAISS index
        print("[Pose Search] Building FAISS index...")
        ds_with_embeddings.add_faiss_index(column="embeddings")
        ds_with_embeddings.save_faiss_index("embeddings", INDEX_PATH)
        ds_with_embeddings.drop_index("embeddings")
        
        # Save dataset to disk
        print(f"[Pose Search] Saving dataset to {SAVE_DIR}...")
        ds_with_embeddings.save_to_disk(SAVE_DIR)
        ds_with_embeddings.load_faiss_index("embeddings", INDEX_PATH)
        _dataset_with_embeddings = ds_with_embeddings
        print("[Pose Search] Dataset and index ready!")
        
    else:
        print(f"[Pose Search] Loading dataset from {SAVE_DIR}...")
        _dataset_with_embeddings = load_from_disk(SAVE_DIR)
        _dataset_with_embeddings.load_faiss_index("embeddings", INDEX_PATH)
        print("[Pose Search] Dataset loaded!")
    
    return _dataset_with_embeddings


def retrieve_pose(pose_query: str, top_k: int = 1, hf_token: str = None) -> Image.Image:
    """
    Retrieve the top-matching OpenPose skeleton image for a pose query.
    
    Args:
        pose_query (str): Naturalistic description of pose, e.g.,
            "A person standing upright with arms at their sides, facing the camera."
        top_k (int): Number of top matches to consider (returns best match)
        hf_token (str): HuggingFace token (required on first run only)
    
    Returns:
        PIL.Image: The conditioning_image (OpenPose skeleton) of the best match
    """
    model = build_model()
    ds = load_pose_index(hf_token=hf_token)
    
    # Embed the query with Nomic prefix
    query_embedding = np.array(model.encode("search_query: " + pose_query))
    
    # Search FAISS index
    scores, retrieved_examples = ds.get_nearest_examples(
        "embeddings",
        query_embedding,
        k=top_k
    )
    
    # Return the top match (lowest L2 distance = best match)
    best_image = retrieved_examples["conditioning_image"][0]
    
    # Log for debugging
    best_text = retrieved_examples["text"][0]
    best_score = scores[0]
    print(f"[Pose Search] Query: {pose_query[:60]}...")
    print(f"[Pose Search] Best match (score={best_score:.4f}): {best_text[:80]}...")
    
    return best_image


def retrieve_top_k_poses(pose_query: str, top_k: int = 5, hf_token: str = None) -> list[Image.Image]:
    """
    Retrieve top-k matching poses (useful for manual selection UI).
    
    Args:
        pose_query (str): Pose description
        top_k (int): Number of candidates to return
        hf_token (str): HuggingFace token (required on first run only)
    
    Returns:
        List of PIL.Image objects (OpenPose skeletons)
    """
    model = build_model()
    ds = load_pose_index(hf_token=hf_token)
    
    # Embed and search
    query_embedding = np.array(model.encode("search_query: " + pose_query))
    scores, retrieved_examples = ds.get_nearest_examples(
        "embeddings",
        query_embedding,
        k=top_k
    )
    
    images = retrieved_examples["conditioning_image"][0:top_k]
    return images


if __name__ == "__main__":
    # Test the module
    print("[Pose Search] Testing retrieve_pose()...")
    try:
        pose_image = retrieve_pose(
            "A person standing upright with arms at their sides, facing the camera.",
            hf_token=os.getenv("HUGGING_FACE_HUB_TOKEN")
        )
        pose_image.save("test_pose_output.png")
        print("[Pose Search] Test passed! Saved output to test_pose_output.png")
    except Exception as e:
        print(f"[Pose Search] Test failed: {e}")
