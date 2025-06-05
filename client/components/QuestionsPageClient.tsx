'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { QuestionsSidebar } from './QuestionsSidebar';

// Mock data structure for questions
interface Question {
  id: string;
  question: string;
  type: 'MCQ' | 'FillInTheBlank' | 'TrueFalse' | 'ShortAnswer';
  difficulty: 'Easy' | 'Medium' | 'Hard';
  bloomLevel: 'Remember' | 'Understand' | 'Apply' | 'Analyze' | 'Evaluate' | 'Create';
  options?: string[];
  correctAnswer?: string;
  upvotes: number;
  downvotes: number;
  userVote?: 'up' | 'down' | null;
}

// Mock questions for the selected document
const mockQuestions: Question[] = [
  {
    id: '1',
    question: 'What is machine learning primarily used for?',
    type: 'MCQ',
    difficulty: 'Easy',
    bloomLevel: 'Remember',
    options: [
      'Creating static websites',
      'Analyzing data patterns and making predictions',
      'Managing databases',
      'Designing user interfaces'
    ],
    correctAnswer: 'Analyzing data patterns and making predictions',
    upvotes: 8,
    downvotes: 1,
    userVote: null
  },
  {
    id: '2',
    question: 'Explain how supervised learning differs from unsupervised learning.',
    type: 'ShortAnswer',
    difficulty: 'Medium',
    bloomLevel: 'Understand',
    upvotes: 12,
    downvotes: 2,
    userVote: 'up'
  },
  {
    id: '3',
    question: 'Neural networks are inspired by the structure of the human ______.',
    type: 'FillInTheBlank',
    difficulty: 'Easy',
    bloomLevel: 'Remember',
    correctAnswer: 'brain',
    upvotes: 5,
    downvotes: 0,
    userVote: null
  },
  {
    id: '4',
    question: 'Apply the concept of feature engineering to improve model performance on a dataset with categorical variables.',
    type: 'ShortAnswer',
    difficulty: 'Hard',
    bloomLevel: 'Apply',
    upvotes: 15,
    downvotes: 3,
    userVote: null
  }
];

interface QuestionSet {
  id: string;
  documentName: string;
  documentType: 'pdf' | 'docx' | 'pptx';
  questionCount: number;
  createdAt: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
}

