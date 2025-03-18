"use client";

import Link from "next/link";
import { useState } from "react";
import { FaBars, FaTimes, FaGlobe, FaCode, FaGithub } from "react-icons/fa";

export default function HeaderNav() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="bg-dark-lightest py-4 px-4 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="flex items-center space-x-2">
          <div className="text-primary text-3xl">
            <FaGlobe className="inline-block animate-pulse-slow" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-primary animate-glow">
              AI Browser Automation
            </h1>
            <p className="text-xs text-gray-400">Powered by Next.js & Flask</p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex space-x-6">
          <Link 
            href="/" 
            className="text-gray-300 hover:text-primary transition-colors"
          >
            Home
          </Link>
          <Link 
            href="/docs" 
            className="text-gray-300 hover:text-primary transition-colors"
          >
            Documentation
          </Link>
          <a 
            href="https://github.com/yourusername/ai-browser-automation" 
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-300 hover:text-primary transition-colors flex items-center"
          >
            <FaGithub className="mr-1" /> GitHub
          </a>
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-gray-300 hover:text-primary"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-expanded={isMenuOpen}
          aria-label="Toggle navigation menu"
        >
          {isMenuOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden container mx-auto mt-4 pb-4">
          <nav className="flex flex-col space-y-4">
            <Link 
              href="/" 
              className="text-gray-300 hover:text-primary transition-colors py-2 px-4 rounded-md hover:bg-gray-800"
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link 
              href="/docs" 
              className="text-gray-300 hover:text-primary transition-colors py-2 px-4 rounded-md hover:bg-gray-800"
              onClick={() => setIsMenuOpen(false)}
            >
              Documentation
            </Link>
            <a 
              href="https://github.com/yourusername/ai-browser-automation" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-300 hover:text-primary transition-colors py-2 px-4 rounded-md hover:bg-gray-800 flex items-center"
              onClick={() => setIsMenuOpen(false)}
            >
              <FaGithub className="mr-2" /> GitHub
            </a>
          </nav>
        </div>
      )}
    </header>
  );
}
