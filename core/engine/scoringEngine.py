"""
Scoring Engine Module
Calculates deterministic, evidence-weighted scores across all 7 AI Search / GEO dimensions.
Enforces score transparency, exclusion of NOT_APPLICABLE from denominator,
and prevents manufacturing scores for UNKNOWN / INSUFFICIENT_DATA categories.
"""

from core.validators.confidenceCalculator import ConfidenceCalculator

class ScoringEngine:
    DIMENSION_WEIGHTS = {
        "technical_accessibility": 0.20,
        "content_retrieval": 0.20,
        "entity_coverage": 0.15,
        "experience_trust": 0.15,
        "citation_readiness": 0.15,
        "external_authority": 0.10,
        "ai_visibility": 0.05
    }

    CATEGORY_TO_DIMENSION = {
        "technical": "technical_accessibility",
        "content": "content_retrieval",
        "entity": "entity_coverage",
        "authority": "experience_trust",
        "citation": "citation_readiness",
        "ui": "technical_accessibility",
        "visibility": "ai_visibility"
    }

    def __init__(self):
        self.confidence_calc = ConfidenceCalculator()

    def calculate_scores(self, findings):
        categories = {
            dim: {
                "total_weight": 0,
                "earned_weight": 0,
                "pass_count": 0,
                "fail_count": 0,
                "warning_count": 0,
                "unknown_count": 0,
                "na_count": 0,
                "findings": [],
                "evidence_ids": []
            } for dim in self.DIMENSION_WEIGHTS.keys()
        }

        p0_count = 0
        p1_count = 0

        for f in findings:
            raw_cat = f.get('category', 'technical')
            dim = self.CATEGORY_TO_DIMENSION.get(raw_cat, 'technical_accessibility')
            status = str(f.get('status', 'unknown')).lower()
            sev = f.get('severity', 'P2')
            fid = f.get('id')

            weight = f.get('scoring_weight', 10)
            if sev == 'P0':
                weight = 20
                if status == 'fail': p0_count += 1
            elif sev == 'P1':
                weight = 15
                if status == 'fail': p1_count += 1
            elif sev == 'P2':
                weight = 10
            else:
                weight = 5

            if fid:
                categories[dim]['evidence_ids'].append(fid)
            categories[dim]['findings'].append(f)

            if status == 'pass':
                categories[dim]['total_weight'] += weight
                categories[dim]['earned_weight'] += weight
                categories[dim]['pass_count'] += 1
            elif status == 'warning':
                categories[dim]['total_weight'] += weight
                categories[dim]['earned_weight'] += (weight * 0.7)
                categories[dim]['warning_count'] += 1
            elif status == 'fail':
                categories[dim]['total_weight'] += weight
                categories[dim]['fail_count'] += 1
            elif status == 'unknown':
                categories[dim]['unknown_count'] += 1
            elif status == 'not_applicable':
                categories[dim]['na_count'] += 1

        component_scores = {}
        weighted_sum = 0
        active_dimension_weights = 0

        for dim, data in categories.items():
            evaluated_count = data['pass_count'] + data['fail_count'] + data['warning_count']
            
            if data['total_weight'] > 0:
                raw_score = (data['earned_weight'] / data['total_weight']) * 100
                score = round(raw_score, 1)
                status = "EVALUATED"
                confidence = self.confidence_calc.calculate_dimension_confidence(data['findings'], dim)
            elif data['unknown_count'] > 0:
                score = None
                status = "INSUFFICIENT_DATA"
                confidence = 0.0
            else:
                # No findings registered for this category
                score = None
                status = "INSUFFICIENT_DATA"
                confidence = 0.0

            reasons = []
            for item in data['findings']:
                if item.get('status') == 'pass':
                    reasons.append(f"Passed: {item.get('title', item.get('id'))}")
                elif item.get('status') in ['fail', 'warning']:
                    reasons.append(f"{item.get('status').upper()}: {item.get('evidence', '')}")

            component_scores[dim] = {
                "score": score,
                "status": status,
                "confidence": confidence,
                "rules_evaluated": len(data['findings']),
                "pass": data['pass_count'],
                "fail": data['fail_count'],
                "warning": data['warning_count'],
                "unknown": data['unknown_count'],
                "not_applicable": data['na_count'],
                "reason": "; ".join(reasons[:2]) if reasons else ("Compliant with baseline rules." if status == "EVALUATED" else "Data unavailable — requires verification.")
            }

            if score is not None:
                dim_w = self.DIMENSION_WEIGHTS.get(dim, 0.15)
                weighted_sum += score * dim_w
                active_dimension_weights += dim_w

        overall_score = round(weighted_sum / active_dimension_weights, 1) if active_dimension_weights > 0 else 0.0

        # 100/100 Safety Cap: Cannot award 100 if any category has insufficient data or unknown rules
        has_insufficient = any(c['status'] == 'INSUFFICIENT_DATA' for c in component_scores.values())
        if overall_score >= 100.0 and has_insufficient:
            overall_score = 98.0

        overall_confidence = self.confidence_calc.calculate_overall_confidence(component_scores)

        return {
            "overall_score": overall_score,
            "overall_confidence": overall_confidence,
            "component_scores": component_scores,
            "scoring_logic": "Normalized weighted average across evaluated dimensions (Technical 20%, Content 20%, Entity 15%, Trust 15%, Citation 15%, Authority 10%, Visibility 5%). NOT_APPLICABLE excluded from denominator. UNKNOWN categorized as INSUFFICIENT_DATA.",
            "critical_issues_count": p0_count,
            "high_impact_count": p1_count
        }
