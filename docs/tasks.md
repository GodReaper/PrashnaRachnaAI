
---

## **Granular Step-by-Step MVP Plan with Validation**

---

### **Frontend Tasks (Next.js with Clerk and Zod Validation)**

#### 1. **Set up Next.js Project**

* **Start**: Initialize a new Next.js project.
* **End**: Verify that the app runs locally (`npm run dev`).
* **Test**: Open the app in a browser to confirm that the default Next.js page loads.

#### 2. **Install Clerk for Authentication**

* **Start**: Install Clerk (`@clerk/nextjs`).
* **End**: Add Clerk’s API keys to the environment variables.
* **Test**: Ensure Clerk authentication works by displaying the login form on the homepage.

#### 3. **Create Landing Page**

* **Start**: Create a `/landing` page accessible to all users.
* **End**: Add basic content (e.g., platform description, CTA).
* **Test**: Visit `/landing` in a browser to verify it’s publicly accessible.

#### 4. **Add Sign-Up and Sign-In Pages (Clerk)**

* **Start**: Create `SignUp` and `SignIn` pages using Clerk components.
* **End**: Implement sign-up/sign-in forms and ensure successful login.
* **Test**: Test the login flow, ensuring users can sign up and log in.

#### 5. **Create the App Router with Protected Routes**

* **Start**: Set up App Router in Next.js to handle routing.
* **End**: Add a route for the logged-in user to upload documents and generate questions.
* **Test**: Test routing with Clerk to ensure routes are protected and only accessible after authentication.

#### 6. **Create UI for Document Upload with Validation**

* **Start**: Create a component for document upload.
* **End**: Add a form where users can upload documents (PDF, DOCX, PPTX).
* **Validation**: Use Zod to validate that the uploaded file is of the correct type (PDF, DOCX, PPTX).

  ```javascript
  import { z } from "zod";

  const fileUploadSchema = z.object({
    file: z
      .instanceof(File)
      .refine((file) => ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.ms-powerpoint"].includes(file.type), {
        message: "File type must be PDF, DOCX, or PPTX"
      }),
  });
  ```
* **Test**: Ensure validation catches invalid file types and shows an error message.

#### 7. **Implement Left Sidebar to Display Previous Questions**

* **Start**: Create a left sidebar layout in the UI.
* **End**: Fetch and display previously generated questions from the backend.
* **Test**: Ensure the sidebar displays correctly and fetches question data from the backend.

#### 8. **Add Question Generation UI with Validation**

* **Start**: Create a UI for selecting question type (MCQ, Fill-in-the-Blank, etc.).
* **End**: Connect this UI to the backend for generating questions.
* **Validation**: Use Zod to validate the selection for question type and Bloom's Taxonomy level.

  ```javascript
  const questionGenerationSchema = z.object({
    questionType: z.enum(["MCQ", "FillInTheBlank", "TrueFalse"]),
    bloomLevel: z.enum(["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]),
  });
  ```
* **Test**: Test by selecting different question types and Bloom's levels, ensuring only valid selections are allowed.

---

### **Backend Tasks (FastAPI, LangChain, Clerk, and Pydantic Validation)**

#### 9. **Set up FastAPI Project**

* **Start**: Initialize a FastAPI project.
* **End**: Create a basic route that returns a "Hello World" message.
* **Test**: Visit the API endpoint in the browser (`localhost:8000`) to confirm the API is running.

#### 10. **Install and Configure Clerk for Backend Authentication**

* **Start**: Install Clerk SDK for FastAPI and configure authentication.
* **End**: Implement JWT token verification for secured routes.
* **Test**: Test that only authenticated users can access protected backend routes.

#### 11. **Create Document Upload API Endpoint with Validation**

* **Start**: Implement an API endpoint for document uploads.
* **Validation**: Use Pydantic for validating the uploaded file’s MIME type.

  ```python
  from pydantic import BaseModel, Field

  class FileUpload(BaseModel):
      file_type: str = Field(..., regex=r"(pdf|docx|pptx)")

  @app.post("/upload")
  async def upload_file(file: UploadFile = File(...)):
      file_upload = FileUpload(file_type=file.content_type)
      # Validation will automatically raise an error if the file type is not valid
      return {"filename": file.filename}
  ```
* **Test**: Upload a document through the frontend and confirm it’s saved and parsed, checking for file type validation.

#### 12. **Implement Document Parsing Logic (LangChain)**

