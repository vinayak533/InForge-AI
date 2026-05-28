import React from "react";
import { Cpu, Award, ShieldAlert, Sparkles, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

export default function MLTab({ data }) {
  console.log("Rendering MLTab with data:", data);
  
  const mlData = (data?.ml_agent && typeof data.ml_agent === "object" && !Array.isArray(data.ml_agent)) ? data.ml_agent : {};
  const taskType = typeof mlData?.task_type === "string" ? mlData.task_type : "predictive";
  const bestModel = typeof mlData?.best_model === "string" ? mlData.best_model : "None";
  const bestScore = typeof mlData?.best_score === "number" ? mlData.best_score : (parseFloat(mlData?.best_score) || 0.0);
  const results = Array.isArray(mlData?.model_results) ? mlData.model_results : [];
  
  const plots = (mlData?.plots && typeof mlData.plots === "object" && !Array.isArray(mlData.plots)) ? mlData.plots : {};
  const explanation = (mlData?.explanation && typeof mlData.explanation === "object" && !Array.isArray(mlData.explanation)) ? mlData.explanation : {};
  
  // Format score string
  let scoreLabel = "Metric Score";
  if (taskType === "classification") scoreLabel = "Accuracy";
  if (taskType === "regression") scoreLabel = "R² Coefficient";
  if (taskType === "clustering") scoreLabel = "Silhouette Score";

  // Helper to safely render text value and prevent React child object crash
  const renderText = (val) => {
    if (val === null || val === undefined) return "";
    if (typeof val === "object") return JSON.stringify(val);
    return String(val);
  };

  if (!mlData || Object.keys(mlData).length === 0) {
    return (
      <div className="p-10 text-center glass-card rounded-[32px] border-glow">
        <ShieldAlert className="w-12 h-12 text-state-warning mx-auto mb-4" />
        <h3 className="text-xl font-bold text-white">No Machine Learning Data Available</h3>
        <p className="text-text-secondary mt-2">The ML agent might have skipped this dataset due to size or quality constraints.</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 animate-fadeIn">
      {/* Structural overview header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Task Type badge */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-8 glass-card card-hover-premium glow-card border-glow rounded-[32px] relative overflow-hidden group"
        >
          <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
            <Cpu className="w-16 h-16 text-accent-blue" />
          </div>
          <span className="text-text-secondary text-[10px] uppercase tracking-[0.2em] font-bold block mb-4">
            Analysis Objective
          </span>
          <h3 className="text-3xl font-black text-white uppercase tracking-tight italic">
            {taskType}
          </h3>
          <div className="mt-6 flex flex-col gap-2">
            <span className="text-[10px] text-text-secondary font-bold uppercase tracking-widest">Target Mapping</span>
            <div className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 font-mono text-accent-cyan text-xs font-bold truncate">
              {data?.potential_target || "UNSUPERVISED"}
            </div>
          </div>
        </motion.div>

        {/* Best Model card */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="p-8 glass-card card-hover-premium glow-card border-glow rounded-[32px] relative overflow-hidden md:col-span-2 group shadow-cyanGlow"
        >
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-accent-cyan/5 rounded-full blur-3xl group-hover:bg-accent-cyan/10 transition-all duration-700" />
          
          <div className="flex flex-col h-full justify-between">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-accent-cyan/10 border border-accent-cyan/20">
                  <Sparkles className="w-4 h-4 text-accent-cyan" />
                </div>
                <span className="text-accent-cyan text-[10px] uppercase tracking-[0.2em] font-bold">
                  Top Performing Engine
                </span>
              </div>
              <h2 className="text-4xl font-black text-white tracking-tight leading-none">
                {bestModel}
              </h2>
            </div>

            <div className="mt-8 flex items-end justify-between">
              <div className="space-y-1">
                <span className="text-[10px] text-text-secondary font-bold uppercase tracking-widest block">{scoreLabel}</span>
                <span className="text-3xl font-black font-mono text-state-success">
                  {(bestScore * 100).toFixed(2)}<span className="text-sm opacity-50 ml-1">%</span>
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                <Award className="w-8 h-8 text-white/20" />
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Model comparison table */}
      {results && results.length > 0 && results[0] && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card glow-card rounded-[32px] overflow-hidden shadow-premium"
        >
          <div className="p-8 border-b border-white/5 flex justify-between items-center">
            <h3 className="text-lg font-bold text-white tracking-tight">
              Benchmarking <span className="text-text-secondary font-medium ml-2 text-sm">/ Cross-Model Performance Matrix</span>
            </h3>
            <div className="flex gap-2">
              <div className="w-2 h-2 rounded-full bg-state-success animate-pulse" />
              <div className="w-2 h-2 rounded-full bg-accent-cyan opacity-40" />
              <div className="w-2 h-2 rounded-full bg-accent-blue opacity-40" />
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="custom-table font-mono">
              <thead>
                <tr>
                  {Object.keys(results[0]).map((h) => (
                    <th key={h} className="text-[10px] tracking-[0.2em]">{String(h).replace(/_/g, " ").toUpperCase()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.map((row, idx) => {
                  if (!row || typeof row !== "object" || Array.isArray(row)) return null;
                  const isBest = row.model === bestModel;
                  return (
                    <tr 
                      key={idx} 
                      className={`transition-colors duration-300 ${isBest ? "bg-accent-cyan/5" : "hover:bg-white/[0.02]"}`}
                    >
                      {Object.entries(row).map(([k, val], cIdx) => {
                        let cellContent = typeof val === "number" ? val.toFixed(4) : String(val);
                        if (k === "model" && isBest) {
                          return (
                            <td key={cIdx} className="font-sans font-bold text-accent-cyan flex items-center gap-3">
                              <div className="p-1.5 rounded-lg bg-accent-cyan/20 border border-accent-cyan/30">
                                <Award className="w-4 h-4 text-accent-cyan" />
                              </div>
                              <span className="tracking-tight">{cellContent}</span>
                            </td>
                          );
                        }
                        return (
                          <td key={cIdx} className={`${k === "model" ? "font-sans font-bold text-white" : "text-text-secondary"} ${isBest && k !== "model" ? "text-accent-cyan/80" : ""}`}>
                            {cellContent}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Textual rationalization & performance verdicts */}
      {explanation && Object.keys(explanation).length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="space-y-6"
        >
          {/* Top Recommendation Highlight */}
          {explanation.recommendation && (
            <div className="p-8 glass-card border-glow rounded-[32px] relative overflow-hidden bg-gradient-to-br from-accent-cyan/10 to-transparent shadow-cyanGlow">
              <div className="absolute top-0 right-0 p-8 opacity-10">
                <Sparkles className="w-24 h-24 text-accent-cyan" />
              </div>
              <div className="relative z-10 flex flex-col md:flex-row gap-6 items-center">
                <div className="w-16 h-16 rounded-2xl bg-accent-cyan/20 flex items-center justify-center text-accent-cyan border border-accent-cyan/30 flex-shrink-0">
                  <TrendingUp className="w-8 h-8" />
                </div>
                <div className="flex-grow text-center md:text-left">
                  <span className="text-accent-cyan text-xs uppercase tracking-widest font-bold">Expert Strategic Recommendation</span>
                  <h4 className="text-xl font-bold text-white mt-1 leading-tight">
                    {renderText(explanation.recommendation)}
                  </h4>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="p-8 glass-card card-hover-premium border-glow rounded-[32px] lg:col-span-2 space-y-6">
              {explanation.model_rationalization && (
                <div>
                  <span className="text-accent-cyan text-[10px] uppercase tracking-[0.2em] font-bold flex items-center gap-2 mb-3">
                    <div className="w-1 h-1 rounded-full bg-accent-cyan" />
                    Model Rationalization
                  </span>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    {renderText(explanation.model_rationalization)}
                  </p>
                </div>
              )}
              {explanation.feature_influence_explanation && (
                <div className="pt-6 border-t border-white/5">
                  <span className="text-accent-cyan text-[10px] uppercase tracking-[0.2em] font-bold flex items-center gap-2 mb-3">
                    <div className="w-1 h-1 rounded-full bg-accent-cyan" />
                    Feature Influence Analysis
                  </span>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    {renderText(explanation.feature_influence_explanation)}
                  </p>
                </div>
              )}
            </div>
            
            {explanation.performance_verdict && (
              <div className="p-8 glass-card card-hover-premium border-glow rounded-[32px] flex flex-col justify-between relative overflow-hidden group">
                <div className="absolute inset-0 bg-state-warning/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="relative z-10">
                  <span className="text-state-warning text-[10px] uppercase tracking-[0.2em] font-bold flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4" />
                    Readiness Verdict
                  </span>
                  <p className="text-text-secondary text-xs leading-relaxed mt-6 italic font-medium">
                    "{renderText(explanation.performance_verdict)}"
                  </p>
                </div>
                
                <div className="relative z-10 mt-8 pt-6 border-t border-white/5 flex items-center gap-3 font-mono text-[10px] text-text-secondary">
                  <div className="p-2 rounded-lg bg-white/5">
                    <Cpu className="w-4 h-4 text-accent-cyan" />
                  </div>
                  Agent Core ML Evaluator
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Model Visual Plots (SHAP, Confusion matrix or Residual plot) */}
      {plots && Object.keys(plots).length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-8"
        >
          {Object.entries(plots).map(([plotName, plotB64], idx) => (
            <div 
              key={plotName}
              className="p-6 glass-card card-hover border-glow rounded-xl flex flex-col items-center justify-center overflow-hidden"
            >
              <span className="text-[10px] font-bold text-accent-cyan uppercase tracking-wider font-mono self-start mb-4">
                {renderText(plotName).replace(/_/g, " ").toUpperCase()} Assessment Plot
              </span>
              
              <div className="w-full p-4 bg-bg-dark/40 border border-card-border rounded-xl flex items-center justify-center">
                {plotB64 && typeof plotB64 === "string" ? (
                  <img 
                    src={plotB64.startsWith("data:") ? plotB64 : `data:image/png;base64,${plotB64}`} 
                    alt={plotName}
                    className="max-h-[35vh] object-contain rounded-lg shadow-xl"
                  />
                ) : (
                  <div className="text-text-secondary text-xs font-mono">No plot visual data generated.</div>
                )}
              </div>
            </div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
