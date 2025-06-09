// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types for API responses
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface Question {
  id: string;
  question: string;
  type: string;
  correct_answer: string | string[] | Record<string, string>;
  options?: Record<string, string> | string[];
  explanation?: string;
  bloom_level?: string;
  difficulty?: string;
  topic?: string;
  upvotes?: number;
  downvotes?: number;
  created_at: string;
  document_id?: string;
}

export interface QuestionGenerationRequest {
  document_ids: string[];
  question_type?: string;
  bloom_level?: string;
  difficulty?: string;
  num_questions?: number;
  model?: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  processing_status: string; // "completed", "processing", "failed", "pending"
  chunk_count?: number;
  error_message?: string;
  parsing_result?: {
    success: boolean;
    chunks_created: number;
    processing_time: number;
    message: string;
  };
}

export interface QuestionMetadata {
  generation_time: number;
  model?: string;
  question_type: string;
  bloom_level: string;
  difficulty: string;
  num_requested: number;
  num_generated: number;
  content_chunks_used: number;
  user_id: string;
  questions_stored: number;
  documents_used: Array<{ id: string; filename: string }>;
}

export interface QuestionPagination {
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface OllamaModel {
  name: string;
  size: number;
  modified_at: string;
}

// API client class
class ApiClient {
  private baseURL: string;

  // This will be set by the component that uses the API client
  private authToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  public setAuthToken(token: string | null) {
    this.authToken = token;
  }

  private async getAuthToken(): Promise<string | null> {
    return this.authToken;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const token = await this.getAuthToken();
      
      const config: RequestInit = {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
      };

      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (errorData.error) {
            errorMessage = errorData.error;
          }
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return {
        success: true,
        data: data
      };
    } catch (error) {
      let errorMessage = 'Unknown error occurred';
      
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (error && typeof error === 'object') {
        // Handle error objects properly
        if ('message' in error) {
          errorMessage = String(error.message);
        } else if ('detail' in error) {
          errorMessage = String(error.detail);
        } else {
          errorMessage = JSON.stringify(error);
        }
      }
      
      console.error(`API Error (${endpoint}):`, error);
      return {
        success: false,
        error: errorMessage
      };
    }
  }

  // Document API methods
  async uploadDocument(file: File): Promise<ApiResponse<Document>> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = await this.getAuthToken();
      
      const response = await fetch(`${this.baseURL}/documents/upload`, {
        method: 'POST',
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data
      };
    } catch (error) {
      console.error('Upload error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed'
      };
    }
  }

  async getDocuments(): Promise<ApiResponse<Document[]>> {
    return this.makeRequest<Document[]>('/documents/');
  }

  async getDocument(documentId: string): Promise<ApiResponse<Document>> {
    return this.makeRequest<Document>(`/documents/${documentId}`);
  }

  async deleteDocument(documentId: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  async parseDocument(documentId: string): Promise<ApiResponse<{
    success: boolean;
    chunks_created: number;
    processing_time: number;
    message: string;
  }>> {
    return this.makeRequest(`/documents/${documentId}/parse`, {
      method: 'POST',
    });
  }

  async getDocumentChunks(documentId: string): Promise<ApiResponse<{
    document_id: number;
    total_chunks: number;
    chunks: Array<{
      id: string;
      text: string;
      metadata: Record<string, unknown>;
    }>;
  }>> {
    return this.makeRequest(`/documents/${documentId}/chunks`);
  }

  // Question API methods
  async generateQuestions(request: QuestionGenerationRequest): Promise<ApiResponse<{
    questions: Question[];
    metadata: QuestionMetadata;
  }>> {
    const result = await this.makeRequest<{
      questions: Question[];
      metadata: QuestionMetadata;
    }>('/questions/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return result;
  }

  async getQuestions(params?: {
    skip?: number;
    limit?: number;
    question_type?: string;
    bloom_level?: string;
    difficulty?: string;
  }): Promise<ApiResponse<{
    questions: Question[];
    pagination: QuestionPagination;
  }>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/questions/${searchParams.toString() ? `?${searchParams}` : ''}`;
    return this.makeRequest(endpoint);
  }

  async getQuestion(questionId: string): Promise<ApiResponse<{
    question: Question;
  }>> {
    return this.makeRequest(`/questions/${questionId}`);
  }

  async submitQuestionFeedback(
    questionId: string,
    feedback: {
      vote?: string;
      difficulty_rating?: number;
      quality_rating?: number;
      comments?: string;
      is_helpful?: boolean;
      is_accurate?: boolean;
    }
  ): Promise<ApiResponse<void>> {
    return this.makeRequest(`/questions/${questionId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  async deleteQuestion(questionId: string): Promise<ApiResponse<void>> {
    return this.makeRequest(`/questions/${questionId}`, {
      method: 'DELETE',
    });
  }

  // System API methods
  async getSupportedQuestionTypes(): Promise<ApiResponse<{
    question_types: string[];
    bloom_levels: string[];
    difficulty_levels: string[];
  }>> {
    return this.makeRequest('/questions/types/supported');
  }

  async getOllamaStatus(): Promise<ApiResponse<{
    ollama_healthy: boolean;
    models: OllamaModel[];
    service_url: string;
  }>> {
    return this.makeRequest('/questions/ollama/status');
  }

  async pullOllamaModel(modelName: string): Promise<ApiResponse<void>> {
    return this.makeRequest('/questions/ollama/pull-model', {
      method: 'POST',
      body: JSON.stringify({ model_name: modelName }),
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export individual API functions for convenience
export const {
  uploadDocument,
  getDocuments,
  getDocument,
  deleteDocument,
  generateQuestions,
  getQuestions,
  getQuestion,
  submitQuestionFeedback,
  deleteQuestion,
  getSupportedQuestionTypes,
  getOllamaStatus,
  pullOllamaModel,
} = apiClient; 