"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function DevelopersPage() {
  const [openApiSpec, setOpenApiSpec] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/openapi.json")
      .then((res) => res.json())
      .then((data) => {
        setOpenApiSpec(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching OpenAPI spec:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center text-white">
        <p className="text-lg animate-pulse">Loading API Reference...</p>
      </div>
    );
  }

  if (!openApiSpec) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center text-white">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-4">Failed to load API spec.</p>
          <p className="text-gray-500">Make sure the backend is running on http://127.0.0.1:8000</p>
        </div>
      </div>
    );
  }

  // نستخدم Scalar API Reference
  // سكريبت تحميل Scalar
  return (
    <div className="min-h-screen bg-[#0d0d0d] text-white">
      <header className="px-6 py-4 border-b border-gray-800 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Link href="/" className="text-gray-400 hover:text-white">← Home</Link>
          <h1 className="text-xl font-bold text-purple-400">Developer Studio</h1>
        </div>
        <a 
          href="http://127.0.0.1:8000/openapi.json" 
          target="_blank" 
          className="text-sm text-gray-400 hover:text-white"
        >
          View OpenAPI Spec ↗
        </a>
      </header>

      {/* تحميل Scalar عبر CDN (أو مكتبة) */}
      <div className="p-4">
        <iframe 
          src="/scalar.html" 
          className="w-full border-0 rounded-xl"
          style={{ height: "calc(100vh - 120px)" }}
          title="API Reference"
        />
      </div>
    </div>
  );
}
