from docx import Document as DocxDocument
import os

class WordReader:
    def __init__(self, file_paths):
        self.file_paths = file_paths

    def read_word_document(self, file_path):
        """
        Đọc tài liệu Word và trả về danh sách các đoạn văn.
        :param file_path: Đường dẫn đến file Word.
        :return: Danh sách các đoạn văn.
        """
        try:
            doc = DocxDocument(file_path)
            paragraphs = [para for para in doc.paragraphs if para.text.strip()]  # Lọc đoạn văn không rỗng
            return paragraphs
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {file_path}: {str(e)}")
            return []

    def is_bold_and_uppercase(self, paragraph):
        """
        Kiểm tra xem đoạn văn có chứa văn bản in đậm và viết hoa toàn bộ không.
        :param paragraph: Đối tượng đoạn văn của docx.
        :return: True nếu đoạn văn có định dạng in đậm và viết hoa toàn bộ, False nếu không.
        """
        text = paragraph.text.strip()
        return any(run.bold for run in paragraph.runs) and any(word.isupper() for word in text.split())

    def split_by_format(self, paragraphs):
        """
        Phân đoạn văn bản dựa trên định dạng tiêu đề.
        :param paragraphs: Danh sách các đoạn văn từ tài liệu Word.
        :return: Danh sách các section được phân tách.
        """
        sections = []
        current_section = []

        for paragraph in paragraphs:
            if self.is_bold_and_uppercase(paragraph):
                # Nếu gặp tiêu đề mới, chỉ tách khi tiêu đề có một sự thay đổi rõ rệt
                if current_section:
                    sections.append("\n".join([p.text.strip() for p in current_section if p.text.strip()]))
                    current_section = []
                current_section.append(paragraph)  # Tiêu đề là phần đầu tiên của section mới
            else:
                current_section.append(paragraph)

        # Thêm section cuối cùng (nếu có)
        if current_section:
            sections.append("\n".join([p.text.strip() for p in current_section if p.text.strip()]))

        return sections

    def process_documents(self):
        """
        Xử lý tất cả các file Word được cung cấp, trích xuất tất cả nội dung một lần.
        """
        try:
            all_paragraphs = [
                para
                for file_path in self.file_paths if os.path.exists(file_path)
                for para in self.read_word_document(file_path)
            ]
            sections = self.split_by_format(all_paragraphs)

            # Nếu số lượng sections quá nhiều, chỉ lấy những section quan trọng
            # (Giảm bớt các section không cần thiết)
            filtered_sections = [section.strip() for section in sections if len(section.splitlines()) > 1]
            return filtered_sections
        except Exception as e:
            print(f"❌ Lỗi khi xử lý tài liệu: {str(e)}")
            return []
