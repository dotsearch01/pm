"""
Recommendation Validator Module
Enforces that every recommendation traces directly to a verified Finding ID, Rule ID, Evidence, and Priority.
Recommendations without direct evidence relationship are classified as GENERAL_RECOMMENDATION.
"""

class RecommendationValidator:
    def __init__(self):
        pass

    def validate_recommendation(self, rec, verified_findings=None):
        """
        Validates traceability and calibrated language of a recommendation item.
        """
        errors = []
        finding_id = rec.get('finding_id')
        rule_id = rec.get('rule_id')
        evidence = rec.get('evidence')
        action = rec.get('action', '')

        is_linked = False
        if verified_findings and (finding_id or rule_id):
            matching = [f for f in verified_findings if f.get('id') in [finding_id, rule_id]]
            if matching:
                is_linked = True
                if not evidence:
                    evidence = matching[0].get('evidence')

        if not is_linked and not evidence:
            rec['type'] = 'GENERAL_RECOMMENDATION'
            rec['traceability'] = 'unlinked'
        else:
            rec['type'] = 'PROJECT_FINDING_RECOMMENDATION'
            rec['traceability'] = f"linked:{finding_id or rule_id}"

        # Calibrated language check
        forbidden_terms = ['guarantee', 'guaranteed', 'will rank #1', 'will definitely cite', '100% traffic']
        for term in forbidden_terms:
            if term in action.lower():
                errors.append(f"Forbidden guarantee term '{term}' in recommendation action.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "classification": rec['type'],
            "recommendation": rec
        }

    def validate_all(self, recommendations, verified_findings=None):
        results = []
        all_errors = []
        for r in recommendations:
            res = self.validate_recommendation(r, verified_findings)
            results.append(res['recommendation'])
            if not res['is_valid']:
                all_errors.extend(res['errors'])

        return {
            "is_valid": len(all_errors) == 0,
            "errors": all_errors,
            "validated_recommendations": results
        }
