import React from "react";
import { Database, Columns, AlertTriangle, Layers } from "lucide-react";
import { motion } from "framer-motion";

export default function OverviewTab({ data }) {
  const rowCount = data.row_count || 0;
  const columnCount = data.column_count || 0;
  const nullCounts = data.cleaning_agent?.null_counts || {};
  const duplicateCount = data.cleaning_agent?.duplicate_count || 0;
  const targetCol = data.potential_target || "None";
  const targetReason = data.ingestion_agent?.target_reasoning || "";
  
  const schema = data.ingestion_agent?.schema || [];
  const sampleRows = data.sample_rows || [];
  
  // Format null ratio
  const totalNulls = nullCounts.total || 0;
  const totalCells = rowCount * columnCount;
  const nullPercent = totalCells > 0 ? (totalNulls / totalCells) * 100 : 0.0;

  // Metric Cards Specs
  const kpis = [
    { label: "Total Rows", val: rowCount.toLocaleString(), icon: Database, color: "text-accent-cyan" },
    { label: "Total Columns", val: columnCount.toLocaleString(), icon: Columns, color: "text-accent-blue" },
    { label: "Missing Cell Ratio", val: `${nullPercent.toFixed(2)}%`, icon: AlertTriangle, color: "text-state-warning" },
    { label: "Duplicates Detected", val: duplicateCount.toLocaleString(), icon: Layers, color: "text-state-error" }
  ];

  return (
    <div className="space-y-10 animate-fadeIn">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, idx) => (
          <motion.div 
            key={kpi.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="group p-8 glass-card card-hover-premium glow-card rounded-[24px] relative overflow-hidden"
          >
            <div className="flex flex-col gap-4 relative z-10">
              <div className={`w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center transition-all duration-500 group-hover:scale-110 group-hover:border-accent-cyan/30 ${kpi.color}`}>
                <kpi.icon className="w-6 h-6" />
              </div>
              <div>
                <span className="text-text-secondary text-[10px] font-bold uppercase tracking-[0.15em]">
                  {kpi.label}
                </span>
                <h3 className="text-3xl font-extrabold text-white mt-1 font-mono tracking-tight">
                  {kpi.val}
                </h3>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Target Column Highlight */}
      {targetCol !== "None" && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="p-8 glass-card glow-card card-hover-premium rounded-[32px] bg-gradient-to-br from-accent-cyan/5 to-transparent"
        >
          <div className="flex flex-col md:flex-row gap-8 justify-between md:items-center">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 rounded-full bg-accent-cyan text-bg-dark text-[10px] font-black uppercase tracking-widest">
                  Primary Feature
                </span>
                <span className="text-accent-cyan text-[10px] font-bold uppercase tracking-[0.2em]">
                  Auto-Detected Target
                </span>
              </div>
              <h2 className="text-3xl font-black text-white font-mono tracking-tight italic">
                {targetCol}
              </h2>
              <p className="text-text-secondary text-sm font-medium max-w-3xl leading-relaxed">
                {targetReason}
              </p>
            </div>
            <div className="flex-shrink-0 flex items-center justify-center w-24 h-24 rounded-full border border-accent-cyan/20 bg-accent-cyan/5 shadow-[0_0_30px_rgba(0,245,255,0.05)]">
               <Layers className="w-10 h-10 text-accent-cyan opacity-50" />
            </div>
          </div>
        </motion.div>
      )}

      {/* Schema Table */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card glow-card rounded-[32px] overflow-hidden"
      >
        <div className="p-8 border-b border-white/5 flex justify-between items-center">
          <h3 className="text-lg font-bold text-white tracking-tight">
            Dataset Architecture <span className="text-text-secondary font-medium ml-2 text-sm">/ Schema Analysis</span>
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Detection</th>
                <th>Uniqueness</th>
                <th>Integrity</th>
                <th>Contextual Logic</th>
              </tr>
            </thead>
            <tbody>
              {schema.map((col, idx) => {
                const cname = col.column_name;
                const ctype = col.detected_type;
                const reason = col.reasoning;
                const uniqueVal = col.unique_count ?? "N/A";
                const missPercent = col.missing_percent ?? 0.0;
                
                return (
                  <tr key={cname}>
                    <td className="font-bold font-mono text-accent-cyan text-sm">{cname}</td>
                    <td>
                      <span className="px-3 py-1 rounded-lg text-[10px] font-bold uppercase border bg-white/5 border-white/5 text-text-secondary">
                        {ctype}
                      </span>
                    </td>
                    <td className="font-mono text-text-secondary text-xs">{uniqueVal.toLocaleString()}</td>
                    <td>
                      <div className="flex flex-col gap-2 w-32">
                        <div className="flex justify-between items-center text-[10px] font-bold font-mono">
                          <span className={missPercent > 10 ? "text-state-warning" : "text-state-success"}>
                            {missPercent.toFixed(1)}% MISSING
                          </span>
                        </div>
                        <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.min(100, missPercent)}%` }}
                            transition={{ duration: 1, delay: 0.6 + idx * 0.05 }}
                            className={`h-full rounded-full ${
                              missPercent > 50 
                                ? "bg-state-error" 
                                : missPercent > 10 
                                  ? "bg-state-warning" 
                                  : "bg-state-success"
                            }`}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="text-text-secondary text-xs font-medium leading-relaxed max-w-md italic">
                      {reason}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </motion.div>


      {/* Dataset Sample Table */}
      {sampleRows.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="p-6 glass-card card-hover border-glow rounded-xl overflow-hidden"
        >
          <h3 className="text-base font-semibold text-text-primary mb-6">
            Raw Head Sample Data (First 5 Rows)
          </h3>
          <div className="overflow-x-auto">
            <table className="custom-table font-mono text-xs">
              <thead>
                <tr>
                  {Object.keys(sampleRows[0]).map((k) => (
                    <th key={k}>{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sampleRows.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((val, cIdx) => (
                      <td key={cIdx} className="text-text-secondary truncate max-w-[150px]">
                        {val === null || val === undefined ? (
                          <span className="text-state-warning italic">null</span>
                        ) : (
                          String(val)
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
}
