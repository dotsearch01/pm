import os
import sys
import json
import argparse

# Ensure core is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from core.engine.reportPipeline import ReportPipeline
from core.engine.exportEngine import ExportEngine

def main():
    parser = argparse.ArgumentParser(description="Poonia Movers Centralized AI SEO & GEO Global Rule Engine")
    parser.add_argument('command', choices=['audit', 'audit-all', 'validate', 'export-markdown'], help="Audit command")
    parser.add_argument('--page', default='website/jaipur-transport-services.html', help="Target HTML page")
    parser.add_argument('--output', default='audit_report.json', help="Output report path")
    args = parser.parse_args()

    pipeline = ReportPipeline(base_dir='.')
    export_engine = ExportEngine()

    if args.command in ['audit', 'validate', 'export-markdown']:
        target_page = args.page
        if not os.path.exists(target_page):
            print(f"Error: Target page '{target_page}' not found.")
            sys.exit(1)

        result = pipeline.run_pipeline(target_page)
        
        print("\n==========================================================================")
        print(f"POONIA MOVERS AI SEO / GEO AUDIT REPORT — {result['page']}")
        print("==========================================================================")
        print(f"Quality Gate Status: {'✅ VALIDATED' if result['status'] == 'VALIDATED' else '⚠️ NEEDS_REVIEW'}")
        print(f"Overall AI Search Readiness Score: {result['overall_score']} / 100 (Confidence: {result['overall_confidence']})")
        print(f"Rules Evaluated: {result['counts']['total_rules']} | Passed: {result['counts']['passed']} | Warnings: {result['counts']['warnings']} | Failed: {result['counts']['failed']}")
        print("--------------------------------------------------------------------------")
        print("DIMENSION SCORES:")
        for dim, sdata in result['scores']['component_scores'].items():
            sc_str = f"{sdata['score']:>5.1f} / 100" if sdata['score'] is not None else " INSUFFICIENT DATA"
            print(f"  • {dim.replace('_', ' ').title():<28}: {sc_str} (Conf: {sdata.get('confidence', 0.0)})")
        print("--------------------------------------------------------------------------")

        if result['priorities']['P0_critical']:
            print("🚨 P0 CRITICAL ISSUES:")
            for issue in result['priorities']['P0_critical']:
                print(f"  - [{issue['id']}] {issue['title']}: {issue['evidence']}")
                print(f"    Action: {issue['recommendation']}")
        else:
            print("🚨 CRITICAL ISSUES: No P0 critical issues detected.")

        if result['priorities']['P1_high']:
            print("\n⚠️ P1 HIGH IMPACT OPPORTUNITIES:")
            for issue in result['priorities']['P1_high']:
                print(f"  - [{issue['id']}] {issue['title']}: {issue['evidence']}")

        if result['priorities']['quick_wins']:
            print("\n⚡ QUICK WINS:")
            for qw in result['priorities']['quick_wins']:
                print(f"  - {qw['title']} -> {qw['action']}")

        print("==========================================================================\n")

        if args.command == 'export-markdown':
            md_output = export_engine.to_markdown(result)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md_output)
            print(f"Full markdown report saved to '{args.output}'")
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Full audit report saved to '{args.output}'")

    elif args.command == 'audit-all':
        website_dir = 'website'
        pages = [os.path.join(website_dir, f) for f in os.listdir(website_dir) if f.endswith('.html')]
        all_results = []
        for p in pages:
            res = pipeline.run_pipeline(p)
            all_results.append(res)
            print(f"[{res['page']}] Score: {res['overall_score']} (Conf: {res['overall_confidence']}) | Status: {res['status']}")

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nAll pages audited. Consolidated report written to '{args.output}'")

if __name__ == '__main__':
    main()
