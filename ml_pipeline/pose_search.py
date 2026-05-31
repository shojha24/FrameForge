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

def _is_valid_skeleton(img: Image.Image, min_fill_ratio: float = 0.02) -> bool:
    """
    Reject obviously corrupt/degenerate skeletons.
    A valid OpenPose skeleton should have a reasonable number of non-black pixels
    distributed across the image, not just a tiny cluster.
    """
    arr = np.array(img.convert("RGB"))
    nonblack = np.any(arr > 10, axis=2)
    total_pixels = arr.shape[0] * arr.shape[1]
    nonblack_ratio = nonblack.sum() / total_pixels

    # Also check that the skeleton spans a reasonable height
    rows = np.where(nonblack)[0]
    if len(rows) == 0:
        return False
    height_span = (rows.max() - rows.min()) / arr.shape[0]

    return nonblack_ratio >= min_fill_ratio and height_span >= 0.15


def retrieve_pose(pose_query: str, top_k: int = 1, hf_token: str = None) -> Image.Image:
    model = build_model(device="cpu")
    dataset, index = load_pose_index(hf_token=hf_token)

    query_embedding = model.encode("search_query: " + pose_query)
    query_vec = np.array([query_embedding], dtype=np.float32)

    # Fetch more candidates so we can filter bad ones
    distances, indices = index.search(query_vec, 20)

    for rank, (idx, score) in enumerate(zip(indices[0], distances[0])):
        candidate_img = dataset[int(idx)]["conditioning_image"]
        candidate_text = dataset[int(idx)]["text"]

        if _is_valid_skeleton(candidate_img):
            print(f"[Pose Search] Query: {pose_query[:60]}...")
            print(f"[Pose Search] Best valid match (rank={rank}, score={score:.4f}): {candidate_text[:80]}...")
            return candidate_img
        else:
            print(f"[Pose Search] Skipping corrupt skeleton at rank={rank}, score={score:.4f}: {candidate_text[:40]}...")

    # Fallback: return best match anyway
    print("[Pose Search] Warning: no valid skeleton found in top 20, using best match anyway")
    return dataset[int(indices[0][0])]["conditioning_image"]


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