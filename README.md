#  RAG-NL2SQL-Agent  
### Multi-Agent NLP-to-SQL System with RAG, RBAC & Snowflake Integration

An end-to-end GenAI-powered system that converts natural language queries into secure, validated SQL statements using a Retrieval-Augmented Generation (RAG) pipeline and executes them in Snowflake with role-based access control.

---

##  Overview

This project enables non-technical users to query structured databases using plain English.

The system translates user intent into optimized SQL queries, validates them for safety, enforces role-based permissions, executes them in Snowflake, and generates AI-powered analytical summaries with visualizations.

---

## System Architecture

The pipeline follows a multi-stage orchestration process:

1. User Login (Admin / Analyst / Finance)
2. Natural Language Query Input
3. Context Retrieval (RAG + Vector Embeddings)
4. SQL Generation via LLM
5. SQL Safety Validation (Blocks UPDATE, DELETE, ALTER)
6. Role-Based Access Check (RBAC)
7. Secure Execution in Snowflake
8. AI-Generated Analytical Summary + Visualization

---

##  Key Features

- RAG-based schema-aware SQL generation  
- Multi-agent AI architecture (Planner, Validator, Optimizer)  
- Role-Based Access Control (Admin, Analyst, Finance)  
- SQL sanitization and validation layer  
- Snowflake database integration  
- AI reasoning visibility (confidence, plan, performance tips)  
- Interactive charts and tabular outputs  
- Admin panel for user management  

---

## 🛠 Tech Stack

- Python  
- Snowflake  
- OpenAI / LLM APIs  
- Dify (Workflow-based RAG orchestration)  
- Vector Embeddings  
- SQL  
- Role-Based Access Control (RBAC)  

---

## 📂 Project Structure

