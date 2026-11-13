import re

SKILLS = [
    "Python", "C++", "C", "Java", "SQL", "Pandas", "NumPy", "TensorFlow",
    "PyTorch", "Scikit-learn", "OpenCV", "YOLO", "ROS2", "IoT",
    "Embedded Systems", "Power BI", "Data Analysis", "PLC", "MATLAB",
]


def analyze_opportunity(title, text, profile_skills=None):
    content = f"{title} {text}".lower()
    pfe_terms = ("pfe", "fin d'études", "fin d’etudes", "final year", "end of studies")
    is_pfe = any(term in content for term in pfe_terms)
    student_fit = any(term in content for term in ("ingénieur", "engineering", "étudiant", "student", "bac+5", "final year"))
    found = [skill for skill in SKILLS if re.search(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", content)]
    profile = {item.strip().lower() for item in (profile_skills or []) if item.strip()}
    matched = [skill for skill in found if skill.lower() in profile]
    score = min(100, (40 if is_pfe else 0) + (20 if student_fit else 0) + min(30, len(matched) * 10) + min(10, len(found) * 2))
    reasons = []
    reasons.append("PFE / end-of-studies wording found" if is_pfe else "No explicit PFE wording found")
    reasons.append("Student or engineering level mentioned" if student_fit else "Academic level not clearly specified")
    if matched:
        reasons.append("Matching skills: " + ", ".join(matched))
    return {"is_pfe": is_pfe, "skills": found, "matching_skills": matched, "score": score, "explanation": "; ".join(reasons)}
