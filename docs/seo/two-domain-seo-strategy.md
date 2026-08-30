# Sanctify + Goa Web Design Specialist: Two-Domain SEO Strategy

- **Main business and brand:** `https://www.sanctify.in/`
- **Web-design specialist:** `https://webdesigncompanygoa.in/`
- **Strategy date:** 2026-08-30
- **Migration map:** [`sanctify-web-design-migration-map.csv`](sanctify-web-design-migration-map.csv)
- **Keyword source of truth:** [`keyword-map.csv`](keyword-map.csv), [`local-seo-keywords.csv`](local-seo-keywords.csv), and [`content-roadmap.csv`](content-roadmap.csv)

## Decision

Operating two domains is not automatically a Google violation or penalty. The risk comes from how the domains are used. Google identifies multiple similar sites or pages created to rank for similar queries and funnel users to one destination as [doorway abuse](https://developers.google.com/search/docs/essentials/spam-policies). Google may also cluster substantially duplicate pages and select only one representative canonical, regardless of the owner’s preferred URL.

The safe model is therefore **one business entity, two genuinely distinct site purposes, and one canonical owner for every search intent**:

- **Sanctify** remains the corporate brand, business entity, Google Business Profile owner, and authority for advertising, digital marketing, SEO, Local SEO, Google Business Profile work, PPC, social media, branding, About, Contact, legal information, and broad corporate proof.
- **Web Design Company Goa by Sanctify** becomes a focused, independently useful web-design specialist. It owns Goa website design, development, ecommerce, WordPress, redesign, maintenance, performance, pricing, web-design industries, portfolio/case studies, and web-design buying guides.

This is a section migration and specialization strategy—not two sites competing with copied pages.

## Non-negotiable launch condition

The specialist domain currently returns `403 Forbidden` in a headless browser and has no accessible canonical, `robots.txt`, or sitemap from the research environment. Do not redirect any Sanctify URL until the intended specialist target:

1. returns a stable `200` to users and Googlebot;
2. is indexable and self-canonical;
3. is at least as useful as the source page;
4. appears in a valid XML sitemap;
5. has passed Search Console URL Inspection live testing; and
6. has analytics, conversion tracking, and server-log monitoring enabled.

A premature redirect to a blocked, empty, or materially weaker page would discard value and harm users.

## Domain roles and canonical ownership

| Topic/entity | Canonical owner | Rule |
|---|---|---|
| Corporate brand and Organization identity | Sanctify | One stable Organization entity and NAP source of truth. |
| Advertising and broad digital marketing | Sanctify | Keep service and informational clusters on the main brand site. |
| SEO and Local SEO services | Sanctify | Existing owner: `/sanctify-facility/local-seo-services-goa/`. Do not recreate on the specialist. |
| GBP/Google Maps/Local SEO guide intent | Sanctify | Existing owner: `/local-seo-google-business-profile-goa/`. Consolidate overlapping guide intent here. |
| Google Business Profile | Sanctify | One profile for the real business; do not create a profile for the exact-match domain alone. |
| Website design company/agency/designer in Goa | Specialist | The specialist homepage owns all close wording variants. |
| Website development | Specialist | `/website-development-goa/`. |
| Ecommerce web design/development | Specialist | `/ecommerce-website-development-goa/`. |
| WordPress, redesign, maintenance, speed, UI/UX, landing pages | Specialist | One differentiated service page per material intent. |
| Website pricing/cost | Specialist | One owner: `/website-design-cost-goa/`. |
| Web-design verticals and web-design buying guides | Specialist | Publish only with substantial industry/process/proof value. |
| About, contact, legal, team, corporate credentials | Sanctify primary | Specialist may have concise contextual pages, but must identify Sanctify and link to the authoritative corporate source. |

The generated CSVs make this ownership machine-readable through `site_owner` and `canonical_url`. Their `target_url` is root-relative to the named owner, not implicitly relative to the specialist domain. The migration map uses the unambiguous `target_path` plus `target_owner` contract and derives the same absolute `canonical_url`; unresolved audits deliberately leave `target_path` and `canonical_url` blank.

## Why the current overlap is unsafe

Sanctify already exposes indexable pages for the same web-design intents planned for the specialist, including its principal web-design service, website cost, WordPress, ecommerce, hotel, restaurant, real estate, responsive design, SEO-friendly design, corporate design, conversion, and agency-selection topics. Publishing equivalent specialist pages while leaving those URLs unchanged would create:

- keyword cannibalization and unstable landing-page selection;
- duplicate or near-duplicate content clusters;
- fragmented links, engagement, and entity signals;
- a doorway appearance if one domain mainly funnels leads to the other; and
- confusing users who cannot tell whether the sites represent one or two businesses.

Cross-domain `rel="canonical"` is not the preferred solution when the old URL is being retired. Google treats canonicals as signals, while redirects are stronger; the migration should use one-to-one permanent redirects after the target is ready. See Google’s [canonicalization overview](https://developers.google.com/search/docs/crawling-indexing/canonicalization), [duplicate URL consolidation guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), and [site-move guidance](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes).

## Migration method

### Phase 0 — verify facts and ownership

- Complete [`business-facts-required.md`](business-facts-required.md), including Sanctify’s legal/public identity, NAP, GBP, service ownership, web-design capabilities, portfolio permissions, and claims.
- Export the last 16 months of Search Console page/query data for both properties where available.
- Export current organic landing pages, backlinks, conversions, and server response data.
- Crawl Sanctify’s web-design section and inventory every indexable URL, canonical, internal link, image, structured-data block, and downloadable asset.
- Approve the final map in [`sanctify-web-design-migration-map.csv`](sanctify-web-design-migration-map.csv). No source can redirect to a merely related target without content-equivalence review.
- Treat a row as executable only when `redirect_ready=true`. That requires `status=approved_for_cutover`, a roadmap-owned destination, named/date-stamped equivalence approval, destination HTTP `200`, confirmed indexability, and verified self-canonical. The generator rejects incomplete or contradictory ready states.
- Leave `target_path` and `canonical_url` blank for unresolved content audits. A proposed destination must not be pre-populated where equivalence is unknown.

### Phase 1 — build the specialist as a real destination

- Launch a complete homepage, relevant P0 service pages, About/relationship disclosure, contact route, privacy/terms, portfolio/case-study framework, and useful conversion paths.
- Write each destination for its assigned intent from first-hand knowledge. Do not copy Sanctify paragraphs and swap the brand/domain.
- Move and improve useful source material, preserving facts and attribution while removing outdated or unsupported claims.
- Add visible wording such as **“Web Design Company Goa by Sanctify”** and explain that Sanctify is the company behind the specialist.
- Give the site standalone user value: scope guidance, process, deliverables, FAQs, proof, case studies, platform guidance, and transparent ownership—not a thin lead form.

### Phase 2 — pre-cutover technical validation

For every destination:

- `200` response; indexable; self-referencing HTTPS canonical;
- unique title, H1, copy, structured data, and social metadata;
- no staging canonical, accidental `noindex`, blocked resource, redirect chain, or soft 404;
- equivalent or better content than the old page;
- updated internal links and sitemap inclusion;
- working forms, calls, email links, consent, and analytics; and
- mobile, accessibility, Core Web Vitals, and structured-data checks.

### Phase 3 — controlled one-to-one cutover

- Move a small, coherent batch first: one lower-risk guide or vertical plus its media and internal links.
- Activate destination `200`, the old-URL redirect, sitemap changes, and internal-link changes in one controlled release. Keep any unavoidable duplicate-`200` overlap within that deployment window (target: under 60 minutes), not days or weeks.
- Configure a direct server-side `301` or `308` from each approved old URL to its exact destination.
- Avoid redirect chains, JavaScript redirects, meta refreshes, and blanket redirects to the specialist homepage.
- Remove redirected source URLs from Sanctify’s sitemap and add destination URLs to the specialist sitemap.
- Change Sanctify’s internal links to destination URLs; do not depend on redirects for internal navigation.
- Keep legacy URLs in the redirect table for at least 12 months and preferably indefinitely, following Google’s [site-move guidance](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes).
- Submit both sitemaps and inspect representative source and destination URLs in Search Console.
- Expand in batches only after response, indexing, ranking, and conversion checks pass.

Do not use Search Console’s Change of Address tool: this is a partial section move, not a whole-domain move.

### Phase 4 — retarget Sanctify

After the specialist is healthy and the mapped redirects are live:

- keep Sanctify’s homepage focused on **Digital Marketing Agency in Goa**;
- retain one concise web-design capability card and a contextual branded link to the specialist;
- remove or rewrite substantial blocks that make the Sanctify homepage compete for “web design company in Goa”;
- keep corporate proof, team, contact, and cross-service context on Sanctify; and
- eliminate internal links to retired Sanctify web-design URLs.

## Redirect and canonical rules

1. **Exact equivalence first.** A source redirects only after its destination covers the same user need and important content.
2. **No blanket homepage mapping.** When no equivalent exists, keep and improve the source temporarily, build the right destination, or return a truthful `404/410` if it has no value.
3. **One hop.** Old Sanctify URL → final specialist HTTPS URL.
4. **Self-canonical destinations.** Do not point a live specialist page’s canonical back to Sanctify.
5. **No duplicate `200` pair.** Once migrated, the source permanently redirects; it does not remain indexable.
6. **No mixed signals.** Redirect, canonical, sitemap, hreflang if ever used, and internal links must agree.
7. **Preserve relevance.** Transfer useful media, headings, FAQs, references, and links when they remain accurate, but rewrite and improve rather than cloning.

## Entity, schema, NAP, and GBP

### One business identity

Use one durable Organization identifier, preferably:

```text
https://www.sanctify.in/#organization
```

Sanctify’s Organization markup should be the authoritative source for the approved legal/public name, URL, logo, contact points, address or service area, and sameAs profiles. Consolidate the duplicate Organization/WebSite declarations currently observed on Sanctify rather than emitting competing identities. The proposed `@id` must be verified as stable and actually emitted by Sanctify before specialist schema references it. Follow Google’s [Organization structured-data guidance](https://developers.google.com/search/docs/appearance/structured-data/organization).

The specialist may emit:

- `WebSite` with its own specialist URL and name;
- `Service` for actual web-design services;
- `WebPage`, `BreadcrumbList`, `Article`, or `FAQPage` only where eligible and accurate; and
- `provider`/`publisher` references to `https://www.sanctify.in/#organization`.

Do not create a second unrelated `Organization` or `LocalBusiness` identity with the same people, NAP, and operations. Schema must describe verified reality; it is not a ranking loophole.

### One Google Business Profile

Google’s [business representation guidelines](https://support.google.com/business/answer/3038177?hl=en) generally allow one profile per real business, including when it offers multiple services. Keep Sanctify’s genuine profile. Do not create another profile merely because the specialist domain has a keyword-rich name. The specialist can be linked contextually from Sanctify and, only if useful and policy-compliant, from a relevant GBP service or update; the primary GBP website destination should remain a deliberate conversion and measurement decision for the one business.

## Cross-domain linking policy

Allowed:

- a branded relationship link such as “Web Design Company Goa by Sanctify”;
- a contextual Sanctify web-design card linking to the specialist homepage;
- specialist footer/About attribution linking to Sanctify’s corporate About or homepage;
- contextual links from relevant Sanctify marketing pages to a specialist resource when it genuinely helps the reader; and
- contextual specialist links to Sanctify’s SEO/digital-marketing services when those are the correct canonical resources.

Prohibited:

- sitewide exact-match anchors such as “best website design company in Goa”;
- large reciprocal link blocks;
- linking every page on one domain to every page on the other;
- hidden, template-spun, or paid links intended to manipulate rankings; and
- presenting two sites as independent companies when they are the same operation.

Google’s [spam policies](https://developers.google.com/search/docs/essentials/spam-policies) identify excessive reciprocal linking and manipulative link patterns as link spam. Keep links sparse, descriptive, branded where appropriate, and user-led.

## Content quality and anti-doorway gate

Before publishing any specialist page, answer “yes” to all applicable checks:

- Does it serve a distinct, documented intent assigned to the specialist?
- Is it useful if the reader never visits Sanctify?
- Does it contain substantial first-hand process, expertise, proof, or tools rather than generic SEO prose?
- Is the relationship to Sanctify transparent?
- Is its locality or industry value more than place/industry token replacement?
- Are every testimonial, metric, client, award, timeline, price, and capability approved?
- Does it avoid an equivalent indexable Sanctify page?
- Does it have a clear conversion path without acting only as a bridge?

Use Google’s [helpful-content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) as an editorial standard. Town and industry pages that fail this gate remain research candidates and are not published.

## Search Console, analytics, and monitoring

### Search Console

- Maintain separate Domain properties for `sanctify.in` and `webdesigncompanygoa.in`.
- Record pre-cutover query/page exports and indexing counts.
- Submit each domain’s own sitemap.
- Inspect migrated source/destination pairs and monitor Page indexing, Crawl stats, HTTPS, Core Web Vitals, manual actions, and security issues.
- Compare query ownership by canonical URL; investigate any query cluster appearing on both hosts after recrawling.

### GA4 and lead attribution

- Use one GA4 property if unified customer-journey reporting is required, with both domains configured for cross-domain measurement.
- Preserve hostname in reports and create domain/landing-page segments.
- Exclude unwanted self-referrals; verify session continuity by testing navigation in both directions.
- Add hidden landing-host and first-landing-page values to enquiry records where lawful and practical.
- Keep campaign parameters intentional; do not add UTM parameters to ordinary cross-domain navigation if they overwrite genuine acquisition.

### Weekly cutover dashboard

Monitor by source/destination pair and cluster:

- response code, canonical, index status, sitemap status, and Google-selected canonical;
- impressions, clicks, average position, and query-to-page ownership;
- organic sessions, qualified leads, conversion rate, and assisted conversions;
- backlink destinations and high-value links still pointing to redirecting sources;
- crawl errors, soft 404s, redirect chains, blocked requests, and WAF events; and
- branded versus non-branded visibility for each host.

Temporary volatility is normal during recrawling, but persistent decline must be diagnosed at the URL and query-cluster level.

## Rollback and incident rules

A normal ranking fluctuation is not a reason to restore duplicates. Roll back a batch only for a confirmed implementation failure such as destination `5xx/403`, accidental `noindex`, wrong redirect target, broken conversion path, severe content loss, or WAF blocking Googlebot.

For an incident:

1. stop the next batch;
2. fix the destination or redirect in place whenever possible;
3. restore a source `200` only if the destination cannot be repaired promptly, and then remove conflicting redirect/canonical/sitemap signals;
4. document the exact URLs and timestamps;
5. re-run live URL tests and analytics checks; and
6. resume only after the batch passes the launch gate.

Do not alternate repeatedly between duplicate `200` pages and redirects; unstable signals delay consolidation.

## Success criteria

The strategy is successfully implemented only when:

- the specialist is consistently crawlable and useful, not a 403 or thin funnel;
- every migrated source has one direct permanent redirect to a content-equivalent destination;
- Sanctify no longer exposes competing indexable web-design pages for migrated intents;
- Local SEO, GBP, corporate identity, NAP, and Organization ownership remain on Sanctify;
- the specialist visibly identifies Sanctify as provider/publisher;
- Search Console increasingly reports the intended host as canonical for each assigned cluster;
- no manual action, doorway pattern, duplicate entity, second GBP, or manipulative cross-link scheme exists;
- total qualified organic enquiries are stable or improving across both domains after the migration settles; and
- all claims, schema, services, locations, prices, and proof remain verifiable.

## Official references

- [Google Search spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Google canonicalization overview](https://developers.google.com/search/docs/crawling-indexing/canonicalization)
- [Google: consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google: site moves with URL changes](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)
- [Google: creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Business Profile representation guidelines](https://support.google.com/business/answer/3038177?hl=en)
- [Google Business Profile duplicate-profile guidance](https://support.google.com/business/answer/12756178)
- [Google Organization structured data](https://developers.google.com/search/docs/appearance/structured-data/organization)
- [Schema.org `provider`](https://schema.org/provider)

External guidance is summarized and rephrased; no source text is reproduced as site copy.
