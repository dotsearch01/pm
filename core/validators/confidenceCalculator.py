"""
Confidence Calculator Module
Calculates deterministic confidence levels for audit categories and overall report.
Confidence is strictly separated from score value.
"""

class ConfidenceCalculator:
    def __init__(self):
        pass

    def calculate_dimension_confidence(self, findings, dimension_rules):
        """
        Calculates confidence for a specific category based on:
        - Ratio of evaluated vs unknown rules
        - Average confidence of passing/failing findings
        - Coverage of mandatory evidence
        """
        if not findings:
            return 0.0

        evaluated = [f for f in findings if f.get('status') in ['pass', 'fail', 'warning', 'not_applicable']]
        if not evaluated:
            return 0.0

        confidences = [f.get('confidence', 0.8) for f in evaluated if f.get('status') != 'not_applicable']
        if not confidences:
            return 1.0 # only N/A rules

        avg_conf = sum(confidences) / len(confidences)
        coverage_ratio = len(evaluated) / max(len(findings), 1)
        
        return round(avg_conf * coverage_ratio, 2)

    def calculate_overall_confidence(self, component_scores):
        """
        Calculates overall report confidence across all evaluated dimensions.
        """
        valid_confs = []
        for dim, data in component_scores.items():
            conf = data.get('confidence')
            if conf is not None and conf > 0:
                valid_confs.append(conf)

        if not valid_confs:
            return 0.0

        return round(sum(valid_confs) / len(valid_confs), 2)
