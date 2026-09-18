"""
Claim Validator Module
Enforces strict anti-hallucination, no-guaranteed-outcome rules,
validates unsupported AI platform claims, and verifies numerical consistency against factual datasets.
"""

import re

class ClaimValidator:
    FORBIDDEN_GUARANTEES = [
        r'guaranteed?\s+(?:ranking|citation|traffic|recommendation|conversion|top\s*\d+)',
        r'will\s+rank\s+(?:#?1|top\s*\d+|first)',
        r'guarantee\s+top',
        r'will\s+definitely\s+cite',
        r'will\s+guarantee',
        r'100%\s+guaranteed?\s+results?',
        r'will\s+increase\s+traffic\s+by'
    ]

    UNSUPPORTED_AI_PLATFORM_CLAIMS = [
        r'chatgpt\s+(?:requires|demands|mandates|will\s+always\s+cite)',
        r'perplexity\s+(?:cross-references\s+everything|always\s+prefers|guarantees\s+inclusion)',
        r'ai\s+systems\s+definitely\s+(?:require|ignore|rank\s+highest)',
        r'google\s+ai\s+overviews?\s+will\s+exclusively\s+cite'
    ]

    ALLOWED_CALIBRATED_PATTERNS = [
        r'potential\s+to\s+improve',
        r'stronger\s+citation-readiness',
        r'may\s+improve\s+discoverability',
        r'opportunity\s+to\s+target',
        r'designed\s+to\s+improve\s+retrieval',
        r'expected\s+improvement\s+in\s+retrieval\s+readiness',
        r'alignment\s+with\s+ai\s+search\s+best\s+practices'
    ]

    def __init__(self):
        pass

    def validate_text(self, text, verified_dataset=None, page_scope=None):
        """
        Validates text for:
        1. Absence of forbidden guaranteed claims
        2. Absence of unsupported AI platform claims
        3. Numerical metric existence in verified dataset
        4. Cross-page scope isolation
        """
        violations = []

        # 1. Check for forbidden guaranteed language
        for pattern in self.FORBIDDEN_GUARANTEES:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for m in matches:
                    violations.append({
                        "type": "FORBIDDEN_GUARANTEE",
                        "severity": "P0",
                        "match": m,
                        "message": f"Forbidden guarantee language detected: '{m}'. Replace with calibrated probability phrasing."
                    })

        # 2. Check for unsupported AI platform claims
        for pattern in self.UNSUPPORTED_AI_PLATFORM_CLAIMS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for m in matches:
                    violations.append({
                        "type": "UNSUPPORTED_AI_PLATFORM_CLAIM",
                        "severity": "P1",
                        "match": m,
                        "message": f"Unsupported absolute AI platform claim detected: '{m}'. Rephrase as retrieval readiness consideration or general GEO principle."
                    })

        # 3. Check numerical claims if dataset provided
        if verified_dataset:
            known_numbers = self._extract_numbers_from_dataset(verified_dataset)
            text_numbers = self._extract_numbers_from_text(text)
            for num in text_numbers:
                # Exclude common years, generic small single digits like 1, 2, 3 unless metric specific
                if num in [1, 2, 3, 4, 5, 2025, 2026, 100, 0]:
                    continue
                if num not in known_numbers:
                    # Check if it's a suspicious unsupported numerical claim
                    if any(kw in text.lower() for kw in ['traffic', 'revenue', 'customers', 'rank', 'queries', 'backlinks', 'leads', 'conversions']):
                        violations.append({
                            "type": "UNSUPPORTED_NUMERICAL_STATISTIC",
                            "severity": "P1",
                            "match": str(num),
                            "message": f"Numerical claim '{num}' not found in verified project dataset."
                        })

        # 4. Multi-page data scope check
        if page_scope:
            other_pages = ['index.html', 'jaipur-transport-services.html', 'about.html', 'contact.html']
            other_pages = [p for p in other_pages if p != page_scope and p.lower() in text.lower()]
            if other_pages:
                violations.append({
                    "type": "CROSS_PAGE_EVIDENCE_MIXING",
                    "severity": "P1",
                    "match": ", ".join(other_pages),
                    "message": f"Text contains references to other page scopes ({', '.join(other_pages)}) without explicit multi-page aggregation."
                })

        return {
            "is_valid": len([v for v in violations if v['severity'] == 'P0']) == 0,
            "violations": violations
        }

    def _extract_numbers_from_text(self, text):
        raw_nums = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        nums = []
        for rn in raw_nums:
            try:
                nums.append(float(rn) if '.' in rn else int(rn))
            except:
                pass
        return nums

    def _extract_numbers_from_dataset(self, dataset):
        known = set()
        if isinstance(dataset, dict):
            for k, v in dataset.items():
                if isinstance(v, (int, float)):
                    known.add(v)
                elif isinstance(v, str):
                    for n in self._extract_numbers_from_text(v):
                        known.add(n)
                elif isinstance(v, (list, dict)):
                    known.update(self._extract_numbers_from_dataset(v))
        elif isinstance(dataset, list):
            for item in dataset:
                known.update(self._extract_numbers_from_dataset(item))
        return known

    def classify_source_type(self, statement, evidence=None):
        if evidence and len(evidence) > 10:
            return "project_evidence"
        if any(term in statement.lower() for term in ['recommend', 'should', 'suggest', 'consider', 'deploy']):
            return "recommendation"
        if any(term in statement.lower() for term in ['indicates', 'suggests', 'implies', 'likely']):
            return "inference"
        return "general_knowledge"

    def sanitize_claim(self, claim_text):
        sanitized = claim_text
        sanitized = re.sub(r'will\s+rank\s+(?:top\s*1–3|top\s*3|#1)', 'has the potential to improve visibility in top organic positions', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'guaranteed?\s+citations?', 'stronger citation-readiness potential', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'guaranteed?\s+traffic', 'expected improvement in organic discovery', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'chatgpt\s+requires', 'ChatGPT search indexing benefits from', sanitized, flags=re.IGNORECASE)
        return sanitized
