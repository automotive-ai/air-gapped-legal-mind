#Copyright of Automotive Artificial Intelligence (AAI) GmbH

import os
import torch
import pickle
from sentence_transformers import SentenceTransformer

RAW_TEXT_FOLDER = './data/documents' 
NEW_INDEX_PATH = './data/semantic_index.pkl'
MODEL_NAME = 'all-MiniLM-L6-v2'
DEVICE = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')

def build_lite_index():
    print(f"🚀 Building Cora Lite Index using {MODEL_NAME} on {DEVICE.upper()}...")
    
    model = SentenceTransformer(MODEL_NAME, device=DEVICE)
    documents, snippets = [], []
    
    file_list = [f for f in os.listdir(RAW_TEXT_FOLDER) if f.endswith('.txt')]
    print(f"📊 Found {len(file_list)} documents. Reading...")

    for filename in file_list:
        filepath = os.path.join(RAW_TEXT_FOLDER, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            snippet = f.read(2500).strip()
            if len(snippet) > 50:
                documents.append({'filename': filename, 'snippet': snippet})
                snippets.append(snippet)

    print(f"🧠 Generating embeddings...")
    embeddings = model.encode(snippets, batch_size=32, show_progress_bar=True, convert_to_tensor=True, device=DEVICE)

    os.makedirs(os.path.dirname(NEW_INDEX_PATH), exist_ok=True)
    with open(NEW_INDEX_PATH, 'wb') as f:
        pickle.dump({'model_name': MODEL_NAME, 'embeddings': embeddings.cpu(), 'documents': documents}, f)

    print(f"🎉 Index built and saved to {NEW_INDEX_PATH}!")

if __name__ == "__main__":
    build_lite_index()