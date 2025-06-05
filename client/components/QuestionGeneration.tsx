'use client';

import React, { useState } from 'react';
import { z } from 'zod';

// Zod schema for question generation validation
const questionGenerationSchema = z.object({
  questionType: z.enum(["MCQ", "FillInTheBlank", "TrueFalse", "ShortAnswer"], {
    errorMap: () => ({ message: "Please select a valid question type" })
  }),
  bloomLevel: z.enum(["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"], {
    errorMap: () => ({ message: "Please select a valid Bloom's Taxonomy level" })
  }),
  numberOfQuestions: z.number().min(1, "Must generate at least 1 question").max(50, "Cannot generate more than 50 questions"),
  difficulty: z.enum(["Easy", "Medium", "Hard"], {
    errorMap: () => ({ message: "Please select a difficulty level" })
  })
});

type QuestionGenerationData = z.infer<typeof questionGenerationSchema>;

interface QuestionGenerationProps {
  documentName?: string;
  onGenerate?: (data: QuestionGenerationData) => void;
  isGenerating?: boolean;
}

const questionTypeOptions = [
  { value: 'MCQ', label: 'Multiple Choice Questions', icon: '◯', description: 'Questions with multiple answer options' },
  { value: 'FillInTheBlank', label: 'Fill in the Blank', icon: '✏️', description: 'Complete the missing word or phrase' },
  { value: 'TrueFalse', label: 'True/False', icon: '✓✗', description: 'Simple true or false statements' },
  { value: 'ShortAnswer', label: 'Short Answer', icon: '📝', description: 'Brief descriptive responses' }
];

const bloomLevelOptions = [
  { value: 'Remember', label: 'Remember', color: 'bg-green-100 text-green-800 border-green-200', description: 'Recall facts and basic concepts' },
  { value: 'Understand', label: 'Understand', color: 'bg-blue-100 text-blue-800 border-blue-200', description: 'Explain ideas or concepts' },
  { value: 'Apply', label: 'Apply', color: 'bg-yellow-100 text-yellow-800 border-yellow-200', description: 'Use information in new situations' },
  { value: 'Analyze', label: 'Analyze', color: 'bg-orange-100 text-orange-800 border-orange-200', description: 'Draw connections among ideas' },
  { value: 'Evaluate', label: 'Evaluate', color: 'bg-red-100 text-red-800 border-red-200', description: 'Justify a stand or decision' },
  { value: 'Create', label: 'Create', color: 'bg-purple-100 text-purple-800 border-purple-200', description: 'Produce new or original work' }
];

const difficultyOptions = [
  { value: 'Easy', label: 'Easy', color: 'text-green-600 bg-green-100 border-green-200' },
  { value: 'Medium', label: 'Medium', color: 'text-yellow-600 bg-yellow-100 border-yellow-200' },
  { value: 'Hard', label: 'Hard', color: 'text-red-600 bg-red-100 border-red-200' }
];

export function QuestionGeneration({ documentName, onGenerate, isGenerating = false }: QuestionGenerationProps) {
  const [formData, setFormData] = useState<QuestionGenerationData>({
    questionType: 'MCQ',
    bloomLevel: 'Remember',
    numberOfQuestions: 5,
    difficulty: 'Medium'
  });
  const [errors, setErrors] = useState<Partial<Record<keyof QuestionGenerationData, string>>>({});
  const [isValid, setIsValid] = useState(false);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm(formData)) {
      onGenerate?.(formData);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Generate Questions</h3>
        {documentName && (
          <p className="text-gray-600 text-sm">
            Generate questions from: <span className="font-medium">{documentName}</span>
          </p>
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
                  onChange={(e) => handleInputChange('questionType', e.target.value as QuestionGenerationData['questionType'])}
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
                  onChange={(e) => handleInputChange('bloomLevel', e.target.value as QuestionGenerationData['bloomLevel'])}
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
                className={`relative flex items-center justify-center px-4 py-2 border rounded-lg cursor-pointer hover:opacity-80 transition-opacity ${
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
                  onChange={(e) => handleInputChange('difficulty', e.target.value as QuestionGenerationData['difficulty'])}
                  className="sr-only"
                />
                <span className="text-sm font-medium">{option.label}</span>
                {formData.difficulty === option.value && (
                  <svg className="h-4 w-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
              </label>
            ))}
          </div>
          {errors.difficulty && (
            <p className="mt-1 text-sm text-red-600">{errors.difficulty}</p>
          )}
        </div>

        {/* Number of Questions */}
        <div>
          <label htmlFor="numberOfQuestions" className="block text-sm font-medium text-gray-700 mb-2">
            Number of Questions <span className="text-red-500">*</span>
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              id="numberOfQuestions"
              min="1"
              max="50"
              value={formData.numberOfQuestions}
              onChange={(e) => handleInputChange('numberOfQuestions', parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="1"
                max="50"
                value={formData.numberOfQuestions}
                onChange={(e) => handleInputChange('numberOfQuestions', parseInt(e.target.value) || 1)}
                className="w-16 px-2 py-1 border border-gray-300 rounded text-sm text-center focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="text-sm text-gray-600">questions</span>
            </div>
          </div>
          {errors.numberOfQuestions && (
            <p className="mt-1 text-sm text-red-600">{errors.numberOfQuestions}</p>
          )}
        </div>

        {/* Generate Button */}
        <div className="pt-4 border-t border-gray-200">
          <button
            type="submit"
            disabled={!isValid || isGenerating}
            className={`w-full font-medium py-3 px-6 rounded-lg transition-colors ${
              isValid && !isGenerating
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isGenerating ? (
              <div className="flex items-center justify-center space-x-2">
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Generating Questions...</span>
              </div>
            ) : (
              `Generate ${formData.numberOfQuestions} Question${formData.numberOfQuestions !== 1 ? 's' : ''}`
            )}
          </button>

          {!isValid && (
            <p className="mt-2 text-sm text-red-600 text-center">
              Please complete all required fields to generate questions
            </p>
          )}
        </div>
      </form>

      {/* Validation Status Indicator */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isValid ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-700">
            {isValid ? 'All validations passed' : 'Please fix validation errors above'}
          </span>
        </div>
      </div>
    </div>
  );
} 