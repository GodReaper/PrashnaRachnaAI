import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

import TestQuestionGenerationClient from '@/components/TestQuestionGenerationClient';

export default async function TestQuestionGenerationPage() {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🧪 Task 8: Question Generation UI Validation Test
              </h1>
              <p className="text-gray-600 mt-1">
                Test the question generation form with Zod validation
              </p>
            </div>
            <Link href="/dashboard">
              <button className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded">
                ← Back to Dashboard
              </button>
            </Link>
          </div>
        </div>
      </div>

      {/* Test Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Test Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-blue-900 mb-3">
            🎯 Validation Testing Instructions
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-blue-800 mb-2">✅ Test Valid Selections:</h3>
              <ul className="text-blue-700 text-sm space-y-1">
                <li>• Select different question types</li>
                <li>• Choose various Bloom&apos;s taxonomy levels</li>
                <li>• Adjust number of questions (1-50)</li>
                <li>• Pick different difficulty levels</li>
                <li>• Submit form when all fields are valid</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-blue-800 mb-2">🚫 Test Invalid Scenarios:</h3>
              <ul className="text-blue-700 text-sm space-y-1">
                <li>• Try numbers outside 1-50 range</li>
                <li>• Clear number field (empty/invalid)</li>
                <li>• Watch validation status indicator</li>
                <li>• Notice disabled submit button</li>
                <li>• Check error messages display</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Zod Schema Info */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-green-900 mb-3">
            🛡️ Zod Validation Schema
          </h2>
          <div className="bg-white border border-green-200 rounded p-4">
            <pre className="text-sm text-green-800 overflow-x-auto">
{`const questionGenerationSchema = z.object({
  questionType: z.enum(["MCQ", "FillInTheBlank", "TrueFalse", "ShortAnswer"]),
  bloomLevel: z.enum(["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]),
  numberOfQuestions: z.number().min(1).max(50),
  difficulty: z.enum(["Easy", "Medium", "Hard"])
});`}
            </pre>
          </div>
        </div>

        {/* Question Generation Component */}
        <TestQuestionGenerationClient />

        {/* Test Results */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-8">
          <h2 className="text-lg font-semibold text-yellow-900 mb-3">
            📊 Expected Test Results
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-yellow-800 mb-2">When Valid:</h3>
              <ul className="text-yellow-700 text-sm space-y-1">
                <li>• Green validation indicator</li>
                <li>• Submit button enabled and blue</li>
                <li>• No error messages visible</li>
                <li>• Form submission shows success alert</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-yellow-800 mb-2">When Invalid:</h3>
              <ul className="text-yellow-700 text-sm space-y-1">
                <li>• Red validation indicator</li>
                <li>• Submit button disabled and gray</li>
                <li>• Error messages under invalid fields</li>
                <li>• Form submission blocked</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Link href="/upload">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">
              Test Full Upload Flow →
            </button>
          </Link>
          <Link href="/questions">
            <button className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded">
              View Questions Interface →
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
} 