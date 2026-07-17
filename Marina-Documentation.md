# Marina

**Software Blueprint, Requirements, and Design System — v1.0**

Project Name: Marina
Business: Marina Gadgets Kano
Status: Architecture & Planning Phase

---

## Part 1 — Software Blueprint

### 1. Project Mission

Marina is a premium e-commerce platform built exclusively for Marina Gadgets Kano. Its primary purpose is to provide customers with a fast, trustworthy, and modern shopping experience while giving Marina staff powerful tools to manage products, inventory, orders, payments, deliveries, customer communication, and business growth.

Although Marina begins as an e-commerce platform, every architectural decision should support future expansion into additional Marina businesses without requiring major redesign. The first release focuses solely on e-commerce.

### 2. Project Goals

**Customer Goals**
- Browse products effortlessly
- Purchase securely
- Track every order
- Communicate easily with Marina
- Build trust
- Receive fast support
- Feel rewarded for loyalty

**Business Goals**
- Increase online sales
- Reduce manual work
- Improve inventory accuracy
- Improve customer satisfaction
- Create reusable infrastructure for future Marina businesses

### 3. Engineering Philosophy

Every decision must satisfy these principles.

**1. Simple**
- Simple code
- Simple UI
- Simple deployment
- Simple maintenance

**2. Scalable**
Support 10 users → 100 users → 1,000 users → 100,000 users without redesigning the application.

**3. Maintainable**
- A new developer should understand the project quickly
- Code should be modular
- Documentation should stay updated

**4. Secure**
Security is built in from the beginning, not added later.

**5. Performance**
- The application should feel fast
- Images optimized
- Caching
- Lazy loading
- Minimal unnecessary JavaScript

### 4. High-Level Architecture

```
                    Internet
                        │
                Cloudflare (Future)
                        │
                    Nginx
                        │
                  Gunicorn
                        │
                    Django
                        │
      ┌─────────────────┼─────────────────┐
      │                 │                 │
 PostgreSQL          Redis            Celery
      │                 │                 │
      └────────────Media Storage──────────┘
```

### 5. Technology Stack

**Backend — Django**
Reason: mature, secure, excellent ORM, excellent admin, huge ecosystem.

**API — Django REST Framework**
Even if most pages use Django Templates, we'll expose APIs where they make sense. This also prepares Marina for future mobile apps and integrations.

**Database — PostgreSQL**
Reason: excellent reliability, strong relational support, powerful indexing, JSON support when needed, widely used in production.

**Cache — Redis**
Used for: OTP sessions, caching, background task coordination, rate limiting support.

**Background Jobs — Celery**
Used for: sending OTPs, WhatsApp notifications, SMS, image optimization, scheduled tasks, order reminders, feedback notifications.

**Web Server — Gunicorn**

**Reverse Proxy — Nginx**

**Media Storage**
- Development: local storage
- Production: S3-compatible object storage (such as Cloudflare R2, Backblaze B2, or AWS S3)

**Frontend**
- Django Templates
- Standard HTML
- Standard CSS
- Vanilla JavaScript

Why?
- One codebase
- Excellent SEO
- Lower complexity
- Faster development
- Easier maintenance
- Interactive UX without a separate frontend framework or library dependency

### 6. Folder Structure

```
marina/
├── config/
│
├── apps/
│   ├── accounts/
│   ├── customers/
│   ├── catalog/
│   ├── brands/
│   ├── inventory/
│   ├── cart/
│   ├── wishlist/
│   ├── checkout/
│   ├── orders/
│   ├── payments/
│   ├── delivery/
│   ├── notifications/
│   ├── rewards/
│   ├── feedback/
│   ├── media/
│   ├── homepage/
│   ├── analytics/
│   ├── dashboard/
│   └── core/
│
├── templates/
├── static/
├── media/
└── requirements/
```

Each app has a single responsibility.

### 7. User Types

For Version 1, we define:

| Role | Responsibility |
|---|---|
| Customer | Shops on the website |
| Sales Staff | Manage customer orders |
| Inventory Staff | Manage products and stock |
| Dispatch Staff | Handle deliveries |
| Customer Support | Communicate with customers |
| Marketing Staff | Homepage banners, featured products, announcements |
| Administrator | Business management |
| Super Administrator | System configuration and developer-level administration |

### 8. Customer Side

