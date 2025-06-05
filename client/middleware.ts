import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)', '/upload(.*)', '/questions(.*)', '/test-upload(.*)', '/test-question-generation(.*)']);

export default clerkMiddleware(async (auth, req) => {
  const { userId } = await auth();
  
  // Protect dashboard, upload, questions, and test-upload routes
  if (isProtectedRoute(req)) {
    if (!userId) {
      return NextResponse.redirect(new URL('/', req.url));
    }
  }

  // If user is signed in and on homepage, redirect to dashboard
  if (userId && req.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', req.url));
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};