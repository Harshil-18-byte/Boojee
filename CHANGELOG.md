# Changelog

All notable changes to the Boojee Platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.0] - 2026-08-21

### Added
- **Authentic Media Pipeline**: Downloaded and integrated 38 high-definition assets directly from `boojeecafe.com` including 4K roastery process video, official team portrait, cafe interior photography, and 12-item visual gallery.
- **Roastery Video Experience**: Embedded HTML5 MP4 video player and six-stage thermodynamic roasting process illustrations (`frontend/roastery.html`).
- **Interactive Visual Gallery**: Implemented responsive gallery grid with category tags and modal Lightbox viewer (`frontend/gallery.html`).
- **Enquiry & Gathering Booking API**: Built backend `/api/enquiries` endpoint backed by Beanie `Enquiry` model and interactive client confirmation cards (`visit.html`, `contact.html`).
- **Authentic Shop Inventory**: Expanded backend and frontend catalogs with single-origin beans (*Coal Black*, *Experimental Lot*), canvas barista aprons, ceramic cups, and bakery boxes.

### Changed
- **Unified Site Directory**: Harmonized complete 15-page footer navigation across all HTML files.
- **OLED Dark Mode**: Transitioned theme from brown/espresso tones to pure OLED black (`#000000`) with high-contrast text and white button styling.
- **Navigation Routing**: Fixed "Plan a gathering" navigation to direct smoothly to reservation forms without opening the order drawer.

---

## [2.0.0] - 2026-08-17

### Added
- **MongoDB NoSQL Integration**: Migrated persistence layer to MongoDB utilizing `Beanie` asynchronous ODM.
- **Background Worker Fleet**: Integrated `arq` and Redis for background job execution.
- **Generic Cell Rate Algorithm (GCRA)**: Rate limiting protection via `quart-rate-limiter`.
- **Multi-Factor Authentication (MFA)**: TOTP verification via `pyotp`.
- **Pydantic Validation**: Payload schema coercion and type safety.
