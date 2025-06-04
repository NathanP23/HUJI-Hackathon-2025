# HUJI Hackathon 2025 Project

### Contributors

* [Nathan Pasder](https://www.linkedin.com/in/nathan-p-6038282b0/) – 3rd year B.Sc Data Science & CS Minor
* [shzmr](https://github.com/shzmr) – 2nd year B.Sc in CS & Minor in Physics
* [Meital Lubarski](https://github.com/Meital-Lubarski) – 2nd year B.Sc in CS
* [Tal Schlezinger](https://github.com/Tal-Schhlezinger) – 2nd year B.Sc in CS
* [Yonatan Zehavi](https://github.com/YonatanZehavi319) – 2nd year B.Sc in CS & Data Science
* [Noam Azoulay](LINK) – 2nd year B.Sc in CS

This project was developed during the 2025 HUJI Hackathon in under 24 hours. It's a proof of concept (PoC) designed to showcase an AI-driven, full-stack application that integrates multiple LLM APIs (OpenAI, Gemini, Claude) into a real-time backend with a React frontend.

As with many hackathon projects, the current codebase is functional but still rough — the backend needs further refactoring, and the overall system architecture would benefit from more time for polish, testing, and optimization.

The GitHub repository reflects our initial sprint and is intended as a starting point for a more complete application.

## Prerequisites

- Python 3.10+
- Node.js 18+

## Backend Setup

1. Install Python dependencies:
   ```bash
   pip install openai google-generativeai anthropic python-dotenv aiohttp python-socketio
   ```
2. Create a `.env` file at the repository root with your API keys:
   ```env
   OPENAI_API_KEY=<your OpenAI key>
   GEMINI_API_KEY=<your Gemini key>
   ANTHROPIC_API_KEY=<your Anthropic key>
   ```
3. Start the backend server:
   ```bash
   python backend/Main.py
   ```
   This runs an aiohttp + Socket.IO server on port `4000`.

## Frontend Setup

1. Install Node dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the React development server:
   ```bash
   npm start
   ```
   The app will open on `http://localhost:3000` and connect to the backend at `http://localhost:4000`.

## Project Structure

- `backend/` – Python server and LLM utilities.
- `frontend/` – React client application.
- `מצגת האקתון.pptx` – Presentation from the hackathon.

