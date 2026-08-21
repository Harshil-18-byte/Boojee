# Boojee UI/UX Design System

The Boojee frontend is engineered to project absolute premium luxury. We categorically reject standard, generic UI frameworks in favor of a highly curated, bespoke design language. The aesthetic relies on glassmorphism, fluid micro-animations, striking typography, and true OLED black dark mode.

## 1. Design Philosophy
*   **Tactile Responsiveness**: Every interactive element (buttons, cards, input fields, toggles) must respond instantly to user hover, focus, and active click states, providing visceral, tactile feedback via CSS transitions. If an element is clickable, it must feel physically reactive.
*   **Spatial Hierarchy & Negative Space**: We utilize aggressive whitespace (negative space) to draw focus to high-value conversion elements (products, add-to-cart actions, checkout flows). Clutter is the enemy of premium design.
*   **OLED Pure Black Native**: The platform features a dedicated OLED true black (`#000000`) canvas with high-contrast text (`#ffffff` / `#d4d4d4`) and crisp monochrome button controls, eliminating muddy brown tones.

## 2. Core Tokens & CSS Variables

All CSS across the platform inherits from global CSS custom properties defined in the root stylesheets (`style.css` and `site-features.css`).

### 2.1. Color Palette Matrix

#### Light Canvas (Daylight Minimal)
*   `--paper`: `#ffffff`
*   `--ink`: `#000000`
*   `--cream`: `#f5f5f5`
*   `--line`: `#dcdcdc`
*   `--rust`: `#333333`

#### OLED Dark Canvas (True Black Mode)
*   `--paper`: `#000000` (Deepest pure black canvas)
*   `--cream`: `#0c0c0c` (Elevated cards and surfaces)
*   `--line`: `#262626` (Subtle boundary lines)
*   `--ink`: `#ffffff` (High contrast text)
*   `--rust`: `#e0e0e0` (Neutral accent)

### 2.2. Glassmorphism Utilities
To achieve our signature premium look, floating navigation headers, modal overlays, and notification toasts utilize hardware-accelerated backdrop filters.
```css
.glass-panel, .header.inner-header {
    background: rgba(12, 12, 12, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
```

## 3. Typography Hierarchy
We exclusively pair **Playfair Display** (editorial serif) for headings with **DM Sans** (clean geometric sans-serif) for body and UI elements:

*   **Headings (`h1` - `h3`)**: *Playfair Display*, font weight `600` or `700`, with tight letter-spacing (`-0.04em`) to create an editorial, artisanal feel.
*   **Body Text (`p`, `span`)**: *DM Sans*, font weight `400` or `500` with relaxed line-height (`1.55` to `1.7`) for optical balance.
*   **Labels, Kickers & System UI**: *DM Sans*, font weight `700`, uppercase transformation with wide letter-spacing (`0.16em`).

## 4. Responsive Grid & Breakpoints
The platform utilizes a fluid, CSS Grid and Flexbox-based layout system. Media queries strictly adhere to the following mobile-first breakpoints:

*   **Mobile (Base)**: `0px` - `720px` (1-column stacks, full-screen mobile menu drawer, stacked footer).
*   **Tablet (SM)**: `721px` - `1024px` (2-column grids, condensed navigation).
*   **Desktop (MD)**: `1025px` - `1240px` (3-column fluid product grids, expanded headers).
*   **Max Wrapper**: `1240px` (Locked container with `max(5vw, 28px)` fluid side padding).

## 5. Universal Layout Consistency
*   **Navigation Header**: Consistent frosted sticky topbar across all inner pages (`.header.inner-header`).
*   **Universal 15-Page Directory Footer**: Synchronized across every page with full links (*Menu, Our Craft, Visit, Shop, Roastery, Experiences, Journal, Gallery, Contact, Join Our Team, Privacy Policy, Terms of Service, Refund Policy, Shipping Policy, Contact Info*) and interactive Fresh Drop alert triggers.

## Mobile App Support (Capacitor)
This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.
