# ExpenseIQ — Intelligent Expense Categorization & Budget Monitoring System

## Overview

**ExpenseIQ** is an AI-powered expense management system that automatically categorizes expenses using a Large Language Model (LLM) and monitors spending against predefined budgets. The system provides real-time analytics, visual dashboards, and budget alerts to help organizations track financial activity efficiently.

This project was developed as part of a **backend engineering hackathon / internship evaluation**, demonstrating skills in API design, database integration, AI integration, and full-stack system development.

---

## Key Features

* AI-powered expense categorization using an LLM
* Real-time expense tracking
* Budget monitoring and alerts
* Interactive analytics dashboard
* Employee-wise expense analysis
* RESTful API architecture
* PostgreSQL database integration
* Clean modular backend design
* Automatic dashboard updates

---

## Tech Stack

### Backend

* FastAPI
* Python
* SQLAlchemy (ORM)
* Pydantic
* Uvicorn

### Database

* PostgreSQL

### AI / LLM

* OpenAI API
* Natural language expense classification

### Frontend

* HTML
* CSS
* JavaScript
* Chart.js

### Tools

* Git
* GitHub
* VS Code
* Virtual Environment (venv)

---

## System Architecture

User → Frontend Dashboard → FastAPI Backend → LLM Agent → PostgreSQL Database → Budget Manager → Analytics Dashboard

---

## Project Structure

```
expense-categorizer/
│
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── llm.py               # LLM categorization logic
│   ├── budget_manager.py    # Budget control logic
│   └── __init__.py
│
├── frontend/
│   └── index.html           # Dashboard UI
│
├── .env                     # Environment variables
├── requirements.txt
└── README.md
```

---

## LLM Agent — Expense Categorization

The system uses a Large Language Model to automatically classify expenses into predefined categories.

### Categories

* Travel
* Software
* Office
* Meals
* Other

### Example

Input:

```
Cab from airport to Pune
```

Output:

```
Travel
```

---

## API Endpoints

### Create Expense

POST `/expenses`

Request:

```json
{
  "description": "Lunch at restaurant",
  "amount": 250,
  "employee_id": "EMP001"
}
```

Response:

```json
{
  "category": "Meals",
  "amount": 250
}
```

---

### Get All Expenses

GET `/expenses`

---

### Expense Summary

GET `/expenses/summary`

Returns category totals.

---

### Analytics

GET `/expenses/analytics`

Returns:

```json
{
  "total_expense": 12000,
  "average_expense": 2400,
  "max_expense": 5000,
  "transaction_count": 5
}
```

Used for:

* KPI cards
* Analytics charts

---

### Employee Breakdown

GET `/expenses/employee/{employee_id}`

---

### Budget Monitoring

GET `/budgets`

Returns:

```json
{
  "Travel": {
    "budget": 10000,
    "spent": 7500,
    "alert": "Within budget"
  }
}
```

---

## Budget Configuration

Budgets are controlled directly in:

```
budget_manager.py
```

Example:

```python
BUDGETS = {
    "Travel": 10000,
    "Software": 100000,
    "Office": 10000,
    "Meals": 10000,
    "Other": 100000
}
```

To change budgets:

1. Edit values in `budget_manager.py`
2. Restart the server

---

## Installation

### 1. Clone the Repository

```
git clone https://github.com/pranavsomawar17/ExpenseIQ.git
cd ExpenseIQ
```

---

### 2. Create Virtual Environment

```
python -m venv venv
```

Activate:

Linux / Mac:

```
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate
```

---

### 3. Install Dependencies

```
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create `.env` file:

```
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
OPENAI_API_KEY=your_openai_api_key
```

---

### 5. Run Server

```
python -m uvicorn app.main:app --reload
```

---

### 6. Open Dashboard

```
http://127.0.0.1:8000
```

or open:

```
frontend/index.html
```

---

## Database Tables

### expenses

```
id
employee_id
description
amount
category
created_at
```

### budget_alerts

```
id
department
budget
spent
alert
created_at
```

---

## Workflow

1. User enters expense
2. Frontend sends request to API
3. Backend calls LLM
4. LLM categorizes expense
5. Expense stored in database
6. Budget updated
7. Dashboard refreshes

---

## Example System Flow

Input:

```
Airport to Pune
Amount: 800
Employee: EMP001
```

System:

```
LLM → Travel
Database updated
Budget checked
Dashboard updated
```

## Author

Pranav Somawar , Pratiksha Pawar

---
