# AfterSaleAgent

AfterSaleAgent is a B2B ecommerce after-sales agent backend project.

It helps merchant support teams handle refund, return, shipment, compensation, and after-sales ticket requests by combining:

- FastAPI backend APIs
- PostgreSQL business data
- pgvector knowledge retrieval
- LangGraph agent workflow
- DeepSeek model integration
- tool calling
- human approval
- audit logs
- streaming run events

The project is designed as a portfolio-grade backend + agent application for Python developers applying to Agent application development roles.

## Project Goal

Build a production-style backend system where a customer service operator can ask:

> Order 10086 was delivered two days ago. The customer wants a refund. Can we refund it directly?

The system should:

1. Parse the user's intent and order id.
2. Query order, payment, shipment, and product data.
3. Retrieve after-sales policy documents.
4. Assess refund risk.
5. Create a refund request, after-sales ticket, or approval request.
6. Stream every agent step back to the client.
7. Persist all runs, steps, tool calls, approvals, and audit logs.

## Documentation

Start here:

- [中文项目开发总文档](docs/项目开发总文档.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)

The guides include product requirements, architecture, database design, API list, LangGraph workflow, development schedule, demo cases, and frontend AI prompts.

## Recommended Stack

- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0 async
- Alembic
- PostgreSQL
- pgvector
- Redis
- ARQ or Celery
- LangGraph
- LiteLLM
- DeepSeek API
- pytest
- ruff
- Docker Compose

## MVP Demo Cases

1. Normal refund: delivered 2 days ago, low amount, ordinary product.
2. High-value refund: high amount, requires manager approval.
3. Non-refundable item: virtual or fresh product, rejected based on policy.
