"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";

const GithubIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
  </svg>
);

const AnimatedGraphBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let nodes: { x: number; y: number; vx: number; vy: number; radius: number }[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initNodes();
    };

    const initNodes = () => {
      nodes = [];
      const numNodes = Math.floor((window.innerWidth * window.innerHeight) / 15000);
      for (let i = 0; i < numNodes; i++) {
        nodes.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1,
        });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = "rgba(88, 166, 255, 0.15)";
      ctx.lineWidth = 1;
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      nodes.forEach((node) => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(163, 113, 247, 0.7)";
        ctx.fill();

        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1;
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener("resize", resize);
    resize();
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full z-0 opacity-40 pointer-events-none"
    />
  );
};

export default function Home() {
  return (
    <div className="relative w-full h-[calc(100vh-80px)] bg-black overflow-hidden flex flex-col items-center justify-center">
      
      <AnimatedGraphBackground />

      <div className="z-10 flex flex-col items-center justify-center text-center px-4">
        
                <h1 className="text-8xl md:text-9xl font-extrabold tracking-tighter mb-6 shimmer-text">
          ELKM
        </h1>
        
        <p className="text-xl md:text-2xl mb-12 max-w-2xl font-light shimmer-text">
          Egyptian Legal Knowledge Model
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link 
            href="/chat" 
            className="px-8 py-3 bg-white text-black font-semibold rounded-lg hover:bg-gray-200 transition-colors duration-200"
          >
            Start Chat
          </Link>

          <Link 
            href="https://github.com/heshammalek/ELKM-Egyptian-Legal-Knowledge-Model" 
            target="_blank"
            className="px-8 py-3 bg-transparent border border-gray-700 text-white font-semibold rounded-lg hover:bg-gray-900 hover:border-gray-500 transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <GithubIcon />
            Documentation
          </Link>
        </div>
      </div>

      <div className="absolute bottom-10 left-10 z-50 flex items-center gap-4">
        <div className="w-16 h-16 bg-[#111] border border-gray-700 rounded-full flex items-center justify-center animate-bounce shadow-xl">
          <span className="text-3xl">🤖</span>
        </div>
        <div className="text-sm shimmer-text font-medium">
          Legal Expert Assistant
        </div>
      </div>

    </div>
  );
}

      <div className="absolute bottom-10 left-10 z-50 flex items-center gap-4">
        <div className="w-16 h-16 bg-[#111] border border-gray-700 rounded-full flex items-center justify-center animate-bounce shadow-xl">
          <span className="text-3xl">🤖</span>
        </div>
        <div className="text-sm text-gray-400 shimmer-text font-medium">
          Legal Expert Assistant
        </div>
      </div>

    
