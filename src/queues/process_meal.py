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

        # TODO: I need to figure out how to handle timeout in lambda to process meal properly
        try:
            meal_details = ""
            if meal.input_type.value == "audio":
                audio_data = self.storage_service.read_object_content(key=meal.input_file_key)
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

            print(meal_details)
                
            await self.meal_repository.update_meal_data(
                meal_id=meal.id,
                new_status=MealStatus.success,
                name="Café da manhã",
                icon="",
                foods=[
                    {
                        "name": "Pão",
                        "quantity": "2 fatias",
                        "calories": 100,
                        "proteins": 200,
                        "carbohydrates": 400,
                        "fats": 400,
                    }
                ]
            )
        except Exception as e:
            logging.error(f"Failed to process meal: {e}")
            await self.meal_repository.update_meal_status(
                meal_id=meal.id,
                new_status=MealStatus.failed
            )
        except TimeoutError:
            """Retry if lambda throws timeout error"""
            raise