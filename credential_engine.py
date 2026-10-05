"""
Credential Normalization & GPA Engine
Demonstrates automated international transcript parsing and conversion to US 4.0 standards.
"""

from typing import List, Dict, Any

# Standardized Conversion Matrix
CONVERSION_MATRIX: Dict[str, Dict[str, Any]] = {
    "INDIA_10_POINT": {
        "credit_multiplier": 1.0,
        "grade_scale": [
            {"min": 9.0, "us_grade": "A", "points": 4.0},
            {"min": 8.0, "us_grade": "A-", "points": 3.7},
            {"min": 7.0, "us_grade": "B", "points": 3.0},
            {"min": 6.0, "us_grade": "C", "points": 2.0},
            {"min": 0.0, "us_grade": "F", "points": 0.0},
        ]
    },
    "UK_HONOURS": {
        "credit_multiplier": 0.25,  # 120 UK credits = 30 US semester credits
        "grade_scale": [
            {"min": 70, "us_grade": "A", "points": 4.0},
            {"min": 60, "us_grade": "B+", "points": 3.3},
            {"min": 50, "us_grade": "B", "points": 3.0},
            {"min": 40, "us_grade": "C", "points": 2.0},
            {"min": 0, "us_grade": "F", "points": 0.0},
        ]
    },
    "ECTS_EUROPE": {
        "credit_multiplier": 0.5,   # 60 ECTS = 30 US semester credits
        "grade_scale": {
            "A": {"us_grade": "A", "points": 4.0},
            "B": {"us_grade": "A-", "points": 3.7},
            "C": {"us_grade": "B", "points": 3.0},
            "D": {"us_grade": "C", "points": 2.0},
            "F": {"us_grade": "F", "points": 0.0},
        }
    }
}

def evaluate_transcript(system_key: str, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    rules = CONVERSION_MATRIX.get(system_key)
    if not rules:
        raise ValueError(f"System key '{system_key}' not supported.")

    total_us_credits = 0.0
    total_quality_points = 0.0
    converted_courses = []

    for course in courses:
        local_credits = course["credits"]
        raw_grade = course["raw_grade"]
        
        # Apply standard credit hour ratios
        us_credits = local_credits * rules["credit_multiplier"]
        
        # Determine equivalent points
        if system_key == "ECTS_EUROPE":
            grade_info = rules["grade_scale"].get(raw_grade, {"us_grade": "F", "points": 0.0})
            us_grade = grade_info["us_grade"]
            grade_points = grade_info["points"]
        else:
            us_grade = "F"
            grade_points = 0.0
            for tier in rules["grade_scale"]:
                if raw_grade >= tier["min"]:
                    us_grade = tier["us_grade"]
                    grade_points = tier["points"]
                    break

        quality_points = us_credits * grade_points
        total_us_credits += us_credits
        total_quality_points += quality_points

        converted_courses.append({
            "course_name": course["name"],
            "original_credits": local_credits,
            "raw_grade": raw_grade,
            "us_credits": round(us_credits, 2),
            "us_grade": us_grade,
            "quality_points": round(quality_points, 2)
        })

    calculated_gpa = (total_quality_points / total_us_credits) if total_us_credits > 0 else 0.0

    return {
        "system_evaluated": system_key,
        "total_us_credits": round(total_us_credits, 2),
        "cumulative_us_gpa": round(calculated_gpa, 2),
        "course_breakdown": converted_courses
    }

if __name__ == "__main__":
    sample_uk_transcript = [
        {"name": "Computer Architecture", "credits": 20, "raw_grade": 72},
        {"name": "Data Systems", "credits": 20, "raw_grade": 64},
        {"name": "Discrete Mathematics", "credits": 20, "raw_grade": 58},
    ]
    
    result = evaluate_transcript("UK_HONOURS", sample_uk_transcript)
    print(f"Evaluated US GPA: {result['cumulative_us_gpa']} across {result['total_us_credits']} US Credits")
