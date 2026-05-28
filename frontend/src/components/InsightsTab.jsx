import React from "react";
import { Sparkles, MessageSquare, Lightbulb, ShieldAlert, Award } from "lucide-react";
import { motion } from "framer-motion";

export default function InsightsTab({ data }) {
  const insightsData = data.insights_agent || {};
  const execSummary = insightsData.executive_summary || "";
  const insights = insightsData.insights || [];
  const recommendations = insightsData.recommendations || [];
  const dataQualityFlags = insightsData.data_quality_flags || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Executive Summary Section */}
      {execSummary && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 glass-card card-hover border-glow rounded-xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-24 h-24 bg-accent-cyan/5 rounded-bl-full flex items-center justify-center border-l border-b border-accent-cyan/15">
            <Sparkles className="w-6 h-6 text-accent-cyan/20 translate-x-2 -translate-y-2" />
          </div>
          
          <span className="text-accent-cyan text-xs uppercase tracking-wider font-semibold font-mono flex items-center gap-1.5">
            <Award className="w-3.5 h-3.5" />
            Executive Analytical Digest
          </span>
          <h2 className="text-lg font-bold text-text-primary mt-2 mb-3">
            Platform Analysis Executive Summary
          </h2>
          <p className="text-text-secondary text-sm leading-relaxed max-w-4xl">
            {execSummary}
          </p>
        </motion.div>
      )}

      {/* Strategic Insights */}
      {insights.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-text-primary flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-accent-cyan" />
            Data-Driven Strategic Insights
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {insights.map((insight, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="p-5 glass-card card-hover border-glow rounded-xl flex gap-4 items-start"
              >
                <div className="p-2 bg-accent-cyan/10 rounded-lg text-accent-cyan flex-shrink-0 mt-0.5 font-mono text-[10px] font-bold w-6 h-6 flex items-center justify-center">
                  0{idx+1}
                </div>
                <p className="text-text-secondary text-xs md:text-sm leading-relaxed">
                  {insight}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Actionable Recommendations */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-text-primary flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-state-warning" />
            Strategic Business Recommendations
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendations.map((rec, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.08 }}
                className="p-6 glass-card card-hover border-glow rounded-xl flex flex-col justify-between"
              >
                <span className="text-[10px] font-bold text-accent-blue uppercase tracking-wider font-mono">
                  Action Recommendation {idx+1}
                </span>
                
                <p className="text-text-primary text-xs md:text-sm leading-relaxed mt-4 mb-6">
                  {rec}
                </p>
                
                <div className="w-full h-1 bg-bg-dark rounded-full overflow-hidden">
                  <div className="w-1/3 h-full bg-accent-blue rounded-full" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Data Quality and Warning Flags */}
      {dataQualityFlags.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-5 bg-state-error/5 border border-state-error/15 rounded-xl flex gap-4 items-start"
        >
          <div className="p-2 bg-state-error/10 rounded-lg text-state-error flex-shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-state-error">Analytical Integrity Constraints</h4>
            <div className="space-y-2 mt-3">
              {dataQualityFlags.map((flag, idx) => (
                <p key={idx} className="text-xs text-text-secondary leading-relaxed">
                  &bull; {flag}
                </p>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
