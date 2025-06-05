import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { Navigation } from '@/components/Navigation';
import UploadClient from '@/components/UploadClient';

export default async function UploadPage() {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  const userName = user.firstName || user.emailAddresses[0].emailAddress;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <Navigation currentPath="/upload" userName={userName} />

      {/* Upload Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            Upload Document for Question Generation
          </h1>
          
          {/* Document Upload Component */}
        <UploadClient />

          {/* Validation Info */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded p-4">
            <h3 className="font-semibold text-blue-900 mb-2">✅ Task 6 Complete: File Upload with Validation</h3>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• <strong>Zod validation</strong> - File type and size validation</li>
              <li>• <strong>Drag & Drop</strong> - Interactive file upload interface</li>
              <li>• <strong>Error handling</strong> - Clear error messages for invalid files</li>
              <li>• <strong>File preview</strong> - Shows selected file details</li>
              <li>• <strong>Supported formats</strong> - PDF, DOCX, PPTX (up to 10MB)</li>
            </ul>
          </div>

          {/* Next Features */}
          <div className="mt-6 bg-green-50 border border-green-200 rounded p-4">
            <h3 className="font-semibold text-green-900 mb-2">🚀 Coming in Next Tasks:</h3>
            <ul className="text-green-800 text-sm space-y-1">
              <li>• Backend API endpoint creation</li>
              <li>• Document parsing with LangChain</li>
              <li>• Semantic chunking and storage</li>
              <li>• Question type selection interface</li>
              <li>• AI-powered question generation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
} 