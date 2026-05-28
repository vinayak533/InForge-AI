import React, { useState } from "react";
import { Copy, Check, Download, Terminal } from "lucide-react";
import { motion } from "framer-motion";

export default function CodeTab({ data }) {
  const codeObj = data.code_agent || {};
  const rawCode = codeObj.code || "# No script generated yet.";
  
  const [copied, setCopied] = useState(false);

  // Copy code to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(rawCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  // Download raw Python script file
  const handleDownload = () => {
    const blob = new Blob([rawCode], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "inforge_analysis_script.py";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col gap-6 animate-fadeIn h-[75vh]">
      {/* Visual code box title bar */}
      <div className="flex justify-between items-center p-4 glass-card border-glow rounded-xl">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-accent-cyan" />
          <span className="text-xs font-semibold text-text-primary">
            Standalone Python Pipeline Script (.py)
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-bg-dark hover:bg-bg-dark/80 active:scale-95 border border-card-border text-xs font-semibold text-text-primary rounded-lg transition-all"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-state-success" />
                Copied
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-text-secondary" />
                Copy Code
              </>
            )}
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-accent-cyan hover:bg-accent-cyan/95 active:scale-95 text-xs font-bold text-bg-dark rounded-lg transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            Download .py
          </button>
        </div>
      </div>

      {/* Code Display Area */}
      <div className="flex-grow min-h-0 bg-bg-dark border border-card-border rounded-xl p-6 font-mono text-xs overflow-auto select-text relative border-glow">
        {/* Soft layout accent background blur */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-accent-cyan/5 rounded-bl-full filter blur-xl opacity-20 pointer-events-none" />
        
        <pre className="text-text-secondary whitespace-pre-wrap leading-relaxed select-text font-mono">
          <code className="select-text font-mono text-[#F0F4FF]">
            {rawCode}
          </code>
        </pre>
      </div>
    </div>
  );
}