Public website. Includes:
- Homepage
- Products
- Categories
- Brands
- Search
- Product Details
- Cart
- Wishlist
- Checkout
- Order Tracking
- Login
- Register
- Feedback

### 9. My Marina

Customer dashboard. Contains:
- Profile
- Orders
- Wishlist
- Notifications
- Rewards
- Saved Addresses
- Suggestions
- Settings

### 10. Staff Portal

Separate from the customer-facing website. Modules:
- Dashboard
- Orders
- Inventory
- Products
- Brands
- Categories
- Payments
- Customers
- Delivery
- Reports
- Rewards
- Feedback
- Announcements
- Homepage
- Staff Management

### 11. Django Admin

Django Admin will remain enabled, but it is not the day-to-day interface for staff. Its purpose is:
- Superuser management
- Permissions and groups
- Emergency maintenance
- Developer tools
- System configuration

We will change the default admin URL to a private internal path and keep it for technical administration only.

### 12. Development Strategy

We will not build everything at once. We'll deliver in functional milestones:

1. Foundation & Project Setup
2. Authentication
3. Customer Accounts
4. Product Catalog
5. Inventory
6. Shopping Cart
7. Wishlist
8. Checkout
9. Payments
10. Orders
11. Delivery
12. Notifications
13. Feedback
14. Rewards
15. Staff Portal
16. Analytics & Reports
17. Production Hardening

Each milestone ends with a working application.

---

## Part 2 — Software Requirements Specification (SRS)

Project: Marina
Business: Marina Gadgets Kano
Platform Type: Premium E-commerce Platform

**Technology Stack**
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- HTML
- CSS
- Vanilla JavaScript

### Document Structure

The SRS is divided into 18 sections:

1. Introduction
2. Business Rules
3. User Roles
4. Functional Requirements
5. Non-functional Requirements
6. User Journey
7. Authentication
8. Customer Module
9. Product Module
10. Inventory Module
11. Shopping Module
12. Checkout & Payment Module
13. Order & Delivery Module
14. Communication Module
15. Staff Portal
16. Database Requirements
17. API Requirements
18. Security Requirements

Each section will be reviewed before moving to the next, so that any changes happen before coding begins.

---

### SECTION 1 — Introduction

**1.1 Purpose**

Marina is a premium e-commerce platform for Marina Gadgets Kano. It enables customers to browse products, place orders, make payments, communicate with Marina staff, track deliveries, receive rewards, and manage their accounts. The platform also provides Marina staff with tools to manage inventory, orders, customer communication, payments, and reports.

Although Version 1 focuses only on e-commerce, the architecture shall support future expansion without requiring a major redesign.

**1.2 Primary Objectives**

The system shall:
- Sell products online
- Build customer trust
- Simplify operations
- Reduce manual work
- Improve inventory control
- Improve communication
- Support business growth
- Maintain a premium brand identity

**1.3 Target Users**

*External Users*
- Visitors
- Customers

*Internal Users*
- Sales Staff
- Inventory Staff
- Dispatch Staff
- Customer Support
- Marketing Staff
- Administrators
- Super Administrators

**1.4 System Scope**

*Version 1 includes:*
- Product catalog
- Categories
- Brands
- Product search
- Shopping cart
- Wishlist
- OTP authentication
- Customer dashboard
- OPay payments
- WhatsApp-assisted checkout
- Request-a-call checkout
- Order management
- Delivery tracking
- Notifications
- Feedback system
- Rewards
- Staff portal
- Reporting
- Inventory management

*Version 1 excludes:*
- Marketplace (multiple vendors)
- MarinaGo logistics
- Marina Auto
- Marina Construction
- Marina Properties
- Mobile applications
- Multi-currency
- Multi-language

The architecture, however, must not prevent these features from being added in future versions.

---

### SECTION 2 — Business Rules

Rules that the software must always enforce.

