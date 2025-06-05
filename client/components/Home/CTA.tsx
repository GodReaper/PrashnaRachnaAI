"use client";

import React from 'react';
import { motion } from "framer-motion";

import { SignUpButton } from '@clerk/nextjs';

export const CTASection = () => {
  return (
    <section className="w-full py-24 relative">
      <div className="grid-background absolute inset-0 z-0 opacity-30" />
      <motion.div 
        className="relative z-10 mx-auto max-w-2xl text-center px-4"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <div className="rounded-2xl bg-neutral-900 border border-neutral-800 p-8 md:p-12">
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
           Ready to Transform Your Teaching?
          </h2>
          <p className="mt-4 text-neutral-400">
          Join educators who are already using AI to create better assessments.
          </p>
          <div className="mt-8">
          <SignUpButton mode="modal">
          <button className="bg-white hover:bg-gray-100 text-gray-950 font-bold py-3 px-8 rounded-lg text-lg">
            Get Started for Free
          </button>
        </SignUpButton>

          </div>
        </div>
      </motion.div>
    </section>
  );
}; 