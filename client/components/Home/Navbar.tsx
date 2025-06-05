"use client";

import React from 'react';
import { SignInButton, SignUpButton } from '@clerk/nextjs';

export function Navbar() {
  return (
    <nav className="bg-black border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-white">
              Prashna Rachna AI
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <SignInButton mode="modal">
              <button className="text-gray-300 hover:text-white font-medium">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-xl">
                Get Started
              </button>
            </SignUpButton>
          </div>
        </div>
      </div>
    </nav>
  );
} 