| ID | Rule |
|---|---|
| BR-001 | A customer account is identified by a unique phone number. |
| BR-002 | Passwords are not used for customer authentication. |
| BR-003 | Every login requires OTP verification unless the device has been marked as trusted and the trust period has not expired. |
| BR-004 | A customer cannot purchase an out-of-stock product. |
| BR-005 | Stock quantity is reduced only after payment is confirmed or after staff confirms an offline order, depending on the checkout method. |
| BR-006 | Every stock change must be recorded in an inventory history log. No stock adjustment may occur without creating an audit record. |
| BR-007 | Orders cannot be permanently deleted. They may only be archived or cancelled. |
| BR-008 | Every payment transaction must have a unique reference. |
| BR-009 | Every customer notification must be stored in the notification history, even if delivery fails. |
| BR-010 | Every order must belong to exactly one customer. Guest checkout is not supported. If someone starts checkout without an account, OTP verification creates their account as part of the checkout process. |
| BR-011 | Only users with appropriate permissions may modify products, prices, inventory, or order status. |
| BR-012 | Product prices shown to customers are the currently active prices. Price changes do not affect historical orders. |
| BR-013 | Each product must have exactly one cover image. Additional images and videos are optional. |
| BR-014 | Products may exist in a draft state before they are published, letting staff prepare listings without making them visible immediately. |
| BR-015 | Every customer action that affects business records (orders, reviews, feedback, rewards) must be timestamped for auditing. |

---

### SECTION 3 — User Roles

Marina uses Role-Based Access Control (RBAC) instead of giving every staff member full access.

**Visitor**
- Can: browse products, search products, view categories, read product details
- Cannot: place orders, save wishlist, view order history

**Customer**
- Can: login with OTP, manage profile, save addresses, add items to cart, add wishlist, checkout, track orders, submit feedback, receive rewards

**Sales Staff**
- Can: view orders, confirm orders, update order status, contact customers, view payment information
- Cannot: change system settings, manage staff accounts

**Inventory Staff**
- Can: create products, edit products, upload images, manage brands, manage categories, update stock, view inventory reports
- Cannot: manage payments, manage permissions

**Dispatch Staff**
- Can: assign drivers, record dispatch details, upload package photos, update delivery status

**Customer Support**
- Can: view customer profiles, respond to feedback, handle support requests, review notifications
- Cannot: change inventory, process refunds, change pricing

**Marketing Staff**
- Can: manage homepage banners, featured products, announcements, promotional content
- Cannot: edit inventory, change payments

**Administrator**
- Can manage all business operations, including products, orders, inventory, customers, reports, rewards, and staff (except Super Administrators)

**Super Administrator**
- Reserved for technical administration
- Can: manage administrators, configure system settings, access the Django administration site, perform maintenance, view audit logs, manage permissions

> **Note:** These requirements define *what* the system must do, not *how* it will be coded. That separation makes the project easier to build, test, and maintain.

---

### SECTION 4 — Functional Requirements

Version 1 of Marina contains 16 core modules.

| ID | Module | Priority |
|---|---|---|
| FR-01 | Homepage | High |
| FR-02 | Authentication | High |
| FR-03 | Customer Account (My Marina) | High |
| FR-04 | Product Catalog | High |
| FR-05 | Search & Filtering | High |
| FR-06 | Shopping Cart | High |
| FR-07 | Wishlist | High |
| FR-08 | Checkout | High |
| FR-09 | Payments | High |
| FR-10 | Orders | High |
| FR-11 | Delivery | High |
| FR-12 | Notifications | High |
| FR-13 | Feedback ("Build Marina With Us") | Medium |
| FR-14 | Rewards | Medium |
| FR-15 | Staff Portal | High |
| FR-16 | Reports & Analytics | Medium |

Each module below is defined by: Objective, Features, Business Rules, Validation Rules, Edge Cases, Permissions, and Future Considerations.

#### FR-01 — Homepage

**Objective**
The homepage is the digital storefront of Marina. It should immediately communicate trust, professionalism, and the Marina brand.

**Features**
- Hero banner (managed from the staff portal)
- Featured products
- New arrivals
- Popular categories
- Shop by brand
- Promotional banners
- "Why Choose Marina" section
- Customer testimonials (future)
- Build Marina With Us call-to-action
- Newsletter placeholder (future)
- Footer with contact information

**Business Rules**
- Homepage content must be manageable by staff
- Products shown must be active and in stock (unless explicitly marked otherwise)
- Hero banners must support scheduling (future-ready)

**Future Ready**
- Personalized homepage based on customer behavior
- AI-powered product recommendations

#### FR-02 — Authentication

**Objective**
Provide a passwordless, secure, and simple login experience using phone numbers and OTP.

**Login Flow**
1. Customer enters phone number
2. System validates format
3. Customer chooses WhatsApp OTP or SMS OTP
4. OTP is generated
5. OTP expires after a configurable time (e.g., 5 minutes)
6. Customer enters OTP
7. If valid: create account if it doesn't exist, then log customer in
8. If first login: prompt for First Name and Last Name only

