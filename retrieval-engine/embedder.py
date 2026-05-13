import torch
from transformers import AutoModel, AutoTokenizer
import faiss
import numpy as np

class DocumentEmbedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.model.to(self.device)
        
        # Initialize FAISS Index
        self.embedding_dim = self.model.config.hidden_size
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        
        # Load some dummy data
        self._load_dummy_data()

    def _load_dummy_data(self):
        docs = [
            "Synapse is an enterprise AI solution designed to handle internal company documents.",
            "The retrieval latency for Synapse must be under 200ms.",
            "Synapse uses PyTorch and FAISS for its core vector retrieval engine.",
            "The Model Context Protocol (MCP) standardizes context delivery to the LLM.",
            "React and TypeScript are used to build the responsive Web GUI."
        ]
        self.add_documents(docs)

    @torch.no_grad()
    def embed(self, texts):
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(self.device)
        outputs = self.model(**inputs)
        
        # Mean pooling
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        embeddings = sum_embeddings / sum_mask
        
        return torch.nn.functional.normalize(embeddings, p=2, dim=1).cpu().numpy()

    def add_documents(self, docs):
        if not docs:
            return
        vectors = self.embed(docs)
        self.index.add(vectors)
        self.documents.extend(docs)

    def search(self, query, top_k=3):
        if self.index.ntotal == 0:
            return []
            
        query_vector = self.embed([query])
        
        # Adjust top_k if we have fewer documents than requested
        k = min(top_k, self.index.ntotal)
        
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        return results

# Global singleton
embedder = DocumentEmbedder()
