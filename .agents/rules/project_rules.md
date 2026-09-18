# Project Architecture & Coding Rules — Poonia Movers

## 1. Universal Master Footer Rule (STRICT MANDATE)
- **Zero Variation Policy**: Every single current and future page (all 1,000+ programmatic city, corridor, route, and service landing pages) MUST include the exact standardized master footer component:
  ```html
  <footer class="master-footer">
    <div class="container-wide">
      <div class="footer-top-grid">
        <!-- 1. Brand Info with ISO 9001:2015, VKI Harmada Address & Helpline -->
        <!-- 2. Relocation Services Column -->
        <!-- 3. Jaipur Localities Column -->
        <!-- 4. Intercity Corridors Column -->
        <!-- 5. Fleet & Tools Column -->
      </div>
      <!-- Embedded Google Map Card with Official CID Embed -->
      <div class="footer-map-card">...</div>
      <!-- Bottom Legal & Copyright Bar -->
      <div class="footer-bottom">...</div>
    </div>
  </footer>
  ```
- Under no circumstances should any alternate footer class (`.main-footer`, `.simple-footer`, etc.) be introduced.

## 2. Common CSS Design System
- **Central Stylesheet**: All pages must link to `css/style.css`.
- **Zero Inline `<style>` Blocks**: Custom styling must use the standardized design tokens and utility classes (`.grid-2`, `.grid-3`, `.grid-4`, `.calc-card`, `.glass-card`, `.section`, `.badge`, `.btn`, etc.).
- **Responsive Guarantee**: All components must support Mobile (<768px), Tablet (768px-1024px), and Desktop (>1024px) seamlessly.

## 3. SEO & Knowledge Graph Integrity
- All pages must maintain complete E-E-A-T schemas (WebPage, BreadcrumbList, LocalBusiness / LogisticsService, FAQPage).

## 4. Universal FAQ Accordion & Schema Rule (STRICT MANDATE)
- **Unified HTML Structure**: Every single page with an FAQ section MUST use the exact same classes:
  ```html
  <section class="faq-section section-py" id="faq">
    <div class="container">
      <div class="section-header">
        <span class="badge badge-primary section-eyebrow">Clear Answers</span>
        <h2>Frequently Asked Questions — [Topic/City]</h2>
        <p>[Description]</p>
      </div>
      <div class="faq-container">
        <div class="faq-item">
          <button class="faq-question-btn" type="button" aria-expanded="false">
            <span>[Question Text]?</span>
            <div class="faq-icon-toggle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="width:16px;height:16px;"><path d="M6 9l6 6 6-6"/></svg>
            </div>
          </button>
          <div class="faq-answer-wrap">
            <div class="faq-answer-content">
              [Answer text formatted with strong highlights]
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
  ```
- **1-to-1 JSON-LD Schema Parity**: Every FAQ item rendered in the HTML must be mirrored verbatim in the `<head>` structured data under the `FAQPage` entity:
  ```json
  {
    "@type": "FAQPage",
    "@id": "https://pooniamovers.com/[page-slug]#faq",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "[Exact Question]",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "[Exact Answer]"
        }
      }
    ]
  }
  ```

## 5. Universal Strict Card & Grid Integrity Rule (STRICT MANDATE)
- **Zero Distortion Policy**: Under NO circumstances should cards ever squish, deform into vertical slivers, overflow containers, or break alignment on any of the 1,000+ programmatic landing pages.
- **Strict Grid System**: All multi-column containers must use the unified grid utility classes with `minmax(0, 1fr)`:
  ```css
  .grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px; width: 100%; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 28px; width: 100%; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 24px; width: 100%; }
  .grid-5 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 18px; width: 100%; }
  .reviews-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; width: 100%; }
  ```
- **Universal Card Sizing Base**: Every card component (`.review-card`, `.glass-card`, `.feature-card`, `.service-card`, `.stat-card`, etc.) must always adhere to:
  ```css
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  overflow-wrap: break-word;
  word-wrap: break-word;
  ```
- **Strict Isolation for Slider / Carousel Tracks**: Flex width calculations (e.g. `calc((100% - 48px) / 3)`) must NEVER be set on base card classes. They are strictly scoped ONLY to `.reviews-track > .review-card`.
- **Standardized Review Card HTML Structure**:
  ```html
  <div class="review-card glass-card">
    <div class="review-card-top">
      <div class="review-route-badge">📍 [Origin ➔ Destination]</div>
      <div class="review-stars">★★★★★</div>
    </div>
    <p class="review-text">"[Quote Text]"</p>
    <div class="review-author">
      <div class="author-avatar av-blue">[Initials]</div>
      <div class="author-info">
        <div class="author-name-row">
          <h5>[Customer Name]</h5>
          <span class="verified-client-badge">✓ Verified</span>
        </div>
        <p>[Role / Move Type]</p>
      </div>
    </div>
  </div>
  ```
- **Standardized Responsive Breakpoints**:
  - **Desktop (>1024px)**: Full grid columns (2, 3, 4, or 5).
  - **Tablet (768px – 1024px)**: Auto-collapse to 2 columns (`repeat(2, minmax(0, 1fr))`).
  - **Mobile (<768px)**: Single column 100% width (`1fr`) with equal gap.

