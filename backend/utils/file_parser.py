import io
import pandas as pd

def parse_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Parses a CSV or Excel file content into a Pandas DataFrame.
    Handles encoding fallback for CSV files.
    """
    if filename.endswith(('.xlsx', '.xls')):
        # Parse Excel
        return pd.read_excel(io.BytesIO(file_content))
    else:
        # Parse CSV with fallback encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
        for encoding in encodings:
            try:
                return pd.read_csv(io.BytesIO(file_content), encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise ValueError(f"Error parsing CSV with encoding {encoding}: {str(e)}")
        
        # If all fail, try letting pandas autodetect or raise
        raise ValueError("Failed to decode CSV file with standard encodings (UTF-8, Latin-1, CP1252, UTF-16).")
