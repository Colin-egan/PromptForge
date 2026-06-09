"use client";

import { useState, useEffect } from "react";
import { analyzeModel, type AnalysisResponse, type AnalysisIssue } from "../lib/api";

interface AnalysisReportProps {
  modelId: string;
}

export default function AnalysisReport({ modelId }: AnalysisReportProps) {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (modelId) {
      loadAnalysis();
    }
  }, [modelId]);

  const loadAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await analyzeModel(modelId);
      setAnalysis(result);
      setExpanded(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to analyze model";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ready":
        return "✅";
      case "needs_attention":
        return "⚠️";
      case "not_printable":
        return "❌";
      default:
        return "❓";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
        return "#10b981";
      case "needs_attention":
        return "#f59e0b";
      case "not_printable":
        return "#ef4444";
      default:
        return "var(--muted)";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return "🔴";
      case "warning":
        return "🟡";
      case "info":
        return "🔵";
      default:
        return "⚪";
    }
  };

  if (loading) {
    return (
      <div className="p-4 rounded-lg" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
        <div className="flex items-center gap-2" style={{ color: "var(--muted)" }}>
          <div className="animate-spin">⚙️</div>
          <span className="text-sm">Analyzing model...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg" style={{ background: "#fee", border: "1px solid #fcc" }}>
        <div className="flex items-center gap-2" style={{ color: "#c00" }}>
          <span>❌</span>
          <span className="text-sm">{error}</span>
        </div>
        <button
          onClick={loadAnalysis}
          className="mt-2 text-xs px-3 py-1 rounded"
          style={{ background: "#fff", color: "#c00", border: "1px solid #fcc" }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="p-4 rounded-lg" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
        <button
          onClick={loadAnalysis}
          className="w-full text-sm px-4 py-2 rounded-lg font-medium"
          style={{ background: "var(--accent)", color: "#fff" }}
        >
          Analyze Print-Readiness
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-lg overflow-hidden" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between"
        style={{ background: "var(--bg)" }}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getStatusIcon(analysis.status)}</span>
          <div className="text-left">
            <div className="text-sm font-semibold" style={{ color: getStatusColor(analysis.status) }}>
              {analysis.status === "ready" && "Ready to Print"}
              {analysis.status === "needs_attention" && "Needs Attention"}
              {analysis.status === "not_printable" && "Not Printable"}
            </div>
            <div className="text-xs" style={{ color: "var(--muted)" }}>
              {analysis.issues.length} issue{analysis.issues.length !== 1 ? "s" : ""} found
            </div>
          </div>
        </div>
        <span className="text-sm" style={{ color: "var(--muted)" }}>
          {expanded ? "▼" : "▶"}
        </span>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="p-4 space-y-4">
          {/* AI Report */}
          {analysis.report && (
            <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--text)" }}>
              {analysis.report}
            </div>
          )}

          {/* Issues */}
          {analysis.issues.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>
                Issues
              </h4>
              <div className="space-y-2">
                {analysis.issues.map((issue: AnalysisIssue, i: number) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg text-sm"
                    style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
                  >
                    <div className="flex items-start gap-2">
                      <span className="flex-shrink-0">{getSeverityIcon(issue.severity)}</span>
                      <div className="flex-1">
                        <div className="font-medium mb-1" style={{ color: "var(--text)" }}>
                          {issue.message}
                        </div>
                        {issue.suggestion && (
                          <div className="text-xs" style={{ color: "var(--muted)" }}>
                            💡 {issue.suggestion}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {analysis.recommendations.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>
                Recommendations
              </h4>
              <ul className="space-y-1">
                {analysis.recommendations.map((rec: string, i: number) => (
                  <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text)" }}>
                    <span className="flex-shrink-0">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Metadata */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>
              Model Info
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span style={{ color: "var(--muted)" }}>Dimensions:</span>
                <div style={{ color: "var(--text)" }}>
                  {analysis.metadata.dimensions.x.toFixed(1)} × {analysis.metadata.dimensions.y.toFixed(1)} × {analysis.metadata.dimensions.z.toFixed(1)} mm
                </div>
              </div>
              <div>
                <span style={{ color: "var(--muted)" }}>Volume:</span>
                <div style={{ color: "var(--text)" }}>
                  {(analysis.metadata.volume_mm3 / 1000).toFixed(2)} cm³
                </div>
              </div>
            </div>
          </div>

          {/* Re-analyze button */}
          <button
            onClick={loadAnalysis}
            disabled={loading}
            className="w-full text-xs px-3 py-2 rounded-lg font-medium"
            style={{ background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)" }}
          >
            Re-analyze
          </button>
        </div>
      )}
    </div>
  );
}

// Made with Bob
