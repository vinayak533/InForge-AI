import React from "react";
import { CheckCircle2, Loader2, Circle, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function AgentProgress({ agents, activeStep, error }) {
  // Compute connecting line progress percent
  const percentComplete = (activeStep / (agents.length - 1)) * 100;

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] w-full max-w-3xl mx-auto px-6 py-12">
      <div className="text-center mb-16 relative">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute -top-12 left-1/2 -translate-x-1/2 w-32 h-32 bg-accent-cyan/10 blur-[60px] rounded-full"
        />
        <h2 className="text-3xl md:text-5xl font-extrabold text-white mb-4 tracking-tight">
          InForge <span className="text-accent-cyan">Core</span> Active
        </h2>
        <p className="text-text-secondary text-sm md:text-base max-w-md mx-auto leading-relaxed">
          Our multi-agent neural network is autonomously processing your dataset using advanced heuristics.
        </p>
      </div>

      {error ? (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-4 p-5 bg-state-error/10 border border-state-error/20 rounded-[24px] text-state-error text-sm w-full max-w-lg mb-12 backdrop-blur-xl shadow-[0_0_30px_rgba(239,68,68,0.1)]"
        >
          <div className="p-2 rounded-xl bg-state-error/10">
            <AlertCircle className="w-6 h-6 flex-shrink-0" />
          </div>
          <div>
            <span className="font-bold uppercase tracking-wider text-[10px] block mb-1">Pipeline Execution Blocked</span>
            <p className="text-white/80">{error}</p>
          </div>
        </motion.div>
      ) : null}

      <div className="relative w-full max-w-lg">
        {/* Continuous Connecting Line */}
        <div className="absolute left-[24px] top-8 bottom-8 w-[2px] bg-white/5" />
        
        {/* Dynamic Glowing Connecting Line */}
        <motion.div 
          className="absolute left-[24px] top-8 w-[2px] bg-gradient-to-b from-accent-cyan to-accent-blue shadow-[0_0_15px_rgba(0,212,255,0.5)]"
          initial={{ height: "0%" }}
          animate={{ height: `${percentComplete}%` }}
          transition={{ duration: 0.5, ease: "circOut" }}
          style={{ maxHeight: "calc(100% - 64px)" }}
        />

        {/* Steps */}
        <div className="flex flex-col gap-10 relative z-10">
          {agents.map((agent, index) => {
            const isCompleted = agent.state === "completed";
            const isActive = agent.state === "active";
            const isPending = agent.state === "pending";
            const isFailed = agent.state === "failed";

            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex gap-8 items-start p-6 rounded-[28px] transition-all duration-500 relative group ${
                  isActive 
                    ? "glass-card border-glow shadow-cyanGlow scale-[1.02]" 
                    : isCompleted ? "opacity-90" : "opacity-30 grayscale"
                }`}
              >
                {/* Background Glow for Active */}
                {isActive && (
                  <div className="absolute inset-0 bg-accent-cyan/5 rounded-[28px] animate-pulse" />
                )}

                {/* Timeline Icon */}
                <div className="flex-shrink-0 w-12 h-12 flex items-center justify-center relative z-10">
                  {isCompleted && (
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200 }}>
                      <div className="w-10 h-10 rounded-2xl bg-state-success/10 flex items-center justify-center border border-state-success/30 shadow-[0_0_20px_rgba(0,229,160,0.1)]">
                        <CheckCircle2 className="w-6 h-6 text-state-success" />
                      </div>
                    </motion.div>
                  )}
                  
                  {isActive && (
                    <div className="w-12 h-12 flex items-center justify-center rounded-2xl bg-bg-dark border-2 border-accent-cyan shadow-[0_0_20px_rgba(0,212,255,0.3)] relative">
                      <Loader2 className="w-6 h-6 text-accent-cyan animate-spin" />
                      <div className="absolute inset-0 rounded-2xl border border-accent-cyan animate-ping opacity-20" />
                    </div>
                  )}
                  
                  {isPending && (
                    <div className="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                      <Circle className="w-4 h-4 text-text-secondary/40 fill-transparent" />
                    </div>
                  )}

                  {isFailed && (
                    <div className="w-10 h-10 rounded-2xl bg-state-error/10 flex items-center justify-center border border-state-error/30">
                      <AlertCircle className="w-6 h-6 text-state-error" />
                    </div>
                  )}
                </div>

                {/* Step Details */}
                <div className="flex-grow min-w-0 pt-1 relative z-10">
                  <div className="flex justify-between items-center mb-1">
                    <h3 className={`text-sm font-bold tracking-tight transition-colors duration-300 ${
                      isActive ? "text-accent-cyan" : isCompleted ? "text-white" : "text-text-secondary"
                    }`}>
                      {agent.label}
                    </h3>
                    {isCompleted && (
                      <span className="text-[9px] font-bold text-state-success uppercase tracking-widest bg-state-success/10 px-2 py-0.5 rounded-md border border-state-success/20">
                        Verified
                      </span>
                    )}
                  </div>
                  <p className={`text-xs transition-colors duration-300 truncate leading-relaxed ${
                    isActive ? "text-white font-medium" : "text-text-secondary/60"
                  }`}>
                    {agent.status_text}
                  </p>
                  
                  {/* Subtle active step progress slider */}
                  <AnimatePresence>
                    {isActive && (
                      <motion.div 
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4"
                      >
                        <div className="relative h-1 w-full bg-white/5 rounded-full overflow-hidden">
                          <motion.div 
                            className="absolute top-0 left-0 h-full bg-gradient-to-r from-accent-cyan to-accent-blue"
                            initial={{ width: "5%" }}
                            animate={{ width: "95%" }}
                            transition={{ repeat: Infinity, repeatType: "reverse", duration: 2, ease: "easeInOut" }}
                          />
                        </div>
                        <div className="mt-2 flex justify-between">
                          <span className="text-[9px] font-bold text-accent-cyan/50 uppercase tracking-[0.2em] animate-pulse">Processing...</span>
                          <span className="text-[9px] font-mono text-accent-cyan/50">AUTO_SCALE_OPS</span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