export function QuestionsPageClient() {
  const [selectedQuestionSetId, setSelectedQuestionSetId] = useState<string>('1');
  const [selectedQuestionSet, setSelectedQuestionSet] = useState<QuestionSet | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterBloomLevel, setFilterBloomLevel] = useState<string>('all');

  const handleQuestionSetSelect = (questionSet: QuestionSet) => {
    setSelectedQuestionSetId(questionSet.id);
    setSelectedQuestionSet(questionSet);
  };

  const handleVote = (questionId: string, voteType: 'up' | 'down') => {
    // TODO: Implement voting functionality with backend
    console.log(`Voted ${voteType} on question ${questionId}`);
  };

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'MCQ': return '◯';
      case 'FillInTheBlank': return '✏️';
      case 'TrueFalse': return '✓✗';
      case 'ShortAnswer': return '📝';
      default: return '❓';
    }
  };

  const getBloomLevelColor = (level: string): string => {
    switch (level) {
      case 'Remember': return 'bg-green-100 text-green-800';
      case 'Understand': return 'bg-blue-100 text-blue-800';
      case 'Apply': return 'bg-yellow-100 text-yellow-800';
      case 'Analyze': return 'bg-orange-100 text-orange-800';
      case 'Evaluate': return 'bg-red-100 text-red-800';
      case 'Create': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600 bg-green-100';
      case 'Medium': return 'text-yellow-600 bg-yellow-100';
      case 'Hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const filteredQuestions = mockQuestions.filter(question => {
    const matchesType = filterType === 'all' || question.type === filterType;
    const matchesBloomLevel = filterBloomLevel === 'all' || question.bloomLevel === filterBloomLevel;
    return matchesType && matchesBloomLevel;
  });

  return (
    <>
      {/* Questions Sidebar */}
      <QuestionsSidebar
        selectedQuestionSetId={selectedQuestionSetId}
        onQuestionSetSelect={handleQuestionSetSelect}
      />

      {/* Main Content */}
      <div className="flex-1 bg-white flex flex-col">
        {selectedQuestionSetId ? (
          <>
            {/* Content Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {selectedQuestionSet?.documentName || 'Introduction to Machine Learning.pdf'}
                  </h1>
                  <p className="text-gray-600 mt-1">
                    {filteredQuestions.length} questions generated • Medium difficulty
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg">
                    Generate More Questions
                  </button>
                  <button className="border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-lg">
                    Export Questions
                  </button>
                </div>
              </div>

              {/* Filters */}
              <div className="flex items-center space-x-4 mt-4">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Types</option>
                  <option value="MCQ">Multiple Choice</option>
                  <option value="FillInTheBlank">Fill in the Blank</option>
                  <option value="TrueFalse">True/False</option>
                  <option value="ShortAnswer">Short Answer</option>
                </select>

                <select
                  value={filterBloomLevel}
                  onChange={(e) => setFilterBloomLevel(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Bloom Levels</option>
                  <option value="Remember">Remember</option>
                  <option value="Understand">Understand</option>
                  <option value="Apply">Apply</option>
                  <option value="Analyze">Analyze</option>
                  <option value="Evaluate">Evaluate</option>
                  <option value="Create">Create</option>
                </select>
              </div>
            </div>

            {/* Questions List */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {filteredQuestions.map((question, index) => (
                  <div key={question.id} className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                    {/* Question Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2 py-1 rounded">
                          Q{index + 1}
                        </span>
                        <span className="text-lg">{getTypeIcon(question.type)}</span>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getBloomLevelColor(question.bloomLevel)}`}>
                          {question.bloomLevel}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
                          {question.difficulty}
                        </span>
                      </div>
                    </div>

                    {/* Question Content */}
                    <div className="mb-4">
                      <p className="text-lg font-medium text-gray-900 mb-3">{question.question}</p>
                      
                      {question.type === 'MCQ' && question.options && (
                        <div className="space-y-2">
                          {question.options.map((option, optionIndex) => (
                            <div key={optionIndex} className="flex items-center space-x-3">
                              <span className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-sm font-medium">
                                {String.fromCharCode(65 + optionIndex)}
                              </span>
                              <span className={`${option === question.correctAnswer ? 'text-green-700 font-medium' : 'text-gray-700'}`}>
                                {option}
                                {option === question.correctAnswer && ' ✓'}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}

                      {question.type === 'FillInTheBlank' && question.correctAnswer && (
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">Correct Answer: <span className="font-medium text-green-700">{question.correctAnswer}</span></p>
                        </div>
                      )}
                    </div>

                    {/* Question Actions */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                      <div className="flex items-center space-x-4">
                        <button
                          onClick={() => handleVote(question.id, 'up')}
                          className={`flex items-center space-x-1 px-3 py-1 rounded ${
                            question.userVote === 'up' 
                              ? 'bg-green-100 text-green-700' 
                              : 'text-gray-500 hover:text-green-600'
                          }`}
                        >
                          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                          </svg>
                          <span>{question.upvotes}</span>
                        </button>

                        <button
                          onClick={() => handleVote(question.id, 'down')}
                          className={`flex items-center space-x-1 px-3 py-1 rounded ${
                            question.userVote === 'down' 
                              ? 'bg-red-100 text-red-700' 
                              : 'text-gray-500 hover:text-red-600'
                          }`}
                        >
                          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span>{question.downvotes}</span>
                        </button>
                      </div>

                      <div className="flex items-center space-x-2">
                        <button className="text-gray-500 hover:text-gray-700 px-3 py-1 text-sm">
                          Edit
                        </button>
                        <button className="text-gray-500 hover:text-red-600 px-3 py-1 text-sm">
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* Empty State */
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Select a Document
              </h2>
              
              <p className="text-gray-600 mb-6">
                Choose a document from the sidebar to view its generated questions.
              </p>

              <Link href="/upload">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">
                  Upload New Document
                </button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </>
  );
} 