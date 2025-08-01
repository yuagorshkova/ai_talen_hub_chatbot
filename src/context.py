from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class AcademicPlanLoader:
    def __init__(self):
        self.ai_plan = self._load_academic_plan("resources/academic_plan_ai.csv")
        self.ai_product_plan = self._load_academic_plan(
            "resources/academic_plan_ai_product.csv"
        )
        self._validate_plans()

    def _load_academic_plan(self, path: str) -> List[Dict]:
        """Load and validate academic plan CSV with specific expected columns"""
        try:
            if not Path(path).exists():
                raise FileNotFoundError(f"Academic plan file not found: {path}")

            df = pd.read_csv(path)

            # Validate required columns
            required_columns = {
                "course_code",
                "course_name",
                "semester",
                "credits",
                "prerequisites",
            }
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns in {path}: {missing}")

            # Convert NaN to empty string
            df = df.fillna("")
            return df.to_dict("records")

        except Exception as e:
            print(f"Error loading academic plan {path}: {e}")
            return []

    def _validate_plans(self):
        """Validate relationships between plans"""
        if self.ai_plan and self.ai_product_plan:
            ai_codes = {course["course_code"] for course in self.ai_plan}
            product_codes = {course["course_code"] for course in self.ai_product_plan}

            # Check for overlapping courses
            overlaps = ai_codes & product_codes
            if overlaps:
                print(f"Warning: Overlapping course codes between plans: {overlaps}")

    def get_course_info(self, course_code: str) -> Optional[Dict]:
        """Get course details from either plan by course code"""
        for course in self.ai_plan + self.ai_product_plan:
            if course["course_code"].lower() == course_code.lower():
                return course
        return None

    def get_semester_plan(self, semester: int, plan_type: str = "ai") -> List[Dict]:
        """Get courses for specific semester"""
        plan = self.ai_plan if plan_type == "ai" else self.ai_product_plan
        return [c for c in plan if c["semester"] == semester]

    def get_plan_context(self, plan_type: str = "both") -> str:
        """Generate formatted context string for LLM prompts"""
        context = []

        if plan_type in ("ai", "both") and self.ai_plan:
            context.append("=== AI ACADEMIC PLAN ===")
            context.extend(self._format_course(c) for c in self.ai_plan)

        if plan_type in ("product", "both") and self.ai_product_plan:
            context.append("\n=== AI PRODUCT ACADEMIC PLAN ===")
            context.extend(self._format_course(c) for c in self.ai_product_plan)

        return "\n".join(context) if context else "No academic plans available"

    def _format_course(self, course: Dict) -> str:
        """Format individual course for display"""
        return (
            f"{course['course_code']}: {course['course_name']} "
            f"(Semester {course['semester']}, {course['credits']} credits)\n"
            f"Prerequisites: {course['prerequisites'] or 'None'}\n"
        )


# Initialize the loader
academic_loader = AcademicPlanLoader()
