import React, { useState, useEffect, useRef } from "react";
import { UploadCloud, File, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { API_BASE } from "../config/api";

export default function Landing({ onStartAnalysis }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);

  // 1. Drifting Particle Canvas System
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    let animationFrameId;
    let particles = [];
    const particleCount = 80;
    const connectionDist = 120;
    
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3, // slow drift
        vy: (Math.random() - 0.5) * 0.3,
        radius: Math.random() * 1.5 + 1
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw particles
      particles.forEach((p, idx) => {
        p.x += p.vx;
        p.y += p.vy;
        
        // Wrap edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(0, 212, 255, 0.15)";
        ctx.fill();
        
        // Connect close particles
        for (let j = idx + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p2.x - p.x, p2.y - p.y);
          if (dist < connectionDist) {
            const alpha = (1 - dist / connectionDist) * 0.12;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(0, 212, 255, ${alpha})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      });
      
      animationFrameId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  // 2. Drag & Drop Event Handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    const filename = selectedFile.name;
    if (filename.endsWith(".csv") || filename.endsWith(".xlsx") || filename.endsWith(".xls")) {
      setFile(selectedFile);
    } else {
      setError("Supported file types are restricted to CSV, XLSX, and XLS format.");
    }
  };

  // 3. Upload triggers to FastAPI
  const handleAnalyze = async () => {
    if (!file || isLoading) return;
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Target file upload failed. Try again.");
      }

      const data = await response.json();
      onStartAnalysis(data.session_id, file.name);
    } catch (err) {
      console.error(err);
      setError("Failed to establish server connection. Verify backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-bg-dark overflow-hidden font-sans select-none">
      {/* Background Particles Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none opacity-40" />

      {/* Decorative Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-accent-cyan/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-accent-blue/5 blur-[150px] pointer-events-none" />

      {/* Main Container Content */}
      <div className="relative z-10 w-full max-w-4xl mx-auto flex flex-col items-center justify-center px-6">
        
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-[10px] font-bold uppercase tracking-[0.2em] text-accent-cyan flex items-center gap-2"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse" />
          Powered by Advanced Analytical Intelligence
        </motion.div>

        {/* Title Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col items-center mb-6 text-center"
        >
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-4">
            InForge <span className="text-accent-cyan">AI</span>
          </h1>
          <p className="max-w-xl text-text-secondary text-sm md:text-lg font-medium leading-relaxed">
            Transform raw data into actionable insights with our premium 
            AI-driven analytical engine. Effortless, precise, and professional.
          </p>
        </motion.div>

        {/* Error Callout */}
        {error && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 p-4 bg-state-error/10 border border-state-error/20 rounded-2xl text-state-error text-xs w-full max-w-md mb-8 backdrop-blur-xl"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="font-medium">{error}</span>
          </motion.div>
        )}

        {/* Drag and Drop Zone / File Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="w-full max-w-md"
        >
          {!file ? (
            /* Upload Dropzone */
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
              className={`group relative h-[240px] w-full rounded-[32px] flex flex-col items-center justify-center gap-4 cursor-pointer glass-card card-hover-premium border-glow ${
                dragActive ? "border-accent-cyan ring-4 ring-accent-cyan/10" : ""
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".csv, .xlsx, .xls"
                onChange={handleChange}
              />
              
              <div className="p-5 rounded-3xl bg-white/5 border border-white/10 group-hover:border-accent-cyan/30 group-hover:bg-accent-cyan/5 transition-all duration-500">
                <UploadCloud className="w-8 h-8 text-text-secondary group-hover:text-accent-cyan transition-colors" />
              </div>

              <div className="text-center">
                <p className="text-base font-bold text-white tracking-tight">
                  Drop your dataset here
                </p>
                <p className="text-xs text-text-secondary mt-1.5 font-medium">
                  Supports CSV, XLSX, and XLS formats
                </p>
              </div>

              {/* Shimmer Effect */}
              <div className="absolute inset-0 rounded-[32px] overflow-hidden pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="absolute inset-0 animate-shimmer" />
              </div>
            </div>
          ) : (
            /* Selected File Card */
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-8 glass-card card-hover-premium rounded-[32px] flex flex-col gap-6 w-full relative overflow-hidden"
            >
              <div className="flex gap-5 items-center">
                <div className="p-4 bg-accent-cyan/10 rounded-2xl text-accent-cyan border border-accent-cyan/20">
                  <File className="w-7 h-7" />
                </div>
                <div className="min-w-0 flex-grow">
                  <h3 className="text-base font-bold text-white truncate">
                    {file.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="px-2 py-0.5 rounded-md bg-white/5 text-[10px] font-bold text-text-secondary font-mono border border-white/5 uppercase">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                    <span className="w-1 h-1 rounded-full bg-white/20" />
                    <span className="text-[10px] font-bold text-accent-cyan uppercase tracking-wider">
                      Ready for analysis
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <button
                  onClick={handleAnalyze}
                  disabled={isLoading}
                  className="premium-button flex items-center justify-center gap-3 w-full py-5 bg-accent-cyan hover:bg-white text-bg-dark font-bold text-sm rounded-[24px] transition-all shadow-[0_0_30px_rgba(0,245,255,0.3)] hover:shadow-[0_0_40px_rgba(255,255,255,0.3)] disabled:opacity-50 group/btn overflow-hidden relative"
                >
                  {isLoading ? (
                    <div className="flex items-center gap-3 relative z-10">
                      <div className="relative">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <div className="absolute inset-0 animate-ping opacity-20 bg-bg-dark rounded-full" />
                      </div>
                      <span className="tracking-widest uppercase text-xs">Initializing Neural Engine...</span>
                    </div>
                  ) : (
                    <>
                      <span className="relative z-10">Initialize Analysis</span>
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000" />
                    </>
                  )}
                </button>
                
                {!isLoading && (
                  <button 
                    onClick={() => setFile(null)}
                    className="py-2 text-[11px] font-bold text-text-secondary hover:text-state-error transition-colors uppercase tracking-widest"
                  >
                    Cancel and Replace
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Footer Stats/Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-16 grid grid-cols-3 gap-8 w-full max-w-2xl"
        >
          {[
            { label: "Data Quality", val: "Enterprise" },
            { label: "AI Models", val: "Proprietary" },
            { label: "Insights", val: "Real-time" }
          ].map((stat, i) => (
            <div key={i} className="flex flex-col items-center">
              <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest mb-1">{stat.label}</span>
              <span className="text-sm font-bold text-white">{stat.val}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );

}
