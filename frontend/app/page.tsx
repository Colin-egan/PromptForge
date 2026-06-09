"use client";

import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import ParameterSliders from "./components/ParameterSliders";
import AnalysisReport from "./components/AnalysisReport";
import dynamic from "next/dynamic";
import type { Parameter } from "./lib/api";

// ModelViewer uses WebGL — must be client-side only (no SSR)
const ModelViewer = dynamic(() => import("./components/ModelViewer"), { ssr: false });

export default function Home() {
  const [activeModelId, setActiveModelId] = useState<string | null>(null);
  const [parameters, setParameters] = useState<Parameter[]>([]);

  const handleModelReady = (modelId: string, params?: Parameter[]) => {
    setActiveModelId(modelId);
    if (params) {
      setParameters(params);
    }
  };

  const handleParametersUpdated = (newModelId: string) => {
    setActiveModelId(newModelId);
    // Parameters will be updated when the chat panel receives the response
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      {/* Chat sidebar */}
      <div className="w-80 flex-shrink-0 h-full">
        <ChatPanel
          onModelReady={handleModelReady}
          onParametersUpdate={setParameters}
        />
      </div>

      {/* 3D viewer */}
      <div className="flex-1 h-full">
        <ModelViewer modelId={activeModelId} />
      </div>

      {/* Right sidebar: Parameters & Analysis */}
      <div className="w-96 flex-shrink-0 h-full flex flex-col" style={{ background: "var(--surface)", borderLeft: "1px solid var(--border)" }}>
        {activeModelId ? (
          <>
            {/* Analysis Report */}
            <div className="p-4" style={{ borderBottom: "1px solid var(--border)" }}>
              <AnalysisReport modelId={activeModelId} />
            </div>

            {/* Parameter Controls */}
            <div className="flex-1 overflow-hidden">
              {parameters.length > 0 ? (
                <ParameterSliders
                  modelId={activeModelId}
                  parameters={parameters}
                  onParametersUpdated={handleParametersUpdated}
                />
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center px-4" style={{ color: "var(--muted)" }}>
                    <div className="text-4xl mb-2">⚙️</div>
                    <p className="text-sm">No parameters available</p>
                    <p className="text-xs mt-1 opacity-60">
                      This model has no adjustable parameters
                    </p>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center px-4" style={{ color: "var(--muted)" }}>
              <div className="text-4xl mb-2">📊</div>
              <p className="text-sm">Analysis & Parameters</p>
              <p className="text-xs mt-1 opacity-60">
                Generate a model to see details
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
