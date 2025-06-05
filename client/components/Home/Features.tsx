"use client";

import React from 'react';
import { motion } from "framer-motion";

export const FeaturesSection = () => {
  const features = [
    {
      icon: "📷",
      title: "Generate questions with textbooks",
      description: "Generate questions from a textbook, a pdf, or a ppt in bulk at the speed of light."
    },
    {
      icon: "💬",
      title: "Create various types of questions",
      description: "Create various questions with a single button click. Customize as per your requirements and the AI will take care of the rest."
    },
    {
      icon: "🔍",
      title: "Built for educators",
      description: "Built for professors, teachers and doers."
    },
    {
      icon: "💻",
      title: "Ease of use",
      description: "It&apos;s as easy as using an Apple, and as expensive as buying one."
    },
    {
      icon: "💰",
      title: "Pricing like no other",
      description: "Our prices are best in the market. No cap, no lock, no credit card required."
    },
    {
      icon: "☁️",
      title: "100% Uptime guarantee",
      description: "We just cannot be taken down by anyone."
    },
    {
      icon: "👥",
      title: "Multi-tenant Architecture",
      description: "You can simply share passwords instead of buying new seats."
    },
    {
      icon: "🧑‍💻",
      title: "24/7 Customer Support",
      description: "We are available a 100% of the time. Atleast our AI Agents are."
    },
    {
      icon: "💯",
      title: "Money back guarantee",
      description: "If you donot like EveryAI, we will convince you to like us."
    },
    {
      icon: "❤️",
      title: "And everything else",
      description: "I just ran out of copy ideas. Accept my sincere apologies."
    }
  ];

  return (
    <section className="w-full py-20">
      <div className="mx-auto max-w-7xl px-4">
        <div className="text-center">
          <motion.h2 
            className="text-4xl font-bold md:text-5xl"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            Packed with thousands of features
          </motion.h2>
          
          <motion.p
            className="mx-auto mt-4 max-w-2xl text-lg text-neutral-400"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            From MCQ to Comphrehensive, Prashna AI has Agents
            for literally questions. It can even create a full question paper copy for you.
          </motion.p>
        </div>
        
        <div className="mt-20 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="col-span-1 rounded-xl border border-neutral-800 p-6"
          >
            <h3 className="text-xl font-medium mb-2">Generate questions with textbooks</h3>
            <p className="text-neutral-400 mb-6">Generate questions from a textbook, a pdf, or a ppt in bulk at the speed of light..</p>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg overflow-hidden border border-neutral-700 aspect-square">
                <div className="w-full h-full bg-neutral-800 flex items-center justify-center text-xl">
                  🖼️
                </div>
              </div>
              <div className="rounded-lg overflow-hidden border border-neutral-700 aspect-square">
                <div className="w-full h-full bg-neutral-800 flex items-center justify-center text-xl">
                  🖼️
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="col-span-1 rounded-xl border border-neutral-800 p-6"
          >
            <h3 className="text-xl font-medium mb-2">Create various types of questions</h3>
            <p className="text-neutral-400 mb-6">Create various questions with a single button click. Customize as per your requirements and the AI will take care of the rest.</p>
            
            <div className="rounded-lg overflow-hidden border border-neutral-700">
              <div className="w-full p-3 bg-neutral-800">
                <div className="p-3 rounded-lg bg-neutral-700 mb-3 text-sm">
                
                </div>
                <div className="p-3 rounded-lg bg-neutral-900 mb-3 text-sm">
              
                </div>
                <div className="p-3 rounded-lg bg-neutral-700 mb-3 text-sm">
    
                </div>
              </div>
            </div>
          </motion.div>

          <div className="col-span-1 lg:col-span-1 grid grid-cols-1 gap-6">
            {features.slice(2, 6).map((feature, idx) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.1 * idx + 0.3 }}
                className="rounded-xl border border-neutral-800 p-4"
              >
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{feature.icon}</div>
                  <div>
                    <h3 className="font-medium text-lg">{feature.title}</h3>
                    <p className="text-sm text-neutral-400">{feature.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
        
        <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.slice(6).map((feature, idx) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.1 * idx }}
              className="rounded-xl border border-neutral-800 p-4"
            >
              <div className="flex items-center gap-3">
                <div className="text-2xl">{feature.icon}</div>
                <div>
                  <h3 className="font-medium text-lg">{feature.title}</h3>
                  <p className="text-sm text-neutral-400">{feature.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}; 