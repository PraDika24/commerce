# Multi-User E-Commerce Backend (Django REST Framework)

Backend API untuk platform e-commerce multi-user (Buyer & Seller) yang dibangun dengan fokus pada keamanan data, skalabilitas infrastruktur cloud, dan performa tinggi.

## 🚀 Tech Stack

- **Framework:** Django 5.x & Django REST Framework (DRF)
- **Database:** PostgreSQL 18 (Relational Data)
- **Caching & Session:** Redis 7.2 (Performance)
- **Authentication:** JWT (JSON Web Token) via SimpleJWT
- **Infrastruktur:** Docker & Docker Compose (Containerized)
- **Security:** Django-cors-headers, python-dotenv (Environment Protection)

## Project Progress

### Authentication & Authorization

* [x] User Registration
* [x] Email & Password Login
* [x] JWT Authentication
* [x] Refresh Token
* [x] Logout
* [x] Email Verification
* [x] Resend Verification Email
* [x] Forgot Password
* [x] Reset Password
* [x] Change Password
* [x] Delete Account
* [x] Google OAuth Login
* [x] Facebook OAuth Login
* [x] Link Social Account
* [x] Unlink Social Account
* [x] Role-Based Access Control (RBAC)
* [ ] Multi-Factor Authentication (MFA)

---

### User Management

* [x] User Profile
* [x] Update Profile
* [x] Upload Profile Image
* [x] Buyer Role
* [x] Seller Role
* [x] Admin Role
* [ ] Seller Application Workflow
* [ ] Store Verification

---

### Store Management

* [ ] Create Store
* [ ] Update Store
* [ ] Store Profile
* [ ] Store Banner
* [ ] Store Status Management

---

### Product Management

* [ ] Create Product
* [ ] Update Product
* [ ] Delete Product
* [ ] Product Images
* [ ] Product Categories
* [ ] Product Variants
* [ ] Product Inventory
* [ ] Product Search
* [ ] Product Filtering

---

### Shopping Features

* [ ] Shopping Cart
* [ ] Wishlist
* [ ] Product Review
* [ ] Product Rating

---

### Order Management

* [ ] Checkout
* [ ] Order Creation
* [ ] Order Status Tracking
* [ ] Order History
* [ ] Order Cancellation

---

### Payment Integration

* [ ] Midtrans Integration
* [ ] Payment Notification Webhook
* [ ] Payment Verification
* [ ] Refund Handling

---

### Notifications

* [x] Email Verification Notification
* [x] Password Reset Notification
* [ ] Order Notification
* [ ] Payment Notification
* [ ] Seller Notification

---

### Background Jobs

* [x] Redis Integration
* [x] Celery Integration
* [x] Email Background Tasks
* [ ] Scheduled Tasks
* [ ] Notification Queue

---

### Infrastructure

* [x] Docker Compose
* [x] PostgreSQL
* [x] Redis
* [x] Environment Configuration
* [ ] Nginx
* [ ] CI/CD Pipeline
* [ ] Production Deployment

---

### API Documentation

* [x] Swagger Documentation
* [x] OpenAPI Schema
* [ ] Postman Collection
* [ ] API Versioning

---

### Security

* [x] Password Hashing
* [x] JWT Authentication
* [x] Email Verification
* [x] Password Reset Token
* [x] Refresh Token Blacklisting
* [ ] MFA / TOTP
* [ ] Rate Limiting
* [ ] Audit Logging
* [ ] Security Headers

---

## Current Progress

### Completed

Authentication system is fully implemented, including:

* User Registration
* Login & Logout
* JWT Authentication
* Email Verification
* Forgot Password
* Reset Password
* Change Password
* Delete Account
* Google Login
* Facebook Login
* Social Account Linking
* Role-Based Access Control
* Dockerized PostgreSQL & Redis
* Celery Background Tasks

### In Progress

* Seller Application Workflow
* Store Management

### Planned

* Product Management
* Shopping Cart
* Wishlist
* Checkout
* Midtrans Integration
* Order Management
* Notification System
* Production Deployment
