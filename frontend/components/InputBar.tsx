"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function InputBar({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const [cameraOpen, setCameraOpen] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!cameraOpen) return;
    let stream: MediaStream | null = null;
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((s) => {
        stream = s;
        if (videoRef.current) videoRef.current.srcObject = s;
      })
      .catch((err) => console.error("Camera error:", err));
    return () => stream?.getTracks().forEach((t) => t.stop());
  }, [cameraOpen]);

  const send = () => {
    const t = value.trim();
    if (!t || disabled) return;
    onSend(t);
    setValue("");
  };

  return (
    <>
      <div className="p-4 bg-[#0d0d0d] shrink-0 flex justify-center border-t border-gray-800">
        <div className="w-full max-w-3xl bg-[#1a1a1a] border border-[#2a2a2a] rounded-2xl p-2 flex items-end gap-2 shadow-lg">
          <input type="file" ref={fileRef} className="hidden" />
          <button onClick={() => fileRef.current?.click()} className="p-2 text-gray-500 hover:text-gray-300 transition rounded-lg" title="Attach">📎</button>
          <textarea
            value={value}
            dir="auto"
            rows={1}
            placeholder="Message LexChain..."
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault();
                send();
              }
            }}
            className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500 resize-none max-h-32 overflow-y-auto py-2 text-sm"
          />
          <button onClick={() => setCameraOpen((v) => !v)} className="p-2 text-gray-500 hover:text-gray-300 transition rounded-lg" title="Camera">📷</button>
          <button onClick={send} disabled={disabled || !value.trim()} className="p-2 bg-white text-black rounded-lg hover:bg-gray-200 transition disabled:opacity-50">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="19" x2="12" y2="5" />
              <polyline points="5 12 12 5 19 12" />
            </svg>
          </button>
        </div>
      </div>

      {cameraOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[60]">
          <div className="bg-[#1a1a1a] p-4 rounded-xl border border-[#2a2a2a]">
            <video ref={videoRef} autoPlay playsInline className="w-80 h-60 bg-black rounded-lg mb-4 object-cover" />
            <div className="flex justify-end gap-2">
              <button onClick={() => setCameraOpen(false)} className="px-4 py-2 text-sm text-gray-400 hover:text-white">Close</button>
              <button className="px-4 py-2 text-sm bg-white text-black rounded">Capture</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
