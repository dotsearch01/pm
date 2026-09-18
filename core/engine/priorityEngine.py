"""
Priority Engine Module
Calculates deterministic priorities using mathematical weighting across severity, business impact,
AI-search impact, evidence confidence, and implementation effort.
"""

class PriorityEngine:
    SEVERITY_WEIGHTS = {
        "P0": 10.0,
        "P1": 7.5,
        "P2": 5.0,
        "P3": 2.5
    }

    CATEGORY_IMPACT = {
        "technical": 9.0,
        "content": 8.5,
        "entity": 8.0,
        "authority": 8.5,
        "citation": 8.0,
        "ui": 7.0,
        "visibility": 7.5
    }

    def __init__(self):
        pass

    def calculate_priority_score(self, finding):
        sev = finding.get('severity', 'P2')
        cat = finding.get('category', 'technical')
        conf = float(finding.get('confidence', 0.8))

        sev_score = self.SEVERITY_WEIGHTS.get(sev, 5.0)
        impact_score = self.CATEGORY_IMPACT.get(cat, 7.5)
        effort_score = 3.0 if cat in ['technical', 'ui'] else 6.0

        # Formula: (Severity * 0.45) + (Impact * 0.35) + (Confidence * 10 * 0.20) - (Effort * 0.10)
        raw_score = (sev_score * 0.45) + (impact_score * 0.35) + (conf * 10.0 * 0.20) - (effort_score * 0.10)
        priority_score = round(max(1.0, min(10.0, raw_score)), 1)

        return {
            "priority": sev,
            "priority_score": priority_score,
            "factors": {
                "severity": sev_score,
                "impact": impact_score,
                "confidence": conf,
                "effort": effort_score
            }
        }

    def prioritize_findings(self, findings):
        p0 = []
        p1 = []
        p2 = []
        p3 = []
        quick_wins = []

        for f in findings:
            status = f.get('status', '').lower()
            if status in ['fail', 'warning']:
                calc = self.calculate_priority_score(f)
                enriched_finding = dict(f)
                enriched_finding['priority_calculation'] = calc

                sev = f.get('severity')
                if sev == 'P0':
                    p0.append(enriched_finding)
                elif sev == 'P1':
                    p1.append(enriched_finding)
                elif sev == 'P2':
                    p2.append(enriched_finding)
                else:
                    p3.append(enriched_finding)

                # Quick win detection: High confidence, low effort, high/medium impact
                if f.get('confidence', 0) >= 0.90 and calc['factors']['effort'] <= 4.0:
                    quick_wins.append({
                        "id": f.get('id'),
                        "title": f.get('title'),
                        "action": f.get('recommendation'),
                        "effort": "Low",
                        "impact": "High" if sev in ['P0', 'P1'] else "Medium",
                        "finding_id": f.get('id'),
                        "rule_id": f.get('id'),
                        "evidence": f.get('evidence')
                    })

        return {
            "P0_critical": p0,
            "P1_high": p1,
            "P2_medium": p2,
            "P3_low": p3,
            "quick_wins": quick_wins
        }
