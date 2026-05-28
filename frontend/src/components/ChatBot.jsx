import React, { useState, useEffect, useRef } from "react";
import { MessageSquare, X, Send, Loader2, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { API_BASE } from "../config/api";

export default function ChatBot({ sessionId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMsg, setInputMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const bottomRef = useRef(null);

  // Suggested questions based on the analytical environment
  const suggestions = [
    "What are the most important features in this data?",
    "Which machine learning model succeeded and why?",
    "Are there any significant correlations?",
    "Highlight the data quality issues resolved."
  ];

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading, isOpen]);

  // Handle send message
  const handleSend = async (textToSend) => {
    const queryText = textToSend || inputMsg;
    if (!queryText.trim() || isLoading) return;
    
    // Add user message to local state
    const userMsgObj = { role: "user", content: queryText };
    setMessages((prev) => [...prev, userMsgObj]);
    setInputMsg("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat/${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: queryText })
      });
      
      if (!response.ok) {
        throw new Error("Failed to post chat message");
      }
      
      const data = await response.json();
      
      // Update assistant reply
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer }]);
    } catch (err) {
      console.error("Chatbot query error: ", err);
      setMessages((prev) => [...prev, { role: "assistant", content: "Apologies, the agent failed to process that request. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-8 right-8 z-[9999] font-sans">
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="group w-16 h-16 rounded-[24px] bg-accent-cyan hover:bg-white flex items-center justify-center text-bg-dark transition-all duration-500 shadow-[0_0_30px_rgba(0,245,255,0.4)] hover:shadow-[0_0_40px_rgba(255,255,255,0.4)] hover:-translate-y-1 active:scale-95 overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
            >
              <X className="w-7 h-7" />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 1.5, opacity: 0 }}
              className="relative"
            >
              <MessageSquare className="w-7 h-7" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full border-2 border-accent-cyan" />
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Shimmer Effect on Button */}
        <div className="absolute inset-0 animate-shimmer opacity-0 group-hover:opacity-100 transition-opacity" />
      </button>

      {/* Slide-up Chat Drawer */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.95 }}
            transition={{ duration: 0.4, cubicBezier: [0.23, 1, 0.32, 1] }}
            className="absolute bottom-20 right-0 w-[400px] sm:w-[440px] h-[600px] glass-card border-glow rounded-[32px] shadow-[0_30px_60px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden backdrop-blur-3xl"
          >
            {/* Drawer Header */}
            <div className="p-6 bg-white/5 border-b border-white/5 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-xl bg-accent-cyan/10 border border-accent-cyan/20 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-accent-cyan" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-state-success border-2 border-bg-dark" />
                </div>
                <div>
                  <span className="block text-xs font-black text-white uppercase tracking-widest">
                    AI Assistant
                  </span>
                  <span className="block text-[10px] font-bold text-accent-cyan uppercase tracking-[0.2em] mt-0.5">
                    Online & Ready
                  </span>
                </div>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-text-secondary hover:text-white hover:bg-white/5 transition-all"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Chat Messages Panel */}
            <div className="flex-grow p-6 overflow-y-auto space-y-6 custom-scrollbar">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center text-center py-10 h-full space-y-6">
                  <div className="w-20 h-20 rounded-[32px] bg-accent-cyan/5 border border-accent-cyan/10 flex items-center justify-center animate-float">
                    <Sparkles className="w-10 h-10 text-accent-cyan opacity-40" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-lg font-bold text-white tracking-tight">
                      How can I assist you?
                    </h4>
                    <p className="text-xs text-text-secondary max-w-[240px] leading-relaxed font-medium">
                      Query your dataset's architecture, relationships, or predictive insights in plain language.
                    </p>
                  </div>
                  
                  {/* Suggested pills */}
                  <div className="flex flex-col gap-2.5 w-full pt-4 max-w-[280px]">
                    {suggestions.map((s) => (
                      <button
                        key={s}
                        onClick={() => handleSend(s)}
                        className="text-left text-[11px] font-bold px-4 py-3 bg-white/5 hover:bg-white/10 text-text-secondary hover:text-white border border-white/5 rounded-2xl transition-all duration-300"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat Thread */}
              {messages.map((msg, idx) => {
                const isUser = msg.role === "user";
                return (
                  <motion.div 
                    initial={{ opacity: 0, x: isUser ? 10 : -10, y: 10 }}
                    animate={{ opacity: 1, x: 0, y: 0 }}
                    key={idx} 
                    className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                  >
                    <div className={`max-w-[85%] rounded-[24px] px-5 py-4 text-xs font-medium leading-relaxed shadow-lg ${
                      isUser 
                        ? "bg-accent-cyan text-bg-dark rounded-tr-none" 
                        : "bg-white/5 border border-white/5 text-white rounded-tl-none whitespace-pre-wrap"
                    }`}>
                      {msg.content}
                    </div>
                  </motion.div>
                );
              })}

              {/* Loader */}
              {isLoading && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="max-w-[85%] bg-white/5 border border-white/5 rounded-[24px] rounded-tl-none px-5 py-4 flex items-center gap-3 text-xs font-bold text-accent-cyan italic">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Synthesizing response...
                  </div>
                </motion.div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Message Input Footer */}
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="p-6 bg-white/5 border-t border-white/5 flex gap-3 items-center"
            >
              <div className="relative flex-grow">
                <input
                  type="text"
                  placeholder="Ask a question..."
                  value={inputMsg}
                  onChange={(e) => setInputMsg(e.target.value)}
                  className="w-full text-xs font-bold px-5 py-4 bg-bg-dark border border-white/10 text-white placeholder:text-text-secondary/30 rounded-2xl focus:outline-none focus:border-accent-cyan/50 transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={!inputMsg.trim() || isLoading}
                className="w-12 h-12 flex-shrink-0 flex items-center justify-center rounded-2xl bg-accent-cyan text-bg-dark hover:bg-white disabled:opacity-20 transition-all shadow-lg active:scale-90"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

}
