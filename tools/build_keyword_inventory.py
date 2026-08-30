#!/usr/bin/env python3
"""Build the curated Goa web-design SEO keyword inventories.

The generated CSV files intentionally leave volume, difficulty, and CPC blank.
Those metrics must come from first-party Search Console or a dated keyword-tool
export; inventing them would make the strategy less trustworthy.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Iterable

RESEARCH_DATE = "2026-08-30"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "seo"

USER_SEEDS = {
    "website design company in goa",
    "web designing company in goa",
    "website designing agency in goa",
    "top web design company in goa",
}

AUTOCOMPLETE_EVIDENCE = {
    "website design company in goa": (
        "website design company in goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=website%20design%20company%20in%20goa",
    ),
    "web designer goa": (
        "web designer goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=web%20designer%20goa",
    ),
    "web developer goa": (
        "web designer goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=web%20designer%20goa",
    ),
    "website developer goa": (
        "web designer goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=web%20designer%20goa",
    ),
    "web design company goa": (
        "web designer goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=web%20designer%20goa",
    ),
    "website development company in goa": (
        "website development company goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=website%20development%20company%20goa",
    ),
    "website designing company in goa": (
        "website development company goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=website%20development%20company%20goa",
    ),
    "best website development company in goa": (
        "website development company goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=website%20development%20company%20goa",
    ),
    "best website development company in mapusa goa": (
        "website development company goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=website%20development%20company%20goa",
    ),
    "local seo services in goa": (
        "local seo company goa",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q=local%20seo%20company%20goa",
    ),
}

SERP_EVIDENCE = {
    "website designers in goa": ("website design company in Goa", "http://warrenasia.com/"),
    "web designers in goa": ("website design company in Goa", "http://warrenasia.com/"),
    "best website development agency in goa": (
        "website designing agency in Goa",
        "https://brandemic.in/best-website-development-agency-in-goa",
    ),
    "digital marketing and web development agency goa": (
        "web designing company in Goa",
        "https://www.codezion.com/in/goa/",
    ),
    "ecommerce web development in goa": (
        "ecommerce website development in Goa",
        "https://www.codezion.com/in/goa/",
    ),
    "responsive web design goa": ("website design company in Goa", "https://goaweb.dev/"),
    "custom website design goa": ("website design company in Goa", "https://www.thewebcompany.co/"),
    "seo friendly website design goa": (
        "ecommerce website development in Goa",
        "https://dreamlogic.in/",
    ),
    "hotel website design goa": (
        "hotel restaurant resort website design company Goa",
        "https://www.codezion.com/in/goa/",
    ),
    "resort website design goa": (
        "hotel restaurant resort website design company Goa",
        "https://www.codezion.com/in/goa/",
    ),
    "tourism website development goa": (
        "hotel restaurant resort website design company Goa",
        "https://www.codezion.com/in/goa/",
    ),
    "real estate website development goa": (
        "Goa web design agency hotel resort real estate ecommerce WordPress competitors",
        "https://www.codezion.com/in/goa/",
    ),
}


@dataclass(frozen=True)
class KeywordRow:
    keyword: str
    cluster: str
    search_intent: str
    funnel_stage: str
    location_modifier: str
    target_url: str
    page_type: str
    keyword_role: str
    priority: str
    source_evidence: str
    source_query: str
    source_url: str
    observed_at: str
    status: str
    monthly_searches: str = ""
    keyword_difficulty: str = ""
    cpc_inr: str = ""
    notes: str = ""


@dataclass(frozen=True)
class LocalKeywordRow:
    keyword: str
    locality: str
    region: str
    service_cluster: str
    search_intent: str
    target_url: str
    page_strategy: str
    priority: str
    source_evidence: str
    source_query: str
    source_url: str
    observed_at: str
    status: str
    notes: str


@dataclass(frozen=True)
class RoadmapRow:
    priority: str
    phase: str
    proposed_title: str
    target_url: str
    content_type: str
    primary_keyword: str
    supporting_keyword_cluster: str
    search_intent: str
    conversion_goal: str
    prerequisite: str
    status: str
    notes: str


def evidence_for(keyword: str) -> tuple[str, str, str, str]:
    normalized = keyword.casefold()
    if normalized in USER_SEEDS:
        return "user_seed", "User brief", "", RESEARCH_DATE
    if normalized in AUTOCOMPLETE_EVIDENCE:
        query, source_url = AUTOCOMPLETE_EVIDENCE[normalized]
        return "google_autocomplete_in_en", query, source_url, RESEARCH_DATE
    if normalized in SERP_EVIDENCE:
        query, source_url = SERP_EVIDENCE[normalized]
        return "serp_observed", query, source_url, RESEARCH_DATE
    return "strategic_expansion_validate", "", "", ""


def write_rows(path: Path, rows: Iterable[object]) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError(f"Refusing to write an empty inventory: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    field_names = [field.name for field in fields(materialized[0])]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=field_names,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(
            {field_name: getattr(row, field_name) for field_name in field_names}
            for row in materialized
        )


def add_keyword_group(
    rows: list[KeywordRow],
    *,
    phrases: Iterable[str],
    cluster: str,
    search_intent: str,
    funnel_stage: str,
    target_url: str,
    page_type: str,
    keyword_role: str,
    priority: str,
    location_modifier: str = "Goa",
    notes: str = "",
) -> None:
    for phrase in phrases:
        source_evidence, source_query, source_url, observed_at = evidence_for(phrase)
        rows.append(
            KeywordRow(
                keyword=phrase,
                cluster=cluster,
                search_intent=search_intent,
                funnel_stage=funnel_stage,
                location_modifier=location_modifier,
                target_url=target_url,
                page_type=page_type,
                keyword_role=keyword_role,
                priority=priority,
                source_evidence=source_evidence,
                source_query=source_query,
                source_url=source_url,
                observed_at=observed_at,
                status="mapped_needs_volume_validation",
                notes=notes,
            )
        )


def build_keyword_map() -> list[KeywordRow]:
    rows: list[KeywordRow] = []

    add_keyword_group(
        rows,
        phrases=[
            "website design company in goa",
            "web design company in goa",
            "web design company goa",
            "website designing company in goa",
            "web designing company in goa",
            "website design agency in goa",
            "web design agency in goa",
            "website designing agency in goa",
            "web designing agency in goa",
            "website designers in goa",
            "web designers in goa",
            "website designer in goa",
            "web designer in goa",
            "website designer goa",
            "web designer goa",
            "website design in goa",
            "web design in goa",
            "website design goa",
            "web design goa",
            "professional website design company in goa",
            "creative web design agency goa",
            "custom website design company in goa",
            "responsive web design company in goa",
            "mobile friendly website design goa",
            "seo friendly website design goa",
            "business website design company in goa",
            "corporate website design company in goa",
            "small business website design goa",
            "startup website design company goa",
            "goa website design services",
            "website design services in goa",
            "web designing services in goa",
        ],
        cluster="core_web_design_goa",
        search_intent="commercial_transactional",
        funnel_stage="decision",
        target_url="/",
        page_type="homepage",
        keyword_role="primary_and_close_variants",
        priority="P0",
        notes="Use one authoritative homepage; do not create separate pages for wording variants.",
    )

    add_keyword_group(
        rows,
        phrases=[
            "top web design company in goa",
            "best web design company in goa",
            "best website design company in goa",
            "top website design company in goa",
            "leading web design company in goa",
            "top website designing agency in goa",
            "best website designing agency in goa",
            "best web designers in goa",
            "top web designers in goa",
            "award winning web design company goa",
            "trusted website design company goa",
            "reliable web design company goa",
            "premium website design agency goa",
        ],
        cluster="comparison_and_quality_modifiers",
        search_intent="commercial_investigation",
        funnel_stage="consideration",
        target_url="/",
        page_type="homepage",
        keyword_role="secondary",
        priority="P1",
        notes="Support only with verifiable proof such as portfolio, reviews, process, and case studies; never make unsupported superlative claims.",
    )

    add_keyword_group(
        rows,
        phrases=[
            "website development company in goa",
            "web development company in goa",
            "website development company goa",
            "web development agency goa",
            "website development agency in goa",
            "website development services in goa",
            "web development services goa",
            "website developer in goa",
            "web developer in goa",
            "website developer goa",
            "web developer goa",
            "website developers in goa",
            "web developers in goa",
            "best website development company in goa",
            "best web development company in goa",
            "best website development agency in goa",
            "custom web development company goa",
            "full stack web development goa",
            "dynamic website development goa",
            "static website development goa",
            "cms website development goa",
            "web application development company goa",
        ],
        cluster="website_development_goa",
        search_intent="commercial_transactional",
        funnel_stage="decision",
        target_url="/website-development-goa/",
        page_type="service_page",
        keyword_role="primary_and_secondary",
        priority="P0",
    )

    service_groups = [
        (
            "ecommerce_website_development",
            "/ecommerce-website-development-goa/",
            "P0",
            [
                "ecommerce website development company in goa",
                "ecommerce web development in goa",
                "ecommerce website design goa",
                "online store development goa",
                "ecommerce website designer goa",
                "ecommerce website developer goa",
                "woocommerce development company goa",
                "shopify website design company goa",
                "shopify developer in goa",
                "online shopping website development goa",
                "payment gateway integration goa",
                "b2b ecommerce website development goa",
                "d2c ecommerce website design goa",
            ],
        ),
        (
            "wordpress_website_design",
            "/wordpress-website-design-goa/",
            "P1",
            [
                "wordpress website design company in goa",
                "wordpress web design goa",
                "wordpress development company goa",
                "wordpress developer in goa",
                "wordpress website developer goa",
                "custom wordpress website goa",
                "woocommerce developer in goa",
                "wordpress maintenance goa",
                "wordpress seo services goa",
            ],
        ),
        (
            "website_redesign",
            "/website-redesign-goa/",
            "P1",
            [
                "website redesign company in goa",
                "website redesign services goa",
                "web redesign agency goa",
                "business website redesign goa",
                "wordpress website redesign goa",
                "ecommerce website redesign goa",
                "modernize old website goa",
                "website revamp company goa",
                "website migration services goa",
                "responsive website redesign goa",
                "seo website redesign goa",
            ],
        ),
        (
            "website_maintenance",
            "/website-maintenance-goa/",
            "P1",
            [
                "website maintenance services in goa",
                "website maintenance company goa",
                "website support services goa",
                "wordpress maintenance services goa",
                "website amc services goa",
                "website security maintenance goa",
                "website backup services goa",
                "website content updates goa",
                "website bug fixing goa",
                "website hosting and maintenance goa",
                "ongoing website support goa",
            ],
        ),
        (
            "ui_ux_design",
            "/ui-ux-design-goa/",
            "P2",
            [
                "ui ux design agency in goa",
                "ui ux designer goa",
                "user experience design company goa",
                "website ux audit goa",
                "mobile app ui ux design goa",
                "figma website design goa",
                "conversion focused web design goa",
                "saas product design goa",
                "website wireframing services goa",
            ],
        ),
        (
            "performance_and_mobile",
            "/website-speed-optimization-goa/",
            "P2",
            [
                "website speed optimization goa",
                "core web vitals optimization goa",
                "mobile website design goa",
                "responsive website design goa",
                "fast loading website design goa",
                "website performance audit goa",
                "wordpress speed optimization goa",
                "mobile first website design goa",
                "technical website audit goa",
                "website security audit goa",
            ],
        ),
        (
            "landing_pages",
            "/landing-page-design-goa/",
            "P2",
            [
                "landing page design company goa",
                "landing page designer goa",
                "lead generation landing page goa",
                "google ads landing page design goa",
                "conversion landing page design goa",
                "product landing page design goa",
                "real estate landing page goa",
                "hotel booking landing page goa",
            ],
        ),
    ]
    for cluster, target_url, priority, phrases in service_groups:
        add_keyword_group(
            rows,
            phrases=phrases,
            cluster=cluster,
            search_intent="commercial_transactional",
            funnel_stage="decision",
            target_url=target_url,
            page_type="service_page",
            keyword_role="primary_and_secondary",
            priority=priority,
        )

    add_keyword_group(
        rows,
        phrases=[
            "local seo company in goa",
            "local seo agency goa",
            "local seo services in goa",
            "local seo expert goa",
            "local seo consultant goa",
            "best local seo company goa",
            "affordable local seo services goa",
            "google maps seo goa",
            "local search optimization goa",
            "local business seo goa",
            "seo company in goa",
            "seo company goa",
            "seo agency in goa",
            "seo services in goa",
            "seo services goa",
            "best seo company in goa",
            "top seo company in goa",
            "search engine optimization company goa",
            "organic seo services goa",
            "small business seo goa",
            "hotel seo services goa",
            "restaurant seo services goa",
            "real estate seo goa",
            "tourism seo agency goa",
        ],
        cluster="local_seo_and_organic_search",
        search_intent="commercial_transactional",
        funnel_stage="decision",
        target_url="/local-seo-goa/",
        page_type="service_page",
        keyword_role="primary_and_secondary",
        priority="P0",
    )

    add_keyword_group(
        rows,
        phrases=[
            "google business profile optimization goa",
            "google business profile management goa",
            "google business profile setup goa",
            "google my business optimization goa",
            "google my business management goa",
            "google maps ranking services goa",
            "google maps marketing goa",
            "google map listing optimization goa",
            "gmb optimization services goa",
            "gbp optimization services goa",
            "local citation building goa",
            "local business listings goa",
            "nap citation audit goa",
            "google review management goa",
            "local seo audit goa",
            "google business profile audit goa",
            "local rank tracking goa",
        ],
        cluster="google_business_profile",
        search_intent="commercial_transactional",
        funnel_stage="decision",
        target_url="/google-business-profile-optimization-goa/",
        page_type="service_page",
        keyword_role="primary_and_secondary",
        priority="P1",
    )

    pricing_terms = [
        "website design cost in goa",
        "website design price in goa",
        "website design packages goa",
        "web design charges in goa",
        "website development cost in goa",
        "website development price goa",
        "ecommerce website cost in goa",
        "wordpress website cost in goa",
        "small business website cost goa",
        "how much does a website cost in goa",
        "affordable website design company in goa",
        "affordable website designer goa",
        "low cost website design goa",
        "cheap website design goa",
        "website maintenance cost goa",
        "seo pricing goa",
        "local seo packages goa",
        "how much does website design cost in goa",
        "factors affecting website development cost",
        "ecommerce website development cost india",
        "wordpress website cost for small business",
        "website maintenance cost per month india",
        "domain hosting and website cost india",
        "custom website vs template cost",
        "website redesign cost guide",
    ]
    add_keyword_group(
        rows,
        phrases=pricing_terms,
        cluster="pricing_and_packages",
        search_intent="commercial_investigation",
        funnel_stage="consideration",
        target_url="/website-design-cost-goa/",
        page_type="commercial_guide",
        keyword_role="primary_and_secondary",
        priority="P1",
        notes="Publish transparent ranges and scope factors only after commercial pricing is approved.",
    )

    industries = [
        ("hotel", "hotel website design company goa", "hotel website development goa"),
        ("resort", "resort website design goa", "resort booking website development goa"),
        ("villa", "villa website design goa", "holiday villa booking website goa"),
        ("homestay", "homestay website design goa", "guest house website development goa"),
        ("restaurant", "restaurant website design goa", "online food ordering website goa"),
        ("cafe", "cafe website design goa", "cafe website developer goa"),
        ("bar_and_nightlife", "bar website design goa", "nightclub website design goa"),
        ("beach_shack", "beach shack website design goa", "shack menu website goa"),
        ("travel_and_tours", "travel agency website design goa", "tour operator website development goa"),
        ("taxi_and_car_rental", "taxi booking website development goa", "car rental website design goa"),
        ("watersports", "watersports booking website goa", "adventure tourism website goa"),
        ("real_estate", "real estate website design goa", "property portal development goa"),
        ("construction", "construction company website design goa", "builder website development goa"),
        ("architects", "architect website design goa", "architecture portfolio website goa"),
        ("interior_design", "interior designer website design goa", "interior design portfolio website goa"),
        ("wedding", "wedding planner website design goa", "destination wedding website goa"),
        ("events", "event management website design goa", "event booking website goa"),
        ("healthcare", "clinic website design goa", "hospital website development goa"),
        ("dentists", "dentist website design goa", "dental clinic website development goa"),
        ("wellness", "spa website design goa", "wellness retreat website development goa"),
        ("yoga", "yoga retreat website design goa", "yoga class booking website goa"),
        ("education", "school website design goa", "college website development goa"),
        ("coaching", "coaching institute website goa", "online course website development goa"),
        ("professional_services", "law firm website design goa", "chartered accountant website goa"),
        ("consultants", "consulting company website design goa", "business consultant website goa"),
        ("retail", "retail business website design goa", "local shop ecommerce website goa"),
        ("fashion", "fashion brand website design goa", "clothing ecommerce website goa"),
        ("jewellery", "jewellery website design goa", "jewellery ecommerce website goa"),
        ("photography", "photographer website design goa", "photography portfolio website goa"),
        ("ngo", "ngo website design goa", "nonprofit website development goa"),
        ("manufacturing", "manufacturing company website goa", "industrial website design goa"),
        ("b2b", "b2b website design company goa", "lead generation website for goa business"),
    ]
    for industry, primary, secondary in industries:
        add_keyword_group(
            rows,
            phrases=[primary, secondary],
            cluster=f"industry_{industry}",
            search_intent="commercial_transactional",
            funnel_stage="decision",
            target_url=f"/industries/{industry.replace('_', '-')}-website-design-goa/",
            page_type="industry_landing_page",
            keyword_role="primary_and_secondary",
            priority="P1" if industry in {"hotel", "resort", "restaurant", "travel_and_tours", "real_estate", "wedding"} else "P2",
            notes="Create only with industry-specific proof, features, FAQs, and portfolio examples.",
        )

    informational_groups = [
        (
            "website_buying_guides",
            "/guides/choose-web-design-company-goa/",
            [
                "how to choose a web design company in goa",
                "how to find the best web designer in goa",
                "questions to ask a website design agency",
                "web design company vs freelancer goa",
                "what to include in a website design brief",
                "website design process explained",
                "how long does it take to build a website",
                "what makes a good business website",
                "website design checklist for small business",
                "website launch checklist india",
            ],
        ),
        (
            "platform_comparisons",
            "/guides/best-website-platform-small-business-goa/",
            [
                "best website platform for small business in goa",
                "wordpress vs shopify for goa business",
                "wordpress vs wix for small business",
                "shopify vs woocommerce india",
                "custom website vs wordpress",
                "static vs dynamic website for business",
                "best booking engine for hotel website",
                "best cms for tourism website",
            ],
        ),
        (
            "local_seo_guides",
            "/guides/local-seo-goa/",
            [
                "how to optimize google business profile",
                "local seo checklist for goa businesses",
                "google business profile categories for web designer",
                "how to get more google reviews ethically",
                "why nap consistency matters for local seo",
                "local citations for goa businesses",
                "how long does local seo take",
                "local seo vs traditional seo",
                "google maps ranking factors",
                "how to improve local search rankings",
                "local seo for hotels in goa",
                "local seo for restaurants in goa",
                "local seo for real estate in goa",
            ],
        ),
        (
            "conversion_and_performance_guides",
            "/guides/website-conversion-goa-business/",
            [
                "how to make a website generate more leads",
                "website conversion rate optimization checklist",
                "why mobile friendly website matters",
                "how website speed affects seo",
                "core web vitals for business websites",
                "how to reduce website bounce rate",
                "website trust signals for local business",
                "best call to action examples for service website",
            ],
        ),
        (
            "google_maps_guide",
            "/guides/rank-google-maps-goa/",
            ["how to rank on google maps in goa"],
        ),
        (
            "website_redesign_guide",
            "/guides/website-redesign-checklist/",
            ["signs your website needs a redesign"],
        ),
        (
            "hotel_direct_booking_guide",
            "/guides/hotel-direct-booking-website-goa/",
            ["hotel website direct booking optimization"],
        ),
    ]
    for cluster, target_url, phrases in informational_groups:
        add_keyword_group(
            rows,
            phrases=phrases,
            cluster=cluster,
            search_intent="informational_commercial",
            funnel_stage="awareness_consideration",
            target_url=target_url,
            page_type="guide_or_blog",
            keyword_role="primary_and_supporting",
            priority="P2",
            location_modifier="Goa_or_India_where_natural",
        )

    unique: dict[str, KeywordRow] = {}
    for row in rows:
        key = row.keyword.casefold().strip()
        existing = unique.get(key)
        if existing is not None:
            raise ValueError(
                f"Duplicate keyword ownership for {row.keyword!r}: "
                f"{existing.target_url!r} and {row.target_url!r}"
            )
        unique[key] = row
    return list(unique.values())


LOCATIONS = [
    ("Goa", "state", "/", "homepage"),
    ("North Goa", "north_goa", "/locations/north-goa/", "regional_hub"),
    ("South Goa", "south_goa", "/locations/south-goa/", "regional_hub"),
    ("Panaji", "north_goa", "/locations/panaji/", "conditional_local_page"),
    ("Panjim", "north_goa", "/locations/panaji/", "alias_to_panaji_page"),
    ("Porvorim", "north_goa", "/locations/porvorim/", "conditional_local_page"),
    ("Mapusa", "north_goa", "/locations/mapusa/", "conditional_local_page"),
    ("Calangute", "north_goa", "/locations/calangute/", "conditional_local_page"),
    ("Candolim", "north_goa", "/locations/candolim/", "conditional_local_page"),
    ("Baga", "north_goa", "/locations/baga/", "conditional_local_page"),
    ("Anjuna", "north_goa", "/locations/anjuna/", "conditional_local_page"),
    ("Arpora", "north_goa", "/locations/arpora/", "conditional_local_page"),
    ("Assagao", "north_goa", "/locations/assagao/", "conditional_local_page"),
    ("Siolim", "north_goa", "/locations/siolim/", "conditional_local_page"),
    ("Morjim", "north_goa", "/locations/morjim/", "conditional_local_page"),
    ("Mandrem", "north_goa", "/locations/mandrem/", "conditional_local_page"),
    ("Pernem", "north_goa", "/locations/pernem/", "conditional_local_page"),
    ("Dona Paula", "north_goa", "/locations/dona-paula/", "conditional_local_page"),
    ("Taleigao", "north_goa", "/locations/taleigao/", "conditional_local_page"),
    ("Miramar", "north_goa", "/locations/miramar/", "conditional_local_page"),
    ("Old Goa", "north_goa", "/locations/old-goa/", "conditional_local_page"),
    ("Ponda", "central_goa", "/locations/ponda/", "conditional_local_page"),
    ("Vasco da Gama", "south_goa", "/locations/vasco-da-gama/", "conditional_local_page"),
    ("Vasco", "south_goa", "/locations/vasco-da-gama/", "alias_to_vasco_da_gama_page"),
    ("Mormugao", "south_goa", "/locations/mormugao/", "conditional_local_page"),
    ("Verna", "south_goa", "/locations/verna/", "conditional_local_page"),
    ("Margao", "south_goa", "/locations/margao/", "conditional_local_page"),
    ("Madgaon", "south_goa", "/locations/margao/", "alias_to_margao_page"),
    ("Navelim", "south_goa", "/locations/navelim/", "conditional_local_page"),
    ("Salcete", "south_goa", "/locations/salcete/", "conditional_local_page"),
    ("Colva", "south_goa", "/locations/colva/", "conditional_local_page"),
    ("Benaulim", "south_goa", "/locations/benaulim/", "conditional_local_page"),
    ("Varca", "south_goa", "/locations/varca/", "conditional_local_page"),
    ("Cavelossim", "south_goa", "/locations/cavelossim/", "conditional_local_page"),
    ("Canacona", "south_goa", "/locations/canacona/", "conditional_local_page"),
    ("Palolem", "south_goa", "/locations/palolem/", "conditional_local_page"),
]

LOCAL_STEMS = [
    ("website design company", "web_design"),
    ("web design company", "web_design"),
    ("website designer", "web_design"),
    ("web designer", "web_design"),
    ("website development company", "web_development"),
    ("web developer", "web_development"),
    ("local seo company", "local_seo"),
    ("local seo services", "local_seo"),
]


def build_local_keyword_map() -> list[LocalKeywordRow]:
    rows: list[LocalKeywordRow] = []
    major_towns = {
        "Panaji",
        "Panjim",
        "Mapusa",
        "Margao",
        "Madgaon",
        "Porvorim",
        "Vasco da Gama",
        "Vasco",
    }
    statewide_targets = {
        "web_development": "/website-development-goa/",
        "local_seo": "/local-seo-goa/",
    }

    for locality, region, target_url, page_strategy in LOCATIONS:
        for stem, cluster in LOCAL_STEMS:
            phrase = f"{stem} in {locality}"
            mapped_target_url = target_url
            mapped_page_strategy = page_strategy
            notes = (
                "Do not publish a thin location page. Require unique local proof, "
                "relevant work, service details, FAQs, and internal links."
            )

            if locality == "Goa":
                priority = "P0"
                mapped_target_url = {
                    "web_design": "/",
                    **statewide_targets,
                }[cluster]
                mapped_page_strategy = (
                    "homepage" if cluster == "web_design" else "statewide_service_page"
                )
            else:
                if cluster != "web_design":
                    mapped_target_url = statewide_targets[cluster]
                    mapped_page_strategy = "statewide_service_page_pending_local_validation"
                    notes = (
                        "Keep this candidate on the statewide service page unless local "
                        "demand, unique proof, and distinct service content justify an "
                        "explicit town-service page. Do not stuff town lists into copy."
                    )

                if locality in {"North Goa", "South Goa"} and cluster == "web_design":
                    priority = "P1"
                elif locality in major_towns and cluster == "web_design":
                    priority = "P2"
                else:
                    priority = "P3_validate"

            source_evidence, source_query, source_url, observed_at = evidence_for(phrase)
            rows.append(
                LocalKeywordRow(
                    keyword=phrase,
                    locality=locality,
                    region=region,
                    service_cluster=cluster,
                    search_intent="local_transactional",
                    target_url=mapped_target_url,
                    page_strategy=mapped_page_strategy,
                    priority=priority,
                    source_evidence=source_evidence,
                    source_query=source_query,
                    source_url=source_url,
                    observed_at=observed_at,
                    status="candidate_needs_local_volume_and_gsc_validation",
                    notes=notes,
                )
            )

    near_me_terms = [
        ("website design company near me", "web_design", "/"),
        ("web design company near me", "web_design", "/"),
        ("website designer near me", "web_design", "/"),
        ("web designer near me", "web_design", "/"),
        ("website developer near me", "web_development", "/website-development-goa/"),
        ("web development company near me", "web_development", "/website-development-goa/"),
        ("local seo company near me", "local_seo", "/local-seo-goa/"),
        ("seo company near me", "local_seo", "/local-seo-goa/"),
        ("google business profile expert near me", "google_business_profile", "/google-business-profile-optimization-goa/"),
        ("website maintenance company near me", "maintenance", "/website-maintenance-goa/"),
        ("ecommerce website developer near me", "ecommerce", "/ecommerce-website-development-goa/"),
        ("wordpress developer near me", "wordpress", "/wordpress-website-design-goa/"),
    ]
    for phrase, cluster, target_url in near_me_terms:
        rows.append(
            LocalKeywordRow(
                keyword=phrase,
                locality="searcher_proximity",
                region="goa_service_area",
                service_cluster=cluster,
                search_intent="near_me_transactional",
                target_url=target_url,
                page_strategy="optimize_relevant_service_page_and_gbp",
                priority="P1",
                source_evidence="strategic_expansion_validate",
                source_query="",
                source_url="",
                observed_at="",
                status="candidate_needs_gsc_and_gbp_validation",
                notes="Near-me visibility depends heavily on verified location/service area, relevance, distance, and prominence; do not stuff 'near me' into copy.",
            )
        )

    unique: dict[str, LocalKeywordRow] = {}
    for row in rows:
        key = row.keyword.casefold().strip()
        existing = unique.get(key)
        if existing is not None:
            raise ValueError(
                f"Duplicate local keyword ownership for {row.keyword!r}: "
                f"{existing.target_url!r} and {row.target_url!r}"
            )
        unique[key] = row
    return list(unique.values())


def build_roadmap() -> list[RoadmapRow]:
    raw_rows = [
        ("P0", "1", "Website Design Company in Goa", "/", "homepage", "website design company in goa", "core web design variants", "commercial_transactional", "project enquiry", "Resolve public 403; confirm NAP and services", "planned", "One homepage owns all close design/company/agency variants."),
        ("P0", "1", "Website Development Company in Goa", "/website-development-goa/", "service_page", "website development company in goa", "developers, custom development, web apps", "commercial_transactional", "development enquiry", "Confirm development capabilities and portfolio proof", "planned", "Separate design intent from deeper engineering intent."),
        ("P0", "1", "Ecommerce Website Development in Goa", "/ecommerce-website-development-goa/", "service_page", "ecommerce website development company in goa", "Shopify, WooCommerce, online stores", "commercial_transactional", "store build enquiry", "Confirm supported platforms and integrations", "planned", "Include payments, catalog, shipping, and case-study proof."),
        ("P0", "1", "Local SEO Services in Goa", "/local-seo-goa/", "service_page", "local seo services in goa", "SEO company, Maps SEO, local business SEO", "commercial_transactional", "SEO consultation", "Define actual deliverables and reporting", "planned", "Connect website optimization with GBP, citations, reviews, and local content."),
        ("P1", "1", "Google Business Profile Optimization in Goa", "/google-business-profile-optimization-goa/", "service_page", "google business profile optimization goa", "GBP management, Google Maps ranking", "commercial_transactional", "GBP audit request", "Confirm service ownership and access process", "planned", "Use current GBP naming; mention GMB only as a natural legacy synonym."),
        ("P1", "1", "Website Redesign Services in Goa", "/website-redesign-goa/", "service_page", "website redesign company in goa", "revamp, migration, responsive redesign", "commercial_transactional", "redesign audit request", "Create before-and-after evidence", "planned", "Address dated design, slow speed, poor mobile UX, weak conversion, and SEO migration."),
        ("P1", "1", "Website Maintenance Services in Goa", "/website-maintenance-goa/", "service_page", "website maintenance services in goa", "AMC, support, backups, security", "commercial_transactional", "maintenance plan enquiry", "Define plan scope and response times", "planned", "Avoid promises not supported by operations."),
        ("P1", "1", "WordPress Website Design in Goa", "/wordpress-website-design-goa/", "service_page", "wordpress website design company in goa", "WordPress developer, WooCommerce", "commercial_transactional", "WordPress project enquiry", "Confirm WordPress is an offered platform", "conditional", "Do not publish unless this is a real service."),
        ("P1", "1", "Website Design Cost in Goa", "/website-design-cost-goa/", "commercial_guide", "website design cost in goa", "prices, packages, charges", "commercial_investigation", "qualified quote request", "Approve honest pricing ranges", "planned", "Explain scope drivers; avoid bait pricing."),
        ("P1", "2", "Hotel Website Design in Goa", "/industries/hotel-website-design-goa/", "industry_page", "hotel website design company goa", "direct booking, hospitality SEO", "commercial_transactional", "hotel project enquiry", "Require hospitality work or demonstrable expertise", "planned", "Highest-fit Goa vertical; emphasize direct bookings and OTA independence."),
        ("P1", "2", "Resort Website Design in Goa", "/industries/resort-website-design-goa/", "industry_page", "resort website design goa", "booking engine, multilingual, mobile", "commercial_transactional", "resort project enquiry", "Require resort-specific proof", "planned", "May consolidate with hotel page if evidence is thin."),
        ("P1", "2", "Restaurant Website Design in Goa", "/industries/restaurant-website-design-goa/", "industry_page", "restaurant website design goa", "menus, reservations, ordering", "commercial_transactional", "restaurant project enquiry", "Require F&B examples or a tailored demo", "planned", "Cover menu UX, WhatsApp, maps, reservations, and local discovery."),
        ("P1", "2", "Travel Agency Website Design in Goa", "/industries/travel-and-tours-website-design-goa/", "industry_page", "travel agency website design goa", "tour operator, booking, tourism", "commercial_transactional", "tourism project enquiry", "Require tourism workflow knowledge", "planned", "Cover packages, availability, payments, itinerary, and lead capture."),
        ("P1", "2", "Real Estate Website Design in Goa", "/industries/real-estate-website-design-goa/", "industry_page", "real estate website design goa", "property portal, listings, lead generation", "commercial_transactional", "property website enquiry", "Require property-search feature plan", "planned", "Cover listings, maps, filters, WhatsApp, CRM, and project landing pages."),
        ("P1", "2", "Wedding Planner Website Design in Goa", "/industries/wedding-website-design-goa/", "industry_page", "wedding planner website design goa", "destination wedding, portfolio, enquiry", "commercial_transactional", "wedding business enquiry", "Require visual portfolio approach", "planned", "Strong Goa-specific vertical with international and domestic demand."),
        ("P1", "2", "Web Design Company in North Goa", "/locations/north-goa/", "regional_hub", "web design company in north goa", "Panaji, Mapusa, Porvorim, coastal belt", "local_transactional", "local enquiry", "Confirm service coverage and local proof", "conditional", "Build before town pages; include genuine regional evidence."),
        ("P1", "2", "Web Design Company in South Goa", "/locations/south-goa/", "regional_hub", "web design company in south goa", "Margao, Vasco, coastal belt", "local_transactional", "local enquiry", "Confirm service coverage and local proof", "conditional", "Build before town pages; include genuine regional evidence."),
        ("P2", "3", "How to Choose a Web Design Company in Goa", "/guides/choose-web-design-company-goa/", "guide", "how to choose a web design company in goa", "agency vs freelancer, questions, brief", "informational_commercial", "consultation", "Publish service and proof pages first", "planned", "Decision-support content that internally links to homepage and portfolio."),
        ("P2", "3", "Local SEO Guide for Goa Businesses", "/guides/local-seo-goa/", "pillar_guide", "local seo checklist for goa businesses", "Maps, GBP, reviews, citations", "informational_commercial", "SEO audit request", "Local SEO service page live", "planned", "Link to GBP and Local SEO services."),
        ("P2", "3", "How to Rank on Google Maps in Goa", "/guides/rank-google-maps-goa/", "guide", "how to rank on google maps in goa", "GBP ranking, reviews, relevance", "informational_commercial", "GBP audit request", "GBP service page live", "planned", "Base claims on Google guidance; no guaranteed ranking promises."),
        ("P2", "3", "Website Redesign Checklist", "/guides/website-redesign-checklist/", "guide", "signs your website needs a redesign", "migration, mobile, speed, conversion", "informational_commercial", "redesign audit request", "Redesign service page live", "planned", "Include SEO migration safeguards."),
        ("P2", "3", "Best Website Platform for a Goa Small Business", "/guides/best-website-platform-small-business-goa/", "comparison_guide", "best website platform for small business in goa", "WordPress, Shopify, custom", "informational_commercial", "platform consultation", "Confirm offered platforms", "planned", "Recommend by use case, not a one-size-fits-all winner."),
        ("P2", "3", "Hotel Website Direct Booking Guide", "/guides/hotel-direct-booking-website-goa/", "vertical_guide", "hotel website direct booking optimization", "booking engine, OTA, conversion", "informational_commercial", "hotel project enquiry", "Hotel service page live", "planned", "Build topical depth around the strongest Goa vertical."),
        ("P2", "4", "Web Design Company in Panaji", "/locations/panaji/", "local_page", "website design company in panaji", "Panjim synonym, local services", "local_transactional", "local enquiry", "Unique Panaji proof and demand validation", "conditional", "One page handles both Panaji and Panjim naturally."),
        ("P2", "4", "Web Design Company in Mapusa", "/locations/mapusa/", "local_page", "website design company in mapusa", "Mapusa website development", "local_transactional", "local enquiry", "Unique Mapusa proof; autocomplete validation", "conditional", "Do not clone regional copy."),
        ("P2", "4", "Web Design Company in Margao", "/locations/margao/", "local_page", "website design company in margao", "Madgaon synonym, South Goa", "local_transactional", "local enquiry", "Unique Margao proof and demand validation", "conditional", "One page handles Margao and Madgaon naturally."),
        ("P2", "4", "Web Design Company in Porvorim", "/locations/porvorim/", "local_page", "website design company in porvorim", "Porvorim web development", "local_transactional", "local enquiry", "Unique Porvorim proof and demand validation", "conditional", "Publish only if the business genuinely serves and can evidence the area."),
        ("P2", "4", "Web Design Company in Vasco da Gama", "/locations/vasco-da-gama/", "local_page", "website design company in vasco da gama", "Vasco web designer", "local_transactional", "local enquiry", "Unique Vasco proof and demand validation", "conditional", "Use Vasco as a natural synonym."),
        ("P3_validate", "4", "Additional Goa Town Pages", "/locations/{locality}/", "local_page_template", "see local-seo-keywords.csv", "town and neighborhood modifiers", "local_transactional", "local enquiry", "GSC/GBP evidence plus unique proof for each town", "deferred", "Never mass-publish the full locality matrix; it is a research inventory, not a doorway-page instruction."),
    ]
    return [RoadmapRow(*row) for row in raw_rows]


def validate_relationships(
    keyword_rows: list[KeywordRow],
    local_rows: list[LocalKeywordRow],
    roadmap_rows: list[RoadmapRow],
) -> None:
    """Fail generation when canonical ownership or evidence drifts."""
    keyword_index = {row.keyword.casefold(): row for row in keyword_rows}
    local_index = {row.keyword.casefold(): row for row in local_rows}

    for keyword in keyword_index.keys() & local_index.keys():
        keyword_row = keyword_index[keyword]
        local_row = local_index[keyword]
        if (keyword_row.target_url, keyword_row.priority) != (
            local_row.target_url,
            local_row.priority,
        ):
            raise ValueError(
                f"Cross-inventory ownership drift for {keyword!r}: "
                f"{keyword_row.target_url!r}/{keyword_row.priority} and "
                f"{local_row.target_url!r}/{local_row.priority}"
            )

    combined_index: dict[str, KeywordRow | LocalKeywordRow] = {
        **local_index,
        **keyword_index,
    }
    for roadmap_row in roadmap_rows:
        primary_keyword = roadmap_row.primary_keyword.casefold()
        if primary_keyword.startswith("see "):
            continue
        inventory_row = combined_index.get(primary_keyword)
        if inventory_row is None:
            raise ValueError(
                f"Roadmap primary keyword has no inventory row: "
                f"{roadmap_row.primary_keyword!r}"
            )
        if (inventory_row.target_url, inventory_row.priority) != (
            roadmap_row.target_url,
            roadmap_row.priority,
        ):
            raise ValueError(
                f"Roadmap ownership drift for {roadmap_row.primary_keyword!r}: "
                f"{inventory_row.target_url!r}/{inventory_row.priority} and "
                f"{roadmap_row.target_url!r}/{roadmap_row.priority}"
            )

    positive_evidence = {"google_autocomplete_in_en", "serp_observed"}
    for row in [*keyword_rows, *local_rows]:
        if row.source_evidence in positive_evidence and not all(
            (row.source_query, row.source_url, row.observed_at)
        ):
            raise ValueError(f"Positive evidence lacks provenance: {row.keyword!r}")
        if row.source_evidence == "strategic_expansion_validate" and any(
            (row.source_query, row.source_url, row.observed_at)
        ):
            raise ValueError(
                f"Unvalidated expansion contains observation metadata: {row.keyword!r}"
            )

    for row in local_rows:
        if (
            row.locality != "Goa"
            and row.service_cluster != "web_design"
            and row.target_url.startswith("/locations/")
        ):
            raise ValueError(
                f"Non-design town keyword maps to a catch-all location page: "
                f"{row.keyword!r}"
            )

    cost_markers = (
        "cost",
        "price",
        "pricing",
        "packages",
        "charges",
        "cheap",
        "affordable",
        "low cost",
    )
    website_markers = ("website", "web design", "web designer")
    for row in keyword_rows:
        normalized = row.keyword.casefold()
        is_website_cost_query = any(marker in normalized for marker in cost_markers) and any(
            marker in normalized for marker in website_markers
        )
        if is_website_cost_query and row.target_url != "/website-design-cost-goa/":
            raise ValueError(
                f"Website-cost keyword has the wrong canonical owner: {row.keyword!r}"
            )

    valid_priorities = {"P0", "P1", "P2", "P3_validate"}
    for row in [*keyword_rows, *local_rows, *roadmap_rows]:
        if row.priority not in valid_priorities:
            raise ValueError(f"Unknown priority {row.priority!r}")


def main() -> None:
    keyword_rows = build_keyword_map()
    local_rows = build_local_keyword_map()
    roadmap_rows = build_roadmap()
    validate_relationships(keyword_rows, local_rows, roadmap_rows)

    write_rows(OUTPUT_DIR / "keyword-map.csv", keyword_rows)
    write_rows(OUTPUT_DIR / "local-seo-keywords.csv", local_rows)
    write_rows(OUTPUT_DIR / "content-roadmap.csv", roadmap_rows)

    print(f"keyword_map={len(keyword_rows)}")
    print(f"local_keyword_map={len(local_rows)}")
    print(f"content_roadmap={len(roadmap_rows)}")
    print(f"research_date={RESEARCH_DATE}")


if __name__ == "__main__":
    main()
