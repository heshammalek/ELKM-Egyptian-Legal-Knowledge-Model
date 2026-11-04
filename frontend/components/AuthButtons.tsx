"use client";

export default function AuthButtons() {
  return (
    <div className="flex gap-4">
      <button className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition">
        Sign In
      </button>
      <button className="px-4 py-2 text-sm font-medium bg-white text-black rounded-md hover:bg-gray-200 transition">
        Register
      </button>
    </div>
  );
}
