import { SignOutButton } from '@clerk/nextjs';
import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function Dashboard() {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="text-xl font-bold text-gray-800">
                Question Generator
              </Link>
              <div className="hidden md:flex space-x-4">
                <Link href="/dashboard" className="text-blue-600 font-medium">
                  Dashboard
                </Link>
                <Link href="/upload" className="text-gray-600 hover:text-gray-800 font-medium">
                  Upload Document
                </Link>
                <Link href="/questions" className="text-gray-600 hover:text-gray-800 font-medium">
                  My Questions
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">
                Welcome, {user.firstName || user.emailAddresses[0].emailAddress}
              </span>
              <SignOutButton>
                <button className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded">
                  Sign Out
                </button>
              </SignOutButton>
            </div>
          </div>
        </div>
      </nav>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            🎉 Welcome to Your Question Generator Dashboard!
          </h1>
          <p className="text-gray-600">
            Start generating AI-powered questions from your documents with our intelligent question generation system.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Link href="/upload">
            <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-blue-500">
              <div className="flex items-center">
                <svg className="h-8 w-8 text-blue-500 mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Upload Document</h3>
                  <p className="text-gray-600">Upload PDF, DOCX, or PPTX files to generate questions</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/questions">
            <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-green-500">
              <div className="flex items-center">
                <svg className="h-8 w-8 text-green-500 mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">My Questions</h3>
                  <p className="text-gray-600">View and manage your generated questions</p>
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Task 6 Complete Status */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-bold text-green-900 mb-4">
            ✅ Task 6 Complete: Document Upload with Validation
          </h2>
          
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="bg-white border border-green-200 rounded p-4">
              <h3 className="font-semibold text-green-900 mb-2">🔧 Zod Validation</h3>
              <ul className="text-green-800 text-sm space-y-1">
                <li>• File type validation</li>
                <li>• File size limits (10MB)</li>
                <li>• Error message display</li>
              </ul>
            </div>
            
            <div className="bg-white border border-green-200 rounded p-4">
              <h3 className="font-semibold text-green-900 mb-2">🎯 UI Features</h3>
              <ul className="text-green-800 text-sm space-y-1">
                <li>• Drag & drop interface</li>
                <li>• File preview display</li>
                <li>• Upload progress indication</li>
              </ul>
            </div>
            
            <div className="bg-white border border-green-200 rounded p-4">
              <h3 className="font-semibold text-green-900 mb-2">📋 Supported Files</h3>
              <ul className="text-green-800 text-sm space-y-1">
                <li>• PDF documents</li>
                <li>• Word files (.docx)</li>
                <li>• PowerPoint (.pptx)</li>
              </ul>
            </div>
          </div>

          <div className="bg-white border border-green-200 rounded p-4">
            <h3 className="font-semibold text-green-900 mb-2">🧪 Test Validation</h3>
            <p className="text-green-800 text-sm mb-3">
              Test the file upload validation with different file types:
            </p>
            <Link href="/test-upload">
              <button className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded">
                Test Upload Validation
              </button>
            </Link>
          </div>
        </div>

        {/* App Router & Protected Routes Status */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-bold text-blue-900 mb-4">
            🔒 Protected Routes Status
          </h2>
          
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white border border-blue-200 rounded p-4">
              <h3 className="font-semibold text-blue-900 mb-2">✅ Task 5 Routes</h3>
              <ul className="text-blue-800 text-sm space-y-1">
                <li>• /dashboard (authenticated)</li>
                <li>• /upload (authenticated)</li>
                <li>• /questions (authenticated)</li>
              </ul>
            </div>
            
            <div className="bg-white border border-blue-200 rounded p-4">
              <h3 className="font-semibold text-blue-900 mb-2">🛡️ Middleware Protection</h3>
              <ul className="text-blue-800 text-sm space-y-1">
                <li>• Auto-redirect on auth state</li>
                <li>• Route protection enabled</li>
                <li>• Seamless navigation</li>
              </ul>
            </div>
            
            <div className="bg-white border border-blue-200 rounded p-4">
              <h3 className="font-semibold text-blue-900 mb-2">🚀 Next: Task 7</h3>
              <ul className="text-blue-800 text-sm space-y-1">
                <li>• Left sidebar implementation</li>
                <li>• Previous questions display</li>
                <li>• Question history management</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 