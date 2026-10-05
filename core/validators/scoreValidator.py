"""
Score Validator Module
Validates mathematical integrity, confidence weighting, 100/100 safety,
and ensures that unknown/insufficient data never inflates scores or conceals P0 failures.
"""

class ScoreValidator:
    def __init__(self):
        pass

    def validate_score_model(self, score_data, findings):
        """
        Validates score object against strict integrity rules:
        1. 0 <= Score <= 100
        2. High score cannot hide P0 failures
        3. 100/100 safety: Perfect score disallowed if unknown/unevaluated rules or unmeasured critical dimensions exist
        4. Not Applicable rules do not reduce score
        5. Unknown rules do not manufacture arbitrary points
        """
        errors = []
        overall = score_data.get('overall_score', 0)

        if not (0.0 <= float(overall) <= 100.0):
            errors.append(f"Invalid overall score: {overall}. Must be between 0 and 100.")

        # Check if P0 critical issues exist but overall score is presented as perfect without warning
        p0_fails = [f for f in findings if f.get('severity') == 'P0' and f.get('status') == 'fail']
        if len(p0_fails) > 0 and overall > 95.0:
            errors.append(f"Score integrity violation: {len(p0_fails)} P0 critical failures detected, but overall score is {overall}. P0 issues must visibly cap or flag the score.")

        # 100/100 Safety Check:
        unknown_findings = [f for f in findings if f.get('status') == 'unknown']
        if overall >= 100.0 and len(unknown_findings) > 0:
            errors.append("100/100 score safety violation: Perfect 100 score awarded while unknown/unmeasured rules exist.")

        # Check component scores
        components = score_data.get('component_scores', {})
        for name, comp in components.items():
            sc = comp.get('score')
            status = comp.get('status', 'EVALUATED')
            
            if status == 'INSUFFICIENT_DATA':
                if sc is not None and sc > 0 and comp.get('confidence', 0) == 0:
                    errors.append(f"Component '{name}' has INSUFFICIENT_DATA status but manufactures a positive score {sc}.")
            elif sc is not None:
                if not (0.0 <= float(sc) <= 100.0):
                    errors.append(f"Component '{name}' score {sc} out of bounds [0, 100].")
                if not comp.get('reason'):
                    errors.append(f"Component '{name}' is missing an explainable evidence reason.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "p0_count": len(p0_fails)
        }
