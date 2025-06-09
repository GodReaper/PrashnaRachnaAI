'use client';

import React, { useState, useEffect } from 'react';
import { z } from 'zod';
import { apiClient, type QuestionGenerationRequest, type Question } from '../lib/api';
import { useAuth } from '../lib/hooks/useAuth';

// Backend question types (matching the API)
const backendQuestionTypes = [
  'multiple_choice',
  'true_false', 
  'short_answer',
  'fill_in_the_blank',
  'essay',
  'definition',
  'explanation',
  'all_types'
];

// Backend bloom levels (lowercase to match API)
const backendBloomLevels = [
  'remember',
  'understand', 
  'apply',
  'analyze',
  'evaluate',
  'create'
];

// Backend difficulty levels
const backendDifficultyLevels = [
  'basic',
  'intermediate',
  'advanced'
];

// Zod schema for question generation validation
const questionGenerationSchema = z.object({
  questionType: z.enum(backendQuestionTypes as [string, ...string[]], {
    errorMap: () => ({ message: "Please select a valid question type" })
  }),
  bloomLevel: z.enum(backendBloomLevels as [string, ...string[]], {
    errorMap: () => ({ message: "Please select a valid Bloom's Taxonomy level" })
  }),
  numberOfQuestions: z.number().min(1, "Must generate at least 1 question").max(20, "Cannot generate more than 20 questions"),
  difficulty: z.enum(backendDifficultyLevels as [string, ...string[]], {
    errorMap: () => ({ message: "Please select a difficulty level" })
  })
});

type QuestionGenerationData = z.infer<typeof questionGenerationSchema>;

interface QuestionGenerationProps {
  documentIds?: string[]; // Document IDs should always be strings for API compatibility
  documentName?: string;
  onGenerate?: (questions: Question[]) => void;
  isGenerating?: boolean;
  documentsReady?: boolean; // Whether all documents are processed and ready for question generation
}

const questionTypeOptions = [
  { value: 'multiple_choice', label: 'Multiple Choice', icon: '◯', description: 'Questions with 4 answer options (A, B, C, D)' },
  { value: 'true_false', label: 'True/False', icon: '✓✗', description: 'Simple true or false statements' },
  { value: 'short_answer', label: 'Short Answer', icon: '📝', description: 'Brief 1-3 sentence responses' },
  { value: 'fill_in_the_blank', label: 'Fill in the Blank', icon: '✏️', description: 'Complete the missing word or phrase' },
  { value: 'essay', label: 'Essay', icon: '📄', description: 'Comprehensive multi-paragraph responses' },
  { value: 'definition', label: 'Definition', icon: '💡', description: 'Define key terms or concepts' },
  { value: 'explanation', label: 'Explanation', icon: '🔍', description: 'Explain processes or relationships' },
  { value: 'all_types', label: 'All Types (7 questions)', icon: '🎯', description: 'Generate one question of each type' }
];

const bloomLevelOptions = [
  { value: 'remember', label: 'Remember', color: 'bg-green-100 text-green-800 border-green-200', description: 'Recall facts and basic concepts' },
  { value: 'understand', label: 'Understand', color: 'bg-blue-100 text-blue-800 border-blue-200', description: 'Explain ideas or concepts' },
  { value: 'apply', label: 'Apply', color: 'bg-yellow-100 text-yellow-800 border-yellow-200', description: 'Use information in new situations' },
  { value: 'analyze', label: 'Analyze', color: 'bg-orange-100 text-orange-800 border-orange-200', description: 'Draw connections among ideas' },
  { value: 'evaluate', label: 'Evaluate', color: 'bg-red-100 text-red-800 border-red-200', description: 'Justify a stand or decision' },
  { value: 'create', label: 'Create', color: 'bg-purple-100 text-purple-800 border-purple-200', description: 'Produce new or original work' }
];

const difficultyOptions = [
  { value: 'basic', label: 'Basic', color: 'text-green-600 bg-green-100 border-green-200' },
  { value: 'intermediate', label: 'Intermediate', color: 'text-yellow-600 bg-yellow-100 border-yellow-200' },
  { value: 'advanced', label: 'Advanced', color: 'text-red-600 bg-red-100 border-red-200' }
];

