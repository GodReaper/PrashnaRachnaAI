import { currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { Footer } from '@/components/Home/Footer';
import { Navbar } from '@/components/Home/Navbar';
import { HeroSection } from '@/components/Home/Hero';
import { FeaturesSection } from '@/components/Home/Features';
import { CTASection } from '@/components/Home/CTA';

export default async function HomePage() {
  const user = await currentUser();
  
  // If user is authenticated, redirect to dashboard
  if (user) {
    redirect('/dashboard');
  }

  return (
   <div className='bg-black flex min-h-screen flex-col text-white'>
    <Navbar />
    <HeroSection />
    <FeaturesSection />
    <CTASection />
    <Footer />
   </div>
  );
}
