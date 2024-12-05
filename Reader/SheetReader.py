import pandas as pd
import os


class TextWrapper:
    """
    Lớp để bọc dữ liệu và cung cấp thuộc tính `.text`.
    """
    def __init__(self, content):
        self.text = content

    def __str__(self):
        return self.text  # Để in ra nội dung trực tiếp


class SheetReader:
    def __init__(self, file_paths):
        self.file_paths = file_paths

    def read_excel_file(self, file_path):
        """
        Đọc file Excel và trả về dữ liệu từ tất cả các sheet.
        :param file_path: Đường dẫn đến file Excel.
        :return: Dictionary chứa tên sheet và dữ liệu của mỗi sheet.
        """
        try:
            # Đọc tất cả các sheet trong file Excel
            sheets = pd.read_excel(file_path, sheet_name=None)  # Đọc tất cả các sheet
            return sheets
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {file_path}: {str(e)}")
            return {}

    def split_by_format(self, data):
        """
        Phân chia dữ liệu của Excel thành các phần (section) dưới dạng text (văn bản).
        :param data: Dữ liệu của các sheet.
        :return: Danh sách các section dưới dạng đối tượng TextWrapper.
        """
        sections = []
        for sheet_name, sheet_data in data.items():
            print(f"Đang xử lý sheet: {sheet_name}")

            # Kiểm tra kiểu dữ liệu của sheet_data
            if isinstance(sheet_data, pd.DataFrame):
                print(f"Dữ liệu của sheet là DataFrame.")

                # Chuyển DataFrame thành text (văn bản)
                section = f"Sheet: {sheet_name}\n"
                section += sheet_data.to_string(index=False)  # Chuyển DataFrame thành chuỗi văn bản

                # Bọc dữ liệu bằng TextWrapper
                sections.append(TextWrapper(section))
            elif isinstance(sheet_data, str):
                # Nếu sheet_data là chuỗi, bọc vào TextWrapper
                section = f"Sheet: {sheet_name}\n{sheet_data}"
                sections.append(TextWrapper(section))
            else:
                # Nếu không phải DataFrame hoặc chuỗi, chuyển thành chuỗi trước khi bọc
                section = f"Sheet: {sheet_name}\n{str(sheet_data)}"
                sections.append(TextWrapper(section))

        return sections

    def process_documents(self):
        """
        Xử lý tất cả các file Excel được cung cấp và trích xuất dữ liệu từ các sheet.
        :return: Danh sách các sections dưới dạng đối tượng TextWrapper.
        """
        all_sections = []
        try:
            for file_path in self.file_paths:
                print(f"Đang xử lý file: {file_path}")
                if os.path.exists(file_path):
                    sheets = self.read_excel_file(file_path)
                    if not sheets:
                        print(f"⚠️ Không có sheet nào trong file {file_path}")
                        continue

                    sections = self.split_by_format(sheets)

                    # Chỉ lấy các sections có nhiều dữ liệu
                    filtered_sections = [section for section in sections if len(section.text.splitlines()) > 1]
                    all_sections.extend(filtered_sections)

            return all_sections
        except Exception as e:
            print(f"❌ Lỗi khi xử lý tài liệu Excel: {str(e)}")
            return []
