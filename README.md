# 🏭 FoundryMind AI
### Manufacturing Quality Intelligence Powered by Hindsight

FoundryMind AI is an AI-powered manufacturing quality intelligence system that helps organize production incidents, retrieve historical experience, and generate investigation reports.

It uses **Hindsight** as a memory layer to retain and recall past manufacturing incidents and investigation outcomes. **Groq LLM** uses the retrieved context to generate structured investigation reports.

## 🎯 Problem Statement

Manufacturing environments experience recurring quality issues. Investigating these incidents can be difficult when previous observations and investigation outcomes are scattered or forgotten.

FoundryMind AI aims to make historical manufacturing knowledge easier to retrieve and use during quality investigations.

## 💡 Our Solution

FoundryMind AI provides five main modules:

1. **Record Incident** – Record manufacturing defects and incident details.
2. **Ask Memory** – Retrieve relevant historical incidents using Hindsight.
3. **Investigation Assistant** – Generate AI-assisted investigation reports using retrieved memories.
4. **Investigation Outcome** – Save investigation outcomes and verification status back into memory.
5. **Quality Dashboard** – View incident statistics, defect distribution, investigation status, and history.

## 🧠 How Hindsight Works

Hindsight acts as the long-term memory layer of FoundryMind AI.

- **Retain:** Store manufacturing incidents and investigation outcomes.
- **Recall:** Retrieve relevant historical information for a new incident.
- **Reflect:** Use retrieved experience to support an AI-generated investigation report.
- **Learn from outcomes:** Store subsequent investigation outcomes so they can inform future investigations.

The system uses historical context to support investigation. AI-generated hypotheses are suggestions, not confirmed root causes.

## 🏗️ Architecture

```text
Manufacturing Incident
        |
        v
  Streamlit Interface
        |
        v
   Hindsight Memory
   (Retain / Recall)
        |
        v
 Retrieved Context
        |
        v
   Groq LLM
        |
        v
Investigation Report
        |
        v
 Investigation Outcome
        |
        v
 Hindsight Memory
        |
        v
   Quality Dashboard
```

## 🛠️ Technology Stack

- Python
- Streamlit
- Hindsight
- Groq API
- python-dotenv
- JSON-based local dashboard records

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FoundryMind-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project directory:

```env
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
GROQ_API_KEY=your_groq_api_key
```

Never commit your actual `.env` file or API keys to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal.

## 📊 Key Features

- Manufacturing incident recording
- Historical memory retrieval
- AI-assisted investigation reports
- Investigation outcome tracking
- Quality analytics dashboard
- Downloadable investigation reports

## 🚀 Future Improvements

- Computer vision-based defect detection
- Integration with manufacturing inspection systems
- Advanced defect trend analysis
- More detailed investigation verification workflows
- Integration with industrial data sources

## ⚠️ Disclaimer

FoundryMind AI is a prototype for manufacturing quality intelligence. Its AI-generated investigation reports provide decision-support suggestions and do not replace expert engineering inspection or verified root-cause analysis.

## 👥 Team

**Team Nexora**

Built for the AI Agents That Learn Using Hindsight hackathon.