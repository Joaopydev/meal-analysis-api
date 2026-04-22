import io
from datetime import datetime

from openai import AsyncOpenAI


client = AsyncOpenAI()

class AIClient:

    @classmethod
    async def transcribe_audio(cls, audio_data: bytes, key: str) -> str:
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = key.split('/')[-1]

            transcript = await client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )
            return transcript.text
        except Exception as e:
            raise RuntimeError(f"Audio transcription failed ({e})")
        
    @classmethod
    async def get_meal_details_from_text(
        input: str,
        created_at: datetime,
    ) -> str:
        system_input = """
            You are a nutritionist and are seeing your patients. You must respond to them following the instructions below.

            Your role is:
            1.Give the meal a name and choose an emoji based on its time of day.
            2.Identify the foods present in the image.
            3.Estimate, for each identified food:
            - Food Name (in Portuguese)
            - Approximate Quantity (in grams or units)
            - Calories (kcal)
            - Carbohydrates (g)
            - Protein (g)
            - Fat (g)

            Be direct, objective, and avoid explanations (Do not include any explanation, text, or markdown.). Only return the data in JSON format below:

            {
                "name": "Dinner",
                "icon": "🍗",
                "foods": [
                    {
                        "name": "Arroz branco",
                        "quantity": "150g",
                        "calories": 100,
                        "carbohydrates": 42,
                        "proteins": 3.5,
                        "fats": 0.4,
                    },
                    {
                        "name": "Frango grelhado",
                        "quantity": "100g",
                        "calories": 165,
                        "carbohydrates": 32,
                        "proteins": 31,
                        "fats": 3.6,
                    },
                ]
            }
        """
        user_input = f"""
            Date: {created_at}
            Meal: {input}
        """
        try:
            response = await client.chat.completions.create(
                model="gtp-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_input
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to process meal details by text ({e})")
    
    @classmethod
    async def get_meal_details_from_image(cls, image_url: str, created_at: datetime) -> str:
        system_input = f"""
            Meal Date: {created_at}
            
            You are a nutritionist specializing in food image analysis. The following image was taken by a 
            user to document a meal.

            Your role is:
            1.Give the meal a name and choose an emoji based on its time of day.
            2.Identify the foods present in the image.
            3.Estimate, for each identified food:
            - Food Name (in Portuguese)
            - Approximate Quantity (in grams or units)
            - Calories (kcal)
            - Carbohydrates (g)
            - Protein (g)
            - Fat (g)

            Consider proportions and visible volume to estimate the quantity. When there is uncertainty about the exact type of food (e.g., type of rice, cut of meat), use the most common type. Be direct, objective, and avoid explanations(Do not include any explanation, text, or markdown.). Only return the data in JSON format below:

            {{
                "name": "Dinner",
                "icon": "🍗",
                "foods": [
                    {{
                        "name": "Arroz branco",
                        "quantity": "150g",
                        "calories": 100,
                        "carbohydrates": 42,
                        "proteins": 3.5,
                        "fats": 0.4
                    }},
                    {{
                        "name": "Frango grelhado",
                        "quantity": "100g",
                        "calories": 165,
                        "carbohydrates": 32,
                        "proteins": 31,
                        "fats": 3.6
                    }}
                ]
            }}
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_input
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to process meal by image ({e})")