from huggingface_hub import login, whoami
from datasets import load_dataset, load_from_disk
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import os
import dotenv

# Note: Make sure you run `pip install einops` as Nomic's model requires it.

dotenv.load_dotenv()

DATASET = "raulc0399/open_pose_controlnet"
SAVE_DIR = "./open_pose_controlnet_dataset"
INDEX_PATH = os.path.join(SAVE_DIR, "index.faiss")

print("Authenticating with Hugging Face...")
try:
    login(os.getenv("HUGGING_FACE_HUB_TOKEN"))
    user_info = whoami()
    print(f"[Success] Authenticated actively as: {user_info['name']}\n")
except Exception as e:
    print(f"[Error] Hugging Face authentication failed: {e}")
    exit(1)

print("Initializing SentenceTransformer model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# --- CHANGE 1: Nomic Model with Matryoshka Truncation ---
model = SentenceTransformer(
    "nomic-ai/nomic-embed-text-v1.5", 
    device=device,
    trust_remote_code=True, 
    truncate_dim=256 # Truncates the default 768 vectors down to 256 automatically
)
print("SentenceTransformer model initialized successfully!")

# --- CHANGE 2: Nomic requires task-specific prefixes ---
def generate_embeddings(batch):
    prefixed_texts = ["search_document: " + text for text in batch["text"]]
    return {"embeddings": model.encode(prefixed_texts).tolist()}

if not os.path.exists(SAVE_DIR):
    print(f"'{SAVE_DIR}' does not exist. Proceeding to download the dataset...")
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    ds = load_dataset(DATASET, split="train")

    # --- CHANGE 3: Strip heavy columns to save laptop space ---
    print("Removing heavy image columns to save space...")
    
    # Ensure an ID column exists
    if "id" not in ds.column_names:
        ds = ds.add_column("id", range(len(ds)))
    
    # Keep strictly what you asked for (this drops the massive 'image' column)
    cols_to_keep = ["id", "conditioning_image", "text"]
    cols_to_remove = [col for col in ds.column_names if col not in cols_to_keep]
    ds = ds.remove_columns(cols_to_remove)

    print("Generating text embeddings (this might take a minute)...")
    ds_with_embeddings = ds.map(generate_embeddings, batched=True, batch_size=32)

    print("Building FAISS index...")
    ds_with_embeddings.add_faiss_index(column="embeddings")

    print("Saving FAISS index to disk...")
    ds_with_embeddings.save_faiss_index("embeddings", INDEX_PATH)

    ds_with_embeddings.drop_index("embeddings")

    print(f"Saving stripped-down dataset to '{SAVE_DIR}'...")
    ds_with_embeddings.save_to_disk(SAVE_DIR)
    
    ds_with_embeddings.load_faiss_index("embeddings", INDEX_PATH)
    print("Download and save complete!")

else:
    print(f"'{SAVE_DIR}' already exists. Loading dataset from local disk...")
    ds_with_embeddings = load_from_disk(SAVE_DIR)
    ds_with_embeddings.load_faiss_index("embeddings", INDEX_PATH)


# ==========================================
# --- SEARCHING THE VECTOR DATABASE ---
# ==========================================

query = "A singular man standing with arms crossed."
print(f"\nSearching for: '{query}'")

# --- CHANGE 4: Nomic requires the query prefix ---
query_embedding = np.array(model.encode("search_query: " + query))

k = 5 
scores, retrieved_examples = ds_with_embeddings.get_nearest_examples(
    "embeddings", 
    query_embedding, 
    k=k
)

best_match_texts = retrieved_examples["text"][0:5]
best_match_images = retrieved_examples["conditioning_image"][0:5] 
best_match_ids = retrieved_examples["id"][0:5] 

print("\n--- Search Results ---")
print(f"Similarity Score: {scores[0]:.4f} (Lower is closer/better in FAISS L2 distance)")

for i, text in enumerate(best_match_texts):
    print(f"Match {i+1} (ID: {best_match_ids[i]}): {text}")
    best_match_images[i].save(f"best_match_{i+1}.png")