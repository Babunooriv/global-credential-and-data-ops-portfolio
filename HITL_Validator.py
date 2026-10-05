"""
HITL Extraction Guard & JSON Validator
Simulates OCR data extraction validation and error flagging for human auditor review.
"""

from typing import Dict, Any, List

def audit_extracted_transcript(payload: Dict[str, Any]) -> Dict[str, Any]:
    flags: List[str] = []
    sanitized_records: List[Dict[str, Any]] = []

    # 1. Header validations
    if not payload.get("institution_name"):
        flags.append("CRITICAL: Missing institution name.")
    
    # 2. Record validation & bounds checking
    courses = payload.get("extracted_courses", [])
    if not courses:
        flags.append("CRITICAL: No course records detected by OCR parser.")

    for idx, c in enumerate(courses):
        course_name = c.get("name", "").strip()
        credits_raw = c.get("credits")
        grade_raw = c.get("grade", "").strip()

        # Check for empty fields
        if not course_name or credits_raw is None or not grade_raw:
            flags.append(f"ROW_{idx+1}: Incomplete tabular extraction.")
            continue

        # Check for numeric consistency
        try:
            credits_val = float(credits_raw)
            if credits_val < 0 or credits_val > 30:
                flags.append(f"ROW_{idx+1}: Credit value {credits_val} exceeds legitimate threshold.")
        except ValueError:
            flags.append(f"ROW_{idx+1}: Non-numeric credit token '{credits_raw}'.")
            credits_val = 0.0

        sanitized_records.append({
            "course_title": course_name,
            "credits": credits_val,
            "grade_token": grade_raw
        })

    # 3. Structural verdict
    requires_human_triage = len(flags) > 0

    return {
        "status": "FLAGGED_FOR_HUMAN_TRIAGE" if requires_human_triage else "READY_FOR_EXPORT",
        "error_count": len(flags),
        "audit_flags": flags,
        "clean_payload": sanitized_records if not requires_human_triage else None
    }

if __name__ == "__main__":
    raw_ocr_payload = {
        "institution_name": "University of Mumbai",
        "extracted_courses": [
            {"name": "Applied Mathematics I", "credits": 4.0, "grade": "A"},
            {"name": "Engineering Physics", "credits": "O", "grade": "B"}, # OCR Error: 'O' instead of 0/number
            {"name": "Basics of Electrical Eng", "credits": 40.0, "grade": "A"} # OCR Error: out of bounds
        ]
    }

    audit_result = audit_extracted_transcript(raw_ocr_payload)
    print("Audit Status:", audit_result["status"])
    print("Actionable Flags:", audit_result["audit_flags"])
