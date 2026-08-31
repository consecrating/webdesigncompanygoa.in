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
REVIEW_DIR: Final[Path] = ROOT / "review-preview"
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
FONT_FILES: Final[tuple[str, ...]] = (
    "plus-jakarta-sans-latin-variable.woff2",
    "roboto-latin-variable.woff2",
    "OFL-plus-jakarta-sans.txt",
    "OFL-roboto.txt",
)
FONT_WOFF2_FILES: Final[tuple[str, ...]] = tuple(
    name for name in FONT_FILES if name.endswith(".woff2")
)
FAVICON_FILES: Final[tuple[str, ...]] = (
    "favicon.ico",
    "favicon.svg",
    "apple-touch-icon.png",
)
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
    article_date: str | None = None
    article_image: str | None = None
    content_html: str | None = None
    matrix: bool = False

    @property
    def url(self) -> str:
        return f"{BASE_URL}{self.route}"


_CORE_PAGES: Final[tuple[Page, ...]] = (
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
        route="/website-redesign-goa/",
        fragment="website-redesign-goa.html",
        title="Website Redesign Services in Goa | Web Design by Sanctify",
        description="Plan a website redesign for a business serving Goa, improving structure, content, responsive design and speed without discarding pages that already work.",
        label="Website redesign in Goa",
        schema_type="WebPage",
        service_name="Website redesign",
        faqs=(
            Faq("Will a redesign lose my existing pages?", "A redesign begins with an audit so pages that already work keep their address and intent, and redirects are planned when any address must change."),
            Faq("Can you redesign only part of the website?", "Yes. A focused redesign can improve structure, key templates or specific journeys when a full rebuild is not required by the review."),
            Faq("Do you promise better rankings after a redesign?", "No ranking or traffic outcome is promised. The work aims for a clearer, faster and more usable website with a careful migration plan."),
        ),
    ),
    Page(
        route="/website-maintenance-goa/",
        fragment="website-maintenance-goa.html",
        title="Website Maintenance Services in Goa | by Sanctify",
        description="Understand website maintenance for businesses serving Goa, covering updates, backups, security checks, small content edits and dependable ongoing support.",
        label="Website maintenance in Goa",
        schema_type="WebPage",
        service_name="Website maintenance",
        faqs=(
            Faq("What does website maintenance include?", "Maintenance can include software updates, regular backups, security checks, small content edits and routine health checks for links, forms and speed."),
            Faq("Do you offer a fixed support guarantee?", "No fixed uptime or response guarantee is stated here. Support hours and response expectations are agreed against real needs before a plan is confirmed."),
            Faq("Can you maintain a website you did not build?", "Yes, after a review of the current platform, hosting access and code, so the maintenance scope and any risks are understood before work begins."),
        ),
    ),
    Page(
        route="/wordpress-website-design-goa/",
        fragment="wordpress-website-design-goa.html",
        title="WordPress Website Design Company in Goa | Sanctify",
        description="Explore WordPress website design and development for businesses serving Goa, with editable content, responsive layouts and a maintainable long-term setup.",
        label="WordPress website design in Goa",
        schema_type="WebPage",
        service_name="WordPress website design",
        faqs=(
            Faq("Is WordPress always the right platform?", "No. WordPress suits many content-led sites, but the platform is chosen after discovery, based on requirements, editing needs, hosting and the long-term maintenance plan."),
            Faq("Can you build an online store on WordPress?", "Yes, WooCommerce can support selling once catalogue, checkout, payment and operational needs are confirmed for feasibility during discovery."),
            Faq("Will the website be easy to edit?", "The content model is structured around how the team manages pages, so routine text and image changes can be made without a developer."),
        ),
    ),
    Page(
        route="/website-design-cost-goa/",
        fragment="website-design-cost-goa.html",
        title="Website Design Cost in Goa | Scope and Pricing Factors",
        description="Understand what shapes website design cost in Goa, including scope, pages, content, functionality and maintenance, before you request a tailored quote.",
        label="Website design cost in Goa",
        schema_type="WebPage",
        faqs=(
            Faq("How much does a website cost in Goa?", "Cost depends on scope, so there is no single price. Page count, content readiness, features, design depth and maintenance all shape a tailored quote."),
            Faq("Why is there no price list on this page?", "A public price for every project would mislead, because two sites with the same page count can involve very different work. Ranges are shared against a real brief."),
            Faq("How do I get an accurate quote?", "Prepare the business goal, approximate page count, required features and content owner, then continue to the enquiry route to discuss a tailored quote."),
        ),
    ),
    Page(
        route="/ui-ux-design-goa/",
        fragment="ui-ux-design-goa.html",
        title="UI UX Design Services in Goa | Web Design by Sanctify",
        description="Plan UI and UX design for websites serving Goa, from user research and structure to accessible interface design that helps visitors make clear decisions.",
        label="UI UX design in Goa",
        schema_type="WebPage",
        service_name="UI UX design",
        faqs=(
            Faq("What is the difference between UI and UX?", "UX shapes structure, journeys and how a site helps a visitor complete a task, while UI is the visual interface layer of type, colour, spacing and components."),
            Faq("Do you design before development starts?", "Yes. Research, structure and interface design are planned with implementation in mind so approved layouts translate into responsive front-end components."),
            Faq("Is accessibility part of the design?", "Contrast, focus states, labels and readable type are treated as design decisions rather than extras added at the end of the project."),
        ),
    ),
    Page(
        route="/website-speed-optimization-goa/",
        fragment="website-speed-optimization-goa.html",
        title="Website Speed Optimization in Goa | Web Performance",
        description="Improve website speed for businesses serving Goa, focusing on Core Web Vitals, responsive images, code and hosting factors that shape real world performance.",
        label="Website speed optimization in Goa",
        schema_type="WebPage",
        service_name="Website speed optimization",
        faqs=(
            Faq("What usually makes a website slow?", "Large images, unused code, too many requests and slow hosting are common causes, but measurement is needed because each site slows down for different reasons."),
            Faq("Can you promise a specific speed score?", "No fixed score is promised in advance. Results depend on the current build, hosting and content, so the work reports measured changes on the same tests."),
            Faq("Do I need a full rebuild for better speed?", "Not always. Many gains come from images, caching and code cleanup, and a rebuild is only suggested when the current foundation truly limits performance."),
        ),
    ),
    Page(
        route="/landing-page-design-goa/",
        fragment="landing-page-design-goa.html",
        title="Landing Page Design Services in Goa | by Sanctify",
        description="Plan focused landing pages for businesses serving Goa, built around one clear action, honest messaging and responsive design for campaign and ad traffic.",
        label="Landing page design in Goa",
        schema_type="WebPage",
        service_name="Landing page design",
        faqs=(
            Faq("How is a landing page different from a homepage?", "A landing page focuses one audience on a single action for a campaign, while a homepage introduces the whole business and links to many sections."),
            Faq("Do you guarantee a conversion rate?", "No conversion rate or result is promised in advance. The aim is a clear, fast and honest page that gives a campaign a fair chance to work."),
            Faq("Can a landing page use real proof only?", "Yes. Only honest, verifiable trust signals are used, because invented claims or numbers waste ad spend and quickly damage visitor trust."),
        ),
    ),
    Page(
        route="/industries/hotel-website-design-goa/",
        fragment="industries/hotel-website-design-goa.html",
        title="Hotel Website Design in Goa | Direct Booking Focus",
        description="Hotel website design for properties in Goa, built around direct bookings, fast mobile pages and clear room and offer content that reduces dependence on OTAs.",
        label="Hotel website design in Goa",
        schema_type="WebPage",
        service_name="Hotel website design",
        faqs=(
            Faq("What makes a good hotel website in Goa?", "A good hotel website is fast on mobile, shows rooms, rates and offers clearly, answers common questions, and keeps the path to book or enquire visible on every page."),
            Faq("Can you connect a booking engine?", "A booking engine or enquiry flow can be planned once your provider, room types and payment needs are confirmed, so the integration fits how you actually take bookings."),
        ),
    ),
    Page(
        route="/industries/resort-website-design-goa/",
        fragment="industries/resort-website-design-goa.html",
        title="Resort Website Design in Goa | Booking and Experience",
        description="Resort website design in Goa for larger properties, covering booking engine integration, multilingual needs, and rooms, dining, spa and activities in one clear place.",
        label="Resort website design in Goa",
        schema_type="WebPage",
        service_name="Resort website design",
        faqs=(
            Faq("How is a resort website different from a hotel website?", "A resort website usually covers more experiences, such as rooms, dining, spa and activities, often for international guests, so structure, multilingual needs and the booking journey need more planning."),
            Faq("Do you support multiple languages?", "Multilingual content can be planned during discovery, based on your main guest markets, so the most valuable languages are prioritised rather than assumed."),
        ),
    ),
    Page(
        route="/industries/restaurant-website-design-goa/",
        fragment="industries/restaurant-website-design-goa.html",
        title="Restaurant Website Design in Goa | Menus and Orders",
        description="Restaurant, cafe and beach shack website design in Goa, focused on fast mobile menus, reservations, WhatsApp ordering, directions and local discovery that drive visits.",
        label="Restaurant website design in Goa",
        schema_type="WebPage",
        service_name="Restaurant website design",
        faqs=(
            Faq("Can customers order or reserve online?", "Yes, depending on how you operate. A simple reservation request or a WhatsApp ordering flow can be built, kept to the fewest steps so more visitors complete it."),
            Faq("Will the menu be easy to update?", "The menu can be structured so routine changes to items and prices are simple to make, without needing a developer for every small update."),
        ),
    ),
    Page(
        route="/industries/travel-and-tours-website-design-goa/",
        fragment="industries/travel-and-tours-website-design-goa.html",
        title="Travel and Tour Website Design in Goa | Bookings",
        description="Travel agency and tour operator website design in Goa, covering packages, availability, itineraries, payments and lead capture for domestic and international travellers.",
        label="Travel and tour website design in Goa",
        schema_type="WebPage",
        service_name="Travel and tour website design",
        faqs=(
            Faq("What does a travel or tour website need?", "It usually needs clear packages or itineraries, availability or enquiry flows, payment or deposit options where relevant, and strong lead capture for domestic and international travellers."),
            Faq("Can you handle seasonal campaigns?", "Seasonal offers and campaign landing pages can be planned so you can promote peak-season packages without rebuilding the site each time."),
        ),
    ),
    Page(
        route="/industries/real-estate-website-design-goa/",
        fragment="industries/real-estate-website-design-goa.html",
        title="Real Estate Website Design in Goa | Listings, Leads",
        description="Real estate and property website design in Goa, covering listings, search filters, maps, project landing pages, WhatsApp enquiries and clean lead routing for agents.",
        label="Real estate website design in Goa",
        schema_type="WebPage",
        service_name="Real estate website design",
        faqs=(
            Faq("What features do real estate websites need?", "Common needs are property listings, search filters, maps, project or locality landing pages, WhatsApp enquiries and clean routing of leads to the right person or CRM."),
            Faq("Can listings be updated easily?", "Listings can be structured so properties are added, edited and marked as sold without technical help, keeping the site current as inventory changes."),
        ),
    ),
    Page(
        route="/industries/wedding-website-design-goa/",
        fragment="industries/wedding-website-design-goa.html",
        title="Wedding Website Design in Goa | Planners and Venues",
        description="Wedding planner and destination wedding website design in Goa, built around visual portfolios, package and venue pages, and high-trust enquiry flows for couples.",
        label="Wedding website design in Goa",
        schema_type="WebPage",
        service_name="Wedding website design",
        faqs=(
            Faq("What makes a strong wedding planner website?", "A visual portfolio, clear package and venue information, and a trusted, simple enquiry flow, since couples often decide from photos and confidence before they get in touch."),
            Faq("Can it handle international enquiries?", "Yes. For destination weddings, the site can be planned around clear information and enquiry flows that work well for guests and couples planning from outside Goa."),
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
        route="/404.html",
        fragment="404.html",
        title="Page Not Found | Web Design Company Goa",
        description="The requested page could not be found. Return home or review website development capabilities from Web Design Company Goa by Sanctify.",
        label="Page not found",
        indexable=False,
    ),
)


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    description: str
    label: str
    image_stem: str
    image_alt: str
    excerpt: str
    faqs: tuple[Faq, ...]


