from typing import List, Dict

class CBCTrackerService:
    """
    Logic to map student outcomes to Kenyan CBC Strands.
    """
    
    CBC_STRANDS = {
        "lower_primary": ["Literacy", "Numeracy", "Environmental Activities", "Movement"],
        "upper_primary": ["Science & Tech", "Mathematics", "English", "Kiswahili", "Agriculture"]
    }

    RUBRIC_MAP = {
        4: "Exceeding Expectations (EE)",
        3: "Meeting Expectations (ME)",
        2: "Approaching Expectations (AE)",
        1: "Below Expectations (BE)"
    }

    def get_strands_for_grade(self, grade: int) -> List[str]:
        if grade <= 3:
            return self.CBC_STRANDS["lower_primary"]
        return self.CBC_STRANDS["upper_primary"]

    def calculate_competency(self, assessments: List[dict]) -> Dict[str, str]:
        """
        Input: List of assessment scores (1-4).
        Output: Aggregated competency level per strand.
        """
        results = {}
        for item in assessments:
            strand = item['strand']
            score = item['score'] # Integer 1-4
            
            # Simple logic: Latest score overrides (Continuous Assessment)
            results[strand] = self.RUBRIC_MAP.get(score, "Not Assessed")
            
        return results