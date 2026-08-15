# Boojee Cafe Platform

## Overview

The Boojee Cafe platform is a comprehensive, production-ready web application designed for premium coffee shops and boutique eateries. It offers a seamless, high-performance user experience, combining an elegantly crafted vanilla front-end with a secure and scalable Python-based back-end architecture. The platform supports dynamic user interactions, secure authentication, and robust session management to deliver an uninterrupted e-commerce and editorial experience.

## System Architecture

The application operates on a lightweight, yet powerful technology stack, ensuring minimal overhead and maximal performance.

### Front-End Infrastructure

- **Core Technologies**: HTML5, CSS3, Vanilla JavaScript (ES6+).
- **Design System**: A fully responsive, grid-based layout utilizing modern CSS variables for a comprehensive design token system.
- **Theming**: Native implementation of light and dark mode toggles with persistent state stored in `localStorage`.
- **Performance Optimization**: Intersection Observers are utilized for lazy-loading elements and triggering scroll-based animations without impacting the main thread.

### Back-End Infrastructure

- **Framework**: Python 3.x with Flask, providing a lightweight WSGI web application framework.
- **Authentication Strategy**: JSON Web Tokens (JWT) facilitated via `PyJWT`. Authentication routes are protected against unauthorized access, utilizing Werkzeug's security modules for PBKDF2 HMAC SHA256 password hashing.
- **Data Persistence**: SQLite database integrated through Python's standard `sqlite3` library. The schema includes normalized tables for user credentials and cart state.

## Core Features

### 1. Secure User Authentication

The platform implements a stateless authentication mechanism. Upon successful registration and login, the server issues a JWT. This token must be included in the `Authorization` header of subsequent API requests. The client securely stores this token in `localStorage`, managing session validity and enforcing access controls for protected routes (e.g., checkout and cart synchronization).

### 2. Cross-Session Cart Persistence

The cart module is engineered for high reliability, catering to both anonymous guests and authenticated users:

- **Guest Users**: Cart operations are synchronized in real-time with the browser's `localStorage`. This guarantees that items are preserved across page navigations and browser restarts without requiring server-side state.
- **Authenticated Users**: The local cart state is securely synchronized with the back-end database. The `/api/cart` endpoints ensure that the user's cart is maintained across entirely different devices and sessions.

### 3. Dynamic Editorial Content

The platform includes an integrated journal and storytelling mechanism. Articles and notes can be filtered dynamically by category using front-end data attributes, offering instantaneous content rendering without server-side rendering delays.

### 4. Interactive Animated Landing Page

The application features a captivating entry point (`landing.html`) built with GSAP and ScrollTrigger. It uses a scroll-linked animation to deliver a highly interactive, cinematic introduction to the Boojee Cafe brand before smoothly transitioning users to the main application.

## Installation and Deployment

### Prerequisites

- Python 3.8 or higher
- Git version control

### Local Environment Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Hulk-oss/Boojee-Cafe.git
   cd Boojee-Cafe
   ```

2. **Initialize a Virtual Environment**

   It is highly recommended to isolate dependencies using a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Install the required Python packages defined in the requirements file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database and Start the Server**

   Execute the main application script. The SQLite database schema will be automatically generated upon initial execution.

   ```bash
   python app.py
   ```

5. **Access the Application**

   The application will be accessible via a local development server at:
   `http://127.0.0.1:5000`

## API Reference

The back-end exposes a RESTful API to manage the application state. All authenticated routes require the `Authorization: Bearer <token>` header.

### Authentication

- `POST /api/register`
  - Payload: `{ "email": "user@example.com", "password": "securepassword" }`
  - Response: Returns a 201 status code upon successful account creation.

- `POST /api/login`
  - Payload: `{ "email": "user@example.com", "password": "securepassword" }`
  - Response: Returns a 200 status code containing the JWT (`{ "token": "<jwt_string>" }`).

### Cart Management

- `GET /api/cart`
  - Authorization: Required.
  - Response: Returns the serialized cart state associated with the authenticated user.

- `POST /api/cart`
  - Authorization: Required.
  - Payload: `{ "cart": { "Item Name": { "price": 120, "quantity": 1 } } }`
  - Response: Returns a 200 status code indicating successful state synchronization.

### Order Processing

- `POST /api/checkout`
  - Authorization: Required.
  - Response: Processes the order, clears the user's database cart, and returns a confirmation message.

## Security Overview

The platform is designed with foundational security principles in mind. All passwords undergo cryptographic hashing, and state-changing API endpoints enforce strict token validation.

Recent hardening includes:

- **Rate Limiting**: Brute-force protection on authentication routes.
- **XSS Mitigation**: Strict HTML escaping on both frontend and backend inputs.
- **Security Headers**: HSTS, CSP, X-Frame-Options, and X-Content-Type-Options are enforced by the server.

For detailed information regarding our vulnerability reporting processes and active support windows, please review the `SECURITY.md` file located in the repository root.

## License and Copyright

© 2026 Boojee Cafe. All rights reserved.