POST_DATE_ISO: Final[str] = "2026-08-30"
POSTS_PER_PAGE: Final[int] = 6

POSTS: Final[tuple[Post, ...]] = (
    Post(
        "how-to-choose-web-design-company-goa",
        "How to Choose a Web Design Company in Goa: A Guide",
        "A practical guide to choosing a web design company in Goa, covering scope, process, proof, ownership and the questions that reveal a good long-term fit.",
        "How to choose a web design company in Goa",
        "client-conversation-goa",
        "Indian business owner and a web strategist reviewing a website plan in Goa",
        "The questions and signals that separate a good long-term web design partner from a long feature list.",
        (
            Faq("What should I ask a web design company in Goa?", "Ask about their process, who writes content, what you own after launch, how they handle responsive design and speed, and how support works once the site is live."),
            Faq("Do I need a local Goa web designer?", "Local context helps, but proof, process and communication matter more than location. Many Goa businesses are served well by teams that understand the market and respond clearly."),
        ),
    ),
    Post(
        "signs-your-website-needs-redesign-goa",
        "Signs Your Business Website in Goa Needs a Redesign",
        "Learn the clear signs a Goa business website needs a redesign, from poor mobile use and slow speed to weak structure, and how to plan the fix without losing value.",
        "Signs your website needs a redesign",
        "goa-local-business-owner",
        "Indian business owner reviewing a website that needs a redesign in Goa",
        "Practical signs your website is working against you, and how to plan a redesign that keeps what already works.",
        (
            Faq("How do I know if my website needs a redesign?", "Common signs are a site that is hard to use on phones, slow loading, unclear structure, outdated content and a design that no longer matches how the business works."),
            Faq("Will a redesign hurt my search rankings?", "A careful redesign protects valuable pages and uses redirects when addresses change, so it aims to preserve search value rather than lose it."),
        ),
    ),
    Post(
        "website-design-cost-factors-goa",
        "What Really Affects Website Design Cost in Goa",
        "Understand the real factors behind website design cost in Goa, including pages, content, features, design depth and maintenance, so you can brief and budget clearly.",
        "What affects website design cost in Goa",
        "final-cta-goa-creative-team",
        "Indian web design team planning a website project in a Goa studio",
        "Why website quotes vary so much, and the scope decisions that move the number up or down.",
        (
            Faq("Why can two Goa websites cost very different amounts?", "Because cost follows scope. Page count, content, features like booking or payments, design depth and ongoing support all change the work involved."),
            Faq("How do I keep website cost predictable?", "Prepare a clear brief, decide what content you will provide, and separate must-have features from later phases so the scope stays defined."),
        ),
    ),
    Post(
        "website-or-ecommerce-store-goa",
        "Website or Ecommerce Store: What a Goa Business Needs",
        "Decide between a standard website and an ecommerce store for your Goa business by matching goals, catalogue, checkout and operations to the right build and platform.",
        "Website or ecommerce store for a Goa business",
        "portfolio-device-showcase",
        "Website and store layouts shown across laptop, tablet and phone",
        "How to decide between a standard website and an online store, based on how your business actually earns.",
        (
            Faq("Do I need an ecommerce store or a normal website?", "If selling online is central now, an ecommerce build fits. If you mainly explain services and collect enquiries, a standard website with a clear contact path may be enough."),
            Faq("Can a website add ecommerce later?", "Yes, if it is planned for. Discussing likely future selling during discovery makes adding a store later much easier and cheaper."),
        ),
    ),
    Post(
        "goa-hotel-website-direct-bookings",
        "How Goa Hotels Can Win More Direct Website Bookings",
        "How Goa hotels and resorts can reduce OTA dependence and earn more direct bookings through faster, clearer, mobile-first websites built around the booking decision.",
        "How Goa hotels win direct bookings",
        "hero-goa-web-design-studio",
        "Designer reviewing a Goa hotel website layout on a large screen",
        "Practical ways a hotel website can reduce commission costs by earning more direct bookings.",
        (
            Faq("How can a Goa hotel get more direct bookings?", "Make the site fast and mobile-first, show rooms and offers clearly, reduce steps to enquire or book, and keep booking information easy to find on every page."),
            Faq("Should a hotel website replace OTAs?", "Not replace, but balance. A strong direct-booking site reduces dependence on OTAs and their commissions while OTAs still add reach."),
        ),
    ),
    Post(
        "goa-restaurant-website-guide",
        "Restaurant Websites in Goa: Menus, Bookings and Orders",
        "A guide to restaurant, cafe and beach shack websites in Goa, covering mobile menus, reservations, WhatsApp ordering, directions and reviews that drive real visits.",
        "Restaurant websites in Goa",
        "client-conversation-goa",
        "Restaurant owner in Goa reviewing a mobile website menu on a tablet",
        "What a restaurant, cafe or beach shack website in Goa needs to turn a hungry browser into a visit.",
        (
            Faq("What should a Goa restaurant website include?", "A fast mobile menu, location and directions, opening hours, a way to reserve or message on WhatsApp, and clear photos, all easy to reach on a phone."),
            Faq("Is a website worth it if I use social media?", "Yes. Social media helps discovery, but a website gives you a stable, searchable home for your menu, hours and bookings that you fully control."),
        ),
    ),
    Post(
        "wordpress-or-custom-website-goa",
        "WordPress or Custom Build for Your Goa Website?",
        "Compare WordPress and custom development for a Goa business website, weighing editing, features, speed, security and maintenance before you commit to a platform.",
        "WordPress or custom build for your Goa website",
        "services-responsive-design-workspace",
        "Designers comparing WordPress and custom website layouts in a Goa studio",
        "How to choose between WordPress and a custom build without following hype in either direction.",
        (
            Faq("Is WordPress good for a Goa business website?", "WordPress suits many content-led sites because it is editable and flexible, but the right choice depends on your features, editing needs, speed goals and maintenance plan."),
            Faq("When is a custom build better than WordPress?", "Custom development can be better when requirements are specific, performance is critical, or a standard platform would need heavy workarounds to fit the business."),
        ),
    ),
    Post(
        "website-speed-core-web-vitals-goa",
        "Website Speed and Core Web Vitals for Goa Businesses",
        "Why website speed and Core Web Vitals matter for Goa businesses, what slows sites down, and how measured performance work keeps visitors from leaving before they act.",
        "Website speed and Core Web Vitals in Goa",
        "portfolio-device-showcase",
        "A website measured for speed across desktop, tablet and phone",
        "Why speed decides whether visitors stay, and how measured performance work actually helps.",
        (
            Faq("Why does website speed matter for a Goa business?", "Many visitors browse on mobile data. A slow site loses people before they read anything, so speed directly affects enquiries and sales."),
            Faq("What are Core Web Vitals?", "They are Google metrics for loading, interactivity and visual stability that reflect how fast and steady a page feels to a real visitor."),
        ),
    ),
    Post(
        "mobile-first-accessible-websites-goa",
        "Mobile-First, Accessible Websites for Goa Businesses",
        "Why mobile-first and accessible design matter for Goa businesses, and how clear structure, readable type and fast pages help more visitors understand and choose you.",
        "Mobile-first, accessible websites in Goa",
        "process-indian-design-team",
        "Indian design team planning a mobile-first, accessible website in Goa",
        "Why designing for phones and accessibility first produces a clearer site for everyone.",
        (
            Faq("What does mobile-first design mean?", "It means designing for small screens first, so the most important content and actions work well on phones, then expanding the layout for larger screens."),
            Faq("Why does accessibility help my business?", "Accessible sites are easier for everyone to read and use, reach more people, and tend to be clearer and better structured, which also helps search engines."),
        ),
    ),
    Post(
        "what-to-prepare-website-project-goa",
        "What to Prepare Before a Website Project in Goa",
        "A practical checklist of what to gather before starting a website project in Goa, from goals and content to functionality, so your first conversation is productive.",
        "What to prepare before a website project",
        "client-conversation-goa",
        "Business owner and strategist preparing a website brief in Goa",
        "The few decisions and assets that make a website project faster, cheaper and calmer.",
        (
            Faq("What should I prepare before a website project?", "Note your main goal, the action visitors should take, the pages and content you have, any features you need, and who will approve decisions."),
            Faq("Do I need all the content ready first?", "Not everything, but the clearer your content and priorities are at the start, the faster and smoother the project runs."),
        ),
    ),
    Post(
        "how-long-website-take-goa",
        "How Long Does It Take to Build a Website in Goa?",
        "What actually drives website timelines in Goa, from content readiness to features and reviews, and how to plan a realistic schedule without cutting quality.",
        "How long a website takes in Goa",
        "process-indian-design-team",
        "Web team planning a project schedule in a Goa studio",
        "What really sets a website timeline, and how to plan a realistic schedule.",
        (
            Faq("How long does a website take in Goa?", "It depends on scope and content. A small site can be quick, while larger sites with features and content creation take longer; a realistic schedule is agreed in discovery."),
            Faq("What slows a website project down most?", "Waiting on content and feedback is the most common delay. Ready content and prompt reviews keep the timeline on track."),
        ),
    ),
    Post(
        "website-ownership-domain-hosting-goa",
        "Website Ownership: Domain, Hosting and Content",
        "What every Goa business should own after a website project, including the domain, hosting access, code and content, so you are never locked out of your own site.",
        "Website ownership: domain, hosting, content",
        "services-responsive-design-workspace",
        "Designers reviewing website ownership and handover details in Goa",
        "Make sure you own your domain, hosting, code and content after any project.",
        (
            Faq("What should I own after a website project?", "You should own the domain, hosting access, the website code and all content, handed over so you are never dependent on one provider."),
            Faq("Who should register my domain?", "Register the domain in your own account where possible, so you keep full control even if you change who maintains the site."),
        ),
    ),
    Post(
        "whatsapp-enquiries-goa-website",
        "Turning WhatsApp Chats Into Website Bookings in Goa",
        "How Goa businesses can use WhatsApp on their website to capture enquiries and bookings, with simple flows that reduce steps and keep conversations organised.",
        "Turning WhatsApp chats into bookings",
        "client-conversation-goa",
        "Owner replying to a website WhatsApp enquiry on a phone in Goa",
        "How to use WhatsApp on a Goa website to turn interest into booked conversations.",
        (
            Faq("Should my website use WhatsApp for enquiries?", "For many Goa businesses, yes. A clear WhatsApp option can turn interest into a quick conversation, especially on mobile."),
            Faq("Is WhatsApp enough, or do I need a form?", "Offer both where it helps. WhatsApp suits fast questions; a short form suits detailed enquiries you want recorded."),
        ),
    ),
    Post(
        "website-content-that-converts-goa",
        "Website Content That Converts for Goa Businesses",
        "How to write website content that helps Goa visitors decide and act, focusing on clarity, structure and honest messaging rather than clever words or jargon.",
        "Website content that converts",
        "hero-goa-web-design-studio",
        "Designer reviewing clear website content on a large screen in Goa",
        "Why clear, structured, honest content converts better than clever copy.",
        (
            Faq("What makes website content convert?", "Clear structure, honest messaging, and one obvious next step. Visitors act when they quickly understand what you offer and what to do."),
            Faq("How much content does a page need?", "Enough to answer the visitor's questions and support the decision, without padding. Clarity matters more than length."),
        ),
    ),
    Post(
        "booking-enquiry-flows-goa",
        "Simple Booking and Enquiry Flows for Goa Sites",
        "Why fewer steps mean more enquiries for Goa websites, and how to design booking and contact flows that visitors actually finish on a phone.",
        "Simple booking and enquiry flows",
        "portfolio-device-showcase",
        "Booking and enquiry flow shown across devices for a Goa website",
        "Why removing steps, not adding features, is the fastest way to more enquiries.",
        (
            Faq("How do I get more enquiries from my website?", "Reduce steps. Make the action obvious, ask only for what you need, and ensure the flow works smoothly on a phone."),
            Faq("Should a booking flow be on every page?", "The path to enquire or book should be easy to reach from every page, even if the full form lives on one page."),
        ),
    ),
    Post(
        "multilingual-website-goa",
        "Multilingual Websites for Goa Visitors and Guests",
        "When a Goa business website needs more than English, how to choose priority languages from real guest markets, and how to plan multilingual content properly.",
        "Multilingual websites for Goa visitors",
        "goa-local-business-owner",
        "Business owner reviewing a multilingual website plan in Goa",
        "When a Goa site needs more than English, and how to plan languages properly.",
        (
            Faq("Does my Goa website need multiple languages?", "Only if your real audience needs them. Choose languages based on your actual guest or customer markets, not assumptions."),
            Faq("Can languages be added later?", "Yes, if planned for. Designing with multilingual content in mind makes adding a language later much simpler."),
        ),
    ),
    Post(
        "website-images-photography-goa",
        "Images and Photos for a Fast Goa Business Website",
        "How to use images on a Goa website without slowing it down, covering sizing, formats, lazy loading and honest photography that builds trust with visitors.",
        "Images and photos for a fast website",
        "portfolio-device-showcase",
        "Optimised website images shown across devices for a Goa business",
        "Have great visuals and speed: sizing, formats, lazy loading and honest photos.",
        (
            Faq("Do images slow down my website?", "Large, unoptimised images are a common cause of slow pages. Correct sizing, modern formats and lazy loading keep the site fast."),
            Faq("Do I need professional photos?", "Honest, clear photos help. They do not have to be expensive, but they should represent your business accurately and load quickly."),
        ),
    ),
    Post(
        "domain-name-goa-business",
        "How to Choose a Domain Name for a Goa Business",
        "Practical guidance on picking a domain name for a Goa business, balancing brand, clarity and local relevance, and what to check before you register it.",
        "Choosing a domain name for a Goa business",
        "services-responsive-design-workspace",
        "Designers choosing a domain name for a Goa business",
        "Simple rules for a clear, memorable domain that fits your brand.",
        (
            Faq("How do I choose a domain name?", "Keep it clear, easy to say and spell, and relevant to your brand. Check availability and avoid names that are easily confused."),
            Faq("Should my domain include Goa or my location?", "Only if it fits your brand and audience naturally. A location in the name can help locally but is not essential."),
        ),
    ),
    Post(
        "website-security-basics-goa",
        "Website Security Basics for Goa Business Owners",
        "The security basics every Goa business website should cover, from HTTPS and updates to backups and access control, explained in plain, non-technical language.",
        "Website security basics",
        "process-indian-design-team",
        "Team reviewing website security basics in a Goa studio",
        "The plain-language security basics every business website should cover.",
        (
            Faq("What are the website security basics?", "Use HTTPS, keep software updated, take regular backups, use strong access control, and limit unnecessary plugins or add-ons."),
            Faq("Is a small business website really a target?", "Yes. Many attacks are automated and target any site, so basic security and backups matter regardless of size."),
        ),
    ),
    Post(
        "seasonality-goa-website-planning",
        "Planning a Goa Website Around Season and Monsoon",
        "How Goa's seasonal patterns should shape your website plan, from peak-season campaigns to monsoon content work, so the site keeps earning through the year.",
        "Planning a Goa website around the season",
        "final-cta-goa-creative-team",
        "Creative team planning a seasonal website calendar in Goa",
        "Work with Goa's rhythm: peak-season readiness and monsoon build time.",
        (
            Faq("How does Goa's season affect my website?", "Peak season needs your site fast, current and ready to convert, while the monsoon is a good time for content, updates and planning."),
            Faq("What website work suits the monsoon?", "Content creation, redesign, performance work and planning the next peak season are all well suited to the quieter months."),
        ),
    ),
    Post(
        "redesign-without-losing-rankings-goa",
        "Website Redesign Without Losing Google Rankings",
        "A migration checklist for redesigning a Goa website without losing search value, covering URLs, redirects, content and the checks to run before and after launch.",
        "Redesign without losing rankings",
        "goa-local-business-owner",
        "Owner reviewing a redesign migration plan for a Goa website",
        "Avoid the common mistakes that cost rankings when a site is redesigned.",
        (
            Faq("Will a redesign hurt my Google rankings?", "It can if URLs and content change without care. A migration plan with redirects and preserved content aims to protect search value."),
            Faq("What protects rankings during a redesign?", "Keep valuable pages, map old URLs to new ones with redirects, preserve useful content, and check indexing before and after launch."),
        ),
    ),
)


