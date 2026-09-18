import os
from core.engine.reportPipeline import ReportPipeline

class PageValidator:
    def __init__(self, base_dir='.'):
        self.base_dir = base_dir
        self.pipeline = ReportPipeline(base_dir=base_dir)

    def validate_page(self, page_path):
        report = self.pipeline.run_pipeline(page_path)
        return {
            "page": report['page'],
            "is_valid": report['status'] == 'VALIDATED',
            "overall_score": report['overall_score'],
            "overall_confidence": report['overall_confidence'],
            "scores": report['scores'],
            "counts": report['counts'],
            "findings": report['findings'],
            "priorities": report['priorities'],
            "recommendations": report['recommendations'],
            "executive_summary": report['executive_summary'],
            "quality_gate": report['quality_gate'],
            "status": report['status']
        }
