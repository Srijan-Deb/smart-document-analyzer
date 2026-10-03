# Smart Document Analyzer — Frontend

Modern, responsive web interface for the **Smart Document Analyzer (RAG)** application built with Next.js 16 (Turbopack), TypeScript, TailwindCSS, Zustand, and Framer Motion.

## 🚀 Features

- **Document Dashboard**: Drag & drop PDF and TXT file uploads with live processing status.
- **RAG Chat Workspace**: Interactive chat interface with real-time SSE token streaming.
- **Source Citation Cards**: View exact chunk extracts and source file references for every generated answer.
- **Multi-Document Selector**: Filter queries to specific documents or search across all documents.
- **Auth Flow**: Form-validated registration and sign-in with persistent JWT session handling.

## 🛠️ Tech Stack

- **Framework**: Next.js 16 (App Router + Turbopack)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Animations**: Framer Motion
- **State Management**: Zustand
- **Forms & Validation**: React Hook Form + Zod
- **Icons**: Lucide React
- **HTTP Client**: Axios

## 💻 Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment (optional, defaults to `http://localhost:8000/api/v1`):
   ```bash
   cp .env.example .env.local
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Build for production:
   ```bash
   npm run build
   ```
