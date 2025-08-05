from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd


class AcademicPlanLoader:
    def __init__(self):
        # Пытаемся загрузить сначала CSV, потом MD
        self.ai_plan = self._load_data("resources/academic_plan_ai")
        self.ai_product_plan = self._load_data("resources/academic_plan_ai_product")

    def _load_data(self, base_path: str) -> Union[List[Dict], str, None]:
        """Пытается загрузить данные сначала из CSV, потом из MD"""
        csv_path = f"{base_path}.csv"
        md_path = f"{base_path}.md"
        
        # Пробуем CSV
        csv_data = self._load_academic_plan(csv_path)
        if csv_data:
            return csv_data
            
        # Если CSV нет, пробуем MD
        if Path(md_path).exists():
            print("Successfully loadeded plans")
            return self._load_markdown_as_text(md_path)
            
        print(f"Warning: No academic plan found at {base_path}.[csv|md]")
        return None

    def _load_academic_plan(self, path: str) -> Optional[List[Dict]]:
        """Load and validate academic plan CSV with specific expected columns"""
        try:
            if not Path(path).exists():
                return None

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
            return None

    def _load_markdown_as_text(self, path: str) -> str:
        """Загружает markdown файл как простой текст"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading markdown file {path}: {e}")
            return ""


    def get_plan_context(self, plan_type: str = "both") -> str:
        """Главный метод - возвращает контекст для LLM в виде строки"""
        context = []

        if plan_type in ("ai", "both"):
            if isinstance(self.ai_plan, list):
                context.append("=== AI ACADEMIC PLAN ===")
                context.extend(self._format_course(c) for c in self.ai_plan)
            elif isinstance(self.ai_plan, str):
                context.append("=== AI ACADEMIC PLAN (MARKDOWN) ===")
                context.append(self.ai_plan)

        if plan_type in ("product", "both"):
            if isinstance(self.ai_product_plan, list):
                context.append("\n=== AI PRODUCT ACADEMIC PLAN ===")
                context.extend(self._format_course(c) for c in self.ai_product_plan)
            elif isinstance(self.ai_product_plan, str):
                context.append("\n=== AI PRODUCT ACADEMIC PLAN (MARKDOWN) ===")
                context.append(self.ai_product_plan)

        return "\n".join(context) if context else "No academic plans available"

    def _format_course(self, course: Dict) -> str:
        """Format individual course for display (только для CSV данных)"""
        return (
            f"{course['course_code']}: {course['course_name']} "
            f"(Semester {course['semester']}, {course['credits']} credits)\n"
            f"Prerequisites: {course['prerequisites'] or 'None'}\n"
        )


# Initialize the loader
academic_loader = AcademicPlanLoader()