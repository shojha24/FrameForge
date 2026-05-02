from huggingface_hub import login, whoami
from datasets import load_dataset, load_from_disk
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import os
import dotenv

dotenv.load_dotenv()

DATASET = "raulc0399/open_pose_controlnet"
SAVE_DIR = "./open_pose_controlnet_dataset"
INDEX_PATH = os.path.join(SAVE_DIR, "index.faiss") # Path for the separate FAISS file

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
model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=device)
print("SentenceTransformer model initialized successfully!")

# Define the embedding function
def generate_embeddings(batch):
    return {"embeddings": model.encode(batch["text"]).tolist()}

if not os.path.exists(SAVE_DIR):
    print(f"'{SAVE_DIR}' does not exist. Proceeding to download the dataset...")
    os.mkdir(SAVE_DIR)
    
    ds = load_dataset(DATASET, split="train")

    print("Generating text embeddings (this might take a minute)...")
    ds_with_embeddings = ds.map(generate_embeddings, batched=True, batch_size=32)

    print("Building FAISS index...")
    ds_with_embeddings.add_faiss_index(column="embeddings")

    # 1. Save the FAISS index structure to a file FIRST
    print("Saving FAISS index to disk...")
    ds_with_embeddings.save_faiss_index("embeddings", INDEX_PATH)

    # 2. Drop the index from memory so Hugging Face allows us to save the dataset
    ds_with_embeddings.drop_index("embeddings")

    # 3. NOW save the dataset
    print(f"Saving dataset with embeddings to '{SAVE_DIR}'...")
    ds_with_embeddings.save_to_disk(SAVE_DIR)
    
    # 4. Re-attach the index to the dataset in memory so we can search it below
    ds_with_embeddings.load_faiss_index("embeddings", INDEX_PATH)
    print("Download and save complete!")


else:
    print(f"'{SAVE_DIR}' already exists. Loading dataset from local disk...")
    ds_with_embeddings = load_from_disk(SAVE_DIR)
    ds_with_embeddings.load_faiss_index("embeddings", INDEX_PATH)


# ==========================================
# --- SEARCHING THE VECTOR DATABASE ---
# ==========================================

query = "A man standing with arms crossed."
print(f"\nSearching for: '{query}'")

query_embedding = np.array(model.encode(query))

k = 5 
scores, retrieved_examples = ds_with_embeddings.get_nearest_examples(
    "embeddings", 
    query_embedding, 
    k=k
)

best_match_texts = retrieved_examples["text"][0:5]
best_match_images = retrieved_examples["conditioning_image"][0:5] 

print("\n--- Search Results ---")
print(f"Similarity Score: {scores[0]:.4f} (Lower is closer/better in FAISS L2 distance)")

for i, text in enumerate(best_match_texts):
    print(f"Match {i+1}: {text}")
    best_match_images[i].save(f"best_match_{i+1}.png")  # Save the image to disk: