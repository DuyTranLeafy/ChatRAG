from RAG.argument import PROMPT_TEMPLATE, MAX_CONTEXT_TOKENS
from RAG.retrieval import CustomEmbeddings, DocumentStore
from RAG.generation import LanguageModel


class RAGPipeline:
    def __init__(self, documents, api_key, model_name='gpt-3.5-turbo'):
        self.embedding_model = CustomEmbeddings()
        self.document_store = DocumentStore(documents, self.embedding_model)
        self.language_model = LanguageModel(api_key=api_key, model_name=model_name)
        self.prompt_template = PROMPT_TEMPLATE
        self.max_context_tokens = MAX_CONTEXT_TOKENS

    def truncate_context(self, context, max_tokens):
        tokens = context.split()
        return ' '.join(tokens[:max_tokens])

    def answer_question(self, question):
        retriever = self.document_store
        results = retriever.retrieve(question)
        # Đảm bảo các tài liệu trong kết quả là chuỗi văn bản và ghép thành ngữ cảnh
        for doc, score in results:
            # In ra từng chunk và điểm số của nó
            print(f"Chunk: {doc.page_content}")
            print(f"Score: {score}")
        context = " ".join(str(doc.page_content) for doc, _ in results)
        context = self.truncate_context(context, self.max_context_tokens)
        prompt = self.prompt_template.format(context=context, question=question)
        return self.language_model.get_response(prompt)
