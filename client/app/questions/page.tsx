'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../lib/hooks/useAuth';
import { apiClient, type Question } from '../../lib/api';
import Link from 'next/link';

interface QuestionWithDocument extends Question {
  document_name?: string;
}

export default function QuestionsPage() {
  const { isLoaded, isSignedIn } = useAuth();
  const [questions, setQuestions] = useState<QuestionWithDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState({
    type: '',
    difficulty: '',
    bloom_level: ''
  });

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      fetchQuestions();
    }
  }, [isLoaded, isSignedIn]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getQuestions();
      if (response.success && response.data) {
        setQuestions(response.data.questions);
      } else {
        setError(response.error || 'Failed to fetch questions');
      }
    } catch (err) {
      console.error('Error fetching questions:', err);
      setError('Error fetching questions');
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (questionId: string, vote: 'upvote' | 'downvote') => {
    try {
      const response = await apiClient.submitQuestionFeedback(questionId, {
        vote: vote,
        is_helpful: vote === 'upvote'
      });
      
      if (response.success) {
        // Update local state
        setQuestions(prev => prev.map(q => 
          q.id === questionId 
            ? {
                ...q,
                upvotes: vote === 'upvote' ? (q.upvotes || 0) + 1 : q.upvotes,
                downvotes: vote === 'downvote' ? (q.downvotes || 0) + 1 : q.downvotes
              }
            : q
        ));
      }
    } catch (err) {
      console.error('Failed to submit rating:', err);
    }
  };

  const filteredQuestions = questions.filter(question => {
    return (
      (!filter.type || question.type === filter.type) &&
      (!filter.difficulty || question.difficulty === filter.difficulty) &&
      (!filter.bloom_level || question.bloom_level === filter.bloom_level)
    );
  });

  const questionTypes = [...new Set(questions.map(q => q.type))];
  const difficulties = [...new Set(questions.map(q => q.difficulty).filter(Boolean))];
  const bloomLevels = [...new Set(questions.map(q => q.bloom_level).filter(Boolean))];

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
                <Link href="/upload" className="text-gray-600 hover:text-gray-800 font-medium">
                  Upload Document
                </Link>
                <Link href="/generate" className="text-gray-600 hover:text-gray-800 font-medium">
                  Generate Questions
                </Link>
                <Link href="/questions" className="text-blue-600 font-medium">
                  My Questions
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Questions</h1>
          <p className="text-gray-600">
            View and manage your generated questions. Rate them to help improve future generations.
          </p>
        </div>

        <div className="flex gap-8">
          {/* Sidebar - Filters */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
              
              {/* Question Type Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Question Type</label>
                <select
                  value={filter.type}
                  onChange={(e) => setFilter({...filter, type: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">All Types</option>
                  {questionTypes.map(type => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>

              {/* Difficulty Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                <select
                  value={filter.difficulty}
                  onChange={(e) => setFilter({...filter, difficulty: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">All Difficulties</option>
                  {difficulties.map(difficulty => (
                    <option key={difficulty} value={difficulty}>
                      {difficulty ? difficulty.charAt(0).toUpperCase() + difficulty.slice(1) : ''}
                    </option>
                  ))}
                </select>
              </div>

              {/* Bloom Level Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Bloom&apos;s Level</label>
                <select
                  value={filter.bloom_level}
                  onChange={(e) => setFilter({...filter, bloom_level: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">All Levels</option>
                  {bloomLevels.map(level => (
                    <option key={level} value={level}>
                      {level ? level.charAt(0).toUpperCase() + level.slice(1) : ''}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => setFilter({ type: '', difficulty: '', bloom_level: '' })}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded text-sm font-medium"
              >
                Clear Filters
              </button>
            </div>

            {/* Quick Actions */}
            <div className="mt-6 bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Link
                  href="/upload"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-sm font-medium text-center block"
                >
                  Upload Document
                </Link>
                <Link
                  href="/generate"
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded text-sm font-medium text-center block"
                >
                  Generate Questions
                </Link>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {loading ? (
              <div className="bg-white shadow rounded-lg p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading questions...</p>
              </div>
            ) : error ? (
              <div className="bg-white shadow rounded-lg p-8 text-center">
                <div className="text-red-600 mb-4">
                  <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 15.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Questions</h3>
                <p className="text-gray-600 mb-4">{error}</p>
                <button
                  onClick={fetchQuestions}
                  className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded font-medium"
                >
                  Try Again
                </button>
              </div>
            ) : filteredQuestions.length === 0 ? (
              <div className="bg-white shadow rounded-lg p-8 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Questions Found</h3>
                <p className="text-gray-600 mb-4">
                  {questions.length === 0 
                    ? "You haven't generated any questions yet. Upload a document and generate some questions to get started."
                    : "No questions match your current filters. Try adjusting or clearing the filters."
                  }
                </p>
                <Link
                  href="/generate"
                  className="inline-block bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded font-medium"
                >
                  Generate Questions
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Results Header */}
                <div className="bg-white shadow rounded-lg p-4">
                  <p className="text-gray-600">
                    Showing <span className="font-medium">{filteredQuestions.length}</span> of <span className="font-medium">{questions.length}</span> questions
                  </p>
                </div>

                {/* Questions List */}
                {filteredQuestions.map((question, index) => (
                  <div key={question.id} className="bg-white shadow rounded-lg p-6">
                    {/* Question Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                          #{index + 1}
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
                      
                      {/* Rating Controls */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleRating(question.id, 'upvote')}
                          className="flex items-center space-x-1 text-green-600 hover:text-green-700"
                        >
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-sm">{question.upvotes || 0}</span>
                        </button>
                        <button
                          onClick={() => handleRating(question.id, 'downvote')}
                          className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                        >
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-sm">{question.downvotes || 0}</span>
                        </button>
                      </div>
                    </div>

                    {/* Question Content */}
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

                    {/* Question Meta */}
                    <div className="pt-4 border-t border-gray-200 text-sm text-gray-500">
                      <div className="flex justify-between">
                        <span>Created: {new Date(question.created_at).toLocaleDateString()}</span>
                        {question.document_name && (
                          <span>From: {question.document_name}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 