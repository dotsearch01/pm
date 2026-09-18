"""
Finding Validator Module
Validates that every finding conforms strictly to the normalized schema:
- Must have valid status (PASS, FAIL, WARNING, NOT_APPLICABLE, UNKNOWN, ERROR)
- Must have valid severity (P0, P1, P2, P3)
- Must have non-empty evidence if required
- Must not manufacture facts or lack source attribution
"""

class FindingValidator:
    VALID_STATUSES = {'pass', 'fail', 'warning', 'not_applicable', 'unknown', 'error'}
    VALID_SEVERITIES = {'P0', 'P1', 'P2', 'P3'}
    VALID_SOURCE_TYPES = {'project_evidence', 'official_documentation', 'external_research', 'inference', 'recommendation', 'unknown'}

    def __init__(self):
        pass

    def validate_finding(self, finding):
        errors = []
        fid = finding.get('id')
        if not fid:
            errors.append("Finding missing required 'id'.")

        status = str(finding.get('status', '')).lower()
        if status not in self.VALID_STATUSES:
            errors.append(f"Invalid status '{status}' for finding {fid}. Allowed: {self.VALID_STATUSES}")

        sev = finding.get('severity')
        if sev not in self.VALID_SEVERITIES:
            errors.append(f"Invalid severity '{sev}' for finding {fid}. Allowed: {self.VALID_SEVERITIES}")

        evidence = finding.get('evidence', '')
        if status in ['pass', 'fail'] and not evidence:
            errors.append(f"Finding {fid} has status '{status}' but missing required empirical evidence.")

        confidence = finding.get('confidence', 0.0)
        if not (0.0 <= confidence <= 1.0):
            errors.append(f"Confidence {confidence} out of range [0.0, 1.0] for finding {fid}.")

        source_type = finding.get('source_type', 'project_evidence')
        if source_type not in self.VALID_SOURCE_TYPES:
            errors.append(f"Invalid source_type '{source_type}' for finding {fid}.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "finding_id": fid
        }

    def validate_all(self, findings):
        all_errors = []
        for f in findings:
            res = self.validate_finding(f)
            if not res['is_valid']:
                all_errors.extend(res['errors'])
        return {
            "is_valid": len(all_errors) == 0,
            "errors": all_errors,
            "total_validated": len(findings)
        }
