# Boojee UI/UX Design System

The Boojee frontend is engineered to project absolute premium luxury. We categorically reject standard, generic UI frameworks (like default Bootstrap, Material UI, or un-styled Tailwind) in favor of a highly curated, bespoke design language. The aesthetic relies heavily on glassmorphism, fluid micro-animations, and striking, legible typography.

## 1. Design Philosophy
*   **Tactile Responsiveness**: Every interactive element (buttons, cards, input fields, toggles) must respond instantly to user hover, focus, and active click states, providing visceral, tactile feedback via CSS transitions. If an element is clickable, it must feel physically reactive.
*   **Spatial Hierarchy & Negative Space**: We utilize aggressive whitespace (negative space) to draw focus to high-value conversion elements (products, add-to-cart actions, checkout flows). Clutter is the enemy of premium design.
*   **Dark Mode Native**: The platform is designed "dark-first." The aesthetic relies on deep, OLED-friendly blacks and subtle elevated grays punctuated by highly vibrant accent colors. This reduces eye strain and increases the perceived value of high-resolution product imagery.

## 2. Core Tokens & CSS Variables

All CSS across the platform must inherit from the global CSS custom properties defined in the root stylesheet (`index.css`). Hardcoding hex values or specific pixel measurements in component files is strictly prohibited.

### 2.1. Color Palette Matrix
```css
:root {
    /* Primary Backgrounds */
    --bg-primary: #0A0A0A;    /* Deep, OLED-friendly black for the main body */
    --bg-secondary: #121212;  /* Slightly elevated surfaces (cards, modals) */
    --bg-tertiary: #1A1A1A;   /* Highly elevated elements (dropdowns, tooltips) */
    
    /* Accents (Vibrant HSL for smooth manipulation) */
    --accent-primary: hsl(340, 80%, 60%); /* Signature Vibrant Pink/Red */
    --accent-hover: hsl(340, 80%, 50%);   /* Darkened for hover states */
    --accent-glow: hsla(340, 80%, 60%, 0.4); /* Used for drop-shadows */
    
    /* Typography */
    --text-primary: #FFFFFF;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --text-muted: rgba(255, 255, 255, 0.4);
    
    /* Structural Elements & Borders */
    --border-subtle: rgba(255, 255, 255, 0.1);
    --border-strong: rgba(255, 255, 255, 0.2);
}
```

### 2.2. Glassmorphism Utilities
To achieve our signature premium look, modal overlays, floating navigation bars, and notification toasts must utilize hardware-accelerated backdrop filters to blur the underlying content.
```css
.glass-panel {
    background: rgba(18, 18, 18, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px); /* Safari support */
    border: 1px solid var(--border-subtle);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); /* Deep dimensional shadow */
    border-radius: 12px;
}
```

## 3. Typography Rules
We exclusively utilize the **Inter** font family (a highly legible, neo-grotesque sans-serif) for all UI elements to guarantee absolute legibility across all viewport dimensions, from 4K monitors to small mobile screens.

*   **Headings (`h1` - `h3`)**: Must utilize font weights of `600` (Semi-Bold) or `700` (Bold), with tight letter-spacing (`-0.02em` to `-0.04em`) to create a compact, modern feel.
*   **Body Text (`p`, `span`)**: Must utilize font weight `400` (Regular) with relaxed line-height (`1.6` or `1.7`) for reading comfort and optical balance.
*   **System UI (Buttons, Labels, Nav Links)**: Must utilize font weight `500` (Medium) with slight uppercase transformation and wide tracking (`0.05em`) for semantic distinction from standard prose.

## 4. Responsive Grid & Breakpoints
The platform utilizes a fluid, CSS Grid and Flexbox-based layout system. Media queries strictly adhere to the following mobile-first breakpoints. Do not use arbitrary max-width queries.

*   **Mobile (Base)**: `0px` - `767px` (1-column stacks, hidden sidebars, bottom-sheet modals)
*   **Tablet (SM)**: `768px` - `1023px` (2-column grids, condensed navigation bars)
*   **Desktop (MD)**: `1024px` - `1439px` (3-column fluid grids, full expanded sidebar)
*   **Ultrawide (LG)**: `1440px+` (Max-width wrappers locked to 1440px to prevent infinite horizontal stretching, centered margin auto)

## 5. Motion & Animation Constraints
Animations must feel snappy, physics-based, and intentional. Sloppy or slow animations degrade the perceived performance of the application.

*   **Durations**: Hover states (color changes, border-radius shifts) should transition at exactly `200ms`. Page entrance animations, modal drops, and heavy layout shifts should not exceed `400ms`.
*   **Easing**: Never use `linear` easing for UI motion. Always use `cubic-bezier(0.4, 0.0, 0.2, 1)` (commonly known as ease-out) for entrance animations, ensuring the movement starts fast and decelerates smoothly, mimicking physical momentum.
*   **Accessibility**: Respect the user's OS-level motion preferences.
    ```css
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    ```