* **Start**: Use LangChain to parse uploaded documents (PDF, DOCX, PPTX).
* **End**: Parse the document and chunk it into semantic sections.
* **Test**: Upload a sample document and check that it’s parsed into meaningful chunks.

#### 13. **Store Parsed Documents in ChromaDB and PostgreSQL**

* **Start**: Set up ChromaDB for semantic search and PostgreSQL for metadata storage.
* **End**: Store the parsed document chunks in ChromaDB and metadata in PostgreSQL.
* **Test**: Ensure that documents are saved in ChromaDB and PostgreSQL after parsing.

#### 14. **Create Question Generation API Endpoint with Validation**

* **Start**: Create an endpoint for generating questions based on document content.
* **Validation**: Use Pydantic to validate incoming question generation data.

  ```python
  from pydantic import BaseModel
  from typing import Literal

  class QuestionGeneration(BaseModel):
      question_type: Literal["MCQ", "FillInTheBlank", "TrueFalse"]
      bloom_level: Literal["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
  ```
* **Test**: Ensure that invalid question types or Bloom's Taxonomy levels are rejected with appropriate error responses.

#### 15. **Store Generated Questions in PostgreSQL**

* **Start**: Store generated questions along with metadata (upvotes, edits, difficulty).
* **End**: Implement a schema to save questions, feedback, and history in PostgreSQL.
* **Test**: Verify that questions and their metadata are stored correctly in the database.

#### 16. **Implement Feedback Collection API**

* **Start**: Implement an endpoint to collect feedback on questions (upvote, difficulty rating).
* **End**: Store the feedback in PostgreSQL.
* **Test**: Ensure feedback (upvote/downvote, difficulty) is stored and can be retrieved.

#### 17. **Fetch Previous Questions for Sidebar**

* **Start**: Create an API endpoint to fetch previously generated questions.
* **End**: Retrieve questions based on user ID and return them to the frontend.
* **Test**: Ensure that previously generated questions are fetched and displayed correctly in the sidebar.

---

### **Database & Storage Tasks (PostgreSQL, ChromaDB, Neo4j)**

#### 18. **Set up PostgreSQL Database**

* **Start**: Initialize a PostgreSQL database and configure tables for storing user data, document metadata, and questions.
* **End**: Implement schema for user authentication, documents, and question storage.
* **Test**: Verify the database schema and ensure data can be inserted and queried.

#### 19. **Set up ChromaDB for Vector Storage**

* **Start**: Install and configure ChromaDB for semantic search.
* **End**: Store document chunks as vectors in ChromaDB.
* **Test**: Ensure that documents are correctly vectorized and stored in ChromaDB.

---

### **Integration & Testing Tasks**

#### 21. **Integrate Frontend with Backend (Document Upload & Question Generation)**

* **Start**: Connect the document upload and question generation features from the frontend to the backend.
* **End**: Ensure the frontend can upload documents, receive questions, and display them.
* **Test**: Test the complete flow from document upload to question generation.

#### 22. **Test User Authentication & Permissions**

* **Start**: Verify that Clerk authentication works end-to-end (frontend and backend).
* **End**: Ensure that only authenticated users can access question upload and generation features.
* **Test**: Test login/logout functionality and protected routes.

#### 23. **Test Document Parsing and Chunking**

* **Start**: Upload sample documents and test the parsing and chunking logic.
* **End**: Ensure documents are correctly parsed into chunks and saved in ChromaDB/PostgreSQL.
* **Test**: Verify that document chunks are stored in the vector store and metadata is saved in PostgreSQL.

#### 24. **Test Question Generation & Feedback Collection**

* **Start**: Generate questions using different types (MCQ, Fill-in-the-Blank, Bloom’s Taxonomy levels).
* **End**: Collect and store user feedback on question difficulty and quality.
* **Test**: Test generating questions, upvoting, downvoting, and providing feedback.

---

### **Final Testing and QA Tasks**

#### 25. **Run End-to-End Tests**

* **Start**: Run comprehensive tests to ensure all components work together (frontend, backend, database).
* **End**: Confirm that the document upload, question generation, and feedback system are functioning as expected.
* **Test**: Perform manual testing or automated tests to confirm the MVP works.

#### 26. **Deploy the MVP**

* **Start**: Deploy the MVP to a staging environment (e.g., Vercel for frontend, Heroku for backend).
* **End**: Ensure that the platform is live and accessible to users.
* **Test**: Perform a final check to ensure all features work in the deployed environment.

---