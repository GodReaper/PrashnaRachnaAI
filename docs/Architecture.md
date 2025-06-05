
````markdown
# Question Generator Platform Architecture (Updated)

This document outlines the architecture for the question generation platform, incorporating the App Router, Clerk authentication on both frontend and backend, a public landing page, and a user interface to upload and generate questions.

## Overview

The platform allows users to upload documents, select question types (MCQ, Fill-in-the-Blank, etc.), and generate questions based on Bloom’s Taxonomy levels. Each question generation task is powered by a dedicated agent using an LLM. The system includes semantic chunking, concept-linking, curriculum alignment, and quality refinement based on user feedback.

### Components
1. **Frontend**: Next.js (with Clerk for Authentication)
2. **Backend**: FastAPI (with LangChain for Document Processing, Clerk for backend auth)
3. **Database**: PostgreSQL for persistent storage
4. **Vector Store**: ChromaDB for semantic search
5. **AI Agents**: CrewAI for question generation
6. **AI Models**: Ollama for LLM tasks

## File + Folder Structure

```plaintext
├── /client                    # Next.js frontend
│   ├── /app                 
│   │   ├── /api               # API routes (for auth, question generation)
│   │   ├── /auth              # Authentication (using Clerk)
│   │   ├── /question          # Question-related pages (e.g., display questions, settings)
│   │   ├── /landing           # Landing page (public)
│   ├── /components            # UI components (buttons, forms, etc.)
│   ├── /styles                # Tailwind CSS or custom styles
├── /backend                   # FastAPI backend
│   ├── /app                    # Core application logic
│   │   ├── /models             # Database models (PostgreSQL)
│   │   ├── /routes             # API routes (user actions, question generation)
│   │   ├── /services           # Business logic (question generation, document parsing)
│   │   ├── /agents             # AI agents for question generation
│   ├── /config                 # Configuration (e.g., database, external APIs)
│   ├── /utils                  # Utility functions (e.g., chunking, semantic search)
│   ├── /auth                   # Backend authentication (using Clerk)
├── /db                         # Database-related files (PostgreSQL, Neo4j for graphs)
│   ├── /migrations             # Database migrations
│   ├── /schema                 # Database schema files
├── /docs                       # Document processing files (parsing logic, language models)
│   ├── /parsers                # Logic for parsing DOCX, PDF, PPTX files
│   ├── /chunkers               # Semantic chunking and splitting
├── /logs                       # Logs for debugging and analytics
├── /tests                      # Unit and integration tests
````

## Service Breakdown

### 1. **Frontend (Next.js + App Router)**

* **Role**: Provides the user interface for interacting with the platform.
* **Main Actions**:

  * **Landing Page**: A public landing page that is accessible to all users.
  * **Authentication**: Using Clerk for sign-in/sign-up.
  * **Document Upload & Question Generation**: After authentication, users can upload documents, select question types, and generate questions.
  * **Sidebar with Previous Questions**: On the left sidebar, users can see a list of previously generated questions.
  * **Question Display**: Users can view, edit, upvote/downvote, and provide feedback on generated questions.
* **State Management**: Client-side state managed by React context or Redux for handling authentication state, question data, document upload, and previous questions.
* **Integration**:

  * **Clerk for Authentication**: The frontend uses Clerk for handling user authentication.
  * **FastAPI Backend**: Frontend communicates with the backend for generating questions and managing feedback.
  * **API Routes**: Use Next.js App Router to manage routes for different pages, including `/auth`, `/landing`, `/question`, and `/upload`.

### 2. **Backend (FastAPI + LangChain + Clerk)**

* **Role**: Handles user requests, processes documents, generates questions, and stores/retrieves data.
* **Main Actions**:

  * **Authentication**: Clerk is used for user authentication. JWT tokens are issued after login.
  * **Document Upload & Parsing**: Uploaded documents are parsed and chunked using LangChain and stored in PostgreSQL (for meta-data) and ChromaDB (for vectorized document content).
  * **Question Generation**: Depending on the question type selected by the user, the backend triggers the corresponding agent (CrewAI). The agent uses the uploaded documents to generate relevant questions.
  * **Feedback Collection**: User feedback on question difficulty and quality is recorded in PostgreSQL and used to refine question generation in future requests.
  * **Previous Questions**: Backend retrieves and stores previously generated questions for display in the frontend sidebar.
* **Integration**:

  * **Clerk for Authentication**: Clerk’s API is used to manage authentication in the backend as well.
  * **CrewAI** for question generation via external APIs.
  * **PostgreSQL** for storing feedback, documents, and metadata.
  * **ChromaDB** for vector search and question retrieval.
  * **Neo4j** for managing concept-skill-assessment linkages and tracking user progression.

### 3. **Database (PostgreSQL + Neo4j + ChromaDB)**

* **Role**: Stores persistent data and facilitates question retrieval and user progression.
* **PostgreSQL**:

  * Stores user data, file metadata, and question histories (e.g., upvotes, edits).
* **Neo4j**:

  * Stores concept, skill, and assessment relationships to map user progression and curriculum alignment.
* **ChromaDB**:

  * Vector store for semantic search and efficient retrieval of document chunks related to user queries.

### 4. **AI Agents (CrewAI + Ollama LLMs)**

* **Role**: Generate questions using different agents, each specialized in a question type or Bloom’s taxonomy level.
* **Integration**:

  * CrewAI routes the request to the correct agent depending on the selected question type or Bloom’s taxonomy level.
  * Ollama provides the underlying LLMs used by the agents for question generation.
  * The agents ensure high-quality questions based on user feedback.

### 5. **Document Parsing & Semantic Chunking (LangChain)**

* **Role**: Processes uploaded documents to break them down into meaningful chunks for question generation.
* **Main Actions**:

  * Documents are parsed into text using libraries like PDFPlumber for PDFs and python-docx for DOCX.
  * Text is chunked semantically using the `RecursiveCharacterTextSplitter` from LangChain.

## Data Flow & Services Connection

1. **User Uploads Documents**:

   * The frontend handles document upload and sends it to the backend (FastAPI).
   * FastAPI processes the document using LangChain and stores document chunks in ChromaDB and metadata in PostgreSQL.

2. **Question Generation**:

   * After authentication, the user selects a question type or Bloom’s taxonomy level.
   * The frontend sends the request to the backend, where CrewAI triggers the corresponding agent to generate questions using the LLM (Ollama).
   * Generated questions are sent back to the frontend.

3. **Sidebar with Previous Questions**:

   * The frontend displays a sidebar with previously generated questions fetched from the backend (stored in PostgreSQL).
   * Users can upvote, downvote, or edit questions, and their feedback is sent back to the backend for future refinement.

4. **Feedback and Refinement**:

   * Users provide feedback on question difficulty and quality (Too Easy / Too Hard / Just Right).
   * Feedback is stored in PostgreSQL and used to refine future question generation.

5. **User Progression and Concept Mapping**:

   * The system tracks user progression through concepts (Neo4j).
   * If a user has mastered a concept (X), the platform generates questions for the next level (X+1) based on progression patterns.

## State Management

* **Frontend**: React context or Redux will manage the UI states like logged-in user, question data, feedback data, document upload progress, and previous questions.
* **Backend**: State management is handled by PostgreSQL for storing documents and feedback data. Neo4j is used for managing user progression and relationships between concepts and assessments.
* **Authentication**: Clerk’s JWT tokens are used for managing user sessions on both the frontend and backend.

## Conclusion

This architecture provides a clear structure for building a robust question generation platform. It integrates modern technologies such as Clerk for authentication, LangChain for document processing, and CrewAI for question generation. The platform ensures a seamless user experience with semantic chunking, personalized question generation, and continuous feedback for quality refinement.

```

```
