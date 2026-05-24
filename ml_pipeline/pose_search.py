import os
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from datasets import load_from_disk
import faiss
import torch

_model = None
_dataset = None
_faiss_index = None
_model_initialized = False

DATASET_NAME = "raulc0399/open_pose_controlnet"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "open_pose_controlnet_dataset")
INDEX_PATH = os.path.join(SAVE_DIR, "index.faiss")

def build_model(device: str = None):
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
        truncate_dim=256
    )
    _model_initialized = True
    print("[Pose Search] Model loaded successfully")
    return _model

def initialize(hf_token: str = None):
    """Call once at startup to pre-load model and index into memory."""
    build_model(device="cpu")  # keep off CUDA so diffusion pipeline has full VRAM
    load_pose_index(hf_token=hf_token)
    print("[Pose Search] ✅ Model and index ready!")

def load_pose_index(hf_token: str = None):
    global _dataset, _faiss_index

    if _dataset is not None and _faiss_index is not None:
        return _dataset, _faiss_index

    build_model()

    if not os.path.exists(SAVE_DIR):
        raise ValueError(
            f"[Pose Search] Dataset not found at {SAVE_DIR}. "
            f"Initialize it first by running: python ml_pipeline/openpose_test.py"
        )

    print(f"[Pose Search] Loading dataset from {SAVE_DIR}...")
    # Load without touching the FAISS integration in datasets at all
    _dataset = load_from_disk(SAVE_DIR)

    print(f"[Pose Search] Loading FAISS index directly from {INDEX_PATH}...")
    # Use raw faiss instead of datasets' wrapper — avoids the SuperKMeans bug
    _faiss_index = faiss.read_index(INDEX_PATH)

    print("[Pose Search] Dataset and index ready!")
    return _dataset, _faiss_index


def retrieve_pose(pose_query: str, top_k: int = 1, hf_token: str = None) -> Image.Image:
    model = build_model(device="cpu")
    dataset, index = load_pose_index(hf_token=hf_token)

    query_embedding = model.encode("search_query: " + pose_query)
    # faiss expects float32, shape (n_queries, dim)
    query_vec = np.array([query_embedding], dtype=np.float32)

    distances, indices = index.search(query_vec, top_k)

    best_idx = indices[0][0]
    best_score = distances[0][0]
    best_text = dataset[best_idx]["text"]
    best_image = dataset[best_idx]["conditioning_image"]

    print(f"[Pose Search] Query: {pose_query[:60]}...")
    print(f"[Pose Search] Best match (score={best_score:.4f}): {best_text[:80]}...")

    return best_image


def retrieve_top_k_poses(pose_query: str, top_k: int = 5, hf_token: str = None) -> list[Image.Image]:
    model = build_model(device="cpu")
    dataset, index = load_pose_index(hf_token=hf_token)

    query_embedding = model.encode("search_query: " + pose_query)
    query_vec = np.array([query_embedding], dtype=np.float32)

    distances, indices = index.search(query_vec, top_k)

    images = [dataset[int(i)]["conditioning_image"] for i in indices[0]]
    return images


if __name__ == "__main__":
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