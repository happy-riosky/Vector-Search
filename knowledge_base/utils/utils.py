from pathlib import Path
import pandas as pd
import numpy as np
import uuid

from .logger import logger

def load_data(path: Path) -> pd.DataFrame:
    """
    从指定路径加载数据，支持 .pkl、.csv、.npy、.parquet 和 .xlsx 文件。

    Args:
        path (Path): 数据文件的路径。

    Returns:
        pd.DataFrame: 加载的数据。
            - 对于 .pkl 和 .csv 文件，返回 pd.DataFrame。
            - 对于 .npy 文件，将转换为 pd.DataFrame 返回。
            - 对于 .xlsx 文件，返回 pd.DataFrame。
            - 如果文件不存在或格式不支持，抛出异常。
    """
    # 确保 path 是 Path 对象
    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = path.suffix.lower()

    try:
        if suffix == ".pkl":
            try:
                data = pd.read_pickle(path)
            except Exception as e:
                logger.error(f"Failed to load {path}: {e}", exc_info=True)
                logger.warning("Return an empty DataFrame")
                return pd.DataFrame()
            if not isinstance(data, pd.DataFrame):
                if isinstance(data, pd.Series):
                    data = data.to_frame()
                    logger.info(f"Converted Series to DataFrame from {path}")
                else:
                    logger.error(
                        f"Loaded .pkl data is not a DataFrame or Series: {type(data)}"
                    )
                    raise TypeError(f"Expected DataFrame or Series, got {type(data)}")
        elif suffix == ".csv":
            data = pd.read_csv(path)
        elif suffix == ".npy":
            array = np.load(path)
            data = pd.DataFrame(array)
            logger.info(f"Converted NumPy array to DataFrame from {path}")
        elif suffix == ".xlsx":
            data = pd.read_excel(path)
            logger.info(f"Loaded Excel file from: {path}")
        elif suffix == ".parquet":
            data = pd.read_parquet(path)
            logger.info(f"Loaded Parquet file from: {path}")
        else:
            logger.error(f"Unsupported format: {suffix} for {path}")
            raise ValueError(f"Unsupported file format: {suffix}")

        logger.info(f"DataFrame loaded from: {path}")
        return data

    except Exception as e:
        logger.error(f"Failed to load {path}: {e}", exc_info=True)
        raise

def get_content_based_uuid(content: str) -> str:
    """基于字符串内容生成固定 UUID（使用 SHA-1 哈希）"""
    namespace = uuid.NAMESPACE_DNS  # 可以使用任意命名空间（如 NAMESPACE_URL）
    return str(uuid.uuid5(namespace, content))
