'use client';

import React, { useState, useRef } from 'react';
import { z } from 'zod';
import { apiClient, type Document } from '../lib/api';
import { useAuth } from '../lib/hooks/useAuth';

// Zod schema for file validation
const fileUploadSchema = z.object({
  file: z
    .instanceof(File)
    .refine((file) => file.size <= 10 * 1024 * 1024, {
      message: "File size must be less than 10MB"
    })
    .refine((file) => [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      "application/vnd.ms-powerpoint"
    ].includes(file.type), {
      message: "File type must be PDF, DOCX, or PPTX"
    }),
});

interface DocumentUploadProps {
  onFileSelect?: (file: File) => void;
  onUpload?: (document: Document) => void;
}

export function DocumentUpload({ onFileSelect, onUpload }: DocumentUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [uploadedDocument, setUploadedDocument] = useState<Document | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Initialize auth
  useAuth();

  const validateFile = (file: File): boolean => {
    try {
      fileUploadSchema.parse({ file });
      setError('');
      return true;
    } catch (err) {
      if (err instanceof z.ZodError) {
        setError(err.errors[0]?.message || 'Invalid file');
      }
      return false;
    }
  };

  const handleFileSelect = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      onFileSelect?.(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError('');
    
    try {
      const response = await apiClient.uploadDocument(selectedFile);
      
      if (response.success && response.data) {
        // Always notify parent component first
        onUpload?.(response.data);
        
        // Handle parsing states - but don't block the upload success
        if (response.data.processing_status === 'completed') {
          // Success! Clear the form
          setSelectedFile(null);
          setUploadedDocument(null);
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
        } else {
          // Document uploaded but needs parsing work - keep it for status tracking
          setUploadedDocument(response.data);
          
          if (response.data.processing_status === 'failed') {
            setError(`Document parsing failed: ${response.data.error_message || 'Unknown error'}`);
          } else if (response.data.processing_status === 'processing') {
            // Wait for processing to complete
            setIsParsing(true);
            await waitForParsingCompletion(response.data.id);
          } else {
            // Try to trigger parsing
            setIsParsing(true);
            await retryParsing(response.data.id);
          }
        }
      } else {
        setError(response.error || 'Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const waitForParsingCompletion = async (documentId: string) => {
    setIsParsing(true);
    const maxAttempts = 30; // Wait up to 30 seconds
    let attempts = 0;

    const checkStatus = async (): Promise<void> => {
      try {
        const response = await apiClient.getDocument(documentId);
        
        if (response.success && response.data) {
          // Always update parent with latest document status
          onUpload?.(response.data);
          
          if (response.data.processing_status === 'completed') {
            // Parsing completed successfully - clear form
            setSelectedFile(null);
            setUploadedDocument(null);
            if (fileInputRef.current) {
              fileInputRef.current.value = '';
            }
            setIsParsing(false);
            return;
          } else if (response.data.processing_status === 'failed') {
            // Parsing failed - keep for retry
            setUploadedDocument(response.data);
            setError(`Parsing failed: ${response.data.error_message || 'Unknown error'}`);
            setIsParsing(false);
            return;
          } else if (attempts < maxAttempts) {
            // Still processing, wait and check again
            setUploadedDocument(response.data); // Update local state too
            attempts++;
            setTimeout(checkStatus, 1000);
          } else {
            // Timeout
            setError('Parsing is taking longer than expected. You can try refreshing or retry parsing.');
            setIsParsing(false);
          }
        } else {
          setError('Failed to check parsing status.');
          setIsParsing(false);
        }
      } catch (error) {
        console.error('Error checking parsing status:', error);
        setError('Failed to check parsing status.');
        setIsParsing(false);
      }
    };

    checkStatus();
  };

  const retryParsing = async (documentId: string) => {
    setIsParsing(true);
    setError('');
    
    try {
      const response = await apiClient.parseDocument(documentId);
      
      if (response.success && response.data) {
        // Parsing started, wait for completion
        await waitForParsingCompletion(documentId);
      } else {
        setError(response.error || 'Failed to start parsing. Please try again.');
        setIsParsing(false);
      }
    } catch (error) {
      console.error('Parse error:', error);
      setError('Failed to parse document. Please try again.');
      setIsParsing(false);
    }
  };

  // Helper function for external retry calls
  const handleRetryParsing = async (documentId: string) => {
    await retryParsing(documentId);
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadedDocument(null);
    setError('');
    setIsParsing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Byte';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = (type: string): string => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word')) return '📝';
    if (type.includes('presentation') || type.includes('powerpoint')) return '📊';
    return '📁';
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <>
          {/* File Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <svg 
              className="mx-auto h-12 w-12 text-gray-400 mb-4" 
              stroke="currentColor" 
              fill="none" 
              viewBox="0 0 48 48"
            >
              <path 
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" 
                strokeWidth={2} 
                strokeLinecap="round" 
                strokeLinejoin="round" 
              />
            </svg>
            
            <div>
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="text-lg font-medium text-gray-900 block mb-2">
                  Drop files here or click to upload
                </span>
                <span className="text-sm text-gray-500">
                  Supports PDF, DOCX, and PPTX files up to 10MB
                </span>
              </label>
              <input
                ref={fileInputRef}
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                accept=".pdf,.docx,.pptx"
                onChange={handleFileChange}
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex">
                <svg className="w-5 h-5 text-red-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <span className="text-red-800 text-sm font-medium">{error}</span>
                  {/* Show retry button if document was uploaded but parsing failed */}
                  {uploadedDocument && uploadedDocument.processing_status === 'failed' && (
                    <div className="mt-2">
                      <button
                        onClick={() => handleRetryParsing(uploadedDocument.id)}
                        disabled={isParsing}
                        className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm font-medium"
                      >
                        {isParsing ? 'Retrying...' : 'Retry Parsing'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Parsing Progress Indicator */}
          {isParsing && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center">
                <svg className="animate-spin h-5 w-5 text-blue-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <div>
                  <p className="text-blue-800 font-medium">Processing document content...</p>
                  <p className="text-blue-600 text-sm">
                    Extracting text and creating searchable chunks for AI question generation.
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Selected File Display */}
          <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="text-2xl mr-3">{getFileIcon(selectedFile.type)}</span>
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(selectedFile.size)} • {selectedFile.type.split('/')[1]?.toUpperCase()}
                  </p>
                </div>
              </div>
              
              <button
                onClick={resetUpload}
                className="text-gray-400 hover:text-gray-600 p-1"
                title="Remove file"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Upload Button */}
          <div className="mt-6">
            <button
              onClick={handleUpload}
              disabled={isUploading || isParsing}
              className={`w-full font-medium py-3 px-6 rounded-lg transition-colors ${
                isUploading || isParsing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {isUploading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Uploading Document...
                </div>
              ) : isParsing ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Parsing Document...
                </div>
              ) : (
                'Upload & Process Document'
              )}
            </button>
          </div>
        </>
      )}
    </div>
  );
} 