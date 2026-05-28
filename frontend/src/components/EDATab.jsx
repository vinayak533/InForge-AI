import React from "react";
import { TrendingUp, Percent, AlertOctagon, HelpCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function EDATab({ data }) {
  const edaData = data.eda_agent || {};
  const stats = edaData.descriptive_stats || {};
  const topCorrelations = edaData.top_correlations || [];
  const skewedCols = edaData.skewed_columns || [];
  const zeroVarCols = edaData.zero_variance_columns || [];
  const textualInsights = edaData.textual_insights || {};

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Structural analysis alerts (skewness / zero variance) */}
      {(skewedCols.length > 0 || zeroVarCols.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Skewed Columns */}
          {skewedCols.length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-5 bg-state-warning/5 border border-state-warning/20 rounded-xl flex gap-4 items-start"
            >
              <div className="p-2.5 bg-state-warning/10 rounded-lg text-state-warning flex-shrink-0">
                <Percent className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-state-warning">Highly Skewed Features</h4>
                <div className="flex flex-wrap gap-2 mt-2">
                  {skewedCols.map((c) => (
                    <span key={c.column} className="px-2 py-0.5 rounded-full text-xs font-mono bg-state-warning/10 border border-state-warning/20 text-state-warning">
                      {c.column} ({c.skewness.toFixed(2)})
                    </span>
                  ))}
                </div>
                <p className="text-xs text-text-secondary mt-2">
                  Highly skewed features might benefit from log/power mathematical transformations prior to linear modeling.
                </p>
              </div>
            </motion.div>
          )}

          {/* Zero Variance Columns */}
          {zeroVarCols.length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-5 bg-state-error/5 border border-state-error/20 rounded-xl flex gap-4 items-start"
            >
              <div className="p-2.5 bg-state-error/10 rounded-lg text-state-error flex-shrink-0">
                <AlertOctagon className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-state-error">Zero Variance Features</h4>
                <div className="flex flex-wrap gap-2 mt-2">
                  {zeroVarCols.map((c) => (
                    <span key={c} className="px-2 py-0.5 rounded-full text-xs font-mono bg-state-error/10 border border-state-error/20 text-state-error">
                      {c}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-text-secondary mt-2">
                  These columns contain a single constant value and carry zero predictive entropy. They have been omitted from predictive calculations.
                </p>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Nemotron Insights */}
      {textualInsights && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <div className="p-6 glass-card card-hover border-glow rounded-xl">
            <span className="text-accent-cyan text-xs uppercase tracking-wider font-semibold">Distribution Analysis</span>
            <p className="text-text-secondary text-sm leading-relaxed mt-3">
              {textualInsights.distribution_analysis}
            </p>
          </div>
          
          <div className="p-6 glass-card card-hover border-glow rounded-xl">
            <span className="text-accent-cyan text-xs uppercase tracking-wider font-semibold">Correlation Insights</span>
            <p className="text-text-secondary text-sm leading-relaxed mt-3">
              {textualInsights.correlation_analysis}
            </p>
          </div>
          
          <div className="p-6 glass-card card-hover border-glow rounded-xl">
            <span className="text-accent-cyan text-xs uppercase tracking-wider font-semibold">Stability Comments</span>
            <p className="text-text-secondary text-sm leading-relaxed mt-3">
              {textualInsights.flags_analysis}
            </p>
          </div>
        </motion.div>
      )}

      {/* Top Correlations Row */}
      {topCorrelations.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="p-6 glass-card card-hover border-glow rounded-xl"
        >
          <h3 className="text-base font-semibold text-text-primary mb-6 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-accent-cyan" />
            Top 5 Correlated Column Pairs
          </h3>
          <div className="flex flex-wrap gap-4">
            {topCorrelations.map((pair, idx) => (
              <div 
                key={idx}
                className="flex items-center gap-3 p-3 bg-bg-dark rounded-xl border border-card-border font-mono text-xs"
              >
                <span className="text-text-primary font-semibold">{pair.feature_1}</span>
                <span className="text-text-secondary/40 font-sans">&lt;&mdash;&gt;</span>
                <span className="text-text-primary font-semibold">{pair.feature_2}</span>
                <span className={`px-2 py-0.5 rounded-full font-bold ml-2 ${
                  Math.abs(pair.correlation) > 0.7 
                    ? "bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/25" 
                    : "bg-accent-blue/10 text-accent-blue border border-accent-blue/25"
                }`}>
                  {pair.correlation > 0 ? "+" : ""}{pair.correlation.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Descriptive Stats Table */}
      {Object.keys(stats).length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="p-6 glass-card card-hover border-glow rounded-xl overflow-hidden"
        >
          <h3 className="text-base font-semibold text-text-primary mb-6">
            Detailed Numeric Descriptive Statistics
          </h3>
          
          <div className="overflow-x-auto">
            <table className="custom-table font-mono text-xs">
              <thead>
                <tr>
                  <th>Column Name</th>
                  <th>Mean</th>
                  <th>Std Dev</th>
                  <th>Minimum</th>
                  <th>25% (Q1)</th>
                  <th>Median</th>
                  <th>75% (Q3)</th>
                  <th>Maximum</th>
                  <th>Skewness</th>
                  <th>Kurtosis</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats).map(([colName, st]) => (
                  <tr key={colName}>
                    <td className="font-semibold text-accent-cyan font-sans">{colName}</td>
                    <td className="text-text-primary">{st.mean.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td className="text-text-secondary">{st.std.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td className="text-text-secondary">{st.min.toLocaleString()}</td>
                    <td className="text-text-secondary">{st.q25.toLocaleString()}</td>
                    <td className="text-text-primary font-semibold">{st.median.toLocaleString()}</td>
                    <td className="text-text-secondary">{st.q75.toLocaleString()}</td>
                    <td className="text-text-secondary">{st.max.toLocaleString()}</td>
                    <td className={`font-semibold ${Math.abs(st.skew) > 1 ? "text-state-warning" : "text-text-secondary"}`}>
                      {st.skew.toFixed(3)}
                    </td>
                    <td className="text-text-secondary">{st.kurtosis.toFixed(3)}</td>
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
