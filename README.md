# webdesigncompanygoa.in

SEO research and implementation planning for a Goa-focused website design and development company.

## SEO deliverables

- [`docs/seo/keyword-strategy.md`](docs/seo/keyword-strategy.md) — research findings, priorities, page ownership, local SEO plan, and guardrails.
- [`docs/seo/business-facts-required.md`](docs/seo/business-facts-required.md) — approval gate for location, NAP, services, platforms, proof, claims, and commercial facts.
- [`docs/seo/keyword-map.csv`](docs/seo/keyword-map.csv) — 310 service, commercial, industry, and informational keyword rows mapped to proposed pages.
- [`docs/seo/local-seo-keywords.csv`](docs/seo/local-seo-keywords.csv) — 300 Goa, regional, town, proximity, and local-search keyword rows.
- [`docs/seo/content-roadmap.csv`](docs/seo/content-roadmap.csv) — 29 proposed pages sequenced by phase, intent, prerequisite, and conversion goal.
- [`tools/build_keyword_inventory.py`](tools/build_keyword_inventory.py) — dependency-free generator for the three CSV inventories.

## Rebuild the inventories

```bash
python3 tools/build_keyword_inventory.py
```

The research snapshot is dated **2026-08-30**. Search volume, keyword difficulty, and CPC fields are deliberately blank until populated from a dated Google Search Console, Google Ads Keyword Planner, or approved third-party export. No metrics or business claims have been fabricated.
