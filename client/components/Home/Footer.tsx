"use client";

import React from 'react';
import Link from 'next/link';

export const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  const footerLinks = [
    {
      title: "Product",
      links: [
        { name: "Pricing", href: "/pricing" },
        { name: "Blog", href: "/blog" },
        { name: "Contact", href: "/contact" },
      ]
    },
    {
      title: "Legal",
      links: [
        { name: "Privacy Policy", href: "/privacy-policy" },
        { name: "Terms of Service", href: "/terms" },
        { name: "Refund Policy", href: "/refund-policy" },
      ]
    },
    {
      title: "Connect",
      links: [
        { name: "Twitter", href: "https://twitter.com" },
        { name: "LinkedIn", href: "https://linkedin.com" },
        { name: "GitHub", href: "https://github.com" },
      ]
    }
  ];
  
  return (
    <footer className="w-full border-t border-neutral-800 py-12">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div className="col-span-1">
            <div className="flex items-center">
              <div className="flex items-center">
                <div className="size-6 rounded-md bg-white mr-2" />
                <span className="text-lg font-medium">Prashna AI</span>
              </div>
            </div>
            <p className="mt-4 text-sm text-neutral-500">
              Copyright © {currentYear} Prashna Rachna AI<br />
              All rights reserved
            </p>
          </div>
          
          {footerLinks.map((group) => (
            <div key={group.title} className="col-span-1">
              <h3 className="font-semibold">{group.title}</h3>
              <ul className="mt-4 space-y-2">
                {group.links.map((link) => (
                  <li key={link.name}>
                    <Link href={link.href} className="text-sm text-neutral-400 hover:text-white transition-colors">
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </footer>
  );
}; 