**Trusted Device**
Customers can choose to trust the device. The system stores:
- Device identifier
- Browser fingerprint (where appropriate)
- Last used date
- Expiry date

**Validation**
- Invalid OTP
- Expired OTP
- Too many attempts
- Rate limiting
- Block abusive requests

**Staff Authentication**
Staff accounts use username/email and password, protected by two-factor authentication (recommended).

#### FR-03 — Customer Account (My Marina)

**Sections**
- Dashboard
- Personal Information
- Contact Information
- Saved Addresses
- Orders
- Wishlist
- Rewards
- Notifications
- Feedback History
- Settings

**Customers can**
- Update profile
- Manage addresses
- Set preferred contact method
- View order history
- Download invoices (future)
- Track rewards
- Review previous feedback

#### FR-04 — Product Catalog

Each product contains:

*Basic Information*
- Product Name
- Slug
- SKU
- Brand
- Category
- Condition
- Short Description
- Full Description

*Media*
- Cover Image
- Gallery Images
- Product Videos

*Inventory*
- Quantity
- Stock Status
- Low Stock Threshold

*Pricing*
- Selling Price
- Previous Price
- Discount (optional)

*Technical Specifications*
Flexible key-value specifications, for example: RAM, Storage, Processor, Screen Size, Battery, Operating System. The flexible structure allows different specification sets for phones, laptops, accessories, etc.

*Product Status*
- Draft
- Published
- Hidden
- Archived

#### FR-05 — Search & Filtering

**Customers can search by:** Product Name, SKU, Brand, Category

**Filters include:** Price Range, Brand, Condition, Availability

**Sorting:** Newest, Price (Low → High), Price (High → Low), Most Popular, Recently Added

**Future enhancements:** Autocomplete, typo tolerance, search suggestions

#### FR-06 — Shopping Cart

**Features**
- Add product
- Remove product
- Change quantity
- Save for later (future)
- View estimated total
- Continue shopping

**Business Rules**
- Cannot exceed available stock
- Quantity cannot be less than 1
- Price is recalculated before checkout

#### FR-07 — Wishlist

**Customers can:** save products, remove products, move items to cart

**Future:** notify customers when wishlisted products are back in stock or discounted

#### FR-08 — Checkout

Three methods, exactly as defined in the product vision:

1. **Online Checkout** — OPay payment, automatic verification, automatic order creation
2. **WhatsApp Assisted Checkout** — pre-filled WhatsApp message, cart summary, customer information (if logged in), staff continues the conversation
3. **Request a Call** — customer requests assistance, staff receives notification, preferred calling number is displayed

All three methods create a trackable order record.

#### FR-09 — Payments

Version 1: OPay integration

**Payment states:** Pending, Processing, Successful, Failed, Refunded (future)

**Every payment includes:** Transaction Reference, Amount, Gateway, Status, Timestamp

The payment service must be modular so additional gateways can be added without changing the checkout flow.

#### FR-10 — Orders

**Order lifecycle**

```
Pending → Awaiting Payment → Payment Verified → Confirmed → Processing
→ Packed → Ready for Dispatch → Dispatched → In Transit → Delivered → Completed
```

**Alternative states:** Cancelled, Failed, Returned (future)

Orders are never permanently deleted.

#### FR-11 — Delivery

**Within Kano:** same-day delivery when possible.

**Outside Kano:** staff can select transport company, assign driver, record departure time, add vehicle details, upload sealed package photo, and update tracking status.

Customers see delivery progress inside My Marina.

#### FR-12 — Notifications

**Channels:** WhatsApp, SMS, in-app notifications

Notification history is stored.

**Typical events:** OTP, order received, payment confirmed, packing complete, dispatch update, delivery completed, feedback request, reward issued

#### FR-13 — Build Marina With Us

**Categories:** Suggestions, Bug Reports, Product Requests, Website Feedback, Delivery Feedback, General Feedback

**Status flow**

```
Received → Under Review → In Progress → Implemented → Closed
```

Customers are notified when the status changes.

#### FR-14 — Marina Appreciation Rewards

**Reward types:** Discount, Store Credit, Free Delivery, Exclusive Offer, Priority Support

**Each reward includes:** Reason, Value, Expiry Date (optional), Status (Active, Redeemed, Expired)

#### FR-15 — Staff Portal

