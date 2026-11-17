"use client";

export default function AuthButtons() {
  return (
    <div className="flex gap-2">
      <button className="px-4 py-2 text-sm bg-gray-700 text-white rounded hover:bg-gray-600 transition">
        Sign In
      </button>
      <button className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-500 transition">
        Register
      </button>
    </div>
  );
}
