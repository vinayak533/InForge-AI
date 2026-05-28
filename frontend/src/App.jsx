import React, { useState, useEffect } from "react";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [filename, setFilename] = useState("");

  useEffect(() => {
    const handleMouseMove = (e) => {
      document.documentElement.style.setProperty("--mouse-x", `${e.clientX}px`);
      document.documentElement.style.setProperty("--mouse-y", `${e.clientY}px`);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const handleStartAnalysis = (id, name) => {
    setSessionId(id);
    setFilename(name);
  };

  const handleBackToLanding = () => {
    setSessionId(null);
    setFilename("");
  };

  return (
    <>
      {!sessionId ? (
        <Landing onStartAnalysis={handleStartAnalysis} />
      ) : (
        <Dashboard 
          sessionId={sessionId} 
          filename={filename} 
          onBackToLanding={handleBackToLanding} 
        />
      )}
    </>
  );
}
