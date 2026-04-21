import json
import asyncio

from ..queues.process_meal import ProcessMeal
from ..repository.meal_repository import MealRepository
from ..services.ai import AIClient
from ..services.storage import StorageService


async def async_handler(event):
    process_meal = ProcessMeal(
        meal_repository=MealRepository(),
        storage_service=StorageService(),
        ai_client=AIClient()
    )
    tasks = [
        process_meal.process(file_key=json.loads(record["body"])["file_key"])
        for record in event["Records"]
    ]
    await asyncio.gather(*tasks)


def handler(event, _):
    asyncio.run(async_handler(event=event))