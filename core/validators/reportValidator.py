"""
Report Validator Module (Global Quality Gate)
Orchestrates end-to-end validation across data, findings, scores, claims, and recommendations.
Sets report status to VALIDATED or NEEDS_REVIEW.
"""

from core.validators.findingValidator import FindingValidator
from core.validators.scoreValidator import ScoreValidator
from core.validators.claimValidator import ClaimValidator
from core.validators.recommendationValidator import RecommendationValidator

class ReportValidator:
    def __init__(self):
        self.finding_validator = FindingValidator()
        self.score_validator = ScoreValidator()
        self.claim_validator = ClaimValidator()
        self.recommendation_validator = RecommendationValidator()

    def validate_report(self, report_data):
        findings = report_data.get('findings', [])
        scores = report_data.get('scores', {})
        summary = report_data.get('executive_summary', {})
        recommendations = report_data.get('recommendations', [])
        page = report_data.get('page', '')

        all_errors = []
        all_warnings = []

        # 1. Finding Validation
        finding_res = self.finding_validator.validate_all(findings)
        if not finding_res['is_valid']:
            all_errors.extend(finding_res['errors'])

        # 2. Score Validation
        score_res = self.score_validator.validate_score_model(scores, findings)
        if not score_res['is_valid']:
            all_errors.extend(score_res['errors'])

        # 3. Recommendation Validation
        rec_res = self.recommendation_validator.validate_all(recommendations, findings)
        if not rec_res['is_valid']:
            all_errors.extend(rec_res['errors'])

        # 4. Claim Validation on Executive Summary text
        if summary:
            summary_text = f"{summary.get('overall_assessment', '')} {summary.get('final_recommendation', '')}"
            claim_res = self.claim_validator.validate_text(summary_text, verified_dataset=findings, page_scope=page)
            for v in claim_res.get('violations', []):
                if v['severity'] == 'P0':
                    all_errors.append(v['message'])
                else:
                    all_warnings.append(v['message'])

        # 5. P0 Critical Failure Check
        p0_fails = [f for f in findings if f.get('severity') == 'P0' and f.get('status') == 'fail']
        if p0_fails:
            all_errors.append(f"{len(p0_fails)} P0 critical issue(s) detected in page audit.")

        status = "VALIDATED" if len(all_errors) == 0 else "NEEDS_REVIEW"

        return {
            "status": status,
            "is_valid": status == "VALIDATED",
            "errors": all_errors,
            "warnings": all_warnings,
            "validation_timestamp": report_data.get('timestamp', '')
        }