## 6. Programmatic SEO & Anti-Spam Page Architecture (STRICT MANDATE)
To ensure that all 1,000+ programmatic landing pages rank in Google's top 3 without triggering "Spam / Thin Content / Duplicate Content" penalties:
1. **Zero Spun/Copied Text Policy**: No programmatic page should be a simple "find & replace city name" clone. Each page must feature authentic, localized data points.
2. **Mandatory High-Intent Data Matrices (Competitor Parity)**:
   - **Live Recent Freight Dispatches Feed**: A dynamic table of 5-8 verified/simulated real cargo movements with exact pickup industrial zone, destination, truck type, payload, distance, and transit time.
   - **Industrial Clusters & Cargo Movement Profile**: 4 localized manufacturing/commercial estates (e.g. VKI, Sitapura, Bagru for Jaipur; Peenya, Whitefield, Electronic City for Bangalore) with core commodities and highway connectivity (NH/Expressways).
   - **Direct Logistics vs Brokers/Aggregators Comparison Matrix**: 6-row transparency table comparing Poonia Movers (0% advance, fixed rate, own verified fleet) vs App Aggregators vs Traditional Brokers.
   - **Fleet & Fare Matrix**: Clear payload limits (Tons), internal container dimensions (Cu. Ft), per-km base pricing, and recommended cargo type.
3. **Keyword Placement & Density Rules**:
   - **Title Tag**: `[Primary Service Keyword] in [City/Route] | Book Trucks from ₹[Rate]/KM | Poonia Movers` (55-60 chars).
   - **Meta Description**: Action-oriented summary mentioning FTL/PTL, vehicle types, 0% advance, and direct phone number (150-155 chars).
   - **Keyword Density**: Natural distribution between 1.0% and 1.8% max. Avoid repetitive keyword stuffing in headers.
   - **LSI Entity Coverage**: Every transport landing page must include E-Way Bill, GST Invoice, Transit Insurance, Digital Lorry Receipt (Bilty/LR), GPS Tracking, and Loading/Unloading labor.
4. **Structured Schema & AEO Verification**:
   - Every page must contain complete JSON-LD entities: `WebPage`, `BreadcrumbList`, `LogisticsService` / `LocalBusiness`, and `FAQPage` with 1-to-1 parity against rendered HTML.

## 7. Mandatory On-Page SEO Architecture (STRICT MANDATE)
Derived from Amit Tiwari's 9-part On-Page SEO Series, the following rules apply automatically to every current and future page in the project:

### 1. Robots Meta & Search Snippet Directives
- Every indexable page MUST contain the following `<meta name="robots">` tag in `<head>`:
  ```html
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  ```
- This ensures search engines and AI assistants can render rich visual snippets and full knowledge panels.

### 2. Canonical & Hreflang Multi-Language Directives
- Every indexable page MUST have an absolute self-referencing canonical tag and primary hreflang tags:
  ```html
  <link rel="canonical" href="https://pooniamovers.com/[page-slug].html">
  <link rel="alternate" hreflang="en-IN" href="https://pooniamovers.com/[page-slug].html">
  <link rel="alternate" hreflang="x-default" href="https://pooniamovers.com/[page-slug].html">
  ```

### 3. Meta Title & Description Standards
- **Meta Title (50–60 characters)**: Primary Keyword front-loaded | Secondary Benefit / Location — Poonia Movers.
- **Meta Description (140–160 characters)**: BLUF rate figures (e.g. starting ₹4,500/trip or ₹25/km), 0% advance, GPS tracking, and phone number CTA.

### 4. Semantic URL Slugs
- All URLs must be lowercase, hyphen-separated, keyword-focused, and concise (e.g. `/jaipur-transport-services.html`). Zero underscores, uppercase, or dynamic parameters.

### 5. Header Tag Hierarchy
- Exactly **1 H1** per page.
- Structured nesting: H1 -> H2 -> H3. Never jump levels (e.g. H1 to H3).
- Headings are structural landmarks, not visual styling shortcuts.

### 6. Image SEO & Visual Placement
- All images must include:
  - Explicit `width` and `height` attributes to prevent Cumulative Layout Shift (CLS).
  - Contextual, descriptive `alt` text explaining what is visually depicted.
  - `loading="lazy"` on all below-the-fold images (`fetchpriority="high"` for hero).
  - Clean CSS border for high contrast if image background matches the page canvas.

### 7. OpenGraph & Social Metadata
- Every page must declare:
  ```html
  <meta property="og:type" content="website">
  <meta property="og:title" content="[Title]">
  <meta property="og:description" content="[Description]">
  <meta property="og:url" content="https://pooniamovers.com/[page-slug].html">
  <meta property="og:image" content="https://pooniamovers.com/img/og-image.jpg">
  <meta name="twitter:card" content="summary_large_image">
  ```

### 8. Contextual Internal Linking & Breadcrumbs
- **Anchor Text Quality**: Banned generic anchor texts ("click here", "read more", "this link"). All internal links must use descriptive target keyword phrases.
- **Breadcrumb Navigation**: Inner service and corridor pages must feature visual `.breadcrumb-nav` and matching `BreadcrumbList` JSON-LD structured data.
