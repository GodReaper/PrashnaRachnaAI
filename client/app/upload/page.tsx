import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { SignOutButton } from '@clerk/nextjs';
import Link from 'next/link';

export default async function UploadPage() {
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
                <Link href="/upload" className="text-blue-600 font-medium">
                  Upload Document
                </Link>
                <Link href="/questions" className="text-gray-600 hover:text-gray-800 font-medium">
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

      {/* Upload Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            Upload Document for Question Generation
          </h1>
          
          <div className="mb-8">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-gray-400 transition-colors">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Drop files here or click to upload
                  </span>
                  <span className="mt-1 block text-sm text-gray-500">
                    Supports PDF, DOCX, and PPTX files up to 10MB
                  </span>
                </label>
                <input id="file-upload" name="file-upload" type="file" className="sr-only" accept=".pdf,.docx,.pptx" />
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
            <h3 className="font-semibold text-blue-900 mb-2">✨ Coming in Next Tasks:</h3>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• File validation with Zod schemas</li>
              <li>• Document parsing with LangChain</li>
              <li>• Semantic chunking and storage</li>
              <li>• Question type selection interface</li>
              <li>• AI-powered question generation</li>
            </ul>
          </div>

          <button 
            disabled 
            className="w-full bg-gray-300 text-gray-500 font-medium py-3 px-6 rounded-lg cursor-not-allowed"
          >
            Upload & Process Document (Coming Soon)
          </button>
        </div>
      </div>
    </div>
  );
} 