def _blog_index_meta(page_number: int) -> tuple[str, str, str, str]:
    """Return (route, title, description, label) for a blog index page."""
    if page_number == 1:
        return (
            "/blog/",
            "Web Design Insights and Guides for Goa Businesses",
            "Practical web design, development and ecommerce guides for businesses serving Goa, covering planning, redesign, platforms, speed and industry-specific websites.",
            "Blog",
        )
    return (
        f"/blog/page/{page_number}/",
        f"Web Design Guides for Goa Businesses | Page {page_number}",
        f"More practical web design and development guides for businesses serving Goa, page {page_number}, covering platforms, speed, content, ownership and industry-specific websites.",
        f"Blog page {page_number}",
    )


def _post_card_html(post: Post) -> str:
    href = f"/blog/{post.slug}/"
    stem = post.image_stem
    srcset = f"/assets/images/{stem}-720.webp 720w, /assets/images/{stem}-1376.webp 1376w"
    return (
        '<article class="blog-card">'
        f'<a class="blog-card__media" href="{href}" tabindex="-1" aria-hidden="true">'
        f'<img src="/assets/images/{stem}-1376.webp" srcset="{srcset}" '
        'sizes="(max-width: 767px) calc(100vw - 28px), (max-width: 1199px) 45vw, 380px" '
        f'alt="{html.escape(post.image_alt, quote=True)}" width="1376" height="768" loading="lazy" decoding="async">'
        '</a>'
        '<div class="blog-card__body">'
        '<p class="blog-card__tag">Web design guide</p>'
        f'<h3><a href="{href}">{html.escape(post.title)}</a></h3>'
        f'<p>{html.escape(post.excerpt)}</p>'
        f'<a class="text-link" href="{href}">Read the guide <span class="arrow-icon" aria-hidden="true"></span></a>'
        '</div>'
        '</article>'
    )


