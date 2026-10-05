"""
Report Pipeline Module
Single unified entry point that executes the end-to-end AI SEO / GEO audit and validation pipeline.
Guarantees that no component, UI, API, or export can bypass rule execution, scoring, or quality gates.
"""

import os
import json
from datetime import datetime

from core.engine.ruleEngine import RuleEngine
from core.engine.scoringEngine import ScoringEngine
from core.engine.priorityEngine import PriorityEngine
from core.engine.recommendationEngine import RecommendationEngine
from core.engine.executiveSummaryEngine import ExecutiveSummaryEngine
from core.validators.reportValidator import ReportValidator

class ReportPipeline:
    def __init__(self, base_dir='.'):
        self.base_dir = base_dir
        self.rule_engine = RuleEngine()
        self.scoring_engine = ScoringEngine()
        self.priority_engine = PriorityEngine()
        self.recommendation_engine = RecommendationEngine()
        self.executive_summary_engine = ExecutiveSummaryEngine()
        self.report_validator = ReportValidator()

    def run_pipeline(self, page_path):
        if not os.path.exists(page_path):
            raise FileNotFoundError(f"Target page '{page_path}' not found.")

        rel_page = os.path.relpath(page_path, self.base_dir)

        # 1. Rule Execution & Normalized Findings
        findings = self.rule_engine.audit_page(page_path, base_dir=self.base_dir)

        # 2. Scoring Engine
        scores = self.scoring_engine.calculate_scores(findings)

        # 3. Priority Engine
        priorities = self.priority_engine.prioritize_findings(findings)

        # 4. Recommendation Engine
        recommendations = self.recommendation_engine.generate_recommendations(findings, priorities)

        # 5. Interim Report Object for Executive Summary
        interim_data = {
            "page": rel_page,
            "overall_score": scores['overall_score'],
            "overall_confidence": scores['overall_confidence'],
            "scores": scores,
            "findings": findings,
            "priorities": priorities
        }

        # 6. Executive Summary Generation & Claim Validation
        exec_summary = self.executive_summary_engine.generate_summary(interim_data)

        # 7. Complete Report Assembly
        report_data = {
            "project": "Poonia Movers",
            "page": rel_page,
            "timestamp": datetime.now().isoformat(),
            "overall_score": scores['overall_score'],
            "overall_confidence": scores['overall_confidence'],
            "scores": scores,
            "counts": {
                "total_rules": len(findings),
                "passed": len([f for f in findings if f.get('status') == 'pass']),
                "failed": len([f for f in findings if f.get('status') == 'fail']),
                "warnings": len([f for f in findings if f.get('status') == 'warning']),
                "unknown": len([f for f in findings if f.get('status') == 'unknown']),
                "not_applicable": len([f for f in findings if f.get('status') == 'not_applicable']),
                "p0_critical": len(priorities['P0_critical']),
                "p1_high": len(priorities['P1_high'])
            },
            "findings": findings,
            "priorities": priorities,
            "recommendations": recommendations,
            "executive_summary": exec_summary
        }

        # 8. Global Quality Gate Validation
        validation_result = self.report_validator.validate_report(report_data)
        report_data['quality_gate'] = validation_result
        report_data['status'] = validation_result['status']

        return report_data
