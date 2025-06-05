'use client';

import React, { useState } from 'react';
import Link from 'next/link';

// Mock data structure for previous questions
interface QuestionSet {
  id: string;
  documentName: string;
  documentType: 'pdf' | 'docx' | 'pptx';
  questionCount: number;
  createdAt: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  isActive?: boolean;
}

// Mock data - will be replaced with backend data
const mockQuestionSets: QuestionSet[] = [
  {
    id: '1',
    documentName: 'Introduction to Machine Learning.pdf',
    documentType: 'pdf',
    questionCount: 15,
    createdAt: '2024-01-15',
    difficulty: 'Medium'
  },
  {
    id: '2',
    documentName: 'Business Presentation Q1.pptx',
    documentType: 'pptx',
    questionCount: 8,
    createdAt: '2024-01-14',
    difficulty: 'Easy'
  },
  {
    id: '3',
    documentName: 'Research Methodology.docx',
    documentType: 'docx',
    questionCount: 12,
    createdAt: '2024-01-12',
    difficulty: 'Hard'
  },
  {
    id: '4',
    documentName: 'Data Structures and Algorithms.pdf',
    documentType: 'pdf',
    questionCount: 25,
    createdAt: '2024-01-10',
    difficulty: 'Hard'
  },
  {
    id: '5',
    documentName: 'Marketing Strategy Guide.docx',
    documentType: 'docx',
    questionCount: 6,
    createdAt: '2024-01-08',
    difficulty: 'Easy'
  }
];

interface QuestionsSidebarProps {
  selectedQuestionSetId?: string;
  onQuestionSetSelect?: (questionSet: QuestionSet) => void;
}

export function QuestionsSidebar({ selectedQuestionSetId, onQuestionSetSelect }: QuestionsSidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState<string>('all');

  const getFileIcon = (type: string): string => {
    switch (type) {
      case 'pdf': return '📄';
      case 'docx': return '📝';
      case 'pptx': return '📊';
      default: return '📁';
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

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  const filteredQuestionSets = mockQuestionSets.filter(set => {
    const matchesSearch = set.documentName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDifficulty = filterDifficulty === 'all' || set.difficulty === filterDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  return (
    <div className="w-80 bg-white border-r border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Previous Questions</h2>
        
        {/* Search */}
        <div className="relative mb-3">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Difficulty Filter */}
        <select
          value={filterDifficulty}
          onChange={(e) => setFilterDifficulty(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="all">All Difficulties</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
      </div>

      {/* Question Sets List */}
      <div className="flex-1 overflow-y-auto">
        {filteredQuestionSets.length === 0 ? (
          <div className="p-4 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-gray-500 text-sm">No documents found</p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {filteredQuestionSets.map((questionSet) => (
              <div
                key={questionSet.id}
                onClick={() => onQuestionSetSelect?.(questionSet)}
                className={`p-3 rounded-lg border cursor-pointer transition-colors hover:bg-gray-50 ${
                  selectedQuestionSetId === questionSet.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-2 flex-1 min-w-0">
                    <span className="text-lg mt-0.5 flex-shrink-0">
                      {getFileIcon(questionSet.documentType)}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate" title={questionSet.documentName}>
                        {questionSet.documentName}
                      </p>
                      <div className="flex items-center justify-between mt-1">
                        <p className="text-xs text-gray-500">
                          {questionSet.questionCount} questions
                        </p>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getDifficultyColor(questionSet.difficulty)}`}>
                          {questionSet.difficulty}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDate(questionSet.createdAt)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <Link href="/upload">
          <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors">
            + Upload New Document
          </button>
        </Link>
        
        <div className="mt-3 text-center">
          <p className="text-xs text-gray-500">
            Total: {filteredQuestionSets.length} document{filteredQuestionSets.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    </div>
  );
} 