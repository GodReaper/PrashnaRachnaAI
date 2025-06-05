'use client'

import React, { useState } from 'react';
import { DocumentUpload } from './DocumentUpload';
import { QuestionGeneration } from './QuestionGeneration';

interface UploadedFile {
  name: string;
  type: string;
  size: number;
}

export default function UploadClient() {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationComplete, setGenerationComplete] = useState(false);

  const handleFileUpload = (file: File) => {
    console.log('File uploaded:', file.name);
    setUploadedFile({
      name: file.name,
      type: file.type,
      size: file.size
    });
    setGenerationComplete(false);
  };

  const handleQuestionGeneration = (data: {
    questionType: string;
    bloomLevel: string;
    numberOfQuestions: number;
    difficulty: string;
  }) => {
    console.log('Generating questions with data:', data);
    setIsGenerating(true);
    
    // Simulate question generation process
    setTimeout(() => {
      setIsGenerating(false);
      setGenerationComplete(true);
      console.log('Questions generated successfully!');
      alert(`Generated ${data.numberOfQuestions} ${data.questionType} questions at ${data.bloomLevel} level with ${data.difficulty} difficulty!`);
    }, 3000);
  };

  const handleReset = () => {
    setUploadedFile(null);
    setIsGenerating(false);
    setGenerationComplete(false);
  };

  return (
    <div className="space-y-6">
      {!uploadedFile ? (
        // Step 1: Document Upload
        <DocumentUpload 
          onFileSelect={(file) => {
            console.log('File selected:', file.name);
          }}
          onUpload={handleFileUpload}
        />
      ) : (
        // Step 2: Question Generation
        <div className="space-y-6">
          {/* File Upload Success */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">
                  Document Uploaded Successfully!
                </h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>📄 <strong>{uploadedFile.name}</strong></p>
                  <p>Size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  <p>Type: {uploadedFile.type}</p>
                </div>
                <div className="mt-3">
                  <button 
                    onClick={handleReset}
                    className="text-green-600 hover:text-green-500 text-sm font-medium"
                  >
                    Upload Different File →
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Question Generation Component */}
          <QuestionGeneration
            documentName={uploadedFile.name}
            onGenerate={handleQuestionGeneration}
            isGenerating={isGenerating}
          />

          {/* Generation Complete */}
          {generationComplete && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Questions Generated Successfully!
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>Your questions have been generated and are ready for review.</p>
                  </div>
                  <div className="mt-3 flex space-x-3">
                    <a 
                      href="/questions"
                      className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded"
                    >
                      View Questions →
                    </a>
                    <button 
                      onClick={handleReset}
                      className="text-blue-600 hover:text-blue-500 text-sm font-medium py-2 px-4"
                    >
                      Generate More Questions
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}