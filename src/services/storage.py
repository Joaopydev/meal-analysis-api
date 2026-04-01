import os
from dotenv import load_dotenv

from botocore.exceptions import ClientError
from ..clients.s3_client import s3_client


load_dotenv()


class StorageService:

    @classmethod
    def get_presigned_url(cls, file_key: str, content_type: str, expires_in: int = 600):
        # Generate pre-signed URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": os.getenv("BUCKET_NAME"),
                    "Key": file_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return presigned_url
        except ClientError as e:
            raise RuntimeError(f"Error generating presigned URL: {e}")