def _pagination_html(current: int, total: int) -> str:
    if total <= 1:
        return ""
    parts: list[str] = ['<nav class="pagination" aria-label="Blog pages">']
    if current > 1:
        prev_route = "/blog/" if current - 1 == 1 else f"/blog/page/{current - 1}/"
        parts.append(f'<a class="pagination__step" href="{prev_route}" rel="prev">Previous</a>')
    for number in range(1, total + 1):
        route = "/blog/" if number == 1 else f"/blog/page/{number}/"
        if number == current:
            parts.append(f'<span aria-current="page">{number}</span>')
        else:
            parts.append(f'<a href="{route}">{number}</a>')
    if current < total:
        next_route = f"/blog/page/{current + 1}/"
        parts.append(f'<a class="pagination__step" href="{next_route}" rel="next">Next</a>')
    parts.append("</nav>")
    return "".join(parts)


def _blog_index_content(page_number: int, total_pages: int, heading: str) -> str:
    start = (page_number - 1) * POSTS_PER_PAGE
    page_posts = POSTS[start : start + POSTS_PER_PAGE]
    cards = "".join(_post_card_html(post) for post in page_posts)
    intro = (
        "Clear, practical guides on planning, building and improving websites for businesses "
        "that serve customers across Goa. No filler, just useful decisions."
    )
    return (
        '<section class="section blog-index" data-reveal>'
        '<div class="container">'
        '<div class="section-heading">'
        '<p class="kicker"><span></span>Web design guides</p>'
        f'<h1>{html.escape(heading)}</h1>'
        f'<p class="lede">{html.escape(intro)}</p>'
        '</div>'
        f'<div class="blog-grid">{cards}</div>'
        f'{_pagination_html(page_number, total_pages)}'
        '</div>'
        '</section>'
    )


