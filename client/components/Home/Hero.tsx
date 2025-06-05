"use client";

import React from 'react';
import { motion } from "framer-motion";
import Link from 'next/link';
import Image from 'next/image';
import { cn } from "@/lib/utils";
import { SignUpButton } from '@clerk/nextjs';

export function HeroSection() {
  return (
    <section className="relative w-full py-20 bg-black">
      {/* Grid background from the demo */}
      <div
        className={cn(
          "absolute inset-0",
          "[background-size:40px_40px]",
          "opacity-40",
          "[background-image:linear-gradient(to_right,#262626_1px,transparent_1px),linear-gradient(to_bottom,#262626_1px,transparent_1px)]",
        )}
      />
      {/* Radial gradient overlay */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-black [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]"></div>
      
      <div className="relative z-10 mx-auto max-w-6xl px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center rounded-full border border-neutral-700 bg-neutral-800/50 px-3 py-1 text-sm">
            <span className="mr-2 rounded-full bg-green-500 px-2 py-0.5 text-xs font-medium">New</span>
            <span className="text-neutral-300">We&apos;ve raised $69M seed funding</span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="ml-1 h-3 w-3">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </div>
        </motion.div>
        
        <motion.h1 
          className="mt-8 text-4xl font-bold leading-tight tracking-tight md:text-8xl bg-gradient-to-b from-white to-neutral-400 bg-clip-text text-transparent"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          AI-Powered Question
          <span className="text-blue-400"> Generation</span>
        </motion.h1>
        
        <motion.p 
          className="mx-auto mt-6 max-w-2xl text-xl text-neutral-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          Transform your documents into comprehensive question sets based on Bloom&apos;s Taxonomy. 
          Generate MCQs, fill-in-the-blanks, and more with intelligent AI agents.
        </motion.p>
        
        <motion.div 
          className="mt-10 flex flex-wrap items-center justify-center gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <SignUpButton mode="modal">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg text-lg">
              Start Generating Questions
            </button>
          </SignUpButton>
          <Link href="#features">
            <button className="border border-gray-600 hover:border-gray-400 text-gray-300 font-medium py-3 px-8 rounded-lg text-lg">
              Learn More
            </button>
          </Link>
        </motion.div>
        
        <motion.div 
          className="mt-16"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.8 }}
        >
          <div className="relative mx-auto max-w-5xl overflow-hidden rounded-xl border border-neutral-800 bg-neutral-900">
            <div className="p-2">
              <Image
                src="/images/landing.png"
                alt="Dashboard preview"
                width={1200}
                height={800}
                className="rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
} 