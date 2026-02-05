import random
import streamlit as st
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import math


# =========================
# ENUMS & MODELS
# =========================

class Goal(Enum):
    MUSKELAUFBAU = "Muskelaufbau 💪"
    ABNEHMEN = "Abnehmen 🔥"


@dataclass(frozen=True)
class Meal:
    name: str
    calories: int
    protein: int
    carbs: int
    fat: int


# =========================
# MEAL DATABASE
# =========================

MEALS: Dict[str, List[Meal]] = {
    "breakfast": [
        Meal("Haferflocken mit Beeren", 500, 30, 55, 15),
        Meal("Skyr mit Nüssen", 480, 40, 35, 18),
        Meal("Rührei & Vollkornbrot", 520, 35, 40, 20),
    ],
    "lunch": [
        Meal("Hähnchen & Reis", 700, 45, 70, 15),
        Meal("Lachs & Kartoffeln", 720, 40, 50, 30),
        Meal("Rinderhack & Quinoa", 680, 42, 55, 25),
    ],
    "dinner": [
        Meal("Putenbrust & Gemüse", 600, 45, 30, 20),
        Meal("Tofu-Gemüse-Pfanne", 580, 35, 40, 22),
        Meal("Omelette & Salat", 550, 40, 20, 25),
    ],
    "snack": [
        Meal("Proteinshake", 250, 30, 10, 5),
        Meal("Hüttenkäse & Obst", 280, 25, 20, 8),
        Meal("Nüsse & Apfel", 300, 10, 25, 20),
    ],
}


# =========================
# CALCULATIONS
# =========================

def bmr(weight, height, age, gender):
    return int(
        10 * weight + 6.25 * height - 5 * age + (5 if gender == "Männlich" else -161)
    )


def tdee(bmr_value, activity):
    return int(bmr_value * activity)


def target_calories(goal, tdee_value):
    return int(tdee_value * (1.15 if goal == Goal.MUSKELAUFBAU else 0.8))


def protein_target(weight, goal):
    return int(weight * (2.2 if goal == Goal.MUSKELAUFBAU else 1.8))


# =========================
# PLAN GENERATION
# =========================

def generate_day_plan():
    used = set()
    plan = []

    for category in MEALS.values():
        options = [m for m in category if m.name not in used]
        meal = random.choice(options)
        used.add(meal.name)
        plan.append(meal)

    return plan


def generate_week_plan():
    week = []
    for _ in range(7):
        week.append(generate_day_plan())
    return week


def totals(meals):
    return {
        "calories": sum(m.calories for m in meals),
        "protein": sum(m.protein for m in meals),
        "carbs": sum(m.carbs for m in meals),
        "fat": sum(m.fat for m in meals),
    }


# =========================
# STREAMLIT UI
# =========================

st.set_page_config("Pro Ernährungsplan", "🥗", layout="wide")
st.title("🥗 Pro Ernährungsplan")

tab_profile, tab_day, tab_week = st.tabs(["👤 Profil", "📅 Tagesplan", "🗓️ Wochenplan"])

# -------- PROFILE --------
with tab_profile:
    col1, col2 = st.columns(2)

    with col1:
        weight = st.number_input("Gewicht (kg)", 40.0, 200.0, 80.0)
        height = st.number_input("Größe (cm)", 140, 220, 180)
        age = st.number_input("Alter", 14, 90, 30)

    with col2:
        gender = st.selectbox("Geschlecht", ["Männlich", "Weiblich"])
        activity = st.selectbox(
            "Aktivitätslevel",
            {
                "Kaum aktiv": 1.2,
                "Leicht aktiv": 1.375,
                "Mittel aktiv": 1.55,
                "Sehr aktiv": 1.725,
            }.items(),
            format_func=lambda x: x[0],
        )

    goal = st.radio("🎯 Ziel", list(Goal), format_func=lambda g: g.value)

    bmr_val = bmr(weight, height, age, gender)
    tdee_val = tdee(bmr_val, activity[1])
    target_kcal = target_calories(goal, tdee_val)
    protein_goal = protein_target(weight, goal)

    st.success(
        f"**Zielkalorien:** {target_kcal} kcal  \n"
        f"**Protein-Ziel:** {protein_goal} g/Tag"
    )

# -------- DAY PLAN --------
with tab_day:
    if "day_plan" not in st.session_state:
        st.session_state.day_plan = generate_day_plan()

    if st.button("🔄 Neuer Tagesplan"):
        st.session_state.day_plan = generate_day_plan()

    day_totals = totals(st.session_state.day_plan)

    for meal in st.session_state.day_plan:
        with st.container(border=True):
            st.markdown(f"### {meal.name}")
            st.write(
                f"🔥 {meal.calories} kcal | "
                f"💪 {meal.protein} g Protein | "
                f"🍞 {meal.carbs} g KH | "
                f"🥑 {meal.fat} g Fett"
            )

    st.metric("Kalorien", day_totals["calories"], day_totals["calories"] - target_kcal)
    st.metric("Protein", day_totals["protein"], day_totals["protein"] - protein_goal)

# -------- WEEK PLAN --------
with tab_week:
    if st.button("📆 Wochenplan erstellen"):
        st.session_state.week_plan = generate_week_plan()

    if "week_plan" in st.session_state:
        for i, day in enumerate(st.session_state.week_plan, 1):
            with st.expander(f"Tag {i}"):
                t = totals(day)
                for meal in day:
                    st.write(f"- {meal.name} ({meal.calories} kcal)")
                st.caption(f"🔥 {t['calories']} kcal | 💪 {t['protein']} g Protein")
