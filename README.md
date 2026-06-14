# 💼 AI-Powered Job Market Intelligence Platform

An interactive data-driven career strategy optimization application designed for **Analyst Trainee** candidates to evaluate skill alignment and market compensation data.

The platform queries a local data warehouse and integrates with a generative language engine to automate skill gap discovery and target regional hiring markets.

---

## 🚀 Core Architectural Features

* **Relational Database Layer (SQL):** Connects securely via a Python DBAPI driver to a custom schema containing regional hiring distributions, application densities, and skill pairings.
* **Dynamic Data Visualizations:** Implements dual-axis and horizontal frequency tracking charts via Plotly to evaluate salary ranges (LPA) against competition levels.
* **Calibrated Profile Scoring:** Uses a weighted data-coefficient matrix to calculate realistic, credible market fit scores (bounded appropriately up to an 82% baseline ceiling) instead of arbitrary perfect metrics.
* **Secure Credential Masking:** Features state-managed interface abstractions that automatically swap active text entry inputs for secure network badges once a connection is validated.
* **GenAI Production Pipeline:** Orchestrates data payloads directly into the `gemini-2.5-flash` model structure with built-in fault-tolerant error handlers to gracefully process heavy traffic.

---

## 🛠️ Technology Stack & Libraries

* **Core Language:** Python 3.11+
* **Database Management:** MySQL Server
* **Web UI Framework:** Streamlit Framework
* **Visualizations:** Plotly (Express & Graph Objects)
* **Data Manipulation:** Pandas DataFrames
* **AI Model Engine:** Google Gemini SDK (`google-genai`)

---

## 💻 Local Installation & Setup Run Guide

### 1. Prerequisites
Ensure you have a running MySQL Server instance with your structured analytical tables loaded into a schema named `job_market_db`.

### 2. Environment Setup
Clone this repository, navigate to the folder, and install the execution dependencies inside your environment terminal:
```bash
pip install streamlit plotly pandas mysql-connector-python google-genai
