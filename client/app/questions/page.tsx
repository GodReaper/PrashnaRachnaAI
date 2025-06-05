import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { Navigation } from '@/components/Navigation';
import { QuestionsPageClient } from '@/components/QuestionsPageClient';

export default async function QuestionsPage() {
  const user = await currentUser();
  
  if (!user) {
    redirect('/');
  }

  const userName = user.firstName || user.emailAddresses[0].emailAddress;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <Navigation currentPath="/questions" userName={userName} />

      {/* Questions Content with Sidebar */}
      <div className="flex h-[calc(100vh-4rem)]">
        <QuestionsPageClient />
      </div>
    </div>
  );
} 