## 🥗 Rare Disease Meal Planner (AI-powered Nutrition Recommendation)

This project provides AI-generated meal recommendations tailored to **users with rare diseases**, based on their dietary restrictions, daily intake status, and ingredient availability. It integrates medical knowledge from structured JSON files and leverages LLM (Large Language Model) prompting via a local Ollama API.

---

### 📌 Features

* ✅ **Disease-aware Meal Planning**: Dynamically adjusts macronutrient limits based on user disease history.
* ✅ **Custom Prompt Engineering**: Constructs a medically informed prompt for the AI, based on real-time user profile and dietary needs.
* ✅ **JSON-based Clinical Constraints**: Loads disease-specific dietary restrictions from `disease_limits.json`.
* ✅ **Explainable AI Output**: Includes dietitian-level expert notes explaining the medical suitability of the meal.
* ✅ **FastAPI Backend**: Accepts user requests and handles LLM calls with structured logic.

---

### 🧠 How It Works

1. **User Input**:
   The API receives structured user data:

   ```json
   {
     "user_info": {
       "age": 30,
       "gender": "female",
       "height": 165,
       "weight": 60,
       "ingredients": ["rice", "chicken", "broccoli"],
       "disease": ["Phenylketonuria (PKU)"]
     },
     "meal_type": "lunch",
     "consumed_so_far": {
       "protein": 10,
       "fat": 20,
       "carbs": 100,
       "sodium": 500
     }
   }
   ```

2. **Disease Constraint Lookup**:

   * The system loads `disease_limits.json`, which includes per-disease thresholds like:

     ```json
     {
       "diseaseName": "Phenylketonuria (PKU)",
       "proteinLimit": 30,
       "sugarLimit": 150,
       "sodiumLimit": 1200,
       "notes": "Limit phenylalanine intake..."
     }
     ```
   * If multiple diseases are given, **the most restrictive limit is chosen**.

3. **Remaining Intake Calculation**:

   * Nutritional targets are first calculated by age, gender, and weight.
   * These are **adjusted downward** based on disease constraints.
   * Any food already consumed is subtracted to yield remaining allowed intake.

4. **Prompt Construction**:
   A detailed instruction is sent to the AI model (`gemma:7b-instruct` via Ollama) with:

   * Patient demographics
   * Ingredient availability
   * Disease list
   * Remaining nutrition budget (protein, fat, carbs, sodium)
   * Request for structured JSON output

5. **AI Output Example**:
   The model returns a strict JSON structure with:

   ```json
   {
     "dish": "Low-Protein Vegetable Bowl",
     "meal_type": "lunch",
     "menu": "boiled broccoli, low-protein rice, olive oil dressing",
     "notes": [
       "This meal restricts protein intake for PKU patients.",
       "Broccoli provides essential vitamins with minimal phenylalanine.",
       "Avoid adding cheese or soy sauce due to high protein content."
     ],
     "calories": 420,
     "protein": 12.0,
     "carbs": 80.0,
     "fat": 15.0,
     "sodium": 700.0
   }
   ```

---

### 🔍 Why This Is Reliable

This system doesn't just **reference** disease data — it **actively uses** structured constraints to:

* Modify AI input (prompt content),
* Influence output meal composition,
* Justify recommendations via clinical logic.

This bridges the gap between **medical dietary guidelines** and **generative AI**.

---

### 🚀 How to Run

1. **Install requirements**:

   ```
   pip install -r requirements.txt
   ```

2. **Start Ollama (Locally)**:

   ```
   ollama run gemma:7b-instruct
   ```

3. **Start FastAPI server**:

   ```
   uvicorn main:app --reload
   ```

4. **Test the API**:
   Send a `POST` request to `/generate-meal` with the structure shown above.

---

### 📌 To Do / Improvements

* [ ] Add front-end meal visualizer
* [ ] Support multilingual explanations
* [ ] Validate JSON output from LLM more strictly

---

필요에 따라 이 README를 한글로 변환하거나, 포스터용 요약 버전으로 재구성해드릴 수도 있어요. 원하시나요?
