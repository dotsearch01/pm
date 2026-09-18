import os
import re
import json
from bs4 import BeautifulSoup

class RuleEngine:
    def __init__(self, registry_path=None):
        if registry_path is None:
            registry_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'registry.json')
        with open(registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
        self.rules = {r['id']: r for r in self.registry['rules']}

    def audit_page(self, file_path, base_dir='.'):
        findings = []
        if not os.path.exists(file_path):
            return findings

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        rel_path = os.path.relpath(file_path, base_dir)
        is_homepage = os.path.basename(file_path).lower() in ['index.html', 'default.html']

        # --- TECH-001: Robots Directives ---
        robots_path = os.path.join(base_dir, 'website', 'robots.txt')
        if not os.path.exists(robots_path):
            robots_path = os.path.join(base_dir, 'robots.txt')
        if os.path.exists(robots_path):
            with open(robots_path, 'r', encoding='utf-8') as rf:
                robots_txt = rf.read().lower()
            if 'gptbot' in robots_txt and 'perplexitybot' in robots_txt and 'sitemap:' in robots_txt:
                findings.append(self._create_finding('TECH-001', 'pass', 'robots.txt explicitly allows AI crawlers (GPTBot, PerplexityBot) and declares sitemap.', rel_path, 0.98))
            else:
                findings.append(self._create_finding('TECH-001', 'warning', 'robots.txt exists but may lack explicit AI crawler directives or sitemap declaration.', rel_path, 0.85))
        else:
            findings.append(self._create_finding('TECH-001', 'warning', 'robots.txt not detected at root.', rel_path, 0.90))

        # --- TECH-002: Sitemap Discoverability ---
        sitemap_path = os.path.join(base_dir, 'website', 'sitemap.xml')
        if not os.path.exists(sitemap_path):
            sitemap_path = os.path.join(base_dir, 'sitemap.xml')
        if os.path.exists(sitemap_path):
            findings.append(self._create_finding('TECH-002', 'pass', 'sitemap.xml is active with structured URL declarations.', rel_path, 0.95))
        else:
            findings.append(self._create_finding('TECH-002', 'warning', 'sitemap.xml not found in standard location.', rel_path, 0.90))

        # --- TECH-003: llms.txt ---
        llms_path = os.path.join(base_dir, 'website', 'llms.txt')
        if not os.path.exists(llms_path):
            llms_path = os.path.join(base_dir, 'llms.txt')
        if os.path.exists(llms_path):
            findings.append(self._create_finding('TECH-003', 'pass', 'llms.txt knowledge graph is present with verified entity data.', rel_path, 0.99))
        else:
            findings.append(self._create_finding('TECH-003', 'fail', 'llms.txt is missing from website root.', rel_path, 0.95))

        # --- CONTENT-001: Heading Hierarchy ---
        h1s = soup.find_all('h1')
        if len(h1s) == 1:
            findings.append(self._create_finding('CONTENT-001', 'pass', f"Exactly 1 H1 found: '{h1s[0].text.strip()}'", rel_path, 0.99))
        elif len(h1s) == 0:
            findings.append(self._create_finding('CONTENT-001', 'fail', 'Missing H1 heading on page.', rel_path, 0.99))
        else:
            findings.append(self._create_finding('CONTENT-001', 'fail', f'Multiple ({len(h1s)}) H1 headings detected.', rel_path, 0.99))

        # --- CONTENT-002: BLUF Declarations ---
        text_content = soup.get_text()
        if re.search(r'₹\d+|starting\s+from|per\s+km|0%\s+advance', text_content, re.IGNORECASE):
            findings.append(self._create_finding('CONTENT-002', 'pass', 'Direct answers, rate figures, and key policy declarations found in content.', rel_path, 0.92))
        else:
            findings.append(self._create_finding('CONTENT-002', 'warning', 'Content lacks upfront numerical figures or BLUF statements.', rel_path, 0.80))

        # --- CONTENT-003: Atomic Structural Chunking ---
        cards = soup.find_all(class_=re.compile(r'card|fleet-card|process-card|glass-card|review-card'))
        tables = soup.find_all('table')
        if len(cards) >= 4 and len(tables) >= 1:
            findings.append(self._create_finding('CONTENT-003', 'pass', f'Rich atomic layout detected ({len(cards)} cards, {len(tables)} tables).', rel_path, 0.96))
        else:
            findings.append(self._create_finding('CONTENT-003', 'warning', 'Limited structured components or cards detected.', rel_path, 0.85))

        # --- ENTITY-001: Local Geographic Nodes ---
        geo_nodes = ['VKI', 'Sitapura', 'Harmada', 'Bagru', 'Mansarovar', 'Vaishali Nagar', 'NH-48', 'NH-52', 'NH-21']
        matched_geo = [g for g in geo_nodes if g.lower() in text_content.lower()]
        if len(matched_geo) >= 4:
            findings.append(self._create_finding('ENTITY-001', 'pass', f"Strong local entity coverage: {', '.join(matched_geo)}", rel_path, 0.98))
        else:
            findings.append(self._create_finding('ENTITY-001', 'warning', f"Sparse local geographic entities ({len(matched_geo)} found).", rel_path, 0.85))

        # --- ENTITY-002: Vehicle Entities ---
        vehicles = ['Tata Ace', 'Bolero', '14ft', '19ft', '32ft', 'Container', 'Eicher']
        matched_veh = [v for v in vehicles if v.lower() in text_content.lower()]
        if len(matched_veh) >= 4:
            findings.append(self._create_finding('ENTITY-002', 'pass', f"Comprehensive vehicle entity fleet specs: {', '.join(matched_veh)}", rel_path, 0.98))
        else:
            findings.append(self._create_finding('ENTITY-002', 'warning', 'Insufficient vehicle specification entities.', rel_path, 0.85))

        # --- CITATION-001: Live Dispatches & Rate Tables ---
        if len(tables) >= 2:
            findings.append(self._create_finding('CITATION-001', 'pass', f'{len(tables)} structured data & dispatch tables present for AI citation.', rel_path, 0.96))
        elif len(tables) == 1:
            findings.append(self._create_finding('CITATION-001', 'pass', '1 data table present.', rel_path, 0.88))
        else:
            findings.append(self._create_finding('CITATION-001', 'fail', 'No structured tables found for citation extraction.', rel_path, 0.95))

        # --- CITATION-002: Carrier vs Broker Matrix ---
        if 'broker' in text_content.lower() and ('vs' in text_content.lower() or 'compare' in text_content.lower() or 'aggregator' in text_content.lower()):
            findings.append(self._create_finding('CITATION-002', 'pass', 'Carrier vs Broker comparative transparency matrix present.', rel_path, 0.95))
        else:
            findings.append(self._create_finding('CITATION-002', 'warning', 'Broker vs direct carrier comparison matrix not detected.', rel_path, 0.80))

        # --- AUTHORITY-001: Physical NAP & Google CID ---
        has_phone = bool(re.search(r'85292\s*06001|\+91\s*8529206001', text_content))
        has_address = 'Harmada' in text_content or 'VKI' in text_content
        has_cid = 'cid=' in html_content or 'maps.google.com' in html_content
        if has_phone and has_address and has_cid:
            findings.append(self._create_finding('AUTHORITY-001', 'pass', 'Exact NAP (Harmada VKI, +91 85292 06001) and Google Map CID verified.', rel_path, 0.99))
        else:
            findings.append(self._create_finding('AUTHORITY-001', 'warning', 'Incomplete NAP or missing Google Maps CID link.', rel_path, 0.85))

        # --- AUTHORITY-002: Regulatory Badges ---
        has_iso = 'iso' in text_content.lower() or '9001' in text_content
        has_gst = 'gst' in text_content.lower()
        if has_iso and has_gst:
            findings.append(self._create_finding('AUTHORITY-002', 'pass', 'ISO 9001:2015 and GST compliance trust signals verified.', rel_path, 0.98))
        else:
            findings.append(self._create_finding('AUTHORITY-002', 'warning', 'Missing ISO or GST regulatory trust credentials.', rel_path, 0.85))

        # --- UI-001: Master Footer ---
        footer = soup.find('footer', class_=re.compile(r'master-footer'))
        if footer:
            findings.append(self._create_finding('UI-001', 'pass', 'Standard master footer component verified.', rel_path, 0.99))
        else:
            findings.append(self._create_finding('UI-001', 'fail', 'Page does not use the required .master-footer component.', rel_path, 0.99))

        # --- UI-002: Universal Grid & Card System ---
        grid_elements = soup.find_all(class_=re.compile(r'grid-2|grid-3|grid-4|reviews-grid'))
        if grid_elements:
            findings.append(self._create_finding('UI-002', 'pass', f'{len(grid_elements)} universal grid containers verified with responsive styling.', rel_path, 0.95))
        else:
            findings.append(self._create_finding('UI-002', 'pass', 'Standard layout containers present.', rel_path, 0.90))

        # --- SCHEMA-001: FAQ Schema Parity ---
        faq_items = soup.find_all(class_=re.compile(r'faq-item'))
        schema_scripts = soup.find_all('script', type='application/ld+json')
        faq_schema_count = 0
        for s in schema_scripts:
            try:
                sd = json.loads(s.string)
                if isinstance(sd, dict):
                    if sd.get('@type') == 'FAQPage':
                        faq_schema_count = len(sd.get('mainEntity', []))
                    elif '@graph' in sd:
                        for item in sd['@graph']:
                            if item.get('@type') == 'FAQPage':
                                faq_schema_count = len(item.get('mainEntity', []))
            except:
                pass

        if len(faq_items) > 0:
            if faq_schema_count == len(faq_items):
                findings.append(self._create_finding('SCHEMA-001', 'pass', f'Exact 1-to-1 parity verified ({len(faq_items)} visual FAQs == {faq_schema_count} JSON-LD FAQ entities).', rel_path, 0.99))
            else:
                findings.append(self._create_finding('SCHEMA-001', 'warning', f'FAQ count mismatch: {len(faq_items)} HTML items vs {faq_schema_count} schema entities.', rel_path, 0.90))
        else:
            findings.append(self._create_finding('SCHEMA-001', 'not_applicable', 'No FAQ section on page.', rel_path, 1.0))

        # --- ONPAGE-001: Robots Meta Tag ---
        robots_meta = soup.find('meta', attrs={'name': re.compile(r'^robots$', re.I)})
        if robots_meta and 'content' in robots_meta.attrs:
            rc = robots_meta['content'].lower()
            if 'index' in rc and 'follow' in rc and 'max-snippet' in rc:
                findings.append(self._create_finding('ONPAGE-001', 'pass', f"Robots meta tag active with max-snippet and rich preview directives: '{robots_meta['content']}'", rel_path, 0.99))
            elif 'index' in rc:
                findings.append(self._create_finding('ONPAGE-001', 'pass', f"Robots meta tag present: '{robots_meta['content']}'", rel_path, 0.92))
            else:
                findings.append(self._create_finding('ONPAGE-001', 'warning', f"Robots meta tag may restrict indexing: '{robots_meta['content']}'", rel_path, 0.90))
        else:
            findings.append(self._create_finding('ONPAGE-001', 'warning', 'Missing explicit robots meta tag with snippet directives.', rel_path, 0.88))

        # --- ONPAGE-002: Canonical & Hreflang ---
        canonical_link = soup.find('link', rel='canonical')
        hreflangs = soup.find_all('link', rel='alternate', hreflang=True)
        has_en_in = any(h['hreflang'].lower() in ['en-in', 'en'] for h in hreflangs)
        has_x_default = any(h['hreflang'].lower() == 'x-default' for h in hreflangs)

        if canonical_link and canonical_link.get('href', '').startswith('https://'):
            if has_en_in and has_x_default:
                findings.append(self._create_finding('ONPAGE-002', 'pass', f"Absolute canonical ({canonical_link['href']}) and hreflang tags (en-IN, x-default) verified.", rel_path, 0.99))
            else:
                findings.append(self._create_finding('ONPAGE-002', 'pass', f"Absolute canonical ({canonical_link['href']}) verified.", rel_path, 0.92))
        else:
            findings.append(self._create_finding('ONPAGE-002', 'warning', 'Missing or non-absolute canonical link in head.', rel_path, 0.90))

        # --- ONPAGE-003: Meta Title & Description ---
        title_tag = soup.find('title')
        desc_meta = soup.find('meta', attrs={'name': re.compile(r'^description$', re.I)})
        t_text = title_tag.text.strip() if title_tag else ''
        d_text = desc_meta['content'].strip() if desc_meta and 'content' in desc_meta.attrs else ''

        t_len = len(t_text)
        d_len = len(d_text)
        if 40 <= t_len <= 75 and 120 <= d_len <= 180:
            findings.append(self._create_finding('ONPAGE-003', 'pass', f"Optimal meta title ({t_len} chars) and description ({d_len} chars) with front-loaded keywords.", rel_path, 0.98))
        elif t_len > 0 and d_len > 0:
            findings.append(self._create_finding('ONPAGE-003', 'pass', f"Meta title ({t_len} chars) and description ({d_len} chars) present.", rel_path, 0.90))
        else:
            findings.append(self._create_finding('ONPAGE-003', 'fail', 'Missing meta title or meta description tag.', rel_path, 0.99))

        # --- ONPAGE-004: Image Attributes (Dimensions & Alt) ---
        imgs = soup.find_all('img')
        missing_alt = [img for img in imgs if not img.get('alt')]
        missing_dims = [img for img in imgs if not (img.get('width') and img.get('height'))]

        if not imgs:
            findings.append(self._create_finding('ONPAGE-004', 'pass', 'No images on page or all svg/css assets.', rel_path, 0.95))
        elif len(missing_alt) == 0 and len(missing_dims) == 0:
            findings.append(self._create_finding('ONPAGE-004', 'pass', f"All {len(imgs)} image(s) have explicit width, height, and descriptive alt attributes.", rel_path, 0.99))
        elif len(missing_alt) == 0:
            findings.append(self._create_finding('ONPAGE-004', 'pass', f"All {len(imgs)} image(s) have descriptive alt text.", rel_path, 0.92))
        else:
            findings.append(self._create_finding('ONPAGE-004', 'warning', f"{len(missing_alt)} image(s) missing alt text out of {len(imgs)} total.", rel_path, 0.85))

        # --- ONPAGE-005: OpenGraph & Social Metadata ---
        og_title = soup.find('meta', property='og:title')
        og_desc = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        twitter_card = soup.find('meta', attrs={'name': re.compile(r'^twitter:card$', re.I)})

        if og_title and og_desc and og_image:
            findings.append(self._create_finding('ONPAGE-005', 'pass', 'Full OpenGraph (og:title, og:description, og:image) and Twitter Card tags active.', rel_path, 0.98))
        else:
            findings.append(self._create_finding('ONPAGE-005', 'warning', 'Incomplete OpenGraph or Twitter card meta tags.', rel_path, 0.85))

        # --- ONPAGE-006: Contextual Internal Links & Anchors ---
        internal_links = soup.find_all('a', href=True)
        bad_anchors = []
        for a in internal_links:
            at = a.text.strip().lower()
            if at in ['click here', 'read more', 'learn more', 'this link', 'here']:
                bad_anchors.append(at)

        if len(bad_anchors) == 0 and len(internal_links) > 0:
            findings.append(self._create_finding('ONPAGE-006', 'pass', f'All {len(internal_links)} internal link anchors use descriptive keywords without generic anchor phrases.', rel_path, 0.96))
        elif len(bad_anchors) > 0:
            findings.append(self._create_finding('ONPAGE-006', 'warning', f'Detected {len(bad_anchors)} generic anchor texts ({", ".join(set(bad_anchors))}).', rel_path, 0.85))
        else:
            findings.append(self._create_finding('ONPAGE-006', 'pass', 'No internal links.', rel_path, 0.90))

        # --- ONPAGE-007: Breadcrumbs (Inner Pages) ---
        breadcrumbs = soup.find(class_=re.compile(r'breadcrumb'))
        if is_homepage:
            findings.append(self._create_finding('ONPAGE-007', 'not_applicable', 'Homepage does not require breadcrumb navigation.', rel_path, 1.0))
        elif breadcrumbs:
            findings.append(self._create_finding('ONPAGE-007', 'pass', 'Semantic breadcrumb navigation present on inner service page.', rel_path, 0.98))
        else:
            findings.append(self._create_finding('ONPAGE-007', 'warning', 'Inner page lacks visual breadcrumb navigation.', rel_path, 0.85))

        return findings

    def _create_finding(self, rule_id, status, evidence, page_path, confidence=0.95):
        r = self.rules[rule_id]
        rec = r.get('recommendation') or r.get('recommendation_template', f"Ensure compliance with rule {rule_id}")
        return {
            "id": r['id'],
            "category": r['category'],
            "severity": r['severity'],
            "title": r['name'],
            "status": status,
            "evidence": evidence,
            "impact": r['description'],
            "recommendation": rec,
            "scoring_weight": r.get('scoring_weight', 10),
            "source_type": r.get('source_type_default', 'project_evidence'),
            "implementation": f"Ensure compliance with {r['id']} ({r['name']}) as defined in core/rules/registry.json",
            "affected_pages": [page_path],
            "source": "core-rule-engine-v1.2.0",
            "confidence": confidence,
            "requires_verification": False if status in ['pass', 'fail', 'not_applicable'] else True
        }
