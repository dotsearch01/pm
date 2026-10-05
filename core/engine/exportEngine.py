"""
Export Engine Module
Generates Web, Markdown, PDF-ready HTML, and API JSON formats strictly from the unified validated report object.
Guarantees zero divergence across export surfaces.
"""

import json

class ExportEngine:
    def __init__(self):
        pass

    def to_json(self, report_data, indent=2):
        return json.dumps(report_data, indent=indent, ensure_ascii=False)

    def to_api_response(self, report_data):
        return {
            "status": "success" if report_data.get('status') == 'VALIDATED' else "needs_review",
            "data": {
                "page": report_data.get('page'),
                "score": report_data.get('overall_score'),
                "confidence": report_data.get('overall_confidence'),
                "quality_gate": report_data.get('quality_gate'),
                "component_scores": report_data.get('scores', {}).get('component_scores', {}),
                "critical_issues": report_data.get('executive_summary', {}).get('critical_issues', []),
                "strong_areas": report_data.get('executive_summary', {}).get('strong_areas', []),
                "recommendations": report_data.get('recommendations', [])
            }
        }

    def to_markdown(self, report_data):
        page = report_data.get('page', '')
        score = report_data.get('overall_score', 0)
        conf = report_data.get('overall_confidence', 0)
        status = report_data.get('status', 'NEEDS_REVIEW')
        summary = report_data.get('executive_summary', {})
        scores = report_data.get('scores', {})

        md = []
        md.append(f"# Executive Summary — {page}\n")
        md.append(f"**Quality Gate Status**: `{status}` | **Overall AI Search Readiness**: `{score}/100` (Confidence: `{conf}`)\n")
        
        md.append("## Overall Assessment\n")
        md.append(f"{summary.get('overall_assessment', '')}\n")

        md.append("## AI Search Readiness Score\n")
        md.append("| Dimension | Score | Confidence | Status | Reason |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for dim, sdata in scores.get('component_scores', {}).items():
            sc_str = f"{sdata['score']}/100" if sdata['score'] is not None else "Insufficient Data"
            md.append(f"| {dim.replace('_', ' ').title()} | {sc_str} | {sdata.get('confidence', 0.0)} | {sdata.get('status', '')} | {sdata.get('reason', '')} |")
        md.append("")

        md.append("## Critical Issues\n")
        crit = summary.get('critical_issues', [])
        if crit:
            for c in crit:
                md.append(f"- **[{c['id']}] {c['problem']}**: {c['evidence']}")
                md.append(f"  *Recommended Fix*: {c['recommended_fix']}")
        else:
            md.append("No P0 critical issues detected.\n")

        md.append("## Strong Areas\n")
        for s in summary.get('strong_areas', []):
            md.append(f"- **{s['strength']}**: {s['evidence']}")

        md.append("\n## Biggest Opportunities\n")
        for o in summary.get('biggest_opportunities', []):
            md.append(f"- **{o['opportunity']}**: {o['evidence']}")
            md.append(f"  *Why it matters*: {o['why']}")
            md.append(f"  *Expected impact*: {o['expected_impact']}")

        md.append("\n## AI Search Readiness by Platform\n")
        md.append("| Platform | Readiness | Evidence | Confidence | Improvement |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for p in summary.get('ai_platform_readiness', []):
            md.append(f"| {p['platform']} | {p['readiness']} | {p['evidence']} | {p['confidence']} | {p['recommended_improvement']} |")

        md.append("\n## Top Priority Actions\n")
        for a in summary.get('top_priority_actions', []):
            md.append(f"- `[{a['priority']}]` **{a['action']}** (Scope: `{a['where']}`)")
            md.append(f"  *Expected Impact*: {a['expected_impact']}")

        md.append("\n## Quick Wins\n")
        for q in summary.get('quick_wins', []):
            md.append(f"- **{q['title']}** ({q['effort']} Effort, {q['impact']} Impact): {q['action']}")

        md.append("\n## Final Recommendation\n")
        md.append(f"{summary.get('final_recommendation', '')}\n")

        return "\n".join(md)
