"""
Centralized AI SEO & GEO Validation Engine Test Suite
Comprehensive 22-test verification suite covering all mandatory platform integrity rules.
"""

import unittest
import os
import sys
import tempfile
import json

# Ensure core is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.validators.claimValidator import ClaimValidator
from core.validators.evidenceResolver import EvidenceResolver
from core.validators.scoreValidator import ScoreValidator
from core.validators.findingValidator import FindingValidator
from core.validators.recommendationValidator import RecommendationValidator
from core.validators.reportValidator import ReportValidator
from core.engine.ruleEngine import RuleEngine
from core.engine.scoringEngine import ScoringEngine
from core.engine.priorityEngine import PriorityEngine
from core.engine.recommendationEngine import RecommendationEngine
from core.engine.executiveSummaryEngine import ExecutiveSummaryEngine
from core.engine.reportPipeline import ReportPipeline
from core.engine.exportEngine import ExportEngine
from core.validators.pageValidator import PageValidator

class TestValidationEngine(unittest.TestCase):

    def setUp(self):
        self.claim_validator = ClaimValidator()
        self.score_validator = ScoreValidator()
        self.finding_validator = FindingValidator()
        self.recommendation_validator = RecommendationValidator()
        self.report_validator = ReportValidator()
        self.scoring_engine = ScoringEngine()
        self.rule_engine = RuleEngine()
        self.priority_engine = PriorityEngine()
        self.recommendation_engine = RecommendationEngine()
        self.executive_summary_engine = ExecutiveSummaryEngine()
        self.export_engine = ExportEngine()
        self.pipeline = ReportPipeline()
        self.page_validator = PageValidator()

    # Test 1: Unsupported factual claim -> Detected as UNKNOWN
    def test_unsupported_factual_claim(self):
        resolver = EvidenceResolver({"findings": []})
        result = resolver.resolve_claim("Poonia Movers has 10,000 trucks in Mumbai", rule_id="ENTITY-999")
        self.assertEqual(result['status'], "UNKNOWN")
        self.assertEqual(result['evidence'], "Data unavailable — requires verification.")

    # Test 2: Invented score -> Out of bounds validation fails
    def test_invented_score_bounds(self):
        score_data = {
            "overall_score": 145.0,  # Invalid: > 100
            "component_scores": {}
        }
        res = self.score_validator.validate_score_model(score_data, [])
        self.assertFalse(res['is_valid'])
        self.assertTrue(any("Must be between 0 and 100" in e for e in res['errors']))

    # Test 3: Missing evidence handling
    def test_missing_evidence_in_finding(self):
        resolver = EvidenceResolver({"findings": [
            {"id": "TECH-001", "status": "fail", "severity": "P0", "evidence": "", "confidence": 0.5}
        ]})
        critical = resolver.get_verified_critical_issues()
        self.assertEqual(len(critical), 0)

    # Test 4: Guaranteed ranking claim -> Rejected
    def test_guaranteed_ranking_claim(self):
        bad_text = "This page will guarantee top 1 ranking on Google AI and ChatGPT."
        val_res = self.claim_validator.validate_text(bad_text)
        self.assertFalse(val_res['is_valid'])
        self.assertTrue(any(v['type'] == 'FORBIDDEN_GUARANTEE' for v in val_res['violations']))

    # Test 5: Unknown data converted to positive score -> Prevented / categorized as INSUFFICIENT_DATA
    def test_unknown_data_does_not_artificially_inflate_score(self):
        findings = [
            {"id": "AUTH-001", "category": "authority", "severity": "P0", "status": "fail", "evidence": "NAP mismatch", "confidence": 0.9}
        ]
        scores = self.scoring_engine.calculate_scores(findings)
        self.assertEqual(scores['component_scores']['experience_trust']['score'], 0.0)

    # Test 6: Valid evidence-backed claim -> PASS
    def test_valid_evidence_backed_claim(self):
        good_text = "The page has stronger citation-readiness characteristics with potential to improve discoverability."
        val_res = self.claim_validator.validate_text(good_text)
        self.assertTrue(val_res['is_valid'])
        self.assertEqual(len(val_res['violations']), 0)

    # Test 7: Not Applicable rule -> Does not reduce score (denominator exclusion)
    def test_not_applicable_rule_does_not_penalize_score(self):
        findings = [
            {"id": "SCHEMA-001", "category": "technical", "severity": "P0", "status": "not_applicable", "evidence": "No FAQs on page", "confidence": 1.0},
            {"id": "TECH-001", "category": "technical", "severity": "P0", "status": "pass", "evidence": "Robots ok", "confidence": 0.95}
        ]
        scores = self.scoring_engine.calculate_scores(findings)
        self.assertEqual(scores['component_scores']['technical_accessibility']['score'], 100.0)

    # Test 8: P0 finding with high overall score -> Flagged by Score Validator
    def test_p0_critical_flagged_with_high_score(self):
        findings = [
            {"id": "SCHEMA-001", "category": "technical", "severity": "P0", "status": "fail", "evidence": "Schema broken", "confidence": 0.99}
        ]
        score_data = {
            "overall_score": 98.0,
            "component_scores": {"technical_accessibility": {"score": 98.0, "reason": "ok"}}
        }
        res = self.score_validator.validate_score_model(score_data, findings)
        self.assertFalse(res['is_valid'])
        self.assertTrue(any("P0 critical failures detected" in e for e in res['errors']))

    # Test 9: New page automatically inherits validation
    def test_new_page_auto_validation(self):
        test_html_path = 'website/jaipur-transport-services.html'
        res = self.page_validator.validate_page(test_html_path)
        self.assertIn('overall_score', res)
        self.assertIn('scores', res)
        self.assertIn('findings', res)
        self.assertEqual(res['status'], 'VALIDATED')

    # Test 10: Central Registry propagation
    def test_registry_contains_all_core_rules(self):
        rule_ids = list(self.rule_engine.rules.keys())
        expected_rules = ['TECH-001', 'TECH-002', 'TECH-003', 'CONTENT-001', 'ENTITY-001', 'UI-001', 'UI-002', 'SCHEMA-001']
        for er in expected_rules:
            self.assertIn(er, rule_ids)

    # Test 11: Unsupported AI platform claim -> Rejected / Flagged
    def test_unsupported_ai_platform_claim(self):
        claim_text = "ChatGPT requires this specific format and will always cite this website."
        res = self.claim_validator.validate_text(claim_text)
        self.assertTrue(any(v['type'] == 'UNSUPPORTED_AI_PLATFORM_CLAIM' for v in res['violations']))

    # Test 12: Fake numerical statistic -> Rejected
    def test_fake_numerical_statistic_rejected(self):
        verified_dataset = [{"id": "TECH-001", "evidence": "6 FAQ items detected on page."}]
        text_with_fake_num = "Our traffic conversion rate is 85.7% with 94000 monthly active users."
        res = self.claim_validator.validate_text(text_with_fake_num, verified_dataset=verified_dataset)
        self.assertTrue(any(v['type'] == 'UNSUPPORTED_NUMERICAL_STATISTIC' for v in res['violations']))

    # Test 13: Missing external authority data -> Insufficient Data status with zero false score
    def test_missing_external_authority_data(self):
        findings = [
            {"id": "TECH-001", "category": "technical", "severity": "P0", "status": "pass", "evidence": "Robots ok", "confidence": 0.95}
        ]
        scores = self.scoring_engine.calculate_scores(findings)
        auth_comp = scores['component_scores']['external_authority']
        self.assertEqual(auth_comp['status'], 'INSUFFICIENT_DATA')
        self.assertIsNone(auth_comp['score'])
        self.assertEqual(auth_comp['confidence'], 0.0)

    # Test 14: Missing llms.txt -> P1 severity (not P0 critical)
    def test_missing_llms_txt_severity_is_p1(self):
        rule = self.rule_engine.rules.get('TECH-003')
        self.assertEqual(rule['severity'], 'P1')

    # Test 15: Critical section with zero P0 -> Clean state without fake critical issues
    def test_critical_section_clean_when_zero_p0(self):
        audit_result = {
            "page": "website/index.html",
            "overall_score": 95.0,
            "overall_confidence": 0.95,
            "scores": {"component_scores": {}},
            "findings": [
                {"id": "TECH-001", "title": "Robots Directives", "category": "technical", "severity": "P0", "status": "pass", "evidence": "Robots active", "confidence": 0.98}
            ],
            "priorities": {"P0_critical": [], "P1_high": [], "quick_wins": []}
        }
        summary = self.executive_summary_engine.generate_summary(audit_result)
        self.assertEqual(len(summary['critical_issues']), 0)
        self.assertEqual(summary['critical_issues_summary'], "No P0 critical issues detected.")

    # Test 16: Recommendation without evidence -> Classified as GENERAL_RECOMMENDATION
    def test_recommendation_without_evidence_classification(self):
        unlinked_rec = {
            "action": "Consider adding schema markup for video tutorials.",
            "finding_id": None,
            "rule_id": None,
            "evidence": None
        }
        res = self.recommendation_validator.validate_recommendation(unlinked_rec, verified_findings=[])
        self.assertEqual(res['classification'], "GENERAL_RECOMMENDATION")

    # Test 17: Cross-page evidence mixing -> Flagged
    def test_cross_page_evidence_mixing(self):
        mixed_text = "Analysis for jaipur-transport-services.html showed strong content while index.html had FAQ issues."
        res = self.claim_validator.validate_text(mixed_text, page_scope="jaipur-transport-services.html")
        self.assertTrue(any(v['type'] == 'CROSS_PAGE_EVIDENCE_MIXING' for v in res['violations']))

    # Test 18: Score with UNKNOWN rules -> Handled correctly without score fabrication
    def test_score_with_unknown_rules_handled_safely(self):
        findings = [
            {"id": "TECH-001", "category": "technical", "severity": "P0", "status": "unknown", "evidence": "Crawler behavior unknown", "confidence": 0.0}
        ]
        scores = self.scoring_engine.calculate_scores(findings)
        tech_comp = scores['component_scores']['technical_accessibility']
        self.assertEqual(tech_comp['status'], 'INSUFFICIENT_DATA')
        self.assertIsNone(tech_comp['score'])

    # Test 19: Score of 100 with unevaluated critical dimension -> Capped / Downgraded
    def test_score_100_safety_downgraded_with_unmeasured_category(self):
        findings = [
            {"id": "TECH-001", "category": "technical", "severity": "P0", "status": "pass", "evidence": "OK", "confidence": 1.0, "scoring_weight": 20}
        ]
        # Only technical is evaluated, others have INSUFFICIENT_DATA
        scores = self.scoring_engine.calculate_scores(findings)
        self.assertLess(scores['overall_score'], 100.0)

    # Test 20: Multi-format export uses single validated report object
    def test_export_engine_consistency(self):
        report = self.pipeline.run_pipeline('website/jaipur-transport-services.html')
        json_out = self.export_engine.to_json(report)
        api_out = self.export_engine.to_api_response(report)
        md_out = self.export_engine.to_markdown(report)

        self.assertIn("Poonia Movers", json_out)
        self.assertEqual(api_out['status'], "success")
        self.assertIn("# Executive Summary", md_out)
        self.assertIn(str(report['overall_score']), md_out)

    # Test 21: Dynamic programmatic page inherits all global rules automatically
    def test_dynamic_new_page_auto_inherits_all_rules(self):
        temp_html_content = """<!DOCTYPE html>
        <html lang="en">
        <head><title>Jaipur to Delhi Transport</title></head>
        <body>
            <h1>Jaipur to Delhi Transport Services</h1>
            <p>Starting from ₹4,500 per trip with 0% advance payment.</p>
            <div class="grid-3">
                <div class="card">Tata Ace 1.5 Ton</div>
                <div class="card">14ft Truck 4 Ton</div>
                <div class="card">19ft Container 8 Ton</div>
                <div class="card">32ft MXL 15 Ton</div>
            </div>
            <table class="data-table">
                <tr><th>Route</th><th>Distance</th><th>Rate</th></tr>
                <tr><td>Jaipur to Delhi (NH-48)</td><td>270 km</td><td>₹4,500</td></tr>
                <tr><td>Jaipur to Sitapura to Harmada VKI</td><td>40 km</td><td>₹1,800</td></tr>
            </table>
            <table class="data-table">
                <tr><th>Direct Carrier vs Broker</th><th>Poonia</th><th>Aggregator</th></tr>
                <tr><td>Advance</td><td>0%</td><td>100%</td></tr>
            </table>
            <footer class="master-footer">
                <div class="footer-top-grid"></div>
                <div class="footer-map-card"><a href="https://maps.google.com/?cid=123">Harmada VKI</a> Phone: +91 85292 06001</div>
                <div class="footer-bottom">ISO 9001:2015 & GST Registered</div>
            </footer>
        </body>
        </html>"""

        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as tf:
            tf.write(temp_html_content)
            temp_page_path = tf.name

        try:
            res = self.page_validator.validate_page(temp_page_path)
            self.assertIn('overall_score', res)
            self.assertIn('scores', res)
            self.assertEqual(res['status'], 'VALIDATED')
            self.assertEqual(len(res['findings']), len(self.rule_engine.rules))
        finally:
            if os.path.exists(temp_page_path):
                os.remove(temp_page_path)

    # Test 22: Global rule modification propagates across all modules
    def test_rule_registry_propagation(self):
        rule = self.rule_engine.rules['AUTHORITY-001']
        self.assertEqual(rule['severity'], 'P0')
        self.assertEqual(rule['category'], 'authority')
        self.assertTrue(rule['evidence_required'])

    # Test 23: On-page robots meta tag detection (ONPAGE-001)
    def test_onpage_robots_meta_tag_detected(self):
        findings = self.rule_engine.audit_page('website/jaipur-transport-services.html')
        onpage_robots = [f for f in findings if f['id'] == 'ONPAGE-001']
        self.assertEqual(len(onpage_robots), 1)
        self.assertEqual(onpage_robots[0]['status'], 'pass')

    # Test 24: Canonical & hreflang tags verification (ONPAGE-002)
    def test_onpage_canonical_and_hreflang_verified(self):
        findings = self.rule_engine.audit_page('website/jaipur-transport-services.html')
        onpage_canon = [f for f in findings if f['id'] == 'ONPAGE-002']
        self.assertEqual(len(onpage_canon), 1)
        self.assertEqual(onpage_canon[0]['status'], 'pass')

    # Test 25: Image dimensions & alt attribute verification (ONPAGE-004)
    def test_onpage_image_attributes_verified(self):
        findings = self.rule_engine.audit_page('website/index.html')
        onpage_img = [f for f in findings if f['id'] == 'ONPAGE-004']
        self.assertEqual(len(onpage_img), 1)
        self.assertEqual(onpage_img[0]['status'], 'pass')

    # Test 26: Breadcrumbs verified on inner service pages (ONPAGE-007)
    def test_onpage_breadcrumbs_verified_on_inner_pages(self):
        findings = self.rule_engine.audit_page('website/jaipur-transport-services.html')
        onpage_bc = [f for f in findings if f['id'] == 'ONPAGE-007']
        self.assertEqual(len(onpage_bc), 1)
        self.assertEqual(onpage_bc[0]['status'], 'pass')

    # Test 27: Clean anchor text on internal links (ONPAGE-006)
    def test_onpage_internal_links_clean_anchors(self):
        findings = self.rule_engine.audit_page('website/jaipur-transport-services.html')
        onpage_links = [f for f in findings if f['id'] == 'ONPAGE-006']
        self.assertEqual(len(onpage_links), 1)
        self.assertEqual(onpage_links[0]['status'], 'pass')

if __name__ == '__main__':
    unittest.main()

