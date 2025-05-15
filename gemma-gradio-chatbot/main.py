from fastapi import FastAPI, Request
from ollama import Client
import json
import re
import os

app = FastAPI()
client = Client()

def calculate_base_nutrients(user):
    if user["gender"].lower() == "male":
        protein = max(56, 0.8 * user["weight"])
        fat = 70
        carbs = 310
        sodium = 2300
    else:
        protein = max(46, 0.8 * user["weight"])
        fat = 60
        carbs = 260
        sodium = 2300

    if user["age"] > 65:
        protein *= 0.9
        fat *= 0.9
        carbs *= 0.9

    return {
        "protein": protein,
        "fat": fat,
        "carbohydrates": carbs,
        "sodium": sodium,
    }


# JSON 데이터 로드
def load_disease_constraints():
    file_path = os.path.join("data", "disease_limits.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/generate-meal")
async def generate_meal(request: Request):
    body = await request.json()

    user = body["user_info"]
    disease_constraints = load_disease_constraints()
    
    # user["disease"] 예: ["Phenylketonuria (PKU)", "Galactosemia"]
    matched_constraints = [d for d in disease_constraints if d["diseaseName"] in user.get("disease", [])]
    
    # 제한 기준 중 가장 보수적인 값 선택 (최솟값 기준)
    protein_limit = min((d["proteinLimit"] for d in matched_constraints), default=None)
    sugar_limit = min((d["sugarLimit"] for d in matched_constraints), default=None)
    sodium_limit = min((d["sodiumLimit"] for d in matched_constraints), default=None)
    disease_notes = [d["notes"] for d in matched_constraints]
    
    meal_type = body["meal_type"]
    consumed = body["consumed_so_far"]

    base_targets = calculate_base_nutrients(user)
    # 남은 권장량을 기존 기준에서 질병 제한 기준까지 낮춤

    adjusted_targets = {
        "protein": min(base_targets["protein"], protein_limit) if protein_limit else base_targets["protein"],
        "fat": base_targets["fat"],
        "carbohydrates": min(base_targets["carbohydrates"], sugar_limit) if sugar_limit else base_targets["carbohydrates"],
        "sodium": min(base_targets["sodium"], sodium_limit) if sodium_limit else base_targets["sodium"],
    }
    
    remaining = {
        "protein": max(0, adjusted_targets["protein"] - consumed.get("protein", 0)),
        "fat": max(0, adjusted_targets["fat"] - consumed.get("fat", 0)),
        "carbohydrates": max(0, adjusted_targets["carbohydrates"] - consumed.get("carbs", 0)),
        "sodium": max(0, adjusted_targets["sodium"] - consumed.get("sodium", 0)),
    }


    prompt = f"""
You are a clinical dietitian for rare disease patients.

Your main goal is to recommend a meal based on the patient's disease-related dietary needs. Ingredients are helpful but secondary.
Analyze the diseases to identify dietary restrictions. Then design a complete and diverse meal adapted to the selected meal type: {meal_type.upper()}.

    - Detailed clinical dietary guidance for rare diseases:
{chr(10).join([
    f"""    - For {d['diseaseName']}:
        - Clinical note: {d['notes']}
        - Foods to avoid: (based on disease pathology; if applicable)
        - Recommended substitutions: (e.g., medical formulas, low-protein products, non-dairy alternatives)
        - Meal planning tip: Prioritize nutritional balance while respecting disease constraints.
    """ for d in matched_constraints
])}

---

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
  "menu": "item 1, item 2, item 3",
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
    response = client.chat(
        model="gemma:7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    raw = response['message']['content']
    print("raw response:", raw)

    try:
        cleaned = raw.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
            cleaned = re.sub(r"```$", "", cleaned)
            cleaned = cleaned.strip()

        result_json = json.loads(cleaned)
        return result_json

    except Exception as e:
        return {
            "error": "Model did not return valid JSON",
            "exception": str(e),
            "raw": raw
        }