**Modules:** Dashboard, Orders, Products, Categories, Brands, Inventory, Customers, Payments, Delivery, Homepage Management, Feedback, Rewards, Reports, Staff Management

Each module respects role-based permissions.

#### FR-16 — Reports & Analytics

**Dashboard cards:** Sales Today, Sales This Week, Sales This Month, Orders, Average Order Value, Top Products, Low Stock Items, Customer Registrations, Revenue, Payment Success Rate

**Export:** CSV, Excel, PDF (future)

---

## Part 3 — UI/UX Design Specification

Product: Marina
Business: Marina Gadgets Kano
Design Goal: Premium Digital Commerce Experience

> **Guiding rule:** Do not imitate Amazon, Jumia, Konga, or Shopify. Create a distinctive Marina identity — premium, modern, clean, and unmistakably Marina.

### 1. Brand Identity

Marina should communicate five emotions immediately:

- **Trust** — "This is a professional company."
- **Premium** — not luxurious, not flashy, simply high quality
- **Simplicity** — everything obvious, no clutter, no unnecessary graphics
- **Confidence** — the interface should never feel confusing; every action has clear feedback
- **Human** — customers should always feel real Marina staff are available to help

### 2. Design Principles

- **Clean** — whitespace is a feature; never fill every corner
- **Consistent** — buttons, cards, forms, and spacing behave the same everywhere
- **Mobile First** — the first design target is a phone; desktop expands naturally
- **Touch Friendly** — buttons large enough to tap comfortably; inputs never feel cramped
- **Fast** — animations enhance the experience, never slow it down

### 3. Color System

| Token | Value | Usage |
|---|---|---|
| Primary | `#185ABD` | Primary buttons, links, active navigation, selected states, highlights |
| Primary Hover | `#144A99` | — |
| Primary Light | `#EAF3FF` | Information cards, notifications, background accents |
| Success | `#16A34A` | Payment successful, order completed, in stock |
| Warning | `#F59E0B` | Low stock, attention needed |
| Danger | `#DC2626` | Errors, failed payments, out of stock |
| Background | `#FFFFFF` | — |
| Surface | `#F8FAFC` | Cards and subtle section backgrounds |
| Text Primary | `#1F2937` | — |
| Text Secondary | `#6B7280` | — |
| Text Muted | `#9CA3AF` | — |

### 4. Typography

Font: **Inter** — highly readable, modern, excellent on both desktop and mobile, wide range of weights.

| Element | Size | Weight |
|---|---|---|
| Hero Title | 48px | 700 |
| Page Title | 32px | 700 |
| Section Title | 24px | 600 |
| Card Title | 20px | 600 |
| Body | 16px | 400 |
| Small Text | 14px | 400 |
| Caption | 12px | 400 |

### 5. Border Radius

Rounded but not exaggerated.

| Component | Radius |
|---|---|
| Buttons | 12px |
| Cards | 16px |
| Inputs | 12px |
| Images | 16px |
| Modals | 20px |

### 6. Shadows

Very soft. Cards should appear elevated without looking heavy.

- Resting card: subtle shadow
- Hovered card: slightly stronger shadow with a gentle upward movement
- No harsh black shadows

### 7. Spacing System

Base unit: **8px**. Use multiples of 8: 8, 16, 24, 32, 40, 48, 64 — this creates visual rhythm and consistency.

### 8. Buttons

**Primary** — blue background, white text, rounded. Used for: Buy Now, Checkout, Login, Save.

**Secondary** — white background, blue border, blue text. Used for secondary actions.

**Text Button** — no background, blue text. Used for links and less prominent actions.

### 9. Cards

Cards are the foundation of Marina's UI: product cards, order cards, notification cards, reward cards, feedback cards.

Each card should have consistent padding, rounded corners, soft shadow, clear hierarchy, and hover feedback on desktop.

### 10. Forms

Forms should feel effortless. Each field includes: label above input, placeholder for examples (not as the only label), inline validation, helpful error messages, success state, disabled state.

### 11. Navigation

**Desktop**
- Marina logo on the left
- Search bar centered
- Actions (Wishlist, Cart, Login/My Marina) on the right
- Categories as secondary navigation below the header

**Mobile**
- Compact header
- Search accessible
- Bottom navigation with five core destinations: Home, Categories, Search, Wishlist, My Marina
- Cart remains visible as a floating badge in the header

### 12. Product Cards

