import os
import asyncio
import json

from dotenv import load_dotenv
from ..app_types.s3_events import S3Event
from ..clients.sqs_client import get_sqs_client

load_dotenv()

async def async_handler(event: S3Event):
    async with get_sqs_client() as client:
        tasks = [
            client.send_message(
                QueueUrl=os.getenv("MEALS_QUEUE_URL"),
                MessageBody=json.dumps({"file_key": record["s3"]["object"]["key"]}),
            )
            for record in event["Records"]
        ]
        await asyncio.gather(*tasks)

def handler(event: S3Event, _):
    asyncio.run(async_handler(event=event))