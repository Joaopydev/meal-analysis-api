import json
import logging

from ..db.models.meals import MealStatus
from ..utils.http import bad_request
from ..repository.meal_repository import MealRepository
from ..services.storage import StorageService
from ..services.ai import AIClient


class ProcessMeal:

    def __init__(self, meal_repository: MealRepository, storage_service: StorageService, ai_client: AIClient):
        self.meal_repository = meal_repository
        self.storage_service = storage_service
        self.ai_client = ai_client

    async def process(self, file_key: str):
        meal = await self.meal_repository.get_meal_by_file_key(file_key)

        if not meal:
            return bad_request(body={"error": "Meal not found"})
            
        if meal.status.value in ["failed", "success"]:
            return
        
        await self.meal_repository.update_meal_status(
            meal_id=meal.id,
            new_status=MealStatus.processing
        )
        try:
            meal_details = ""
            if meal.input_type.value == "audio":
                audio_data = await self.storage_service.read_object_content(key=meal.input_file_key)
                transcription = await self.ai_client.transcribe_audio(
                    audio_data=audio_data,
                    key=file_key
                )
                meal_details = await self.ai_client.get_meal_details_from_text(
                    input=transcription,
                    created_at=meal.created_at
                )
            elif meal.input_type.value == "picture":
                image_url = self.storage_service.get_download_url(file_key)
                meal_details = await self.ai_client.get_meal_details_from_image(
                    image_url=image_url,
                    created_at=meal.created_at,
                )
            parse_meal_details = json.loads(meal_details)
            await self.meal_repository.update_meal_data(
                meal_id=meal.id,
                new_status=MealStatus.success,
                name=parse_meal_details.get("name", ""),
                icon=parse_meal_details.get("icon", ""),
                foods=parse_meal_details.get("foods", []),
            )
        except TimeoutError as e:
            """Retry if lambda throws timeout error"""
            logging.error(f"Timeout error occurred while processing meal: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to process meal: {e}")
            await self.meal_repository.update_meal_status(
                meal_id=meal.id,
                new_status=MealStatus.failed
            )