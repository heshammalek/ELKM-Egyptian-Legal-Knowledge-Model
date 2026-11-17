"use client";

import Link from "next/link";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-[#0d0d0d] text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-6 text-blue-400">LexChain Documentation</h1>
        
        <section className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Overview</h2>
          <p className="text-gray-300 leading-relaxed mb-4">
            LexChain is a legal intelligence platform powered by the ELKM (Egyptian Legal Knowledge Model) ontology.
            It provides structured, queryable, and versioned legal data for Egyptian law.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Features</h2>
          <ul className="list-disc list-inside text-gray-300 space-y-2">
            <li>Graph Knowledge & Legal Ontology</li>
            <li>AI-Powered Legal Intelligence</li>
            <li>Article-Level Precision & Citations</li>
            <li>Temporal Tracking of Legal Texts</li>
            <li>Legislative Conflict Prediction</li>
            <li>Contract Risk Analysis</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Getting Started</h2>
          <p className="text-gray-300 leading-relaxed mb-4">
            To get started with LexChain, visit the <Link href="/chat" className="text-blue-400 underline">Chat interface</Link> or
            explore the <Link href="/developers" className="text-blue-400 underline">Developer Studio</Link>.
          </p>
        </section>

        <Link href="/" className="inline-block mt-8 text-blue-400 underline">
          ← Back to Home
        </Link>
      </div>
    </div>
  );
}
