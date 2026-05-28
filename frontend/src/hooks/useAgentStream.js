import { useState, useEffect, useCallback, useRef } from "react";
import { getWsUrl } from "../config/api";

const INITIAL_STEPS = [
  { name: "ingestion", label: "Data Ingestion", status_text: "Waiting for ingestion...", state: "pending" },
  { name: "cleaning", label: "Data Cleaning", status_text: "Pending diagnostic check...", state: "pending" },
  { name: "eda", label: "Exploration", status_text: "Pending feature exploration...", state: "pending" },
  { name: "visualization", label: "Visualization", status_text: "Pending rendering decisions...", state: "pending" },
  { name: "ml", label: "Machine Learning", status_text: "Pending training models...", state: "pending" },
  { name: "insights", label: "Insights", status_text: "Pending strategic overview...", state: "pending" },
  { name: "code", label: "Code Generation", status_text: "Pending script parsing...", state: "pending" },
  { name: "finalizing", label: "Finalizing", status_text: "Awaiting preceding agent tasks...", state: "pending" }
];

export function useAgentStream(sessionId, onComplete) {
  const [agents, setAgents] = useState(INITIAL_STEPS);
  const [activeStep, setActiveStep] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const onCompleteRef = useRef(onComplete);
  const connectedRef = useRef(false);

  // Keep onComplete ref up to date without causing re-renders
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  const connect = useCallback(() => {
    if (!sessionId) return;
    
    // Prevent duplicate connections
    if (connectedRef.current || (wsRef.current && wsRef.current.readyState <= WebSocket.OPEN)) {
      console.log("WebSocket already connected or connecting, skipping.");
      return;
    }
    
    connectedRef.current = true;
    
    // Construct WebSocket URL
    const wsUrl = getWsUrl(sessionId);
    
    console.log("Connecting WebSocket to: ", wsUrl);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket event: ", data);
      
      const { step_index, agent_name, status_text, state } = data;
      
      setAgents((prevAgents) => {
        return prevAgents.map((ag, idx) => {
          if (idx === step_index) {
            return { ...ag, status_text, state };
          }
          // If a step completes, make sure any prior steps are marked complete
          if (idx < step_index && ag.state !== "completed") {
            return { ...ag, state: "completed" };
          }
          return ag;
        });
      });
      
      if (state === "active") {
        setActiveStep(step_index);
      }
      
      if (agent_name === "finalizing" && state === "completed") {
        setIsCompleted(true);
        ws.close();
        if (onCompleteRef.current) {
          onCompleteRef.current();
        }
      }
      
      if (state === "failed") {
        setError(status_text);
        ws.close();
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket connection error: ", err);
      connectedRef.current = false;
    };

    ws.onclose = () => {
      console.log("WebSocket closed.");
      connectedRef.current = false;
    };
  }, [sessionId]); // onComplete removed — using ref instead

  // Clean up on unmount
  useEffect(() => {
    return () => {
      connectedRef.current = false;
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    agents,
    activeStep,
    isCompleted,
    error,
    connect
  };
}
