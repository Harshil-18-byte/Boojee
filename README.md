# Boojee Cafe Platform
> An Enterprise-Grade, Cloud-Native Specialty Coffee E-Commerce & Editorial Ecosystem.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)]()
[![Version](https://img.shields.io/badge/version-2.2.0-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![Framework](https://img.shields.io/badge/framework-Quart%20%7C%20Beanie%20%7C%20Redis-red.svg)]()

## Table of Contents
1. [Overview & Features](#1-overview--features)
2. [Architecture System Blueprint](#2-architecture-system-blueprint)
3. [Authentic Asset & Media Pipeline](#3-authentic-asset--media-pipeline)
4. [Subsystems & API Specifications](#4-subsystems--api-specifications)
5. [Design System & Theme Engine](#5-design-system--theme-engine)
6. [Strict Prerequisites Runbook](#6-strict-prerequisites-runbook)
7. [Installation & Configuration](#7-installation--configuration)
8. [Testing & Verification](#8-testing--verification)
9. [Mobile App Packaging (Capacitor)](#9-mobile-app-packaging-capacitor)
10. [Production Deployment](#10-production-deployment)

---

## 1. Overview & Features

The Boojee Cafe platform is an enterprise-grade digital ecosystem built for specialty coffee roasteries and hospitality venues. Engineered with an asynchronous microservice backend and high-performance frontend, it powers real-time order processing, click-and-collect fulfillment, interactive roastery media streaming, and gathering reservation workflows with sub-second latency.

*   **Stateless Cryptographic Sessions**: JSON Web Tokens (JWT) secured via `HttpOnly`, `Secure`, and `SameSite=Strict` cookies.
*   **Asynchronous Engine**: Built on `Quart` (ASGI) and `Motor` / `Beanie` ODM for lockless MongoDB transactions and high concurrency.
*   **Authentic Media & Video Pipeline**: High-definition MP4 roastery process streaming, responsive visual gallery with interactive Lightbox, and CDN-optimized product packaging photography.
*   **Distributed Cart Synchronization**: Dual-state cart engine with local `localStorage` persistence and automatic authenticated cloud synchronization via `/api/cart`.
*   **Enquiries & Reservation Engine**: Full gathering reservation and contact management subsystem backed by MongoDB and instant client feedback banners.
*   **Universal Design System**: OLED pure black (`#000000`) dark mode theme engine, responsive fluid typography, frosted glass topbar, and unified 15-page directory footer.

---

## 2. Architecture System Blueprint

```text
[Client Browser / Mobile App]
       |
       | (HTTPS / TLS 1.3)
       v
+-----------------------+      (REST / ASGI)      +-----------------------+
|  Static Presentation  | ----------------------> |   Core API Gateway    |
|  Service (Frontend)   |                         |   (Quart / Hypercorn) |
+-----------------------+                         +-----------------------+
       |                                                    |
       | (Video / Media Streaming)                          | (Beanie ODM)
       v                                                    v
+-----------------------+                         +-----------------------+
| Local Video & Image   |                         | MongoDB NoSQL Cluster |
| Assets Cache Pipeline |                         | (Users, Orders, Carts,|
+-----------------------+                         |  Products, Enquiries) |
                                                  +-----------------------+
                                                            |
                                                            | (Caching / Rate-Limit)
                                                            v
                                                  +-----------------------+
                                                  |  Redis Cache & ARQ    |
                                                  |  Worker Queue Fleet   |
                                                  +-----------------------+
```

---

## 3. Authentic Asset & Media Pipeline

All visual and multimedia assets are organized into dedicated high-performance static pipelines:

*   `frontend/videos/roastery-process.mp4`: Authentic 4K video showing the six-stage thermodynamic roasting curve in action.
*   `frontend/images/roastery/`: Process step diagrams (`step-1-green-beans.png` to `step-6-nitrogen-flush.png`) and roastery facility photography.
*   `frontend/images/gallery/`: High-resolution gallery photography of barista latte art, counter service, and daily bakes.
*   `frontend/images/team/`: Official Boojee team portrait in Bandra West, Mumbai.
*   `frontend/images/shop/`: Authentic specialty coffee bean bags (*Coal Black — Aura Estate*, *Experimental Lot #4*), barista aprons, ceramic stoneware, and artisan bakery boxes.
*   `frontend/images/cafe/`: Real exterior storefront and cafe interior photography.

---

## 4. Subsystems & API Specifications

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/api/register` | `POST` | Public | Registers a new user with strong password schema validation. |
| `/api/login` | `POST` | Public | Authenticates credentials and issues encrypted JWT tokens. |
| `/api/logout` | `POST` | JWT | Blacklists active JWT token in Redis with TTL expiration. |
| `/api/products` | `GET` | Public | Returns cached inventory of whole beans, merchandise, and bakery items. |
| `/api/cart` | `GET` / `POST` | JWT | Retrieves and merges user cart state with cloud persistence. |
| `/api/orders` | `GET` / `POST` | JWT | Manages click-and-collect orders with live status telemetry. |
| `/api/enquiries` | `POST` | Public | Receives table bookings, gathering requests, and contact messages. |
| `/api/newsletter` | `POST` | Public | Subscribes email addresses for fresh drop cafe alerts. |

---

## 5. Design System & Theme Engine

*   **Light Mode**: Architectural warm canvas (`#ffffff`), subtle borders (`#dcdcdc`), and deep ink typography (`#000000`).
*   **Pure Black Dark Mode**: OLED true black canvas (`#000000`), elevated card surfaces (`#0c0c0c` / `#141414`), neutral dividers (`#262626`), high-contrast pure white headings (`#ffffff`), and soft reading text (`#d4d4d4`).
*   **Frosted Header**: Semi-transparent blurred navigation (`.header.inner-header`) with mobile responsive drawer.
*   **Unified Footer**: Standardized 15-page directory links and interactive bell subscription trigger on every page.

---

## 6. Installation & Configuration

### Prerequisites
* Python 3.8+
* Node.js 18+ & npm
* MongoDB instance (Local or Atlas)
* Redis instance

### Setup
```bash
# 1. Clone repository
git clone https://github.com/Harshil-18-byte/Boojee.git
cd Boojee

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install frontend tooling
npm install

# 4. Start local development server
python backend/app.py
```

---

## 7. Testing & Verification

```bash
# Run automated backend test suite
pytest
```

---

## 8. Mobile App Packaging (Capacitor)

The repository includes cross-platform wrappers for iOS and Android:
```bash
# Open in Android Studio
npx cap open android

# Open in Xcode (macOS)
npx cap open ios
```
