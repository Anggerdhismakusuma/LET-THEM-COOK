from fastapi import APIRouter

router = APIRouter()

@router.get("/{food_name}")
async def get_recipe(food_name: str):
    # TODO: fetch recipe from recipes.json
    return {
        "food": food_name,
        "recipe": "This is a dummy recipe for: " + food_name,
        "calories": "123 kcal"
    }