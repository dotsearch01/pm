"""
Recommendation Engine Module
Generates structured, actionable recommendations derived strictly from verified audit findings.
Enforces 100% traceability and non-guaranteed probabilistic language.
"""

from core.validators.recommendationValidator import RecommendationValidator

class RecommendationEngine:
    def __init__(self):
        self.validator = RecommendationValidator()

    def generate_recommendations(self, findings, priorities=None):
        recommendations = []

        # Generate from failing/warning findings
        actionable_findings = [f for f in findings if f.get('status') in ['fail', 'warning']]

        for f in actionable_findings:
            calc = f.get('priority_calculation', {})
            rec = {
                "id": f"REC-{f.get('id')}",
                "finding_id": f.get('id'),
                "rule_id": f.get('id'),
                "title": f.get('title'),
                "action": f.get('recommendation'),
                "evidence": f.get('evidence'),
                "why_it_matters": f.get('impact'),
                "priority": f.get('severity', 'P2'),
                "priority_score": calc.get('priority_score', 5.0),
                "expected_impact": "Expected improvement in AI retrieval and citation readiness (non-guaranteed).",
                "affected_pages": f.get('affected_pages', []),
                "type": "PROJECT_FINDING_RECOMMENDATION"
            }
            recommendations.append(rec)

        # Validate all generated recommendations
        val_res = self.validator.validate_all(recommendations, findings)
        return val_res['validated_recommendations']
