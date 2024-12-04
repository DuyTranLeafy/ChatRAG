from flask import Flask, render_template, request, jsonify
from RAG import RAGPipeline, DocumentStore, CustomEmbeddings
from RAG.retrieval import Document
from Reader.WordReader import WordReader  # Đọc file Word
from dotenv import load_dotenv  # Để sử dụng biến môi trường
import os

# Xử lý lỗi thư viện đa luồng
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Hàm lấy danh sách các tệp từ thư mục
def get_file_paths_from_directory(directory, extensions=None):
    """
    Trả về danh sách đường dẫn đến các tệp trong thư mục, có thể lọc theo phần mở rộng.
    :param directory: Đường dẫn đến thư mục.
    :param extensions: Danh sách phần mở rộng cần lọc (ví dụ: [".docx", ".pdf"]).
    :return: Danh sách đường dẫn tệp.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if not extensions or any(file.endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths

# Khởi tạo Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    """Trang chủ hiển thị giao diện chatbot."""
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    """
    API nhận câu hỏi từ giao diện và trả về câu trả lời từ pipeline.
    """
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Câu hỏi không được để trống."}), 400

    try:
        # Trả lời câu hỏi từ pipeline
        answer = rag_pipeline.answer_question(question)
        return jsonify({"question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý câu hỏi: {str(e)}"}), 500

if __name__ == "__main__":
    # Tải biến môi trường
    load_dotenv()

    # Đường dẫn đến thư mục chứa tài liệu
    directory_path = "doc"  # Thay đổi nếu cần
    extensions = [".docx"]  # Có thể thêm các định dạng khác như ".pdf" nếu cần

    # Tìm tất cả các file phù hợp trong thư mục
    file_paths = get_file_paths_from_directory(directory_path, extensions)
    if not file_paths:
        print("❌ Không tìm thấy tài liệu trong thư mục. Vui lòng kiểm tra đường dẫn hoặc định dạng tệp.")
        exit()

    # Tạo đối tượng WordReader để xử lý tài liệu Word
    try:
        word_reader = WordReader(file_paths)
        sections = word_reader.process_documents()
    except Exception as e:
        print(f"❌ Lỗi khi xử lý tài liệu: {str(e)}")
        exit()

    if not sections:
        print("❌ Không tìm thấy nội dung trong các tài liệu được cung cấp.")
        exit()

    print(f"✅ Đã tải {len(sections)} đoạn nội dung từ tài liệu.")

    # Chuyển đổi các section thành đối tượng Document
    documents = [Document(content=section) for section in sections]

    if not documents:
        print("❌ Không có tài liệu nào được xử lý để đưa vào DocumentStore.")
        exit()

    print(f"✅ Đã chuẩn bị {len(documents)} tài liệu để lưu trữ.")

    # Khởi tạo mô hình nhúng tùy chỉnh
    try:
        embedding_model = CustomEmbeddings()
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo mô hình nhúng: {str(e)}")
        exit()

    # Khởi tạo DocumentStore
    try:
        store = DocumentStore(documents, embedding_model)
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo DocumentStore: {str(e)}")
        exit()

    # Lấy API key từ biến môi trường
    api_key = os.getenv("OPENAI_KEY")
    if not api_key:
        print("❌ Thiếu API key cho OpenAI. Vui lòng thiết lập biến môi trường 'OPENAI_KEY'.")
        exit()

    # Tạo đối tượng RAGPipeline
    try:
        rag_pipeline = RAGPipeline(documents=documents, api_key=api_key, model_name="gpt-3.5-turbo")
        print("✅ RAG Pipeline khởi tạo thành công.")
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo RAG Pipeline: {str(e)}")
        exit()

    # Chạy Flask app
    print("🚀 Đang khởi động Flask server...")
    app.run(debug=True)