export function QuestionGeneration({ documentIds = [], documentName, onGenerate, isGenerating = false, documentsReady = true }: QuestionGenerationProps) {
  const [formData, setFormData] = useState<QuestionGenerationData>({
    questionType: 'all_types',
    bloomLevel: 'understand',
    numberOfQuestions: 7,
    difficulty: 'intermediate'
  });
  const [errors, setErrors] = useState<Partial<Record<keyof QuestionGenerationData, string>>>({});
  const [isValid, setIsValid] = useState(false);
  const [localIsGenerating, setLocalIsGenerating] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Initialize auth
  useAuth();

  const validateForm = (data: QuestionGenerationData) => {
    try {
      questionGenerationSchema.parse(data);
      setErrors({});
      setIsValid(true);
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors: Partial<Record<keyof QuestionGenerationData, string>> = {};
        error.errors.forEach((err) => {
          if (err.path[0]) {
            fieldErrors[err.path[0] as keyof QuestionGenerationData] = err.message;
          }
        });
        setErrors(fieldErrors);
        setIsValid(false);
      }
      return false;
    }
  };

  const handleInputChange = (field: keyof QuestionGenerationData, value: string | number) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    validateForm(newData);
  };

  // Update number of questions based on question type
  useEffect(() => {
    if (formData.questionType === 'all_types') {
      setFormData(prev => ({ ...prev, numberOfQuestions: 7 }));
    }
  }, [formData.questionType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm(formData) || documentIds.length === 0) return;

    setLocalIsGenerating(true);
    setApiError(null); // Clear previous errors
    
    try {
      const request: QuestionGenerationRequest = {
        document_ids: documentIds.map(id => String(id)), // Ensure IDs are strings
        question_type: formData.questionType,
        bloom_level: formData.bloomLevel,
        difficulty: formData.difficulty,
        num_questions: formData.numberOfQuestions
      };

      const response = await apiClient.generateQuestions(request);
      
      if (response.success && response.data) {
        setApiError(null);
        onGenerate?.(response.data.questions);
      } else {
        const errorMsg = response.error || 'Question generation failed. Please try again.';
        setApiError(errorMsg);
        console.error('Question generation failed:', response.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'An unexpected error occurred';
      setApiError(errorMsg);
      console.error('Question generation error:', error);
    } finally {
      setLocalIsGenerating(false);
    }
  };

  const actualIsGenerating = isGenerating || localIsGenerating;
  const canGenerate = documentIds.length > 0 && isValid && !actualIsGenerating && documentsReady;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Generate Questions</h3>
        {documentName && (
          <p className="text-gray-600 text-sm">
            Generate questions from: <span className="font-medium">{documentName}</span>
          </p>
        )}
        {documentIds.length === 0 && (
          <p className="text-red-600 text-sm">
            Please upload a document first to generate questions.
          </p>
        )}
        {!documentsReady && documentIds.length > 0 && (
          <p className="text-yellow-600 text-sm">
            Document is still being processed. Please wait for processing to complete before generating questions.
          </p>
        )}
        {apiError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="text-red-800 font-medium">Error generating questions</p>
                <p className="text-red-600 text-sm">{apiError}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Question Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Question Type <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {questionTypeOptions.map((option) => (
              <label
                key={option.value}
                className={`relative flex items-start p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                  formData.questionType === option.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200'
                }`}
              >
                <input
                  type="radio"
                  name="questionType"
                  value={option.value}
                  checked={formData.questionType === option.value}
                  onChange={(e) => handleInputChange('questionType', e.target.value)}
                  className="sr-only"
                />
                <div className="flex items-start space-x-3">
                  <span className="text-xl mt-0.5">{option.icon}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{option.label}</p>
                    <p className="text-xs text-gray-600">{option.description}</p>
                  </div>
                </div>
                {formData.questionType === option.value && (
                  <div className="absolute top-2 right-2">
                    <svg className="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </label>
            ))}
          </div>
          {errors.questionType && (
            <p className="mt-1 text-sm text-red-600">{errors.questionType}</p>
          )}
        </div>

        {/* Bloom's Taxonomy Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Bloom&apos;s Taxonomy Level <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {bloomLevelOptions.map((option) => (
              <label
                key={option.value}
                className={`relative flex items-start p-3 border rounded-lg cursor-pointer hover:opacity-80 transition-opacity ${
                  formData.bloomLevel === option.value
                    ? `${option.color} border-current`
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="bloomLevel"
                  value={option.value}
                  checked={formData.bloomLevel === option.value}
                  onChange={(e) => handleInputChange('bloomLevel', e.target.value)}
                  className="sr-only"
                />
                <div className="text-center w-full">
                  <p className="text-sm font-medium">{option.label}</p>
                  <p className="text-xs mt-1 opacity-75">{option.description}</p>
                </div>
                {formData.bloomLevel === option.value && (
                  <div className="absolute top-1 right-1">
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </label>
            ))}
          </div>
          {errors.bloomLevel && (
            <p className="mt-1 text-sm text-red-600">{errors.bloomLevel}</p>
          )}
        </div>

        {/* Difficulty Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Difficulty Level <span className="text-red-500">*</span>
          </label>
          <div className="flex space-x-3">
            {difficultyOptions.map((option) => (
              <label
                key={option.value}
                className={`relative flex items-center justify-center px-4 py-2 border rounded-lg cursor-pointer hover:opacity-80 transition-opacity flex-1 ${
                  formData.difficulty === option.value
                    ? `${option.color} border-current`
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="difficulty"
                  value={option.value}
                  checked={formData.difficulty === option.value}
                  onChange={(e) => handleInputChange('difficulty', e.target.value)}
                  className="sr-only"
                />
                <span className="text-sm font-medium">{option.label}</span>
                {formData.difficulty === option.value && (
                  <div className="absolute top-1 right-1">
                    <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </label>
            ))}
          </div>
          {errors.difficulty && (
            <p className="mt-1 text-sm text-red-600">{errors.difficulty}</p>
          )}
        </div>

        {/* Number of Questions (only for non-all_types) */}
        {formData.questionType !== 'all_types' && (
          <div>
            <label htmlFor="numberOfQuestions" className="block text-sm font-medium text-gray-700 mb-2">
              Number of Questions <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="number"
                id="numberOfQuestions"
                min="1"
                max="20"
                value={formData.numberOfQuestions}
                onChange={(e) => handleInputChange('numberOfQuestions', parseInt(e.target.value) || 1)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            {errors.numberOfQuestions && (
              <p className="mt-1 text-sm text-red-600">{errors.numberOfQuestions}</p>
            )}
          </div>
        )}

        {/* Generate Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={!canGenerate}
            className={`w-full font-medium py-3 px-6 rounded-lg transition-colors ${
              canGenerate
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {actualIsGenerating ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating Questions...
              </div>
            ) : (
              `Generate ${formData.questionType === 'all_types' ? '7' : formData.numberOfQuestions} Question${formData.numberOfQuestions !== 1 ? 's' : ''}`
            )}
          </button>
        </div>

        {/* Help Text */}
        <div className="text-xs text-gray-500 text-center">
          Questions will be generated using AI based on your document content
        </div>
      </form>
    </div>
  );
} 