Each card displays: product image, product name, brand, condition badge, current price, previous price (if discounted), stock status, and quick actions (Add to Cart, Save to Wishlist).

Avoid overcrowding the card — keep the emphasis on the product image and pricing.

### 13. Product Detail Page

**Sections**
- Image gallery with thumbnails
- Product information
- Price and condition
- Stock status
- Technical specifications
- Description
- Related products
- Customer reviews
- Build Marina With Us prompt for product feedback

The primary action area (price, stock, Buy Now, Add to Cart, WhatsApp Checkout) should remain visible on larger screens as the customer scrolls.

### 14. My Marina

The dashboard should feel personal and useful, not just a list of links.

- Welcome section with the customer's name
- Quick summary cards: Active Orders, Wishlist Items, Available Rewards, Recent Notifications
- Navigation: Profile, Orders, Addresses, Rewards, Notifications, Feedback, Settings

### 15. Staff Portal

This is a business application, not a public website.

**Design priorities**
- Information density balanced with readability
- Fast workflows
- Clear status indicators
- Powerful search
- Bulk actions where appropriate
- Tables that remain usable on tablets and laptops

**Dashboard widgets:** Sales Today, Orders Awaiting Action, Low Stock Alerts, Recent Customer Feedback, Dispatch Queue

### 16. Motion & Micro-Interactions

Motion should communicate state, not decorate the interface.

- Buttons subtly scale on hover
- Cards gently lift on hover
- Loading skeletons replace spinners where possible
- Toast notifications slide in briefly for success or error feedback
- Smooth transitions between page states
- Animations should generally stay under 250ms

### 17. Accessibility

- Keyboard navigation
- Visible focus indicators
- Sufficient color contrast
- Meaningful alt text for images
- Labels for all form controls
- Semantic HTML
- Screen-reader-friendly status updates

### 18. Responsive Design

| Breakpoint | Range |
|---|---|
| Mobile | up to 767px |
| Tablet | 768px–1023px |
| Desktop | 1024px and above |

Layouts should adapt rather than simply shrink.

### 19. The Marina Identity

The final experience should make someone say: *"This doesn't look like another online shop. It looks like Marina."*

The combination of generous spacing, restrained use of color, soft elevations, consistent typography, and a human-centered communication style should create a recognizable identity that customers associate with professionalism and trust.

---

## Part 4 — Marina Design System (MDS)

**Design Philosophy:** Simple. Premium. Human. Fast. Trustworthy.

This is the design language for the entire company. In the future, even if MarinaGo, Marina Auto, or Marina Properties are built, they'll use this same design system.

### 1. Design Principles

**1. Clarity** — the user should never ask "What does this button do?" Everything should be obvious.

**2. Consistency** — buttons, cards, inputs, and spacing look and behave the same everywhere.

**3. Speed** — every interaction should feel instant. If something takes time, use a Skeleton Loader, Progress Indicator, or Status Message. Never leave users wondering.

**4. Accessibility** — every component must work with keyboard, screen readers, and touch devices.

**5. Human** — instead of robotic messages like "Error 503," use language like "We couldn't reach our servers right now. Please try again in a moment."

### 2. Design Tokens

These are the foundation of the design system. Instead of writing colors directly (e.g. `#185ABD`), we define tokens. If Marina changes branding later, only the tokens change — the UI updates automatically.

**Colors**
- Primary, Primary Hover, Primary Light
- Success, Success Light
- Warning, Warning Light
- Danger, Danger Light
- Background, Surface, Surface Elevated
- Border
- Text Primary, Text Secondary, Text Muted
- White, Black

### 3. Spacing Tokens

Never write random spacing values. Instead:

| Token | Value |
|---|---|
| Space XS | 4px |
| Space SM | 8px |
| Space MD | 16px |
| Space LG | 24px |
| Space XL | 32px |
| Space XXL | 48px |
| Space XXXL | 64px |

Every page uses these.

### 4. Radius Tokens

| Token | Value |
|---|---|
| Small | 8px |
| Medium | 12px |
| Large | 16px |
| Extra Large | 20px |
| Pill | 999px |

### 5. Shadow Tokens

| Level | Usage |
|---|---|
| Level 1 | Cards |
| Level 2 | Hover |
| Level 3 | Dropdowns |
| Level 4 | Dialogs |

No component should invent its own shadow.

### 6. Typography Tokens

