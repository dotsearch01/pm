"""
Evidence Resolver Module
Maps claims, metrics, and recommendations back to verified raw audit data.
Prevents data fabrication and enforces traceability.
"""

class EvidenceResolver:
    def __init__(self, raw_audit_data=None):
        self.raw_data = raw_audit_data or {}
        self.verified_facts = {}
        self._index_audit_data()

    def _index_audit_data(self):
        findings = self.raw_data.get('findings', [])
        for f in findings:
            fid = f.get('id')
            if fid:
                self.verified_facts[fid] = {
                    "rule_id": fid,
                    "title": f.get('title'),
                    "status": f.get('status'),
                    "severity": f.get('severity'),
                    "evidence": f.get('evidence'),
                    "confidence": f.get('confidence', 0.0),
                    "source": f.get('source', 'audit-engine')
                }

    def resolve_claim(self, claim_text, rule_id=None):
        """
        Determines whether a claim is directly OBSERVED, reasonably INFERRED,
        a valid RECOMMENDATION, or UNKNOWN.
        """
        if rule_id and rule_id in self.verified_facts:
            fact = self.verified_facts[rule_id]
            if fact['status'] == 'pass':
                return {
                    "claim": claim_text,
                    "status": "OBSERVED",
                    "evidence": fact['evidence'],
                    "confidence": fact['confidence'],
                    "rule_id": rule_id
                }
            elif fact['status'] in ['fail', 'warning']:
                return {
                    "claim": claim_text,
                    "status": "INFERRED",
                    "evidence": fact['evidence'],
                    "confidence": fact['confidence'],
                    "rule_id": rule_id
                }

        # If no direct evidence exists
        return {
            "claim": claim_text,
            "status": "UNKNOWN",
            "evidence": "Data unavailable — requires verification.",
            "confidence": 0.0,
            "rule_id": None
        }

    def get_verified_strengths(self, min_confidence=0.90):
        """
        Returns only findings that PASS and have high confidence.
        """
        strengths = []
        for fid, fact in self.verified_facts.items():
            if fact['status'] == 'pass' and fact['confidence'] >= min_confidence:
                strengths.append(fact)
        return strengths

    def get_verified_critical_issues(self):
        """
        Returns ONLY findings where severity == P0 AND status == fail AND evidence exists.
        """
        critical = []
        for fid, fact in self.verified_facts.items():
            if fact['severity'] == 'P0' and fact['status'] == 'fail' and fact['evidence']:
                critical.append(fact)
        return critical
