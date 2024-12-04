from pathlib import Path
from typing import Any, Dict, List, Optional
from fsspec import AbstractFileSystem
import importlib

import pandas as pd


class TabularParser:
    """A class to parse tabular data from CSV and Excel files."""

    def __init__(
            self,
            concat_rows: bool = True,
            col_joiner: str = ", ",
            row_joiner: str = "\n",
            pandas_config: dict = {},
            sheet_name=None
    ) -> None:
        """Init params."""
        self._concat_rows = concat_rows
        self._col_joiner = col_joiner
        self._row_joiner = row_joiner
        self._pandas_config = pandas_config
        self._sheet_name = sheet_name

    def load_data(
            self,
            file: Path,
            extra_info: Optional[Dict] = None,
            fs: Optional[AbstractFileSystem] = None,
    ) -> List[Dict[str, Any]]:
        """Parse file based on its extension and return a list of document-like dicts."""
        extension = file.suffix.lower()
        if extension == '.csv':
            return self._load_csv(file, extra_info, fs)
        elif extension in ['.xls', '.xlsx']:
            return self._load_excel(file, extra_info, fs)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

    def _load_csv(
            self,
            file: Path,
            extra_info: Optional[Dict] = None,
            fs: Optional[AbstractFileSystem] = None,
    ) -> List[Dict[str, Any]]:
        """Parse CSV file."""
        try:
            import csv
        except ImportError:
            raise ImportError("csv module is required to read CSV files.")

        text_list = []
        if fs:
            with fs.open(file) as fp:
                csv_reader = csv.reader(fp)
                for row in csv_reader:
                    text_list.append(", ".join(row))
        else:
            with open(file) as fp:
                csv_reader = csv.reader(fp)
                for row in csv_reader:
                    text_list.append(", ".join(row))

        metadata = {"filename": file.name, "extension": file.suffix}
        if extra_info:
            metadata.update(extra_info)

        if self._concat_rows:
            return [{"text": "\n".join(text_list), "metadata": metadata}]
        else:
            return [{"text": text, "metadata": metadata} for text in text_list]

    def _load_excel(
            self,
            file: Path,
            extra_info: Optional[Dict] = None,
            fs: Optional[AbstractFileSystem] = None,
    ) -> List[Dict[str, Any]]:
        """Parse Excel file."""
        openpyxl_spec = importlib.util.find_spec("openpyxl")
        if openpyxl_spec is None:
            raise ImportError(
                "Please install openpyxl to read Excel files. You can install it with 'pip install openpyxl'")

        if fs:
            with fs.open(file) as f:
                dfs = pd.read_excel(f, self._sheet_name, **self._pandas_config)
        else:
            dfs = pd.read_excel(file, self._sheet_name, **self._pandas_config)

        documents = []
        if isinstance(dfs, pd.DataFrame):
            df = dfs.fillna("")
            text_list = df.astype(str).apply(lambda row: " ".join(row.values), axis=1).tolist()
            if self._concat_rows:
                documents.append({"text": "\n".join(text_list), "metadata": extra_info or {}})
            else:
                documents.extend([{"text": text, "metadata": extra_info or {}} for text in text_list])
        else:
            for df in dfs.values():
                df = df.fillna("")
                text_list = df.astype(str).apply(lambda row: " ".join(row), axis=1).tolist()
                if self._concat_rows:
                    documents.append({"text": "\n".join(text_list), "metadata": extra_info or {}})
                else:
                    documents.extend([{"text": text, "metadata": extra_info or {}} for text in text_list])

        return documents