**Font:** Inter
**Weights:** 400, 500, 600, 700
**Sizes:** 12, 14, 16, 18, 20, 24, 32, 40, 48
**Line heights:** consistent throughout

### 7. Grid System

| Breakpoint | Columns |
|---|---|
| Desktop | 12 |
| Tablet | 8 |
| Mobile | 4 |

### 8. Container Width

- Desktop: 1280px
- Content Width: 1200px

Everything aligns to this.

### 9. Components

**Button**
- Variants: Primary, Secondary, Ghost, Danger, Icon, Loading, Disabled
- Sizes: Small, Medium, Large
- States: Default, Hover, Pressed, Disabled, Loading, Focus

**Input**
- Variants: Text, Phone, OTP, Email, Number, Textarea, Search, Password (staff only)
- States: Empty, Typing, Focused, Error, Disabled, Success

**Select** — Single Select, Multi Select, Searchable Select

**Checkbox** — Rounded, Animated, Accessible

**Radio** — Same style everywhere

**Toggle Switch** — used for Published, Featured, Notifications, Settings

**Badge** — Primary, Success, Warning, Danger, Info
Examples: In Stock, Low Stock, New, Featured, Pending, Delivered

**Chips**
Examples: Samsung, Apple, Laptop, Phone, Refurbished, UK Used

**Cards** — Product Card, Order Card, Reward Card, Feedback Card, Analytics Card, Notification Card. All use identical spacing.

**Modal** — Standard, Confirmation, Delete, Success, Error

**Toast** — Success, Warning, Error, Information. Appears briefly without interrupting the user.

**Alert Banner** — Homepage, Admin, Maintenance, Announcements

**Accordion** — Product Specifications, FAQ, Policies

**Tabs** — Example: Description, Specifications, Reviews, Delivery

**Breadcrumb** — Example: Home > Phones > Samsung > Galaxy S24

**Pagination** — Modern, Minimal, Touch Friendly

**Table** — Sorting, Searching, Filtering, Bulk Select, Export, Sticky Header. Used heavily inside the Staff Portal.

**Empty State** — instead of "No Data," use illustrations and helpful guidance.
Example (Wishlist): *"You haven't saved any products yet. Browse our latest gadgets and tap the heart icon to save them for later."*

**Error State** — never "500 Error." Instead: *"Something went wrong while loading this page. Please try again. If the problem continues, contact Marina Support."*

**Loading State** — prefer Skeleton Loaders over Spinners whenever practical.

### 10. Icons

One icon family only: Home, Search, Cart, Wishlist, User, Orders, Rewards, Settings, Notifications. Consistent size and stroke.

### 11. Product Components

Reusable building blocks: Image Gallery, Image Zoom, Product Price, Discount Badge, Stock Badge, Condition Badge, Specification Table, Quantity Selector, Add to Cart Button, Buy Now Button, WhatsApp Checkout Button.

### 12. Order Components

Reusable across My Marina and Staff Portal: Order Timeline, Payment Status, Delivery Status, Driver Information, Package Photo Viewer.

### 13. Feedback Components

For "Build Marina With Us": Submission Card, Status Timeline, Comment Thread (future), Reward Badge, Implementation Badge.

### 14. Motion System

| Element | Duration |
|---|---|
| Buttons | 150ms |
| Cards | 200ms |
| Page transitions | 250ms |
| Dropdown | 150ms |
| Modal | 200ms |

Never exceed 300ms.

### 15. Voice & Content Guidelines

Every piece of text should feel like it comes from the same company.

| Instead of | Use |
|---|---|
| "Submit" | "Send Feedback" |
| "Checkout" | "Complete Your Order" |
| "OTP Invalid" | "That code doesn't look right. Please check it and try again." |

Even small wording choices reinforce a trustworthy, human brand.

### 16. Experience Patterns

Beyond typical design system components, Marina also defines experience patterns — how common interactions should behave everywhere in the product:

- **Search Pattern** — instant suggestions, clear "no results" state, filters remain visible, search term highlighted
- **Confirmation Pattern** — destructive actions always require confirmation; successful actions always provide feedback
- **Status Pattern** — every status (order, payment, delivery, feedback) uses consistent colors, badges, and timelines
- **Empty State Pattern** — every empty page explains what happened, why it's empty, and what the user can do next
- **Media Upload Pattern** — drag-and-drop, preview, reorder, progress indicator, validation, and optimization behave identically across products, banners, and other media
