from fastapi import FastAPI, Request
from langchain_ollama import ChatOllama
import json
import re

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

    prompt = f"""
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

{{
  "dish": "Dish name",
  "meal_type": "{meal_type}",
  "menu": ["item 1", "item 2", "item 3"],
  "notes": ["health advice or dietary context"],
  "calories": 0,
  "protein": 0.0,
  "carbs": 0.0,
  "fat": 0.0,
  "sodium": 0.0
}}

Do NOT wrap the JSON in code blocks or markdown like ```json. Just return plain JSON.
"""

    print("calling...")
    response = model.invoke(prompt)
    print("raw response:", response)

    # 클린업: ```json ... ``` 제거
    cleaned = str(response).strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"```", "", cleaned)
        cleaned = cleaned.strip()

    try:
        result_json = json.loads(cleaned)
        return result_json
    except Exception:
        return {"error": "Model did not return valid JSON", "raw": cleaned}
