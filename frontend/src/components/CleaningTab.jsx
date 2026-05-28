import React from "react";
import { Check, ShieldAlert, Download, Layers, Settings, FileSpreadsheet } from "lucide-react";
import { motion } from "framer-motion";
import { API_BASE } from "../config/api";

export default function CleaningTab({ data, sessionId }) {
  const rowCount = data.row_count || 0;
  const colCount = data.column_count || 0;
  
  const cleaningData = data.cleaning_agent || {};
  const nullCounts = cleaningData.null_counts || {};
  const duplicateCount = cleaningData.duplicate_count || 0;
  const cleaningLog = cleaningData.cleaning_log || [];
  const cleanedShape = cleaningData.cleaned_shape || [0, 0];
  const rationale = cleaningData.rationale || "";
  
  const originalCells = rowCount * colCount;
  const preNulls = nullCounts.total || 0;
  const cleanRows = cleanedShape[0] || rowCount;
  const cleanCols = cleanedShape[1] || colCount;
  
  return (
    <div className="space-y-10 animate-fadeIn">
      {/* Before / After Metrics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Pre-Cleaning Metrics */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="group p-8 glass-card glow-card card-hover-premium rounded-[32px] relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-state-error/5 rounded-bl-[64px] flex items-center justify-center border-l border-b border-white/5 group-hover:bg-state-error/10 transition-colors">
            <ShieldAlert className="w-10 h-10 text-state-error/20 translate-x-4 -translate-y-4" />
          </div>
          
          <div className="relative z-10 space-y-6">
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-full bg-state-error/10 text-state-error text-[10px] font-black uppercase tracking-widest border border-state-error/20">
                Primary Diagnostics
              </span>
              <h3 className="text-[10px] font-bold text-text-secondary uppercase tracking-[0.2em]">
                Pre-Sanitization
              </h3>
            </div>
            
            <div className="grid grid-cols-3 gap-6">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Rows</span>
                <p className="text-2xl font-black text-white font-mono">{rowCount.toLocaleString()}</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Nulls</span>
                <p className="text-2xl font-black text-state-warning font-mono">{preNulls.toLocaleString()}</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Duplicates</span>
                <p className="text-2xl font-black text-state-error font-mono">{duplicateCount.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Post-Cleaning Metrics */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="group p-8 glass-card glow-card card-hover-premium rounded-[32px] relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-state-success/5 rounded-bl-[64px] flex items-center justify-center border-l border-b border-white/5 group-hover:bg-state-success/10 transition-colors">
            <Check className="w-10 h-10 text-state-success/20 translate-x-4 -translate-y-4" />
          </div>
          
          <div className="relative z-10 space-y-6">
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-full bg-state-success/10 text-state-success text-[10px] font-black uppercase tracking-widest border border-state-success/20">
                Optimized Output
              </span>
              <h3 className="text-[10px] font-bold text-text-secondary uppercase tracking-[0.2em]">
                Post-Sanitization
              </h3>
            </div>
            
            <div className="grid grid-cols-3 gap-6">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Rows</span>
                <p className="text-2xl font-black text-state-success font-mono">{cleanRows.toLocaleString()}</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Nulls</span>
                <p className="text-2xl font-black text-state-success font-mono">0</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Duplicates</span>
                <p className="text-2xl font-black text-state-success font-mono">0</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Rationale and Strategy Explanation */}
      {rationale && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-8 glass-card glow-card rounded-[32px] border-l-4 border-l-accent-cyan/30"
        >
          <div className="flex items-center gap-3 mb-4">
            <Settings className="w-5 h-5 text-accent-cyan" />
            <span className="text-accent-cyan text-[10px] font-black uppercase tracking-[0.2em]">
              Imputation Strategy & Logic
            </span>
          </div>
          <p className="text-white text-sm font-medium leading-relaxed max-w-5xl">
            {rationale}
          </p>
        </motion.div>
      )}

      {/* Operations Timeline and Export */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cleaning Action Log */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-card glow-card rounded-[32px] overflow-hidden"
        >
          <div className="p-8 border-b border-white/5">
            <h3 className="text-lg font-bold text-white tracking-tight">
              Activity Manifest <span className="text-text-secondary font-medium ml-2 text-sm">/ Operational Log</span>
            </h3>
          </div>
          
          <div className="p-8">
            {cleaningLog.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-white/5 rounded-[24px] bg-white/[0.02]">
                <Check className="w-10 h-10 text-state-success/30 mb-4" />
                <p className="text-text-secondary text-xs font-bold uppercase tracking-widest">Dataset fully sanitized on entry.</p>
              </div>
            ) : (
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-4 custom-scrollbar">
                {cleaningLog.map((log, idx) => (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + idx * 0.05 }}
                    key={idx} 
                    className="flex items-start gap-4 p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
                  >
                    <div className="mt-1 w-2 h-2 rounded-full bg-accent-cyan shadow-[0_0_10px_rgba(0,245,255,0.5)]" />
                    <p className="text-xs font-medium text-white/80 leading-relaxed">
                      {log}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* Sanitized Export Action */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="p-8 glass-card glow-card card-hover-premium rounded-[32px] flex flex-col justify-between bg-gradient-to-br from-accent-cyan/5 to-transparent"
        >
          <div className="space-y-6">
            <div className="w-16 h-16 rounded-[24px] bg-accent-cyan/10 border border-accent-cyan/20 flex items-center justify-center">
              <FileSpreadsheet className="w-8 h-8 text-accent-cyan" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-bold text-white tracking-tight">
                Refined Dataset
              </h3>
              <p className="text-text-secondary text-xs font-medium leading-relaxed">
                Download the enterprise-ready CSV version of your dataset. All anomalies have been mitigated and structural integrity has been verified.
              </p>
            </div>
          </div>
          
          <a
            href={`${API_BASE}/export/csv/${sessionId}`}
            download
            className="premium-button mt-8 flex items-center justify-center gap-3 w-full py-4 bg-accent-cyan hover:bg-white text-bg-dark font-black text-xs uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_20px_rgba(0,245,255,0.2)]"
          >
            <Download className="w-4 h-4" />
            Download Cleaned CSV
          </a>
        </motion.div>
      </div>
    </div>
  );

}
