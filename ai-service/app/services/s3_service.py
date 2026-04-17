import os
import tempfile
import boto3
import logging
from urllib.parse import urlparse
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
s3_client = boto3.client("s3")


def download_s3_uri_to_temp(s3_uri: str) -> str:
    """
    Parse S3 URI (s3://bucket-name/object-key) và tải file về máy.
    Trả về đường dẫn file tạm vật lý.
    """
    logger.info(f"Đang xử lý S3 URI: {s3_uri}")

    try:
        # Parse s3://bucket-name/path/to/file.mp3
        parsed_url = urlparse(s3_uri)
        if parsed_url.scheme != "s3":
            raise ValueError(f"URL không đúng chuẩn S3 URI: {s3_uri}")

        bucket_name = parsed_url.netloc
        object_key = parsed_url.path.lstrip("/")

        fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        logger.info(f"Đang tải {object_key} từ bucket {bucket_name}...")

        # Boto3 download
        s3_client.download_file(bucket_name, object_key, temp_path)

        logger.info(f"Tải thành công! File lưu tại: {temp_path}")
        return temp_path

    except ClientError as e:
        logger.error(f"Lỗi kết nối AWS S3: {e}")
        raise RuntimeError(f"S3 Download Error: {e}")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi tải file: {e}")
        raise RuntimeError(f"Unexpected Error: {e}")
