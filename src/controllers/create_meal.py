import uuid
from typing import Dict, Any
from enum import StrEnum
from pydantic import BaseModel, ValidationError

from ..utils.http import bad_request, created
from ..app_types.http import HTTPResponse, ProtectedHttpRequest
from ..repository.meal_repository import MealRepository
from ..services.storage import StorageService


class FileType(StrEnum):
    audio = "audio/m4a"
    jpeg = "image/jpeg"


class CreateMealSchema(BaseModel):
    file_type: FileType
    

class CreateMealController:

    def __init__(
        self,
        meal_repository: MealRepository,
        storage_service: StorageService,
    ):
        self.meal_repository = meal_repository
        self.storage_service = storage_service

    def _validate_body(self, body: Dict[str, Any]) -> CreateMealSchema:
        return CreateMealSchema(**body)
    
    async def handle(self, request: ProtectedHttpRequest) -> HTTPResponse:
        # Validate input body with Pydantic
        try:
            data = self._validate_body(body=request.get("body", {}))
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        # Generate file key
        file_id = uuid.uuid4()
        ext = ".m4a" if data.file_type == FileType.audio else ".jpg"
        file_key = f"{file_id}{ext}"
        
        presigned_url = self.storage_service.get_upload_url(
            file_key=file_key,
            content_type=data.file_type.value
        )

        meal = await self.meal_repository.create_meal(
            user_id=int(request["user_id"]),
            input_file_key=file_key,
            file_type=data.file_type.value,
        )

        return created(body={"meal": meal.id, "presigned_url": presigned_url})
