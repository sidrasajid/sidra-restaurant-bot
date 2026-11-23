# 🍽️ Restaurant Concierge AI

An AI-powered restaurant assistant built with Python, FastAPI, WebSockets, and Large Language Models (LLMs). The chatbot helps restaurant guests with menu-related questions, restaurant information, table availability, and frequently asked questions.

## 🚀 Project Features

- **AI Chatbot:** Conversational restaurant assistant.
- **WebSocket Communication:** Real-time communication between frontend and backend.
- **Conversation Memory:** Maintains conversation history during an active chat session.
- **Function Calling:** Uses custom tools to check table availability.
- **RAG (Retrieval-Augmented Generation):** Searches restaurant FAQs to provide relevant answers.
- **FAQ Knowledge Base:** Uses a JSON file containing restaurant frequently asked questions.
- **Simple Web Interface:** HTML, CSS, and JavaScript-based chat interface.
- **Multiple AI Providers:** Supports OpenAI and Gemini integration, depending on configuration and availability.

## 🛠️ Technologies Used

- Python
- FastAPI
- WebSockets
- OpenAI API
- Google Gemini API
- HTML
- CSS
- JavaScript
- ChromaDB
- JSON
- Uvicorn

## 📁 Project Structure

```text
Resturant-bot/
│
├── main.py
├── index.html
├── faqs.json
├── faq_search.py
├── ingest.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── chroma_db/
│
└── .venv/
```

Note: `.venv/` and `chroma_db/` are local environment/data folders. They should not be committed to GitHub unless specifically required.

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Resturant-bot
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can use the virtual environment's Python executable directly.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Keys

Create a `.env` file in the project root directory.

Add the API key or keys required by your configured provider:

```env
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

Use valid API credentials. Never upload your `.env` file or expose API keys publicly.

### 6. Prepare the FAQ Knowledge Base

Run the ingestion script if required:

```powershell
.\.venv\Scripts\python.exe ingest.py
```

This prepares the FAQ data for retrieval.

## ▶️ Running the Application

### 1. Start the FastAPI Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

### 2. Start the Frontend Server

Open a second PowerShell window:

```powershell
cd D:\Resturant-bot
.\.venv\Scripts\python.exe -m http.server 5500
```

### 3. Open the Chat Interface

Open the following URL in your browser:

```text
http://127.0.0.1:5500/index.html
```

The frontend connects to the backend using a WebSocket connection.

## 🧠 Core Functionalities

### 1. Conversation Memory

The chatbot maintains conversation history during an active WebSocket session, allowing it to understand follow-up questions and maintain conversational context.

### 2. Function Calling

The chatbot can call custom Python functions, including:

- `check_table(date, guests)`

This function is designed to check table availability based on the requested date and number of guests.

### 3. Retrieval-Augmented Generation (RAG)

The project includes a restaurant FAQ knowledge base.

Relevant files:

- `faqs.json`
- `ingest.py`
- `faq_search.py`

The chatbot retrieves relevant FAQ information to help answer restaurant-related questions.

## 🧪 Testing

The project includes test scripts for checking chatbot functionality and backend responses.

Run the relevant test script using:

```powershell
.\.venv\Scripts\python.exe .\test-client-openai.py
```

Other available test scripts can be run similarly.

## 🔐 Security Notes

- Never commit `.env` files.
- Never expose API keys in source code.
- Keep virtual environments out of GitHub.
- Use `.env.example` to document required environment variables.
- Configure API billing or provider quotas before running live AI requests.

## 📌 Day 5 Deliverables

- [x] FastAPI backend
- [x] WebSocket chat functionality
- [x] HTML-based chatbot interface
- [x] Conversation memory implementation
- [x] Custom function calling
- [x] FAQ retrieval and RAG implementation
- [x] README documentation

## 🎯 Project Objective

The objective of this project is to develop a restaurant concierge chatbot capable of assisting guests through natural language conversations, retrieving relevant restaurant information, and performing basic restaurant-related operations using AI-powered tools.

## 👨‍💻 Author

Developed as part of the Zigron AI Engineering Internship — 5-Day Chatbot Sprint.

**Project:** Restaurant Concierge AI