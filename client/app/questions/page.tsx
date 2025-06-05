import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { SignOutButton } from '@clerk/nextjs';
import Link from 'next/link';

export default async function QuestionsPage() {
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
                <Link href="/dashboard" className="text-gray-600 hover:text-gray-800 font-medium">
                  Dashboard
                </Link>
                <Link href="/upload" className="text-gray-600 hover:text-gray-800 font-medium">
                  Upload Document
                </Link>
                <Link href="/questions" className="text-blue-600 font-medium">
                  My Questions
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">
                {user.firstName || user.emailAddresses[0].emailAddress}
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

      {/* Questions Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">My Generated Questions</h1>
            <p className="text-gray-600 mt-1">View, edit, and manage your AI-generated questions</p>
          </div>

          {/* Sidebar and Content Layout */}
          <div className="flex">
            {/* Left Sidebar */}
            <div className="w-64 bg-gray-50 border-r border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Question Sets</h3>
              
              <div className="space-y-2">
                <div className="bg-blue-100 border border-blue-200 rounded p-3">
                  <p className="text-sm text-blue-800 font-medium">📄 Sample Document.pdf</p>
                  <p className="text-xs text-blue-600">15 questions • 2 days ago</p>
                </div>
                
                <div className="bg-gray-100 border border-gray-200 rounded p-3">
                  <p className="text-sm text-gray-600 font-medium">📊 Presentation.pptx</p>
                  <p className="text-xs text-gray-500">8 questions • 1 week ago</p>
                </div>
              </div>

              <div className="mt-6">
                <Link href="/upload">
                  <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">
                    + Upload New Document
                  </button>
                </Link>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                <svg className="mx-auto h-12 w-12 text-blue-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                
                <h2 className="text-xl font-bold text-blue-900 mb-2">
                  Ready to Generate Questions?
                </h2>
                
                <p className="text-blue-800 mb-6">
                  Upload a document to start generating AI-powered questions based on Bloom&apos;s Taxonomy.
                </p>

                <div className="bg-white border border-blue-200 rounded p-4 mb-6">
                  <h3 className="font-semibold text-blue-900 mb-2">🚀 Coming Features:</h3>
                  <ul className="text-blue-800 text-sm space-y-1 text-left">
                    <li>• Question generation and display</li>
                    <li>• Upvote/downvote feedback system</li>
                    <li>• Question editing capabilities</li>
                    <li>• Difficulty rating (Too Easy/Just Right/Too Hard)</li>
                    <li>• Export questions to various formats</li>
                    <li>• Bloom&apos;s Taxonomy level filtering</li>
                  </ul>
                </div>

                <Link href="/upload">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">
                    Upload Your First Document
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 