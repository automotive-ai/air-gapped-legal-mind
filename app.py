# Copyright of Automotive Artificial Intelligence (AAI) GmbH
import streamlit as st
import torch
import pickle
import re
import os
from sentence_transformers import SentenceTransformer, util
import ollama

# --- CONFIGURATION ---
DEVICE = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu')
INDEX_PATH = 'data/semantic_index.pkl'
CONFIDENCE_THRESHOLD = 0.25
ANALYST_MODEL = 'qwen2.5'

st.set_page_config(page_title="Cora Legal AI (Lite)", page_icon="⚖️", layout="centered")
st.title("⚖️ Cora: Legal Intake Agent")
st.caption("Powered by Cora Open-Source (1,000 EU Documents)")

@st.cache_resource(show_spinner="Loading Semantic Legal Library...")
def load_library():
    if not os.path.exists(INDEX_PATH):
        st.error(f"Library not found. Please run `python build_lite_index.py` first.")
        st.stop()
    with open(INDEX_PATH, 'rb') as f:
        index_data = pickle.load(f)
    search_model = SentenceTransformer(index_data.get('model_name', 'all-MiniLM-L6-v2'))
    return index_data, search_model

index_data, search_model = load_library()

def extract_metadata(snippet, filename):
    lines = [line.strip() for line in snippet.split('\n') if line.strip()]
    title = " ".join([l for l in lines[:6] if len(l) > 5][:2]) or "Unknown Title"
    date_match = re.search(r"(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})|(\d{1,2}\.\d{1,2}\.\d{4})", snippet)
    date = date_match.group(0) if date_match else "Date Unknown"
    summary = next((line for i, line in enumerate(lines) if i > 3 and len(line) > 50), "No summary available.")
    return title[:97]+"...", date, summary

def rewrite_query(user_query, chat_history):
    recent_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-2:]]) if len(chat_history) > 1 else ""
    messages = [
        {"role": "system", "content": """You are an expert EU Legal Search Query Generator. 
        1. Expand acronyms (e.g., ALKS, GDPR). 
        2. Remove EU country names (EU law is union-wide).
        3. Be concise. Reply ONLY with the rewritten search query."""},
        {"role": "user", "content": f"History:\n{recent_history}\n\nLatest: {user_query}\n\nRewritten Query:"}
    ]
    return ollama.chat(model=ANALYST_MODEL, messages=messages)['message']['content'].strip()

def search_library(query):
    query_emb = search_model.encode(query, convert_to_tensor=True, device=DEVICE)
    library_embeddings = index_data['embeddings'].to(DEVICE) if isinstance(index_data['embeddings'], torch.Tensor) else torch.tensor(index_data['embeddings']).to(DEVICE)
    scores = util.cos_sim(query_emb, library_embeddings)[0]
    
    final_top_results = torch.topk(scores, k=3)
    found_docs = []
    for score, idx in zip(final_top_results.values, final_top_results.indices):
        if score > CONFIDENCE_THRESHOLD:
            doc = index_data['documents'][idx.item()]
            doc['clean_title'], doc['date'], doc['summary'] = extract_metadata(doc['snippet'], doc['filename'])
            found_docs.append(doc)
    return found_docs

def generate_legal_analysis(user_query, retrieved_docs):
    full_context = "\n\n".join([f"Title: {d['clean_title']}\nContent: {d['summary']}" for d in retrieved_docs])
    messages = [
        {"role": "system", "content": "You are Cora, an EU Legal AI. Answer the user's question using ONLY the provided EU documents. If the documents don't answer it, ask a clarifying question. Do not guess."},
        {"role": "user", "content": f"Question: {user_query}\n\nDocuments:\n{full_context}"}
    ]
    return ollama.chat(model=ANALYST_MODEL, messages=messages)['message']['content']

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Cora Lite. I can search 1,000 curated EU laws, including automotive regulations, GDPR, and the AI Act. How can I help?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("E.g., What are the homologation requirements for ALKS?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Cora is reasoning through the local library..."):
            smart_query = rewrite_query(prompt, st.session_state.messages)
            found_docs = search_library(smart_query)
        
            if not found_docs:
                response_text = "I couldn't find a direct match in the Lite Library. Try asking about a different regulation."
                st.write(response_text)
            else:
                try:
                    analysis = generate_legal_analysis(prompt, found_docs)
                    refs_text = "\n\n---\n**📚 References:**\n"
                    for i, doc in enumerate(found_docs, 1):
                        refs_text += f"{i}. **{doc['clean_title']}** \n*(Issued: {doc['date']} | ID: `{doc['filename']}`)*\n\n"
                    response_text = analysis + refs_text
                    st.write(response_text)
                except Exception as e:
                    response_text = f"Analysis Failed. Error: {e}"
                    st.error(response_text)
                    
        st.session_state.messages.append({"role": "assistant", "content": response_text})