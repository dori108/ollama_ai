from fastapi import FastAPI, Request
from langchain_ollama import ChatOllama
import json

app = FastAPI()
model = ChatOllama(model="gemma:7b-instruct", temperature=0)


@app.post("/generate-meal")
async def generate_meal(request: Request):
    body = await request.json()

    user = body["user_info"]
    meal_type = body["meal_type"]
    consumed = body["consumed_so_far"]

    remaining = {
        "protein": 50 - consumed.get("protein", 0),
        "fat": 70 - consumed.get("fat", 0),
        "carbohydrates": 300 - consumed.get("carbs", 0),
        "sodium": 2300 - consumed.get("sodium", 0),
    }

    prompt = """
You are a professional nutritionist.

User Information:
- Age: {user['age']}
- Gender: {user['gender']}
- Height: {user['height']}cm
- Weight: {user['weight']}kg
- Ingredients available: {', '.join(user['ingredients'])}
- Health notes: {', '.join(user['disease'])}

Remaining daily intake allowance:
- Protein: {remaining['protein']}g
- Fat: {remaining['fat']}g
- Carbohydrates: {remaining['carbohydrates']}g
- Sodium: {remaining['sodium']}mg

Please provide a meal plan in the following **strict JSON format only**:

{
  "dish": "Dish name",
  "meal_type": _selectedMealType,
  "menu": ["item 1", "item 2", "item 3"],
  "notes": ["health advice or dietary context"],
  "calories": 0,
  "protein": 0.0,
  "carbs": 0.0,
  "fat": 0.0,
  "sodium":0.0
}

Do not add any text outside the JSON. Only return a complete and valid JSON object.
"""

    print("calling...")
    response = model.invoke(prompt)
    try:
        result_json = json.loads(str(response))
        return result_json
    except Exception:
        return {"error": "Model did not return valid JSON", "raw": str(response)}
    print("result:")
    print(response)
    print("loading...")