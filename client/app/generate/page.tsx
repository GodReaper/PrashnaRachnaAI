'use client';

import React, { useState } from 'react';
import { DocumentUpload } from '../../components/DocumentUpload';
import { QuestionGeneration } from '../../components/QuestionGeneration';
import { useAuth } from '../../lib/hooks/useAuth';
import { type Document, type Question } from '../../lib/api';
import Link from 'next/link';

export default function GeneratePage() {
  const { isLoaded, isSignedIn } = useAuth();
  const [uploadedDocument, setUploadedDocument] = useState<Document | null>(null);
  const [generatedQuestions, setGeneratedQuestions] = useState<Question[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDocumentUpload = (document: Document) => {
    setUploadedDocument(document);
    setGeneratedQuestions([]); // Clear previous questions
  };

  const handleQuestionsGenerate = (questions: Question[]) => {
    setGeneratedQuestions(questions);
    setIsGenerating(false);
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Please sign in to continue</h1>
          <Link href="/" className="text-blue-600 hover:text-blue-800">
            Go to homepage
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="text-xl font-bold text-gray-800">
                Prashna Rachna AI
              </Link>
              <div className="hidden md:flex space-x-4">
                <Link href="/dashboard" className="text-gray-600 hover:text-gray-800 font-medium">
                  Dashboard
                </Link>
                <Link href="/generate" className="text-blue-600 font-medium">
                  Generate Questions
                </Link>
                <Link href="/questions" className="text-gray-600 hover:text-gray-800 font-medium">
                  My Questions
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Generate Questions from Documents</h1>
          <p className="text-gray-600">
            Upload your document and generate AI-powered questions using advanced language models.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column: Document Upload */}
          <div>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Step 1: Upload Document
              </h2>
              <DocumentUpload 
                onUpload={handleDocumentUpload}
              />
            </div>

            {/* Document Status */}
            {uploadedDocument && (
              <div className={`border rounded-lg p-4 ${
                uploadedDocument.processing_status === 'completed' 
                  ? 'bg-green-50 border-green-200' 
                  : uploadedDocument.processing_status === 'processing'
                  ? 'bg-blue-50 border-blue-200'
                  : uploadedDocument.processing_status === 'failed'
                  ? 'bg-red-50 border-red-200'
                  : 'bg-yellow-50 border-yellow-200'
              }`}>
                <div className="flex items-center">
                  {uploadedDocument.processing_status === 'completed' ? (
                    <svg className="h-5 w-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  ) : uploadedDocument.processing_status === 'processing' ? (
                    <svg className="animate-spin h-5 w-5 text-blue-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : uploadedDocument.processing_status === 'failed' ? (
                    <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  )}
                  <div>
                    <p className={`font-medium ${
                      uploadedDocument.processing_status === 'completed' 
                        ? 'text-green-800' 
                        : uploadedDocument.processing_status === 'processing'
                        ? 'text-blue-800'
                        : uploadedDocument.processing_status === 'failed'
                        ? 'text-red-800'
                        : 'text-yellow-800'
                    }`}>
                      {uploadedDocument.processing_status === 'completed' 
                        ? 'Document processed successfully!' 
                        : uploadedDocument.processing_status === 'processing'
                        ? 'Processing document...'
                        : uploadedDocument.processing_status === 'failed'
                        ? 'Document processing failed'
                        : 'Document uploaded (processing pending)'}
                    </p>
                    <p className={`text-sm ${
                      uploadedDocument.processing_status === 'completed' 
                        ? 'text-green-600' 
                        : uploadedDocument.processing_status === 'processing'
                        ? 'text-blue-600'
                        : uploadedDocument.processing_status === 'failed'
                        ? 'text-red-600'
                        : 'text-yellow-600'
                    }`}>
                      {uploadedDocument.filename} • {(uploadedDocument.file_size / 1024 / 1024).toFixed(2)} MB
                      {uploadedDocument.chunk_count && ` • ${uploadedDocument.chunk_count} chunks created`}
                    </p>
                    {uploadedDocument.processing_status === 'processing' && (
                      <p className="text-blue-600 text-sm mt-1">
                        Extracting text and creating searchable chunks...
                      </p>
                    )}
                    {uploadedDocument.processing_status === 'failed' && uploadedDocument.error_message && (
                      <p className="text-red-600 text-sm mt-1">
                        Error: {uploadedDocument.error_message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Question Generation */}
          <div>
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Step 2: Generate Questions
              </h2>
              <QuestionGeneration
                documentIds={uploadedDocument ? [String(uploadedDocument.id)] : []}
                documentName={uploadedDocument?.filename}
                onGenerate={handleQuestionsGenerate}
                isGenerating={isGenerating}
                documentsReady={uploadedDocument?.processing_status === 'completed'}
              />
            </div>
          </div>
        </div>

        {/* Generated Questions Display */}
        {generatedQuestions.length > 0 && (
          <div className="mt-8">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  Generated Questions ({generatedQuestions.length})
                </h2>
                <Link href="/questions" className="text-blue-600 hover:text-blue-800 font-medium">
                  View All Questions →
                </Link>
              </div>

              <div className="space-y-6">
                {generatedQuestions.map((question, index) => (
                  <div key={question.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                          {index + 1}
                        </span>
                        <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">
                          {question.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        {question.bloom_level && (
                          <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">
                            {question.bloom_level}
                          </span>
                        )}
                        {question.difficulty && (
                          <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                            {question.difficulty}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="mb-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Question:</h3>
                      <p className="text-gray-700">{question.question}</p>
                    </div>

                    {/* Answer Display */}
                    <div className="mb-4">
                      <h4 className="text-md font-medium text-gray-900 mb-2">Answer:</h4>
                      {question.type === 'multiple_choice' && question.options ? (
                        <div className="space-y-2">
                          {typeof question.options === 'object' && !Array.isArray(question.options) ? (
                            Object.entries(question.options).map(([key, value]) => (
                              <div 
                                key={key} 
                                className={`p-2 rounded ${
                                  key === question.correct_answer 
                                    ? 'bg-green-100 border border-green-300' 
                                    : 'bg-gray-50'
                                }`}
                              >
                                <span className="font-medium">{key})</span> {value}
                                {key === question.correct_answer && (
                                  <span className="ml-2 text-green-600 font-medium">✓ Correct</span>
                                )}
                              </div>
                            ))
                          ) : (
                            <p className="text-gray-600">{String(question.correct_answer)}</p>
                          )}
                        </div>
                      ) : (
                        <p className="text-gray-600 bg-green-50 p-3 rounded">
                          {String(question.correct_answer)}
                        </p>
                      )}
                    </div>

                    {/* Explanation */}
                    {question.explanation && (
                      <div className="mb-4">
                        <h4 className="text-md font-medium text-gray-900 mb-2">Explanation:</h4>
                        <p className="text-gray-600 bg-blue-50 p-3 rounded">{question.explanation}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex space-x-4">
                  <button
                    onClick={() => {
                      setGeneratedQuestions([]);
                      setUploadedDocument(null);
                    }}
                    className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded"
                  >
                    Generate New Questions
                  </button>
                  <Link 
                    href="/questions"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
                  >
                    View All My Questions
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading State for Question Generation */}
        {isGenerating && (
          <div className="mt-8">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Generating Questions...</h3>
                <p className="text-gray-600">
                  Our AI is analyzing your document and creating personalized questions. This may take a few moments.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 