def _build_blog_pages() -> tuple[Page, ...]:
    total_pages = (len(POSTS) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    pages: list[Page] = []
    for number in range(1, total_pages + 1):
        route, title, description, label = _blog_index_meta(number)
        heading = "Web Design Insights and Guides for Goa Businesses"
        pages.append(
            Page(
                route=route,
                fragment="",
                title=title,
                description=description,
                label=label,
                schema_type="Blog",
                content_html=_blog_index_content(number, total_pages, heading),
            )
        )
    for post in POSTS:
        pages.append(
            Page(
                route=f"/blog/{post.slug}/",
                fragment=f"blog/{post.slug}.html",
                title=post.title,
                description=post.description,
                label=post.label,
                schema_type="BlogPosting",
                faqs=post.faqs,
                article_date=POST_DATE_ISO,
                article_image=post.image_stem,
            )
        )
    return tuple(pages)


@dataclass(frozen=True)
class Area:
    slug: str
    name: str
    kind: str  # "town" or "region"
    blurb: str


MATRIX_AREAS: Final[tuple[Area, ...]] = (
    Area("panaji", "Panaji", "town", "Panaji, the state capital, blends heritage charm with government, hospitality and retail businesses."),
    Area("porvorim", "Porvorim", "town", "Porvorim is a fast-growing residential and business belt just north of Panaji."),
    Area("mapusa", "Mapusa", "town", "Mapusa is North Goa's busy market town and a commercial hub for the northern belt."),
    Area("calangute", "Calangute", "town", "Calangute is one of North Goa's busiest beach and tourism centres."),
    Area("candolim", "Candolim", "town", "Candolim serves a steady flow of hospitality, dining and retail visitors."),
    Area("baga", "Baga", "town", "Baga is a nightlife and beach hotspot with strong hospitality and events demand."),
    Area("anjuna", "Anjuna", "town", "Anjuna is known for its markets, cafes and creative, tourism-led businesses."),
    Area("vagator", "Vagator", "town", "Vagator draws a beach and events crowd through much of the season."),
    Area("morjim", "Morjim", "town", "Morjim serves a quieter coastal and wellness-oriented visitor base."),
    Area("siolim", "Siolim", "town", "Siolim is a growing hospitality and villa belt in North Goa."),
    Area("assagao", "Assagao", "town", "Assagao is a premium hospitality, dining and lifestyle pocket."),
    Area("sinquerim", "Sinquerim", "town", "Sinquerim anchors an upscale beach and resort stretch in North Goa."),
    Area("margao", "Margao", "town", "Margao is South Goa's commercial capital and main business centre."),
    Area("vasco-da-gama", "Vasco da Gama", "town", "Vasco da Gama, near the airport and port, is home to the Sanctify studio in Zuarinagar."),
    Area("colva", "Colva", "town", "Colva is a leading South Goa beach and hospitality destination."),
    Area("benaulim", "Benaulim", "town", "Benaulim serves resorts, villas and hospitality along the south coast."),
    Area("palolem", "Palolem", "town", "Palolem is a popular South Goa beach town with tourism-led businesses."),
    Area("ponda", "Ponda", "town", "Ponda is a central commercial and temple town serving inland Goa."),
    Area("varca", "Varca", "town", "Varca is a resort and villa belt on the south coast."),
    Area("cavelossim", "Cavelossim", "town", "Cavelossim is a premium south-coast resort and hospitality area."),
    Area("north-goa", "North Goa", "region", "North Goa covers the busy coastal belt from Panaji up to the northern beaches."),
    Area("south-goa", "South Goa", "region", "South Goa covers Margao, Vasco and the quieter southern coast."),
)

MATRIX_SERVICES: Final[tuple[tuple[str, str, str], ...]] = (
    ("website-design", "Website Design", "/website-development-goa/"),
    ("website-development", "Website Development", "/website-development-goa/"),
    ("ecommerce-website-development", "Ecommerce Website Development", "/ecommerce-website-development-goa/"),
    ("website-redesign", "Website Redesign", "/website-redesign-goa/"),
    ("website-maintenance", "Website Maintenance", "/website-maintenance-goa/"),
    ("wordpress-website-design", "WordPress Website Design", "/wordpress-website-design-goa/"),
    ("ui-ux-design", "UI UX Design", "/ui-ux-design-goa/"),
    ("website-speed-optimization", "Website Speed Optimization", "/website-speed-optimization-goa/"),
    ("landing-page-design", "Landing Page Design", "/landing-page-design-goa/"),
)

MATRIX_INDUSTRIES: Final[tuple[tuple[str, str, str], ...]] = (
    ("hotel", "Hotel", "/industries/hotel-website-design-goa/"),
    ("resort", "Resort", "/industries/resort-website-design-goa/"),
    ("restaurant", "Restaurant", "/industries/restaurant-website-design-goa/"),
    ("travel-and-tours", "Travel and Tour", "/industries/travel-and-tours-website-design-goa/"),
    ("real-estate", "Real Estate", "/industries/real-estate-website-design-goa/"),
    ("wedding", "Wedding", "/industries/wedding-website-design-goa/"),
    ("cafe-bar", "Cafe and Bar", ""),
    ("spa-wellness", "Spa and Wellness", ""),
    ("fitness-yoga", "Fitness and Yoga", ""),
    ("clinic-healthcare", "Clinic and Healthcare", ""),
    ("retail-boutique", "Retail and Boutique", ""),
    ("professional-services", "Professional Services", ""),
)

_WA_HREF: Final[str] = "https://wa.me/919923352923?text=Hi%2C%20I%20would%20like%20to%20enquire%20about%20a%20website."


def _clamp(text: str, lo: int, hi: int, pad: str) -> str:
    text = " ".join(text.split())
    while len(text) < lo:
        text = " ".join(f"{text}{pad}".split())
    if len(text) > hi:
        cut = text[:hi]
        space = cut.rfind(" ")
        if space >= lo:
            cut = cut[:space]
        text = cut.strip(" ,.|")
        while len(text) < lo:
            text = " ".join(f"{text}{pad}".split())
    return text


def _matrix_image(stem: str, alt: str) -> str:
    return (
        '<figure class="media-frame"><img '
        f'src="/assets/images/{stem}-1376.webp" '
        f'srcset="/assets/images/{stem}-720.webp 720w, /assets/images/{stem}-1376.webp 1376w" '
        'sizes="(max-width: 767px) calc(100vw - 28px), 620px" '
        f'alt="{html.escape(alt)}" width="1376" height="768" loading="lazy" decoding="async"></figure>'
    )


def _matrix_faq_html(faqs: tuple[Faq, ...]) -> str:
    items = "".join(
        f"<details><summary>{html.escape(f.question)}</summary><p>{html.escape(f.answer)}</p></details>"
        for f in faqs
    )
    return f'<div class="faq-list">{items}</div>'


def _rel_button(href: str, label: str, *, secondary: bool = False) -> str:
    cls = "button button--secondary" if secondary else "button"
    return f'<a class="{cls}" href="{href}">{html.escape(label)}</a>'


def _matrix_body(*, kicker: str, h1: str, lede: str, intro_html: str, faqs: tuple[Faq, ...], image_stem: str, image_alt: str, related: str) -> str:
    return (
        '<header class="page-hero"><div class="container">'
        f'<p class="kicker"><span></span>{html.escape(kicker)}</p>'
        f'<h1>{html.escape(h1)}</h1>'
        f'<p class="lede">{html.escape(lede)}</p>'
        '<div class="button-row">'
        f'<a class="button button--whatsapp" href="{_WA_HREF}" target="_blank" rel="noopener">Message on WhatsApp</a>'
        '<a class="button button--secondary" href="/contact/">Start an enquiry</a>'
        '</div></div></header>'
        '<section class="section section--surface" data-reveal><div class="container split">'
        f'<div>{intro_html}</div>{_matrix_image(image_stem, image_alt)}'
        '</div></section>'
        '<section class="section" data-reveal><div class="narrow">'
        '<div class="section-heading"><h2>Common questions</h2></div>'
        f'{_matrix_faq_html(faqs)}'
        f'<div class="button-row">{related}</div>'
        '</div></section>'
    )


def _build_matrix_pages() -> tuple[Page, ...]:
    pages: list[Page] = []
    rotate = 0

    def next_stem() -> str:
        nonlocal rotate
        stem = IMAGE_STEMS[rotate % len(IMAGE_STEMS)]
        rotate += 1
        return stem

    def full_name(area: Area) -> str:
        return f"{area.name}, Goa" if area.kind == "town" else area.name

    area_links = "".join(
        f'<li><a href="/locations/{a.slug}/">Web design in {html.escape(a.name)}</a></li>'
        for a in MATRIX_AREAS
    )
    pages.append(Page(
        route="/locations/", fragment="",
        title=_clamp("Web Design Services Across Goa Locations", 30, 70, " by Sanctify"),
        description=_clamp("Explore web design and development by area across Goa, from Panaji and Mapusa to Margao, Vasco and the North and South Goa coastal belts, all by Sanctify.", 110, 175, " Serving businesses across Goa."),
        label="Goa locations", schema_type="CollectionPage", matrix=True,
        content_html=(
            '<header class="page-hero"><div class="container">'
            '<p class="kicker"><span></span>Areas we serve</p>'
            '<h1>Web Design Across Goa</h1>'
            '<p class="lede">Sanctify serves businesses across Goa from its studio in Vasco-da-Gama. Choose an area to see local web design and development.</p>'
            '</div></header>'
            '<section class="section section--surface" data-reveal><div class="container">'
            '<div class="section-heading"><h2>Goa areas</h2></div>'
            f'<ul class="link-columns">{area_links}</ul>'
            '</div></section>'
        ),
    ))

    industry_links = "".join(
        f'<li><a href="{parent or f"/industries/{islug}-website-design-in-panaji/"}">{html.escape(iname)} website design</a></li>'
        for islug, iname, parent in MATRIX_INDUSTRIES
    )
    pages.append(Page(
        route="/industries/", fragment="",
        title=_clamp("Web Design for Goa Industries and Sectors", 30, 70, " by Sanctify"),
        description=_clamp("Web design and development tailored to Goa industries, from hotels, resorts and restaurants to real estate, weddings, wellness, retail and professional services.", 110, 175, " Built for Goa businesses."),
        label="Industries", schema_type="CollectionPage", matrix=True,
        content_html=(
            '<header class="page-hero"><div class="container">'
            '<p class="kicker"><span></span>Industries we know</p>'
            '<h1>Web Design by Industry in Goa</h1>'
            '<p class="lede">Websites shaped around the way each Goa sector actually earns, from bookings to enquiries to online sales.</p>'
            '</div></header>'
            '<section class="section section--surface" data-reveal><div class="container">'
            '<div class="section-heading"><h2>Goa industries</h2></div>'
            f'<ul class="link-columns">{industry_links}</ul>'
            '</div></section>'
        ),
    ))

    for area in MATRIX_AREAS:
        full = full_name(area)
        svc_links = "".join(
            f'<li><a href="/{sslug}-in-{area.slug}/">{html.escape(sname)} in {html.escape(area.name)}</a></li>'
            for sslug, sname, _ in MATRIX_SERVICES
        )
        ind_links = "".join(
            f'<li><a href="/industries/{islug}-website-design-in-{area.slug}/">{html.escape(iname)} websites in {html.escape(area.name)}</a></li>'
            for islug, iname, _ in MATRIX_INDUSTRIES
        )
        faqs = (
            Faq(f"Do you serve businesses in {area.name}?", f"Yes. Sanctify serves businesses in {full} and across Goa from its studio in Vasco-da-Gama, by phone, WhatsApp and email."),
            Faq(f"What web services are available in {area.name}?", "Website design and development, ecommerce, redesign, maintenance, WordPress, UI and UX, speed optimization and landing pages."),
        )
        intro = (
            f'<h2>Web design for {html.escape(full)}</h2>'
            f'<p class="lede">{html.escape(area.blurb)}</p>'
            f'<p>Sanctify plans clear, fast, responsive websites for businesses in {html.escape(area.name)}, working from its Goa studio and serving the whole state.</p>'
            f'<ul class="link-columns">{svc_links}{ind_links}</ul>'
        )
        pages.append(Page(
            route=f"/locations/{area.slug}/", fragment="",
            title=_clamp(f"Web Design Company in {full}", 30, 70, " by Sanctify"),
            description=_clamp(f"Web design and development for businesses in {full}. {area.blurb} Website, ecommerce and industry services by Sanctify.", 110, 175, " Serving businesses across Goa."),
            label=f"Web design in {area.name}", schema_type="WebPage", service_name="Web design", faqs=faqs, matrix=True,
            content_html=_matrix_body(
                kicker=f"Serving {area.name}", h1=f"Web Design in {full}",
                lede=f"Websites for businesses in {full}, planned around clear structure, speed and enquiries.",
                intro_html=intro, faqs=faqs, image_stem=next_stem(),
                image_alt=f"Web design planning for businesses in {area.name}, Goa",
                related=_rel_button("/locations/", "All Goa locations") + _rel_button("/contact/", "Start an enquiry", secondary=True),
            ),
        ))

    for sslug, sname, parent in MATRIX_SERVICES:
        s_lower = sname.lower()
        for area in MATRIX_AREAS:
            full = full_name(area)
            faqs = (
                Faq(f"Do you build {s_lower} for businesses in {area.name}?", f"Yes. Sanctify plans and builds {s_lower} for businesses in {full} and across Goa, working from its studio in Vasco-da-Gama."),
                Faq(f"How do we start a project in {area.name}?", "Share a short brief by WhatsApp, phone or the contact page, and we will discuss scope, structure and the right approach before any build."),
            )
            intro = (
                f'<h2>{html.escape(sname)} for {html.escape(area.name)} businesses</h2>'
                f'<p class="lede">{html.escape(area.blurb)}</p>'
                f'<p>Sanctify approaches {html.escape(s_lower)} in {html.escape(area.name)} the same careful way as anywhere in Goa: understand the business first, then plan clear structure, responsive design and a fast, maintainable build.</p>'
                '<ul class="tick-list"><li>Clear structure around real visitor decisions</li><li>Responsive, fast and accessible pages</li><li>Practical launch and handover</li></ul>'
            )
            related = _rel_button(parent, f"{sname} in Goa") + _rel_button(f"/locations/{area.slug}/", f"Web design in {area.name}", secondary=True)
            pages.append(Page(
                route=f"/{sslug}-in-{area.slug}/", fragment="",
                title=_clamp(f"{sname} in {full}", 30, 70, " by Sanctify"),
                description=_clamp(f"{sname} for businesses in {full}. {area.blurb} Clear structure, responsive design and a fast build by Sanctify.", 110, 175, " Serving businesses across Goa."),
                label=f"{sname} in {area.name}", schema_type="WebPage", service_name=sname, faqs=faqs, matrix=True,
                content_html=_matrix_body(
                    kicker=f"{sname} in {area.name}", h1=f"{sname} in {full}",
                    lede=f"{sname} for businesses in {full}, focused on clarity, speed and enquiries.",
                    intro_html=intro, faqs=faqs, image_stem=next_stem(),
                    image_alt=f"{sname} for a business in {area.name}, Goa", related=related,
                ),
            ))

    for islug, iname, parent in MATRIX_INDUSTRIES:
        i_lower = iname.lower()
        for area in MATRIX_AREAS:
            full = full_name(area)
            faqs = (
                Faq(f"Do you design websites for {i_lower} businesses in {area.name}?", f"Yes. Sanctify designs websites for {i_lower} businesses in {full} and across Goa, focused on clear structure, speed and enquiries."),
                Faq(f"How do we begin a {i_lower} website in {area.name}?", "Send a short brief by WhatsApp, phone or the contact page, and we will talk through goals and scope before starting."),
            )
            intro = (
                f'<h2>{html.escape(iname)} websites in {html.escape(area.name)}</h2>'
                f'<p class="lede">{html.escape(area.blurb)}</p>'
                f'<p>Sanctify builds {html.escape(i_lower)} websites for {html.escape(area.name)} around the decisions that matter to that sector, with clear structure, fast mobile pages and an easy path to enquire.</p>'
                '<ul class="tick-list"><li>Content shaped around the customer decision</li><li>Fast, mobile-first, accessible pages</li><li>Clear enquiry and contact paths</li></ul>'
            )
            parent_button = _rel_button(parent, f"{iname} websites in Goa") if parent else _rel_button("/website-development-goa/", "Website development in Goa")
            related = parent_button + _rel_button(f"/locations/{area.slug}/", f"Web design in {area.name}", secondary=True)
            pages.append(Page(
                route=f"/industries/{islug}-website-design-in-{area.slug}/", fragment="",
                title=_clamp(f"{iname} Website Design in {full}", 30, 70, " by Sanctify"),
                description=_clamp(f"{iname} website design for businesses in {full}. {area.blurb} Built around clear structure, speed and enquiries by Sanctify.", 110, 175, " Serving businesses across Goa."),
                label=f"{iname} websites in {area.name}", schema_type="WebPage", service_name=f"{iname} website design", faqs=faqs, matrix=True,
                content_html=_matrix_body(
                    kicker=f"{iname} in {area.name}", h1=f"{iname} Website Design in {full}",
                    lede=f"{iname} websites for businesses in {full}, built around clear structure, speed and enquiries.",
                    intro_html=intro, faqs=faqs, image_stem=next_stem(),
                    image_alt=f"{iname} website design for a business in {area.name}, Goa", related=related,
                ),
            ))

    return tuple(pages)


PAGES: Final[tuple[Page, ...]] = _CORE_PAGES + _build_blog_pages() + _build_matrix_pages()


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


def rewrite_preview_markup(markup: str, *, depth: int) -> str:
    """Rewrite root-relative asset and page links to depth-relative branch paths."""
    asset_prefix = ("../" * depth) + "../dist/assets/"
    page_prefix = "../" * depth
    markup = markup.replace('="/assets/', f'="{asset_prefix}')
    markup = markup.replace(", /assets/", f", {asset_prefix}")

    def replace_page_link(match: re.Match[str]) -> str:
        path = match.group("path")
        fragment = match.group("frag") or ""
        if path == "":
            target = "index.html"
        elif path.endswith("/"):
            target = f"{path}index.html"
        else:
            target = path
        return f'href="{page_prefix}{target}{fragment}"'

    return re.sub(r'href="/(?P<path>[^"#]*)(?P<frag>#[^"]*)?"', replace_page_link, markup)


def write_review_preview() -> None:
    """Write a branch-hostable, fully navigable preview without changing production paths."""
    remove_managed_directory(REVIEW_DIR, expected_name="review-preview")
    REVIEW_DIR.mkdir()
    for page in PAGES:
        relative = output_path_for(page).relative_to(BUILD_DIR)
        depth = len(relative.parts) - 1
        markup = (DIST / relative).read_text(encoding="utf-8")
        rewritten = rewrite_preview_markup(markup, depth=depth)
        if '="/assets/' in rewritten or 'href="/' in rewritten:
            raise ValueError(f"Review preview has unresolved root-relative paths: {relative}")
        asset_prefix = ("../" * depth) + "../dist/assets/"
        if f'href="{asset_prefix}css/' not in rewritten or f'src="{asset_prefix}js/' not in rewritten:
            raise ValueError(f"Review preview asset paths were not rewritten: {relative}")
        rewritten = "\n".join(line.rstrip() for line in rewritten.rstrip().splitlines()) + "\n"
        destination = REVIEW_DIR / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rewritten, encoding="utf-8")


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
    font_target = BUILD_DIR / "assets" / "fonts"
    css_target.mkdir(parents=True)
    js_target.mkdir(parents=True)
    image_target.mkdir(parents=True)
    font_target.mkdir(parents=True)
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

    font_dir = SRC / "assets" / "fonts"
    expected_fonts = set(FONT_FILES)
    actual_fonts = {path.name for path in font_dir.iterdir() if path.is_file()}
    missing_fonts = sorted(expected_fonts - actual_fonts)
    unexpected_fonts = sorted(actual_fonts - expected_fonts)
    if missing_fonts or unexpected_fonts:
        raise ValueError(
            f"Font manifest mismatch; missing={missing_fonts}, unexpected={unexpected_fonts}"
        )
    for name in FONT_FILES:
        source = font_dir / name
        if name.endswith(".woff2") and source.read_bytes()[:4] != b"wOF2":
            raise ValueError(f"Invalid WOFF2 signature: {source}")
        if name.endswith(".txt") and "SIL OPEN FONT LICENSE" not in source.read_text(encoding="utf-8"):
            raise ValueError(f"Invalid font license: {source}")
        shutil.copy2(source, font_target / name)

    asset_root = SRC / "assets"
    for name in FAVICON_FILES:
        source = asset_root / name
        if not source.is_file():
            raise ValueError(f"Expected favicon is not a file: {source}")
        shutil.copy2(source, BUILD_DIR / name)
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
    if page.article_date is not None:
        page_node["headline"] = page.title
        page_node["datePublished"] = page.article_date
        page_node["dateModified"] = page.article_date
        page_node["author"] = {"@type": "Organization", "name": "Sanctify"}
        page_node["publisher"] = {"@type": "Organization", "name": "Sanctify"}
        if page.article_image is not None:
            page_node["image"] = f"{BASE_URL}/assets/images/{page.article_image}-1376.webp"
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
    if page.content_html is not None:
        fragment = page.content_html
    else:
        fragment = (SRC / "pages" / page.fragment).read_text(encoding="utf-8")
    image_url = f"{BASE_URL}/assets/images/social-preview.jpg"
    replacements: Mapping[str, str] = {
        "{{TITLE}}": escaped(page.title),
        "{{DESCRIPTION}}": escaped(page.description),
        "{{ROBOTS_META}}": "" if page.indexable else '<meta name="robots" content="noindex, follow">',
        "{{CANONICAL_META}}": f'<link rel="canonical" href="{escaped(page.url)}">' if page.indexable else "",
        "{{PAGE_URL}}": escaped(page.url),
        "{{OG_IMAGE_META}}": f'<meta property="og:image" content="{image_url}"><meta property="og:image:width" content="{IMAGE_WIDTH}"><meta property="og:image:height" content="{IMAGE_HEIGHT}"><meta property="og:image:alt" content="Indian web designer presenting a website in a bright Goa studio">',
        "{{TWITTER_IMAGE_META}}": f'<meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="Indian web designer presenting a website in a bright Goa studio">',
        "{{HERO_PRELOAD}}": '<link rel="preload" as="image" href="/assets/images/hero-goa-web-design-studio-1376.webp" imagesrcset="/assets/images/hero-goa-web-design-studio-720.webp 720w, /assets/images/hero-goa-web-design-studio-1376.webp 1376w" imagesizes="(max-width: 991px) calc(100vw - 28px), 720px" fetchpriority="high">' if page.hero_image else "",
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
    normalized = "\n".join(line.rstrip() for line in rendered.splitlines())
    return normalized.rstrip() + "\n"


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
  AddType font/woff2 .woff2
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 30 days"
  ExpiresByType image/webp "access plus 30 days"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
</IfModule>

<IfModule mod_headers.c>
  <FilesMatch "^site\.[a-f0-9]{10}\.(css|js)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>
"""
    urllist = "".join(f"{url}\n" for url in indexable_urls)
    (BUILD_DIR / "robots.txt").write_text(robots, encoding="utf-8")
    (BUILD_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (BUILD_DIR / "urllist.txt").write_text(urllist, encoding="utf-8")
    (BUILD_DIR / ".htaccess").write_text(htaccess, encoding="utf-8")


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
        Path("urllist.txt"),
        Path(".htaccess"),
        Path("assets") / "css" / css_file,
        Path("assets") / "js" / js_file,
    }
    expected.update(output_path_for(page).relative_to(BUILD_DIR) for page in PAGES)
    expected.update(Path("assets") / "images" / name for name in IMAGE_FILES)
    expected.update(Path("assets") / "fonts" / name for name in FONT_FILES)
    expected.update(Path(name) for name in FAVICON_FILES)
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
    css_path = BUILD_DIR / "assets" / "css" / css_file
    if css_path.is_file():
        css_text = css_path.read_text(encoding="utf-8")
        for external_font_marker in ("@import", "fonts.googleapis.com", "fonts.gstatic.com"):
            if external_font_marker in css_text:
                errors.append(
                    f"Runtime font dependency remains in stylesheet: {external_font_marker}"
                )
        for font_name in FONT_WOFF2_FILES:
            if f'../fonts/{font_name}' not in css_text:
                errors.append(f"Stylesheet does not reference local font: {font_name}")
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
        if "\u2197" in text:
            errors.append(
                f"{path.relative_to(BUILD_DIR)}: font-dependent U+2197 arrow is forbidden"
            )
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
            "theme-color": "#edf1fa",
            "twitter:card": "summary_large_image",
            "twitter:title": page.title,
            "twitter:description": page.description,
            "twitter:image": f"{BASE_URL}/assets/images/social-preview.jpg",
            "twitter:image:alt": "Indian web designer presenting a website in a bright Goa studio",
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
            "og:image:alt": "Indian web designer presenting a website in a bright Goa studio",
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
            title_lo, title_hi = (30, 70) if page.matrix else (45, 65)
            desc_lo, desc_hi = (110, 175) if page.matrix else (130, 170)
            if not title_lo <= len(parser.title) <= title_hi:
                errors.append(f"{relative}: title length {len(parser.title)} is outside {title_lo}-{title_hi}")
            if not desc_lo <= len(parser.description) <= desc_hi:
                errors.append(f"{relative}: description length {len(parser.description)} is outside {desc_lo}-{desc_hi}")
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
        target.write_text(render_page(page, template=template, css_file=css_file, js_file=js_file), encoding="utf-8")
    write_site_files()
    audit_site(css_file=css_file, js_file=js_file)
    install_build()
    write_review_preview()


if __name__ == "__main__":
    build()
