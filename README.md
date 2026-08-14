# OpenShop REST API

A robust, production-ready RESTful API built with **Django** and **Django REST Framework (DRF)** for managing product catalogs. This project implements soft-deletion, advanced search and location filtering, custom data validation, and comes fully verified by a 56-test Postman suite.

## Key Features

- Complete CRUD Operations: Create, retrieve, update, and soft-delete products.
- Soft Delete Pattern:** Deleted products set an `is_deleted` flag rather than being hard-removed from the database.
- Dynamic Search & Filtering: Filter products by `name` (or title) and `location` with full case-insensitive matching support.
- Strict Payload Validation: Custom validation logic ensuring clear `400 Bad Request` responses for invalid data (e.g., negative prices, invalid discounts, missing required fields).
- Automated Quality Assurance: 100% test pass rate across 56 assertion tests in Postman.

## Tech Stack

* **Language:** Python 3.x
* **Framework:** Django, Django REST Framework
* **Database:** SQLite (Development)
* **Testing & Verification:** Postman / Newman

## Endpoints

| Method | Endpoint | Description | Query Params / Body |
| :--- | :--- | :--- | :--- |
| **GET** | `/products/` | List all active products | `name`, `location`, `id` |
| **POST** | `/products/` | Create a new product | Required JSON payload |
| **PUT** | `/products/` | Bulk / First-item update | Product JSON payload |
| **GET** | `/products/<id>/` | Get detailed product by ID | None |
| **PUT** | `/products/<id>/` | Update specific product by ID | Updated JSON payload |
| **DELETE** | `/products/<id>/` | Soft delete product by ID | None |

---

## ⚙️ Local Setup Instructions

### 1. Clone the Repository
```bash
git clone <YOUR_REPOSITORY_URL>
cd openshop
