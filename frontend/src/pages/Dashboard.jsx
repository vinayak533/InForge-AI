import React, { useState, useEffect } from "react";
import { Download, Cpu, FileText, CheckCircle2, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAgentStream } from "../hooks/useAgentStream";
import { API_BASE } from "../config/api";

import AgentProgress from "../components/AgentProgress";
import OverviewTab from "../components/OverviewTab";
import CleaningTab from "../components/CleaningTab";
import EDATab from "../components/EDATab";
import VisualizationTab from "../components/VisualizationTab";
import MLTab from "../components/MLTab";
import InsightsTab from "../components/InsightsTab";
import CodeTab from "../components/CodeTab";
import ChatBot from "../components/ChatBot";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "cleaning", label: "Cleaning" },
  { id: "eda", label: "EDA" },
  { id: "visualizations", label: "Visualizations" },
  { id: "ml", label: "ML Models" },
  { id: "insights", label: "Insights" },
  { id: "code", label: "Code" }
];

export default function Dashboard({ sessionId, filename, onBackToLanding }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [analysisResults, setAnalysisResults] = useState(null);
  const [pipelineFinished, setPipelineFinished] = useState(false);
  const [showSuccessFlash, setShowSuccessFlash] = useState(false);

  // Fetch final compiled results
  const fetchResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/results/${sessionId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch analysis outcomes");
      }
      const data = await response.json();
      if (data.status === "completed") {
        setAnalysisResults(data.results);
        setPipelineFinished(true);
      }
    } catch (err) {
      console.error("Failed to load results: ", err);
    }
  };

  // Connect WebSocket progress listener
  const { agents, activeStep, error, connect } = useAgentStream(sessionId, () => {
    // When final finalizing agent completes
    setShowSuccessFlash(true);
    setTimeout(() => {
      setShowSuccessFlash(false);
      fetchResults();
    }, 1200); // Elegant screen swipe transition duration
  });

  useEffect(() => {
    if (sessionId) {
      connect();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  // Handle PDF exporter
  const handleExportPDF = () => {
    const link = document.createElement("a");
    link.href = `${API_BASE}/export/pdf/${sessionId}`;
    link.download = `InForge_Report_${sessionId.slice(0, 8)}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Render active panel tab
  const renderTabPanel = () => {
    if (!analysisResults) return null;

    switch (activeTab) {
      case "overview":
        return <OverviewTab data={analysisResults} />;
      case "cleaning":
        return <CleaningTab data={analysisResults} sessionId={sessionId} />;
      case "eda":
        return <EDATab data={analysisResults} />;
      case "visualizations":
        return <VisualizationTab data={analysisResults} />;
      case "ml":
        return <MLTab data={analysisResults} />;
      case "insights":
        return <InsightsTab data={analysisResults} />;
      case "code":
        return <CodeTab data={analysisResults} />;
      default:
        return <OverviewTab data={analysisResults} />;
    }
  };

  return (
    <div className="min-h-screen bg-bg-dark text-text-primary flex flex-col font-sans select-none overflow-hidden relative">
      {/* Ambient Pulsing Glows */}
      <div className="absolute top-[-15%] left-[-15%] w-[800px] h-[800px] rounded-full bg-accent-cyan/5 filter blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-15%] right-[-15%] w-[900px] h-[900px] rounded-full bg-accent-purple/5 filter blur-[150px] pointer-events-none z-0" />
      
      {/* Dynamic Screen Swipe Success Flash */}
      <AnimatePresence>
        {showSuccessFlash && (
          <motion.div 
            initial={{ x: "-100%" }}
            animate={{ x: "100%" }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
            className="absolute inset-0 bg-gradient-to-r from-transparent via-accent-cyan/20 to-transparent z-[99999] pointer-events-none"
          />
        )}
      </AnimatePresence>

      {/* Top Navigation Bar */}
      <header className="h-[72px] flex-shrink-0 bg-card-bg/60 border-b border-white/5 backdrop-blur-xl px-8 flex justify-between items-center z-50">
        <div className="flex items-center gap-6">
          <div 
            onClick={onBackToLanding}
            className="flex items-center gap-2 cursor-pointer group"
          >
            <div className="w-8 h-8 rounded-lg bg-accent-cyan flex items-center justify-center text-bg-dark font-black text-lg shadow-[0_0_15px_rgba(0,245,255,0.4)] group-hover:scale-110 transition-transform">
              I
            </div>
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              InForge <span className="text-accent-cyan">AI</span>
            </h2>
          </div>
          <div className="h-6 w-px bg-white/10" />
          <div className="flex items-center gap-2">
            <div className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[10px] font-bold text-text-secondary uppercase tracking-widest">
              Session
            </div>
            <span className="text-xs font-medium text-text-secondary font-mono truncate max-w-[150px]">
              {filename}
            </span>
          </div>
        </div>

        {/* Exporters links visible after pipeline ends */}
        {pipelineFinished && (
          <div className="flex items-center gap-4">
            <a
              href={`${API_BASE}/export/csv/${sessionId}`}
              download
              className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl text-xs font-bold text-white transition-all active:scale-95"
            >
              <Download className="w-3.5 h-3.5 text-accent-cyan" />
              Export CSV
            </a>
            <button
              onClick={handleExportPDF}
              className="flex items-center gap-2 px-4 py-2 bg-accent-cyan hover:bg-white text-bg-dark rounded-xl text-xs font-bold transition-all active:scale-95 shadow-[0_0_15px_rgba(0,245,255,0.2)]"
            >
              <FileText className="w-3.5 h-3.5" />
              Generate Report
            </button>
          </div>
        )}
      </header>

      {/* Tabs Navigation Selector */}
      {pipelineFinished && (
        <nav className="h-[56px] flex-shrink-0 bg-bg-dark border-b border-white/5 px-8 flex gap-2 z-40 items-center overflow-x-auto no-scrollbar">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`h-9 px-5 text-xs font-bold transition-all relative rounded-full flex items-center justify-center whitespace-nowrap ${
                  isActive 
                    ? "bg-white/10 text-accent-cyan border border-white/10" 
                    : "text-text-secondary hover:text-white"
                }`}
              >
                {tab.label}
                {isActive && (
                  <motion.div 
                    layoutId="activeTab"
                    className="absolute inset-0 bg-white/5 rounded-full -z-10"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
              </button>
            );
          })}
        </nav>
      )}

      {/* Main Workspace Frame */}
      <main className="flex-grow min-h-0 overflow-y-auto px-8 py-10 relative z-30 custom-scrollbar">
        <div className="w-full max-w-7xl mx-auto">
          {!pipelineFinished ? (
            /* Active Progress Timeline Screen */
            <AgentProgress agents={agents} activeStep={activeStep} error={error} />
          ) : (
            /* Dashboard Panels View */
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              {renderTabPanel()}
            </motion.div>
          )}
        </div>
      </main>

      {/* Floating Chat Drawer Overlay */}
      {pipelineFinished && <ChatBot sessionId={sessionId} />}
    </div>
  );

}
