import os
import pickle
import torch
import faiss
import warnings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS


class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata is not None else {}


class CustomEmbeddings:
    def __init__(self, model_name='vinai/phobert-base'):
        from transformers import AutoTokenizer, AutoModel
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256, padding="max_length")
        if 'token_type_ids' in inputs and 'token_type_ids' not in self.model.forward.__code__.co_varnames:
            del inputs['token_type_ids']
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()


class DocumentStore:
    def __init__(self, documents, embedding_model, store_file='vector_store.pkl', index_file='faiss_index.bin'):
        self.store_file = store_file
        self.index_file = index_file
        self.embedding_model = embedding_model

        if os.path.exists(store_file) and os.path.exists(index_file):
            self.vector_store = self.load_vector_store()
        else:
            if isinstance(documents[0], str):
                documents = [Document(content=doc) for doc in documents]

            embeddings = [self.embedding_model.embed(doc.page_content) for doc in documents]
            embeddings = torch.tensor(embeddings).numpy()

            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)

            docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(documents)})
            index_to_docstore_id = {i: str(i) for i in range(len(documents))}

            self.vector_store = FAISS(index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id,
                                      embedding_function=self.embedding_model.embed)
            self.save_vector_store()

    def save_vector_store(self):
        faiss.write_index(self.vector_store.index, self.index_file)
        with open(self.store_file, 'wb') as f:
            pickle.dump((self.vector_store.docstore, self.vector_store.index_to_docstore_id), f)

    def load_vector_store(self):
        index = faiss.read_index(self.index_file)
        with open(self.store_file, 'rb') as f:
            docstore, index_to_docstore_id = pickle.load(f)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return FAISS(index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id,
                         embedding_function=self.embedding_model.embed)

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedding_model.embed(query).reshape(1, -1)
        distances, indices = self.vector_store.index.search(query_embedding, top_k)
        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            doc_id = self.vector_store.index_to_docstore_id[idx]
            doc = self.vector_store.docstore.search(doc_id)
            results.append((doc, distances[0][indices[0].tolist().index(idx)]))
        return results
