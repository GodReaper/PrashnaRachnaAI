'use client';

import React, { useState } from 'react';
import { DocumentUpload } from '../../components/DocumentUpload';
import { useAuth } from '../../lib/hooks/useAuth';
import { type Document } from '../../lib/api';
import Link from 'next/link';

export default function UploadPage() {
  const { isLoaded, isSignedIn } = useAuth();
  const [uploadedDocuments, setUploadedDocuments] = useState<Document[]>([]);

  const handleDocumentUpload = (document: Document) => {
    setUploadedDocuments(prev => [document, ...prev]);
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
                <Link href="/upload" className="text-blue-600 font-medium">
                  Upload Document
                </Link>
                <Link href="/generate" className="text-gray-600 hover:text-gray-800 font-medium">
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h1>
          <p className="text-gray-600">
            Upload your PDF, DOCX, or PPTX files to process and generate questions from them.
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload New Document</h2>
          <DocumentUpload onUpload={handleDocumentUpload} />
        </div>

        {/* Uploaded Documents */}
        {uploadedDocuments.length > 0 && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Recently Uploaded ({uploadedDocuments.length})
              </h2>
              <Link href="/generate" className="text-blue-600 hover:text-blue-800 font-medium">
                Generate Questions →
              </Link>
            </div>

            <div className="space-y-4">
              {uploadedDocuments.map((document) => (
                <div key={document.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        {document.file_type.includes('pdf') && (
                          <span className="text-2xl">📄</span>
                        )}
                        {document.file_type.includes('word') && (
                          <span className="text-2xl">📝</span>
                        )}
                        {(document.file_type.includes('presentation') || document.file_type.includes('powerpoint')) && (
                          <span className="text-2xl">📊</span>
                        )}
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">{document.filename}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>{(document.file_size / 1024 / 1024).toFixed(2)} MB</span>
                          <span>{document.file_type}</span>
                          <span className={`px-2 py-1 rounded text-xs ${
                            document.processing_status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : document.processing_status === 'processing'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {document.processing_status}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Link
                        href={`/generate?doc=${document.id}`}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium"
                      >
                        Generate Questions
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">📋 Supported File Types</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <strong className="text-blue-800">PDF Documents</strong>
              <p className="text-blue-700">Research papers, textbooks, articles</p>
            </div>
            <div>
              <strong className="text-blue-800">Word Documents (.docx)</strong>
              <p className="text-blue-700">Essays, reports, study materials</p>
            </div>
            <div>
              <strong className="text-blue-800">PowerPoint (.pptx)</strong>
              <p className="text-blue-700">Lecture slides, presentations</p>
            </div>
          </div>
          <div className="mt-4 text-sm text-blue-800">
            <strong>File size limit:</strong> 10MB per file
          </div>
        </div>
      </div>
    </div>
  );
} 