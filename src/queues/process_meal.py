from ..db.models.meals import MealStatus
from ..utils.http import bad_request
from ..repository.meal_repository import MealRepository


class ProcessMeal:

    def __init__(self, meal_repository: MealRepository):
        self.meal_repository = meal_repository

    async def process(self, file_key: str):
        meal = await self.meal_repository.get_meal_by_file_key(file_key)

        if not meal:
            return bad_request(body={"error": "Meal not found"})
            
        if meal.status.value in ["failed", "success"]:
            return
        
        await self.meal_repository.update_meal_status(
            meal=meal,
            status=MealStatus.processing
        )

        try:
            await self.meal_repository.update_meal_data(
                meal=meal,
                status=MealStatus.success,
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
        except Exception:
            await self.meal_repository.update_meal_status(
                meal=meal,
                status=MealStatus.failed
            )