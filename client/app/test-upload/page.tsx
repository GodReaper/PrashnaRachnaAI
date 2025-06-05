
import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import UploadClient from '@/components/UploadClient';

export default async function TestUploadPage() {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <Link href="/upload" className="text-blue-600 hover:text-blue-800">
            ← Back to Upload Page
          </Link>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            Task 6 Validation Testing
          </h1>
          
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Test File Upload Validation</h2>
            <p className="text-gray-600 mb-4">
              Try uploading different file types to test the Zod validation:
            </p>
            
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div className="bg-green-50 border border-green-200 rounded p-3">
                <h3 className="font-semibold text-green-900 mb-1">✅ Should Work:</h3>
                <ul className="text-green-800 text-sm">
                  <li>• PDF files (.pdf)</li>
                  <li>• Word documents (.docx)</li>
                  <li>• PowerPoint (.pptx)</li>
                  <li>• Files under 10MB</li>
                </ul>
              </div>
              
              <div className="bg-red-50 border border-red-200 rounded p-3">
                <h3 className="font-semibold text-red-900 mb-1">❌ Should Fail:</h3>
                <ul className="text-red-800 text-sm">
                  <li>• Image files (.jpg, .png)</li>
                  <li>• Text files (.txt)</li>
                  <li>• Excel files (.xlsx)</li>
                  <li>• Files over 10MB</li>
                </ul>
              </div>
            </div>
          </div>

        <UploadClient />    

          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded p-4">
            <h3 className="font-semibold text-yellow-900 mb-2">🧪 Testing Instructions:</h3>
            <ol className="text-yellow-800 text-sm space-y-1">
              <li>1. Try uploading a valid file (PDF/DOCX/PPTX) - should work</li>
              <li>2. Try uploading an invalid file type - should show error</li>
              <li>3. Try a file over 10MB - should show size error</li>
              <li>4. Check browser console for file details</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
} 