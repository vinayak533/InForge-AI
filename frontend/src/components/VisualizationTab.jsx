import React, { useState } from "react";
import { Download, BarChart2, PieChart, LineChart, Table2, Settings } from "lucide-react";
import { motion } from "framer-motion";

export default function VisualizationTab({ data }) {
  const visData = data.visualization_agent || {};
  const charts = visData.charts || {};
  const specs = visData.specs || [];
  
  // Categorize our generated charts
  const list = [];
  
  if (charts.correlation_heatmap) {
    list.push({ id: "correlation_heatmap", label: "Correlation Heatmap", category: "Relationship" });
  }
  if (charts.missing_value_heatmap) {
    list.push({ id: "missing_value_heatmap", label: "Missing Values Map", category: "Distribution" });
  }
  
  // Map recommended specs
  specs.forEach((spec, idx) => {
    const key = `recommended_chart_${idx+1}`;
    if (charts[key]) {
      let cat = "Distribution";
      if (spec.chart_type === "scatter") cat = "Relationship";
      if (spec.chart_type === "bar") cat = "Comparison";
      if (spec.chart_type === "box") cat = "Statistical";
      
      list.push({
        id: key,
        label: spec.title || `Custom Plot ${idx+1}`,
        category: cat
      });
    }
  });

  // Fallback if no charts
  if (list.length === 0) {
    Object.keys(charts).forEach((k) => {
      list.push({
        id: k,
        label: k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
        category: "Distribution"
      });
    });
  }

  const [selectedId, setSelectedId] = useState(list[0]?.id || "");
  const selectedChart = list.find(item => item.id === selectedId);
  const activeB64 = charts[selectedId];

  // Download action
  const handleDownload = () => {
    if (!activeB64 || !selectedChart) return;
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${activeB64}`;
    link.download = `${selectedChart.id}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const categories = ["Distribution", "Relationship", "Comparison", "Statistical"];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-10 min-h-[70vh] animate-fadeIn">
      {/* Left Sidebar categories selector */}
      <div className="p-8 glass-card glow-card rounded-[32px] space-y-8 self-start lg:col-span-1 border-r border-white/5">
        <div className="space-y-1">
          <h3 className="text-xs font-black text-white uppercase tracking-[0.2em]">
            Visual Catalog
          </h3>
          <p className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">
            Select Analysis View
          </p>
        </div>
        
        <div className="space-y-8">
          {categories.map((category) => {
            const items = list.filter(x => x.category === category);
            if (items.length === 0) return null;
            
            return (
              <div key={category} className="space-y-3">
                <span className="text-[10px] font-black text-accent-blue uppercase tracking-[0.25em] font-mono">
                  {category}
                </span>
                <div className="flex flex-col gap-1.5">
                  {items.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className={`text-left text-xs px-4 py-3 rounded-xl border transition-all duration-300 font-bold ${
                        selectedId === item.id 
                          ? "bg-accent-cyan/10 border-accent-cyan/40 text-accent-cyan shadow-[0_0_15px_rgba(0,245,255,0.1)]"
                          : "border-transparent text-text-secondary hover:text-white hover:bg-white/5"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Plot rendering and description panel */}
      <div className="lg:col-span-3 flex flex-col gap-8">
        {activeB64 ? (
          <motion.div 
            key={selectedId}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-10 glass-card glow-card card-hover-premium rounded-[40px] flex flex-col items-center justify-center relative overflow-hidden"
          >
            {/* Visual Header */}
            <div className="w-full flex justify-between items-end mb-10">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-accent-cyan/10 text-accent-cyan text-[10px] font-black uppercase tracking-widest border border-accent-cyan/20">
                    {selectedChart?.category}
                  </span>
                  <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">
                    Analytical Representation
                  </span>
                </div>
                <h2 className="text-3xl font-black text-white tracking-tight">
                  {selectedChart?.label}
                </h2>
              </div>
              
              <button
                onClick={handleDownload}
                className="premium-button flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white text-text-secondary hover:text-bg-dark font-black text-[10px] uppercase tracking-widest border border-white/10 rounded-2xl transition-all"
              >
                <Download className="w-4 h-4" />
                Export Assets
              </button>
            </div>

            {/* Rendered Chart */}
            <div className="w-full flex items-center justify-center p-8 bg-black/40 border border-white/5 rounded-[32px] relative shadow-inner group">
              <img 
                src={`data:image/png;base64,${activeB64}`} 
                alt={selectedChart?.label}
                className="max-h-[55vh] object-contain rounded-xl transition-transform duration-700 group-hover:scale-[1.02]"
              />
              
              {/* Decorative Corner Borders */}
              <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-white/10 rounded-tl-xl" />
              <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-white/10 rounded-tr-xl" />
              <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-white/10 rounded-bl-xl" />
              <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-white/10 rounded-br-xl" />
            </div>
          </motion.div>
        ) : (
          <div className="p-20 glass-card border-2 border-dashed border-white/5 rounded-[40px] flex flex-col items-center justify-center text-center space-y-4">
            <div className="p-6 rounded-full bg-white/5">
              <BarChart2 className="w-12 h-12 text-text-secondary opacity-20" />
            </div>
            <p className="text-text-secondary text-sm font-bold uppercase tracking-widest">Select a visualization to initialize display</p>
          </div>
        )}

        {/* Theme visual metadata notes */}
        {visData.theme_notes && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 glass-card glow-card rounded-[32px] border-l-4 border-l-accent-blue/30"
          >
            <div className="flex items-center gap-3 mb-2">
              <Settings className="w-4 h-4 text-accent-blue" />
              <span className="text-[10px] font-black text-white uppercase tracking-widest">Aesthetic Specifications</span>
            </div>
            <p className="text-text-secondary text-xs font-medium leading-relaxed italic">
              {visData.theme_notes}
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );

}
