"""Build and audit the dependency-free static website."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
SRC: Final[Path] = ROOT / "src"
DIST: Final[Path] = ROOT / "dist"
BUILD_DIR: Final[Path] = ROOT / ".dist-build"
BACKUP_DIR: Final[Path] = ROOT / ".dist-backup"
BASE_URL: Final[str] = "https://webdesigncompanygoa.in"
IMAGE_WIDTH: Final[int] = 1200
IMAGE_HEIGHT: Final[int] = 630
IMAGE_STEMS: Final[tuple[str, ...]] = (
    "hero-goa-web-design-studio",
    "services-responsive-design-workspace",
    "portfolio-device-showcase",
    "process-indian-design-team",
    "goa-local-business-owner",
    "client-conversation-goa",
    "final-cta-goa-creative-team",
)
IMAGE_FILES: Final[tuple[str, ...]] = tuple(
    f"{stem}-{width}.webp" for stem in IMAGE_STEMS for width in (720, 1376)
) + ("social-preview.jpg",)
IMAGE_DIMENSIONS: Final[dict[str, tuple[int, int]]] = {
    **{
        f"{stem}-720.webp": (720, 402)
        for stem in IMAGE_STEMS
    },
    **{
        f"{stem}-1376.webp": (1376, 768)
        for stem in IMAGE_STEMS
    },
    "social-preview.jpg": (IMAGE_WIDTH, IMAGE_HEIGHT),
}


@dataclass(frozen=True)
class Faq:
    question: str
    answer: str


@dataclass(frozen=True)
class Page:
    route: str
    fragment: str
    title: str
    description: str
    label: str
    schema_type: str = "WebPage"
    service_name: str | None = None
    faqs: tuple[Faq, ...] = ()
    indexable: bool = True
    hero_image: bool = False

    @property
    def url(self) -> str:
        return f"{BASE_URL}{self.route}"


PAGES: Final[tuple[Page, ...]] = (
    Page(
        route="/",
        fragment="home.html",
        title="Website Design Company in Goa | Web Design by Sanctify",
        description="A focused website design company serving businesses in Goa with clear planning, responsive design and practical development by Sanctify.",
        label="Home",
        schema_type="WebPage",
        faqs=(
            Faq("What does Web Design Company Goa offer?", "The website explains focused planning, responsive interface design and custom website development for businesses that serve customers in Goa."),
            Faq("Is Web Design Company Goa a separate company?", "No. Web Design Company Goa is a focused web-design website by Sanctify, which handles project enquiries and the wider business relationship."),
            Faq("Can you help choose the right website scope?", "Yes. Discovery can compare the information, content, functionality and operational needs before a suitable scope or platform is selected."),
        ),
        hero_image=True,
    ),
    Page(
        route="/website-development-goa/",
        fragment="website-development-goa.html",
        title="Website Development in Goa | Custom Web Builds",
        description="Explore custom website development for businesses serving Goa, including discovery, responsive interfaces, content structure and technical planning.",
        label="Website development in Goa",
        schema_type="WebPage",
        service_name="Website development",
        faqs=(
            Faq("What is included in custom website development?", "A suitable scope can include discovery, information architecture, interface design, responsive front-end development, content integration and launch planning."),
            Faq("How is the technology selected?", "Technology should follow the approved requirements, hosting context, editing needs and long-term operating plan rather than a predetermined platform claim."),
            Faq("Can an existing website be improved?", "An existing site can be reviewed for structure, usability, content and technical constraints before deciding whether focused improvements or a rebuild are more appropriate."),
        ),
    ),
    Page(
        route="/ecommerce-website-development-goa/",
        fragment="ecommerce-website-development-goa.html",
        title="Ecommerce Website Development in Goa | Sanctify",
        description="Plan an ecommerce website for a business serving Goa, from catalogue and checkout requirements to operations, content and conditional platform selection.",
        label="Ecommerce website development in Goa",
        schema_type="WebPage",
        service_name="Ecommerce website development",
        faqs=(
            Faq("How is an ecommerce platform selected?", "Platform selection follows discovery. Catalogue size, checkout needs, operational workflow, hosting, budget and maintenance responsibilities all influence the decision."),
            Faq("What should be prepared before an online store project?", "Prepare product categories, product information, fulfilment rules, payment requirements, customer policies, content responsibilities and the people who will operate the store."),
            Faq("Are specific integrations included?", "No integration is assumed. Any payment, shipping, inventory or business-system connection needs to be confirmed for feasibility and scope during discovery."),
        ),
    ),
    Page(
        route="/about/",
        fragment="about.html",
        title="About Web Design Company Goa | Specialist by Sanctify",
        description="Learn why Sanctify created Web Design Company Goa as a focused specialist website for clear web-design and development information for Goa businesses.",
        label="About",
        schema_type="AboutPage",
    ),
    Page(
        route="/portfolio/",
        fragment="portfolio.html",
        title="Website Portfolio Framework | Web Design Company Goa",
        description="Review an honest portfolio framework with illustrative project briefs showing how website goals, content and delivery decisions can be approached.",
        label="Portfolio framework",
    ),
    Page(
        route="/contact/",
        fragment="contact.html",
        title="Start a Website Project in Goa | Contact Sanctify",
        description="Prepare a concise website project brief, then continue to Sanctify's contact page for enquiries about web design and development serving businesses in Goa.",
        label="Contact",
        schema_type="ContactPage",
    ),
    Page(
        route="/privacy-policy/",
        fragment="privacy-policy.html",
        title="Privacy Policy | Web Design Company Goa by Sanctify",
        description="Read the privacy notice for this static website, including its no-form and no-analytics approach and how external Sanctify pages are handled.",
        label="Privacy policy",
    ),
    Page(
        route="/terms/",
        fragment="terms.html",
        title="Website Terms | Web Design Company Goa by Sanctify",
        description="Read neutral terms for using the Web Design Company Goa information website, including content limits, external links and intellectual property.",
        label="Terms",
    ),
    Page(
        route="/website-redesign-goa/",
        fragment="website-redesign-goa.html",
        title="Website Redesign Services in Goa | Web Design by Sanctify",
        description="Plan a website redesign for a business serving Goa, improving structure, mobile experience, speed and conversion while protecting existing SEO value.",
        label="Website redesign in Goa",
        schema_type="WebPage",
        service_name="Website redesign",
        faqs=(
            Faq("When is a website redesign worth considering?", "A redesign is worth considering when the current site is hard to update, weak on mobile, slow, off brand or no longer guiding visitors toward a clear action."),
            Faq("How is search visibility protected during a redesign?", "Existing URLs, content and internal links are reviewed first, then redirects, structure and metadata are planned so ranking signals are carried across rather than lost."),
            Faq("Can a redesign happen in stages?", "Yes. A redesign can move in reviewed stages, starting with structure and priority pages before wider content, so risk stays visible and decisions remain reversible."),
        ),
    ),
    Page(
        route="/website-maintenance-goa/",
        fragment="website-maintenance-goa.html",
        title="Website Maintenance Services in Goa | Support by Sanctify",
        description="Understand website maintenance for a business serving Goa, covering updates, backups, security checks, small content changes and predictable ongoing support.",
        label="Website maintenance in Goa",
        schema_type="WebPage",
        service_name="Website maintenance",
        faqs=(
            Faq("What can a website maintenance plan include?", "A plan can include software and plugin updates, backups, security monitoring, uptime checks, minor content edits and periodic reviews agreed with the business."),
            Faq("Are maintenance response times guaranteed?", "Response times depend on the agreed plan scope and are confirmed in writing, so expectations for routine changes and urgent issues are clear before work begins."),
            Faq("Is maintenance available for a site built elsewhere?", "A site built elsewhere can be reviewed for platform, hosting and code quality first, then a suitable maintenance arrangement is considered based on what is found."),
        ),
    ),
    Page(
        route="/website-speed-optimization-goa/",
        fragment="website-speed-optimization-goa.html",
        title="Website Speed Optimization in Goa | Faster Web by Sanctify",
        description="Improve website speed and Core Web Vitals for a business serving Goa, using measurement, prioritised fixes and honest reporting rather than guaranteed scores.",
        label="Website speed optimization in Goa",
        schema_type="WebPage",
        service_name="Website speed optimization",
        faqs=(
            Faq("How does a speed optimization project start?", "It starts with measurement on real pages and devices, so the largest and most fixable performance problems are identified before any change is made."),
            Faq("Which issues commonly slow a website down?", "Common causes include heavy images, render blocking scripts, unused code, slow hosting responses and layout shifts that affect Core Web Vitals and perceived speed."),
            Faq("Can a specific performance score be promised?", "No fixed score is promised. Realistic improvement targets are set from the measured baseline, and results are reported against that baseline after changes."),
        ),
    ),
    Page(
        route="/website-design-cost-goa/",
        fragment="website-design-cost-goa.html",
        title="Website Design Cost in Goa | Pricing Factors Explained",
        description="Understand what shapes website design cost in Goa, from pages and features to content and platform, so you can prepare a realistic budget and a clearer quote.",
        label="Website design cost in Goa",
        schema_type="WebPage",
        faqs=(
            Faq("What affects the cost of a website in Goa?", "Cost is shaped by the number of pages, required features, content readiness, design complexity, integrations, platform choice and the level of ongoing support."),
            Faq("Why are fixed prices not shown upfront?", "A responsible quote follows discovery, because a small brochure site and a feature rich store differ greatly, and honest pricing needs the real requirements first."),
            Faq("How can a website budget be used well?", "A budget is used well by funding the pages and features that drive enquiries first, then improving the site in planned stages as results and priorities become clear."),
        ),
    ),
    Page(
        route="/industries/hotel-website-design-goa/",
        fragment="industries/hotel-website-design-goa.html",
        title="Hotel Website Design in Goa | Direct Booking Focus",
        description="Plan a hotel website for a property in Goa, focused on rooms, offers, direct booking readiness and fast mobile pages that reduce dependence on booking portals.",
        label="Hotel website design in Goa",
        schema_type="WebPage",
        service_name="Hotel website design",
        faqs=(
            Faq("What should a hotel website in Goa prioritise?", "It should present rooms, rates, offers and location clearly, load quickly on mobile and make direct enquiry or booking the easiest action for a guest to take."),
            Faq("How can a hotel reduce dependence on booking portals?", "Clear direct offers, trust signals, fast pages and a simple booking or enquiry path give guests a reason to book directly instead of only through travel portals."),
            Faq("Is a booking engine required from the start?", "Not always. Requirements are reviewed first, and a suitable booking or enquiry approach is chosen based on property size, budget and how reservations are managed."),
        ),
    ),
    Page(
        route="/industries/resort-website-design-goa/",
        fragment="industries/resort-website-design-goa.html",
        title="Resort Website Design in Goa | Booking Ready Sites",
        description="Plan a resort website for a property in Goa, presenting rooms, experiences and offers with fast mobile pages and a clear path to direct enquiries and bookings.",
        label="Resort website design in Goa",
        schema_type="WebPage",
        service_name="Resort website design",
        faqs=(
            Faq("What makes a resort website effective?", "An effective resort website shows accommodation, facilities, experiences and offers clearly, loads fast for international visitors and guides guests toward a direct booking."),
            Faq("Can a resort website support more than one language?", "Multilingual support can be planned when the audience needs it, and the structure and content are prepared so additional languages can be added without a rebuild."),
            Faq("How are seasonal offers handled?", "Seasonal offers are planned as content that can be updated easily, so rates, packages and campaigns can change through the year without a developer for every edit."),
        ),
    ),
    Page(
        route="/industries/restaurant-website-design-goa/",
        fragment="industries/restaurant-website-design-goa.html",
        title="Restaurant Website Design in Goa | Menus and Bookings",
        description="Plan a restaurant, cafe or beach shack website in Goa with mobile menus, reservations, directions and ordering links that turn local searches into real visits.",
        label="Restaurant website design in Goa",
        schema_type="WebPage",
        service_name="Restaurant website design",
        faqs=(
            Faq("What should a restaurant website in Goa include?", "It should show the menu, location, hours and contact clearly on mobile, and make reservations, directions or ordering simple for someone deciding where to eat."),
            Faq("How does a website help with local discovery?", "Clear location details, fast mobile pages and consistent business information support the searches people make nearby when they are choosing a place to eat."),
            Faq("Can online ordering or delivery links be added?", "Ordering, delivery or reservation links can be added when the business uses those services, so visitors reach the right tool without a complex custom system."),
        ),
    ),
    Page(
        route="/industries/travel-and-tours-website-design-goa/",
        fragment="industries/travel-and-tours-website-design-goa.html",
        title="Travel Agency Website Design in Goa | Tours and Trips",
        description="Plan a travel agency or tour operator website in Goa with package pages, itineraries, enquiry flows and content built for seasonal demand and international visitors.",
        label="Travel and tours website design in Goa",
        schema_type="WebPage",
        service_name="Travel and tours website design",
        faqs=(
            Faq("What should a travel or tour website show?", "It should present packages, itineraries, inclusions and pricing context clearly, and make enquiry or booking simple for travellers comparing options for a Goa trip."),
            Faq("How are seasonal campaigns supported?", "Content is structured so packages, offers and landing pages can be updated for each season, supporting campaigns without rebuilding the site every time demand shifts."),
            Faq("Can payments or booking tools be added later?", "Payment or booking tools can be introduced when workflow and requirements are confirmed, starting with reliable enquiries before adding heavier online booking systems."),
        ),
    ),
    Page(
        route="/industries/real-estate-website-design-goa/",
        fragment="industries/real-estate-website-design-goa.html",
        title="Real Estate Website Design in Goa | Property Listings",
        description="Plan a real estate website for agents and developers in Goa with property listings, search, map context, project pages and lead capture built for serious buyers.",
        label="Real estate website design in Goa",
        schema_type="WebPage",
        service_name="Real estate website design",
        faqs=(
            Faq("What features does a property website need?", "It typically needs organised listings, search and filters, location context, clear project or property pages and a simple, trustworthy way to capture genuine enquiries."),
            Faq("How are enquiries routed to the sales team?", "Enquiry paths, contact options and any connection to a CRM are agreed during discovery, so leads reach the right person quickly instead of being lost in a form."),
            Faq("Can individual project landing pages be created?", "Dedicated project or property landing pages can be planned, giving each development focused content and a clear enquiry path for campaigns and direct sharing."),
        ),
    ),
    Page(
        route="/industries/wedding-website-design-goa/",
        fragment="industries/wedding-website-design-goa.html",
        title="Wedding Planner Website Design in Goa | Portfolios",
        description="Plan a wedding planner or destination wedding website in Goa with a visual portfolio, service pages and enquiry flows built for domestic and international couples.",
        label="Wedding website design in Goa",
        schema_type="WebPage",
        service_name="Wedding website design",
        faqs=(
            Faq("What matters most on a wedding planner website?", "A strong visual portfolio, clear services, pricing context and an easy enquiry path matter most, because couples judge trust and style quickly before making contact."),
            Faq("How are international enquiries supported?", "Fast pages, clear service areas, timezone friendly contact options and reassuring content help couples planning a Goa wedding from another city or country enquire with confidence."),
            Faq("Can galleries and real events be added over time?", "Galleries are planned so approved event photos and stories can be added over time, keeping the portfolio current without a rebuild as new work becomes available."),
        ),
    ),
    Page(
        route="/guides/choose-web-design-company-goa/",
        fragment="guides/choose-web-design-company-goa.html",
        title="How to Choose a Web Design Company in Goa | Guide",
        description="A practical guide to choosing a web design company in Goa, with the questions, briefs and warning signs that help you compare studios and freelancers fairly.",
        label="How to choose a web design company in Goa",
        schema_type="WebPage",
        faqs=(
            Faq("What should I ask a web design company first?", "Ask how they plan projects, who owns the site and content, what is in and out of scope, how changes are handled and what support exists after the site launches."),
            Faq("Is an agency or a freelancer better?", "Neither is always better. A freelancer can suit small focused work, while a team suits broader scope, so match the choice to complexity, timeline and support needs."),
            Faq("How do I compare quotes fairly?", "Compare quotes on scope, ownership, support and clarity rather than price alone, because the cheapest option can cost more when important work is left out."),
        ),
    ),
    Page(
        route="/guides/website-conversion-goa-business/",
        fragment="guides/website-conversion-goa-business.html",
        title="Website Conversion Guide for Goa Businesses | Sanctify",
        description="Learn how a website turns visitors into enquiries for a Goa business, covering clarity, mobile speed, trust signals and a focused path to a single next action.",
        label="Website conversion guide for Goa businesses",
        schema_type="WebPage",
        faqs=(
            Faq("Why does a website get visits but few enquiries?", "Often the offer is unclear, the page is slow or busy on mobile, trust is thin or the next action is hard to find, so interested visitors leave without making contact."),
            Faq("What is the single most useful conversion change?", "Making the main action obvious on every page is usually the most useful change, so a visitor always knows what to do next without hunting for it."),
            Faq("How is conversion measured honestly?", "Conversion is measured against a clear baseline using real enquiries and page behaviour, so improvements are judged by results rather than by opinion or guesswork."),
        ),
    ),
    Page(
        route="/guides/website-redesign-checklist/",
        fragment="guides/website-redesign-checklist.html",
        title="Website Redesign Checklist for Goa Businesses | Guide",
        description="A website redesign checklist for Goa businesses, covering goals, content, mobile, speed, SEO migration and the safeguards that protect traffic during a rebuild.",
        label="Website redesign checklist",
        schema_type="WebPage",
        faqs=(
            Faq("What are the signs a website needs a redesign?", "Signs include a dated look, poor mobile use, slow loading, content that is hard to update and pages that no longer guide visitors toward a clear action."),
            Faq("What should be prepared before a redesign?", "Prepare current URLs, top performing pages, analytics context, content owners and clear goals, so decisions are grounded in evidence rather than personal taste alone."),
            Faq("How is SEO protected during a rebuild?", "A URL map, planned redirects, preserved content and checks after launch protect SEO, so existing rankings and links are carried across to the new website."),
        ),
    ),
    Page(
        route="/guides/best-website-platform-small-business-goa/",
        fragment="guides/best-website-platform-small-business-goa.html",
        title="Best Website Platform for a Goa Small Business | Guide",
        description="Compare website platforms for a Goa small business, from WordPress to hosted stores and custom builds, matched to budget, control and how you plan to grow.",
        label="Best website platform for a Goa small business",
        schema_type="WebPage",
        faqs=(
            Faq("Which website platform is best for a small business?", "There is no single winner. The best platform depends on your budget, the features you need, who will edit the site and how much control and growth you expect."),
            Faq("Is WordPress or a hosted platform better?", "WordPress offers flexibility and ownership, while a hosted platform trades some control for simplicity, so the right choice follows your workflow and long term plans."),
            Faq("Can the platform be changed later?", "A platform can be changed later, but migration takes effort, so choosing a suitable option early and planning content sensibly reduces cost and disruption over time."),
        ),
    ),
    Page(
        route="/guides/hotel-direct-booking-website-goa/",
        fragment="guides/hotel-direct-booking-website-goa.html",
        title="Hotel Direct Booking Website Guide for Goa | Sanctify",
        description="Learn how a Goa hotel website can win more direct bookings, reducing portal commission with clear offers, fast mobile pages, trust signals and a simple booking path.",
        label="Hotel direct booking website guide",
        schema_type="WebPage",
        faqs=(
            Faq("How can a hotel win more direct bookings?", "Clear direct offers, honest rates, fast mobile pages, trust signals and a simple booking or enquiry path give guests a reason to book directly with the hotel."),
            Faq("Why do guests book through portals instead?", "Guests use portals for habit, perceived deals and convenience, so a hotel site must make the direct value obvious and the booking step easy to overcome that pull."),
            Faq("Does direct booking mean leaving portals entirely?", "No. Portals still bring visibility, and the aim is balance, using them for reach while steadily growing lower cost direct bookings through the hotel website."),
        ),
    ),
    Page(
        route="/404.html",
        fragment="404.html",
        title="Page Not Found | Web Design Company Goa",
        description="The requested page could not be found. Return home or review website development capabilities from Web Design Company Goa by Sanctify.",
        label="Page not found",
        indexable=False,
    ),
)


class AuditParser(HTMLParser):
    """Collect audit-relevant HTML details using the standard library."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.lang = ""
        self.meta_by_name: dict[str, str] = {}
        self.meta_by_property: dict[str, str] = {}
        self.hrefs: list[str] = []
        self.anchors: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.json_ld: list[str] = []
        self.visible_text: list[str] = []
        self._in_title = False
        self._script_type = ""
        self._script_chunks: list[str] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.lang = values.get("lang", "")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = values.get("name", "")
            property_name = values.get("property", "")
            content = values.get("content", "")
            if name:
                self.meta_by_name[name] = content
            if property_name:
                self.meta_by_property[property_name] = content
            if name == "description":
                self.description = content
            if name == "robots":
                self.robots = content
        elif tag == "link":
            self.links.append(values)
            if values.get("rel") == "canonical":
                self.canonical = values.get("href", "")
        elif tag == "a":
            self.hrefs.append(values.get("href", ""))
            self.anchors.append(values)
        elif tag == "img":
            self.images.append(values)
        elif tag == "script":
            self.scripts.append(values)
            self._script_type = values.get("type", "")
            self._script_chunks = []
            self._hidden_depth += 1
        elif tag in {"style", "svg"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            if self._script_type == "application/ld+json":
                self.json_ld.append("".join(self._script_chunks))
            self._script_type = ""
            self._script_chunks = []
            self._hidden_depth = max(0, self._hidden_depth - 1)
        elif tag in {"style", "svg"}:
            self._hidden_depth = max(0, self._hidden_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._script_type:
            self._script_chunks.append(data)
        elif self._hidden_depth == 0 and data.strip():
            self.visible_text.append(data.strip())


def escaped(value: str) -> str:
    return html.escape(value, quote=True)


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:10]


def managed_directory(path: Path, *, expected_name: str) -> Path:
    """Validate that a managed directory is a real sibling of the repository root."""
    resolved = path.resolve()
    if path.is_symlink() or resolved.parent != ROOT.resolve() or resolved.name != expected_name:
        raise ValueError(f"Refusing to manage unexpected path: {path}")
    if path.exists() and not path.is_dir():
        raise ValueError(f"Managed path is not a directory: {path}")
    return resolved


def path_is_present(path: Path) -> bool:
    """Treat even a broken symlink as present so safety validation can reject it."""
    return path.exists() or path.is_symlink()


def remove_managed_directory(path: Path, *, expected_name: str) -> None:
    resolved = managed_directory(path, expected_name=expected_name)
    if path_is_present(path):
        shutil.rmtree(resolved)


def recover_interrupted_install() -> None:
    """Restore or discard a prior backup according to the published dist state."""
    if not path_is_present(BACKUP_DIR):
        return
    managed_directory(BACKUP_DIR, expected_name=".dist-backup")
    if path_is_present(DIST):
        managed_directory(DIST, expected_name="dist")
        remove_managed_directory(BACKUP_DIR, expected_name=".dist-backup")
        return
    BACKUP_DIR.rename(DIST)


def prepare_build_dir() -> None:
    remove_managed_directory(BUILD_DIR, expected_name=".dist-build")
    BUILD_DIR.mkdir(parents=True)


def install_build() -> None:
    """Install an audited stage with rollback and next-run interruption recovery."""
    managed_directory(BUILD_DIR, expected_name=".dist-build")
    if path_is_present(BACKUP_DIR):
        raise ValueError(f"Refusing to overwrite unresolved backup: {BACKUP_DIR}")
    if path_is_present(DIST):
        managed_directory(DIST, expected_name="dist")
        DIST.rename(BACKUP_DIR)
    try:
        BUILD_DIR.rename(DIST)
    except OSError:
        if path_is_present(BACKUP_DIR) and not path_is_present(DIST):
            BACKUP_DIR.rename(DIST)
        raise
    if path_is_present(BACKUP_DIR):
        remove_managed_directory(BACKUP_DIR, expected_name=".dist-backup")


def webp_dimensions(data: bytes) -> tuple[int, int]:
    """Read WebP dimensions from a validated RIFF container."""
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("invalid RIFF/WEBP signature")
    declared_size = int.from_bytes(data[4:8], "little") + 8
    if declared_size != len(data):
        raise ValueError("WebP RIFF size does not match file length")
    offset = 12
    while offset + 8 <= len(data):
        chunk_type = data[offset : offset + 4]
        chunk_size = int.from_bytes(data[offset + 4 : offset + 8], "little")
        payload_start = offset + 8
        payload_end = payload_start + chunk_size
        if payload_end > len(data):
            raise ValueError("truncated WebP chunk")
        payload = data[payload_start:payload_end]
        if chunk_type == b"VP8X":
            if len(payload) < 10:
                raise ValueError("truncated VP8X header")
            width = int.from_bytes(payload[4:7], "little") + 1
            height = int.from_bytes(payload[7:10], "little") + 1
            return width, height
        if chunk_type == b"VP8L":
            if len(payload) < 5 or payload[0] != 0x2F:
                raise ValueError("invalid VP8L header")
            packed = int.from_bytes(payload[1:5], "little")
            width = (packed & 0x3FFF) + 1
            height = ((packed >> 14) & 0x3FFF) + 1
            return width, height
        if chunk_type == b"VP8 ":
            if len(payload) < 10 or payload[3:6] != b"\x9d\x01\x2a":
                raise ValueError("invalid VP8 frame header")
            width = int.from_bytes(payload[6:8], "little") & 0x3FFF
            height = int.from_bytes(payload[8:10], "little") & 0x3FFF
            return width, height
        offset = payload_end + (chunk_size % 2)
    raise ValueError("WebP image chunk not found")


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Read JPEG dimensions from a start-of-frame segment."""
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("invalid JPEG signature")
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    offset = 2
    while offset < len(data):
        if data[offset] != 0xFF:
            raise ValueError("invalid JPEG marker boundary")
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if marker == 0xDA:
            break
        if offset + 2 > len(data):
            raise ValueError("truncated JPEG segment length")
        segment_length = int.from_bytes(data[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(data):
            raise ValueError("invalid JPEG segment length")
        if marker in sof_markers:
            if segment_length < 7:
                raise ValueError("truncated JPEG start-of-frame segment")
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            if width < 1 or height < 1:
                raise ValueError("invalid JPEG dimensions")
            return width, height
        offset += segment_length
    raise ValueError("JPEG start-of-frame segment not found")


def image_dimensions(path: Path) -> tuple[int, int]:
    """Validate an image signature and return its encoded dimensions."""
    data = path.read_bytes()
    if path.suffix == ".webp":
        return webp_dimensions(data)
    if path.suffix == ".jpg":
        return jpeg_dimensions(data)
    raise ValueError(f"Unsupported image format: {path.name}")


def validate_image(path: Path, *, expected: tuple[int, int]) -> None:
    try:
        actual = image_dimensions(path)
    except ValueError as exc:
        raise ValueError(f"Invalid image {path}: {exc}") from exc
    if actual != expected:
        raise ValueError(f"Image dimensions for {path} are {actual}, expected {expected}")


def copy_assets() -> tuple[str, str]:
    css_source = SRC / "assets" / "css" / "site.css"
    js_source = SRC / "assets" / "js" / "site.js"
    css_name = f"site.{fingerprint(css_source)}.css"
    js_name = f"site.{fingerprint(js_source)}.js"
    css_target = BUILD_DIR / "assets" / "css"
    js_target = BUILD_DIR / "assets" / "js"
    image_target = BUILD_DIR / "assets" / "images"
    css_target.mkdir(parents=True)
    js_target.mkdir(parents=True)
    image_target.mkdir(parents=True)
    shutil.copy2(css_source, css_target / css_name)
    shutil.copy2(js_source, js_target / js_name)
    image_dir = SRC / "assets" / "images"
    expected_images = set(IMAGE_FILES)
    actual_images = {path.name for path in image_dir.iterdir() if path.is_file()}
    missing_images = sorted(expected_images - actual_images)
    unexpected_images = sorted(actual_images - expected_images)
    if missing_images or unexpected_images:
        raise ValueError(
            f"Image manifest mismatch; missing={missing_images}, unexpected={unexpected_images}"
        )
    for name in IMAGE_FILES:
        source = image_dir / name
        if not source.is_file():
            raise ValueError(f"Expected image is not a file: {source}")
        validate_image(source, expected=IMAGE_DIMENSIONS[name])
        shutil.copy2(source, image_target / name)
    return css_name, js_name


def breadcrumbs_for(page: Page) -> str:
    if page.route == "/":
        return ""
    return (
        '<nav class="breadcrumbs" aria-label="Breadcrumb">'
        '<ol><li><a href="/">Home</a></li>'
        f'<li aria-current="page">{escaped(page.label)}</li></ol></nav>'
    )


def breadcrumb_schema(page: Page) -> dict[str, object]:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": page.label, "item": page.url},
        ],
    }


def schema_for(page: Page) -> str:
    if not page.indexable:
        return ""
    page_node: dict[str, object] = {
        "@type": page.schema_type,
        "@id": f"{page.url}#webpage",
        "url": page.url,
        "name": page.title,
        "description": page.description,
        "inLanguage": "en-IN",
        "isPartOf": {"@id": f"{BASE_URL}/#website"},
    }
    graph: list[dict[str, object]] = [page_node]
    if page.route == "/":
        graph.insert(
            0,
            {
                "@type": "WebSite",
                "@id": f"{BASE_URL}/#website",
                "url": f"{BASE_URL}/",
                "name": "Web Design Company Goa",
                "inLanguage": "en-IN",
            },
        )
    else:
        graph.append(breadcrumb_schema(page))
    if page.service_name:
        graph.append(
            {
                "@type": "Service",
                "@id": f"{page.url}#service",
                "name": page.service_name,
                "description": page.description,
                "url": page.url,
                "areaServed": {"@type": "AdministrativeArea", "name": "Goa"},
            }
        )
    if page.faqs:
        graph.append(
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {"@type": "Answer", "text": faq.answer},
                    }
                    for faq in page.faqs
                ],
            }
        )
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return f'<script type="application/ld+json">{payload}</script>'


def render_page(page: Page, *, template: str, css_file: str, js_file: str) -> str:
    fragment = (SRC / "pages" / page.fragment).read_text(encoding="utf-8")
    image_url = f"{BASE_URL}/assets/images/social-preview.jpg"
    replacements: Mapping[str, str] = {
        "{{TITLE}}": escaped(page.title),
        "{{DESCRIPTION}}": escaped(page.description),
        "{{ROBOTS_META}}": "" if page.indexable else '<meta name="robots" content="noindex, follow">',
        "{{CANONICAL_META}}": f'<link rel="canonical" href="{escaped(page.url)}">' if page.indexable else "",
        "{{PAGE_URL}}": escaped(page.url),
        "{{OG_IMAGE_META}}": f'<meta property="og:image" content="{image_url}"><meta property="og:image:width" content="{IMAGE_WIDTH}"><meta property="og:image:height" content="{IMAGE_HEIGHT}"><meta property="og:image:alt" content="Illustration of a website design workspace in Goa">',
        "{{TWITTER_IMAGE_META}}": f'<meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="Illustration of a website design workspace in Goa">',
        "{{HERO_PRELOAD}}": '<link rel="preload" as="image" href="/assets/images/hero-goa-web-design-studio-1376.webp" imagesrcset="/assets/images/hero-goa-web-design-studio-720.webp 720w, /assets/images/hero-goa-web-design-studio-1376.webp 1376w" imagesizes="(max-width: 767px) calc(100vw - 28px), 680px" fetchpriority="high">' if page.hero_image else "",
        "{{CSS_FILE}}": css_file,
        "{{JS_FILE}}": js_file,
        "{{SCHEMA}}": schema_for(page),
        "{{BREADCRUMBS}}": breadcrumbs_for(page),
        "{{CONTENT}}": fragment.strip(),
    }
    rendered = template
    for marker, value in replacements.items():
        rendered = rendered.replace(marker, value)
    unresolved = re.findall(r"\{\{[A-Z_]+\}\}", rendered)
    if unresolved:
        raise ValueError(f"Unresolved template markers in {page.route}: {unresolved}")
    return rendered + "\n"


def output_path_for(page: Page) -> Path:
    if page.route == "/":
        return BUILD_DIR / "index.html"
    if page.route.endswith(".html"):
        return BUILD_DIR / page.route.lstrip("/")
    return BUILD_DIR / page.route.strip("/") / "index.html"


def write_site_files() -> None:
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n"
    indexable_urls = [page.url for page in PAGES if page.indexable]
    sitemap_items = "".join(f"  <url><loc>{html.escape(url)}</loc></url>\n" for url in indexable_urls)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_items}</urlset>\n'
    htaccess = r"""Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{HTTPS} !=on [OR]
  RewriteCond %{HTTP_HOST} !^webdesigncompanygoa\.in$ [NC]
  RewriteRule ^ https://webdesigncompanygoa.in%{REQUEST_URI} [R=301,L,NE]
</IfModule>

<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set Strict-Transport-Security "max-age=31536000"
</IfModule>

<IfModule mod_mime.c>
  AddType image/webp .webp
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 30 days"
  ExpiresByType image/webp "access plus 30 days"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
</IfModule>

<IfModule mod_headers.c>
  <FilesMatch "^site\.[a-f0-9]{10}\.(css|js)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>
"""
    (BUILD_DIR / "robots.txt").write_text(robots, encoding="utf-8", newline="\n")
    (BUILD_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    (BUILD_DIR / ".htaccess").write_text(htaccess, encoding="utf-8", newline="\n")


def resolve_internal_href(href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:")):
        return None
    route = parsed.path
    if not route or route.startswith("#"):
        return None
    if route == "/":
        return BUILD_DIR / "index.html"
    if route.endswith("/"):
        return BUILD_DIR / route.strip("/") / "index.html"
    return BUILD_DIR / route.lstrip("/")


def resolve_local_asset(value: str) -> Path | None:
    """Resolve same-origin static assets and ignore genuinely external URLs."""
    parsed = urlparse(value)
    if parsed.netloc and parsed.netloc != "webdesigncompanygoa.in":
        return None
    if parsed.scheme and parsed.scheme != "https":
        return None
    route = parsed.path
    if not route.startswith("/assets/"):
        return None
    return BUILD_DIR / route.lstrip("/")


def inspect_schemas(payloads: list[str]) -> tuple[set[str], set[tuple[str, str]], list[str]]:
    """Return schema types, FAQ pairs and JSON errors from rendered payloads."""
    schema_types: set[str] = set()
    faq_pairs: set[tuple[str, str]] = set()
    errors: list[str] = []
    for payload in payloads:
        try:
            parsed: object = json.loads(payload)
        except json.JSONDecodeError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(parsed, dict):
            errors.append("JSON-LD root must be an object")
            continue
        graph = parsed.get("@graph")
        if not isinstance(graph, list):
            errors.append("JSON-LD must contain an @graph list")
            continue
        for node in graph:
            if not isinstance(node, dict):
                continue
            node_type = node.get("@type")
            if isinstance(node_type, str):
                schema_types.add(node_type)
            if node_type != "FAQPage":
                continue
            entities = node.get("mainEntity")
            if not isinstance(entities, list):
                continue
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                question = entity.get("name")
                accepted_answer = entity.get("acceptedAnswer")
                if not isinstance(question, str) or not isinstance(accepted_answer, dict):
                    continue
                answer = accepted_answer.get("text")
                if isinstance(answer, str):
                    faq_pairs.add((question, answer))
    return schema_types, faq_pairs, errors


def expected_output_manifest(*, css_file: str, js_file: str) -> set[Path]:
    """Return the complete set of regular files allowed in a staged artifact."""
    expected = {
        Path("robots.txt"),
        Path("sitemap.xml"),
        Path(".htaccess"),
        Path("assets") / "css" / css_file,
        Path("assets") / "js" / js_file,
    }
    expected.update(output_path_for(page).relative_to(BUILD_DIR) for page in PAGES)
    expected.update(Path("assets") / "images" / name for name in IMAGE_FILES)
    return expected


def audit_site(*, css_file: str, js_file: str) -> None:
    errors: list[str] = []
    expected_files = expected_output_manifest(css_file=css_file, js_file=js_file)
    actual_files: set[Path] = set()
    for path in BUILD_DIR.rglob("*"):
        relative = path.relative_to(BUILD_DIR)
        if path.is_symlink():
            errors.append(f"Unexpected symbolic link: {relative}")
        elif path.is_file():
            actual_files.add(relative)
    missing_files = sorted(expected_files - actual_files)
    unexpected_files = sorted(actual_files - expected_files)
    if missing_files:
        errors.append(f"Missing output files: {[str(path) for path in missing_files]}")
    if unexpected_files:
        errors.append(f"Unexpected output files: {[str(path) for path in unexpected_files]}")
    for name, expected_dimensions in IMAGE_DIMENSIONS.items():
        image_path = BUILD_DIR / "assets" / "images" / name
        if image_path.is_file():
            try:
                validate_image(image_path, expected=expected_dimensions)
            except ValueError as exc:
                errors.append(str(exc))
    seen_titles: set[str] = set()
    seen_descriptions: set[str] = set()
    html_files = sorted(BUILD_DIR.rglob("*.html"))
    if len(html_files) != len(PAGES):
        errors.append(f"Expected {len(PAGES)} HTML pages, found {len(html_files)}")
    page_by_path = {output_path_for(page): page for page in PAGES}
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        parser = AuditParser()
        parser.feed(text)
        page = page_by_path.get(path)
        relative = path.relative_to(BUILD_DIR)
        if page is None:
            errors.append(f"Unexpected page: {relative}")
            continue
        if parser.lang != "en-IN":
            errors.append(f"{relative}: lang must be en-IN")
        if parser.h1_count != 1:
            errors.append(f"{relative}: expected exactly one H1, found {parser.h1_count}")
        if not parser.title or not parser.description:
            errors.append(f"{relative}: missing title or description")
        expected_name_meta = {
            "description": page.description,
            "viewport": "width=device-width, initial-scale=1",
            "color-scheme": "light",
            "theme-color": "#f4f7f5",
            "twitter:card": "summary_large_image",
            "twitter:title": page.title,
            "twitter:description": page.description,
            "twitter:image": f"{BASE_URL}/assets/images/social-preview.jpg",
            "twitter:image:alt": "Illustration of a website design workspace in Goa",
        }
        expected_property_meta = {
            "og:type": "website",
            "og:locale": "en_IN",
            "og:site_name": "Web Design Company Goa",
            "og:title": page.title,
            "og:description": page.description,
            "og:url": page.url,
            "og:image": f"{BASE_URL}/assets/images/social-preview.jpg",
            "og:image:width": str(IMAGE_WIDTH),
            "og:image:height": str(IMAGE_HEIGHT),
            "og:image:alt": "Illustration of a website design workspace in Goa",
        }
        for name, expected in expected_name_meta.items():
            if parser.meta_by_name.get(name) != expected:
                errors.append(f"{relative}: missing or incorrect {name} metadata")
        for property_name, expected in expected_property_meta.items():
            if parser.meta_by_property.get(property_name) != expected:
                errors.append(f"{relative}: missing or incorrect {property_name} metadata")
        expected_stylesheet = f"/assets/css/{css_file}"
        stylesheets = [
            link.get("href", "")
            for link in parser.links
            if "stylesheet" in link.get("rel", "").split()
        ]
        if stylesheets != [expected_stylesheet]:
            errors.append(f"{relative}: expected stylesheet {expected_stylesheet}, found {stylesheets}")
        expected_script = f"/assets/js/{js_file}"
        script_sources = [script.get("src", "") for script in parser.scripts if script.get("src")]
        if script_sources != [expected_script]:
            errors.append(f"{relative}: expected script {expected_script}, found {script_sources}")
        for asset_url in (*stylesheets, *script_sources):
            target = resolve_local_asset(asset_url)
            if target is None or not target.is_file():
                errors.append(f"{relative}: unresolved stylesheet or script asset {asset_url}")
        if page.indexable:
            if parser.canonical != page.url:
                errors.append(f"{relative}: incorrect canonical {parser.canonical!r}")
            if not 45 <= len(parser.title) <= 65:
                errors.append(f"{relative}: title length {len(parser.title)} is outside 45-65")
            if not 130 <= len(parser.description) <= 170:
                errors.append(f"{relative}: description length {len(parser.description)} is outside 130-170")
            if parser.title in seen_titles or parser.description in seen_descriptions:
                errors.append(f"{relative}: duplicate title or description")
            seen_titles.add(parser.title)
            seen_descriptions.add(parser.description)
        elif "noindex" not in parser.robots:
            errors.append(f"{relative}: non-indexable page is missing noindex")
        visible = " ".join(parser.visible_text)
        schema_types, schema_faqs, schema_errors = inspect_schemas(parser.json_ld)
        for schema_error in schema_errors:
            errors.append(f"{relative}: invalid JSON-LD: {schema_error}")
        required_schema_types = {page.schema_type} if page.indexable else set()
        if page.route == "/":
            required_schema_types.add("WebSite")
        elif page.indexable:
            required_schema_types.add("BreadcrumbList")
        if page.service_name:
            required_schema_types.add("Service")
        if page.faqs:
            required_schema_types.add("FAQPage")
        if not required_schema_types.issubset(schema_types):
            missing_types = sorted(required_schema_types - schema_types)
            errors.append(f"{relative}: missing schema types {missing_types}")
        if "LocalBusiness" in schema_types:
            errors.append(f"{relative}: LocalBusiness schema is not permitted")
        expected_faqs = {(faq.question, faq.answer) for faq in page.faqs}
        if schema_faqs != expected_faqs:
            errors.append(f"{relative}: FAQ schema does not match page data")
        for question, answer in schema_faqs:
            if question not in visible or answer not in visible:
                errors.append(f"{relative}: FAQ schema is not matched by visible content")
        if "—" in visible or "–" in visible:
            errors.append(f"{relative}: visible copy contains a prohibited dash character")
        if re.search(r"\b(?:lorem|todo|placeholder)\b", visible, re.IGNORECASE):
            errors.append(f"{relative}: visible copy contains placeholder language")
        for image in parser.images:
            if not image.get("src") or not image.get("alt") or not image.get("width") or not image.get("height"):
                errors.append(f"{relative}: image is missing src, alt, width or height")
                continue
            if image.get("width") != "1376" or image.get("height") != "768":
                errors.append(f"{relative}: image dimensions must preserve the 1376x768 source ratio")
            srcset = image.get("srcset", "")
            if " 720w" not in srcset or " 1376w" not in srcset:
                errors.append(f"{relative}: image is missing responsive 720w and 1376w candidates")
            image_urls = [image["src"]]
            image_urls.extend(
                candidate.strip().split()[0]
                for candidate in srcset.split(",")
                if candidate.strip()
            )
            for image_url in image_urls:
                target = resolve_local_asset(image_url)
                if target is None or not target.is_file():
                    errors.append(f"{relative}: unresolved image asset {image_url}")
        metadata_images = (
            parser.meta_by_name.get("twitter:image", ""),
            parser.meta_by_property.get("og:image", ""),
        )
        for image_url in metadata_images:
            target = resolve_local_asset(image_url)
            if target is None or not target.is_file():
                errors.append(f"{relative}: unresolved social image {image_url}")
        if page.hero_image:
            preload_links = [link for link in parser.links if link.get("rel") == "preload" and link.get("as") == "image"]
            if len(preload_links) != 1:
                errors.append(f"{relative}: expected one responsive hero preload")
            else:
                preload = preload_links[0]
                preload_urls = [preload.get("href", "")]
                preload_urls.extend(
                    candidate.strip().split()[0]
                    for candidate in preload.get("imagesrcset", "").split(",")
                    if candidate.strip()
                )
                for preload_url in preload_urls:
                    target = resolve_local_asset(preload_url)
                    if target is None or not target.is_file():
                        errors.append(f"{relative}: unresolved preloaded image {preload_url}")
        for anchor in parser.anchors:
            if anchor.get("target") == "_blank" and "noopener" not in anchor.get("rel", "").split():
                errors.append(f"{relative}: target=_blank link is missing rel=noopener")
        for href in parser.hrefs:
            if not href:
                errors.append(f"{relative}: empty href")
                continue
            target = resolve_internal_href(href)
            if target is not None and not target.exists():
                errors.append(f"{relative}: unresolved internal link {href}")
    forbidden = re.compile(r"(?:AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{16,}|BEGIN [A-Z ]*PRIVATE KEY)")
    for path in BUILD_DIR.rglob("*"):
        is_text_asset = path.is_file() and (
            path.name == ".htaccess" or path.suffix in {".html", ".css", ".js", ".txt", ".xml"}
        )
        if is_text_asset and forbidden.search(path.read_text(encoding="utf-8")):
            errors.append(f"{path.relative_to(BUILD_DIR)}: credential-like string found")
    if errors:
        raise ValueError("Site audit failed:\n- " + "\n- ".join(errors))
    print(f"Built and audited {len(html_files)} HTML pages with {len(seen_titles)} indexable canonicals.")


def build() -> None:
    recover_interrupted_install()
    prepare_build_dir()
    css_file, js_file = copy_assets()
    template = (SRC / "templates" / "base.html").read_text(encoding="utf-8")
    for page in PAGES:
        target = output_path_for(page)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(page, template=template, css_file=css_file, js_file=js_file), encoding="utf-8", newline="\n")
    write_site_files()
    audit_site(css_file=css_file, js_file=js_file)
    install_build()


if __name__ == "__main__":
    build()
