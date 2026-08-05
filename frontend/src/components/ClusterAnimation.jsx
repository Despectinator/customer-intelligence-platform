import { useEffect, useState } from "react";

const colors = [
  "#14b8a6",
  "#06b6d4",
  "#f59e0b",
  "#8b5cf6",
];

export default function ClusterAnimation() {
  const [dots, setDots] = useState([]);

  useEffect(() => {
    const generated = [];

    for (let i = 0; i < 40; i++) {
      generated.push({
        id: i,
        top: Math.random() * 100,
        left: Math.random() * 100,
        delay: Math.random() * 3,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 8 + Math.random() * 8,
      });
    }

    setDots(generated);
  }, []);

  return (
    <div className="relative h-full overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 to-slate-800">

      {dots.map((dot) => (
        <div
          key={dot.id}
          className="absolute rounded-full animate-pulse"
          style={{
            top: `${dot.top}%`,
            left: `${dot.left}%`,
            width: dot.size,
            height: dot.size,
            background: dot.color,
            animationDelay: `${dot.delay}s`,
            boxShadow: `0 0 12px ${dot.color}`,
          }}
        />
      ))}

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(20,184,166,.08),transparent_70%)]" />

      <div className="absolute bottom-10 left-10 max-w-md">

        <span className="rounded-full bg-teal-500/20 px-4 py-2 text-sm font-medium text-teal-300">
          AI Customer Analytics
        </span>

        <h2 className="mt-6 text-5xl font-bold leading-tight text-white">
          Customer Intelligence
        </h2>

        <p className="mt-5 text-lg leading-8 text-slate-300">
          Segment customers, discover hidden buying patterns,
          monitor revenue trends, and generate intelligent
          recommendations powered by machine learning.
        </p>

      </div>

    </div>
  );
}
