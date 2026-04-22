import os
from typing import Dict, Any
from dotenv import load_dotenv

from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from ..clients.s3_client import s3_client


load_dotenv()


class StorageService:

    @classmethod
    def get_presigned_url(cls, method_type: str, file_key: str, content_type: str, expires_in: int = 600) -> str:
        # Generate pre-signed URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                method_type,
                Params={
                    "Bucket": os.getenv("BUCKET_NAME"),
                    "Key": file_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return presigned_url
        except ClientError as e:
            raise RuntimeError(f"Error generating presigned URL: {e}") from e
    
    @classmethod
    def get_object_from_bucket(cls, key: str) -> Dict[str, Any]:
        try:
            return s3_client.get_object(
                Bucket=os.getenv("BUCKET_NAME"),
                Key=key
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to fetch object in s3: {e}") from e
        
    @classmethod
    def read_object_content(cls, key: str) -> bytes:
        obj = cls.get_object_from_bucket(key)
        streaming_body: StreamingBody = obj["Body"]
        return streaming_body.read()