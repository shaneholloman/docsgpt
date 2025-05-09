"""Tabular parser.

Contains parsers for tabular data files.

"""
from pathlib import Path
from typing import Any, Dict, List, Union

from application.parser.file.base_parser import BaseParser


class CSVParser(BaseParser):
    """CSV parser.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

    """

    def __init__(self, *args: Any, concat_rows: bool = True, **kwargs: Any) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows

    def _init_parser(self) -> Dict:
        """Init parser."""
        return {}

    def parse_file(self, file: Path, errors: str = "ignore") -> Union[str, List[str]]:
        """Parse file.

        Returns:
            Union[str, List[str]]: a string or a List of strings.

        """
        try:
            import csv
        except ImportError:
            raise ValueError("csv module is required to read CSV files.")
        text_list = []
        with open(file, "r") as fp:
            csv_reader = csv.reader(fp)
            for row in csv_reader:
                text_list.append(", ".join(row))
        if self._concat_rows:
            return "\n".join(text_list)
        else:
            return text_list


class PandasCSVParser(BaseParser):
    r"""Pandas-based CSV parser.

    Parses CSVs using the separator detection from Pandas `read_csv`function.
    If special parameters are required, use the `pandas_config` dict.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

        col_joiner (str): Separator to use for joining cols per row.
            Set to ", " by default.

        row_joiner (str): Separator to use for joining each row.
            Only used when `concat_rows=True`.
            Set to "\n" by default.

        pandas_config (dict): Options for the `pandas.read_csv` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            for more information.
            Set to empty dict by default, this means pandas will try to figure
            out the separators, table head, etc. on its own.
            
        header_period (int): Controls how headers are included in output:
            - 0: Headers only at the beginning
            - 1: Headers in every row
            - N > 1: Headers every N rows
            
        header_prefix (str): Prefix for header rows. Default is "HEADERS: ".
    """

    def __init__(
            self,
            *args: Any,
            concat_rows: bool = True,
            col_joiner: str = ", ",
            row_joiner: str = "\n",
            pandas_config: dict = {},
            header_period: int = 20,
            header_prefix: str = "HEADERS: ",
            **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows
        self._col_joiner = col_joiner
        self._row_joiner = row_joiner
        self._pandas_config = pandas_config
        self._header_period = header_period
        self._header_prefix = header_prefix

    def _init_parser(self) -> Dict:
        """Init parser."""
        return {}

    def parse_file(self, file: Path, errors: str = "ignore") -> Union[str, List[str]]:
        """Parse file."""
        try:
            import pandas as pd
        except ImportError:
            raise ValueError("pandas module is required to read CSV files.")

        df = pd.read_csv(file, **self._pandas_config)
        headers = df.columns.tolist()
        header_row = f"{self._header_prefix}{self._col_joiner.join(headers)}"

        if not self._concat_rows:
            return df.apply(
                lambda row: (self._col_joiner).join(row.astype(str).tolist()), axis=1
            ).tolist()
        
        text_list = []
        if self._header_period != 1:
            text_list.append(header_row)
        
        for i, row in df.iterrows():
            if (self._header_period > 1 and i > 0 and i % self._header_period == 0):
                text_list.append(header_row)
            text_list.append(self._col_joiner.join(row.astype(str).tolist()))
            if self._header_period == 1 and i < len(df) - 1:
                text_list.append(header_row)

        return self._row_joiner.join(text_list)


class ExcelParser(BaseParser):
    r"""Excel (.xlsx) parser.

    Parses Excel files using Pandas `read_excel` function.
    If special parameters are required, use the `pandas_config` dict.

    Args:
        concat_rows (bool): whether to concatenate all rows into one document.
            If set to False, a Document will be created for each row.
            True by default.

        col_joiner (str): Separator to use for joining cols per row.
            Set to ", " by default.

        row_joiner (str): Separator to use for joining each row.
            Only used when `concat_rows=True`.
            Set to "\n" by default.

        pandas_config (dict): Options for the `pandas.read_excel` function call.
            Refer to https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
            for more information.
            Set to empty dict by default, this means pandas will try to figure
            out the table structure on its own.
            
        header_period (int): Controls how headers are included in output:
            - 0: Headers only at the beginning (default)
            - 1: Headers in every row
            - N > 1: Headers every N rows
            
        header_prefix (str): Prefix for header rows. Default is "HEADERS: ".
    """

    def __init__(
            self,
            *args: Any,
            concat_rows: bool = True,
            col_joiner: str = ", ",
            row_joiner: str = "\n",
            pandas_config: dict = {},
            header_period: int = 20,
            header_prefix: str = "HEADERS: ",
            **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._concat_rows = concat_rows
        self._col_joiner = col_joiner
        self._row_joiner = row_joiner
        self._pandas_config = pandas_config
        self._header_period = header_period
        self._header_prefix = header_prefix

    def _init_parser(self) -> Dict:
        """Init parser."""
        return {}

    def parse_file(self, file: Path, errors: str = "ignore") -> Union[str, List[str]]:
        """Parse file."""
        try:
            import pandas as pd
        except ImportError:
            raise ValueError("pandas module is required to read Excel files.")

        df = pd.read_excel(file, **self._pandas_config)
        headers = df.columns.tolist()
        header_row = f"{self._header_prefix}{self._col_joiner.join(headers)}"
        
        if not self._concat_rows:
            return df.apply(
                lambda row: (self._col_joiner).join(row.astype(str).tolist()), axis=1
            ).tolist()
        
        text_list = []
        if self._header_period != 1:
            text_list.append(header_row)

        for i, row in df.iterrows():
            if (self._header_period > 1 and i > 0 and i % self._header_period == 0):
                text_list.append(header_row)
            text_list.append(self._col_joiner.join(row.astype(str).tolist()))
            if self._header_period == 1 and i < len(df) - 1:
                text_list.append(header_row)
        return self._row_joiner.join(text_list)