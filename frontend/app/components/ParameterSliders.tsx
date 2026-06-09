"use client";

import { useState, useEffect } from "react";
import { updateParameters, type Parameter } from "../lib/api";

interface ParameterSlidersProps {
  modelId: string;
  parameters: Parameter[];
  onParametersUpdated: (newModelId: string) => void;
}

export default function ParameterSliders({
  modelId,
  parameters,
  onParametersUpdated,
}: ParameterSlidersProps) {
  const [values, setValues] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize values from parameters
  useEffect(() => {
    const initialValues: Record<string, number> = {};
    parameters.forEach((param) => {
      initialValues[param.name] = param.value;
    });
    setValues(initialValues);
  }, [parameters]);

  // Group parameters by category
  const groupedParams = parameters.reduce((acc, param) => {
    const category = param.category || "Other";
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(param);
    return acc;
  }, {} as Record<string, Parameter[]>);

  const handleSliderChange = (paramName: string, newValue: number) => {
    setValues((prev) => ({ ...prev, [paramName]: newValue }));
  };

  const handleInputChange = (paramName: string, inputValue: string) => {
    const param = parameters.find((p) => p.name === paramName);
    if (!param) return;

    const numValue = parseFloat(inputValue);
    if (isNaN(numValue)) return;

    // Clamp to min/max
    const clampedValue = Math.max(
      param.min,
      Math.min(param.max, numValue)
    );
    setValues((prev) => ({ ...prev, [paramName]: clampedValue }));
  };

  const handleApply = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await updateParameters(modelId, values);
      onParametersUpdated(response.model_id);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to update parameters";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    const defaultValues: Record<string, number> = {};
    parameters.forEach((param) => {
      defaultValues[param.name] = param.value;
    });
    setValues(defaultValues);
  };

  const hasChanges = parameters.some(
    (param) => values[param.name] !== param.value
  );

  if (parameters.length === 0) {
    return (
      <div
        className="h-full flex items-center justify-center"
        style={{ background: "var(--surface)", borderLeft: "1px solid var(--border)" }}
      >
        <div className="text-center px-4" style={{ color: "var(--muted)" }}>
          <div className="text-4xl mb-2">⚙️</div>
          <p className="text-sm">No parameters available</p>
          <p className="text-xs mt-1 opacity-60">
            Generate a model to see adjustable parameters
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="h-full flex flex-col"
      style={{ background: "var(--surface)", borderLeft: "1px solid var(--border)" }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 font-semibold text-sm tracking-wide"
        style={{ borderBottom: "1px solid var(--border)", color: "var(--accent)" }}
      >
        Parameters
      </div>

      {/* Parameters */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {Object.entries(groupedParams).map(([category, params]) => (
          <div key={category}>
            <h3
              className="text-xs font-semibold uppercase tracking-wider mb-3"
              style={{ color: "var(--muted)" }}
            >
              {category}
            </h3>
            <div className="space-y-4">
              {params.map((param) => {
                const currentValue = values[param.name] ?? param.value;
                const percentage =
                  ((currentValue - param.min) / (param.max - param.min)) * 100;

                return (
                  <div key={param.name}>
                    <div className="flex items-center justify-between mb-2">
                      <label
                        className="text-sm font-medium"
                        style={{ color: "var(--text)" }}
                      >
                        {param.label}
                      </label>
                      <input
                        type="number"
                        value={currentValue.toFixed(param.step < 1 ? 1 : 0)}
                        onChange={(e) =>
                          handleInputChange(param.name, e.target.value)
                        }
                        min={param.min}
                        max={param.max}
                        step={param.step}
                        className="w-16 px-2 py-1 text-xs text-right rounded"
                        style={{
                          background: "var(--bg)",
                          color: "var(--text)",
                          border: "1px solid var(--border)",
                        }}
                      />
                    </div>
                    <div className="relative">
                      <input
                        type="range"
                        min={param.min}
                        max={param.max}
                        step={param.step}
                        value={currentValue}
                        onChange={(e) =>
                          handleSliderChange(param.name, parseFloat(e.target.value))
                        }
                        className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                        style={{
                          background: `linear-gradient(to right, var(--accent) 0%, var(--accent) ${percentage}%, var(--border) ${percentage}%, var(--border) 100%)`,
                        }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs" style={{ color: "var(--muted)" }}>
                        {param.min}
                      </span>
                      <span className="text-xs" style={{ color: "var(--muted)" }}>
                        {param.max}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Error message */}
      {error && (
        <div
          className="px-4 py-2 text-xs"
          style={{ background: "#fee", color: "#c00", borderTop: "1px solid var(--border)" }}
        >
          {error}
        </div>
      )}

      {/* Actions */}
      <div
        className="px-4 py-3 flex gap-2"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <button
          onClick={handleReset}
          disabled={!hasChanges || loading}
          className="flex-1 rounded-lg px-3 py-2 text-sm font-medium disabled:opacity-40"
          style={{
            background: "var(--bg)",
            color: "var(--text)",
            border: "1px solid var(--border)",
          }}
        >
          Reset
        </button>
        <button
          onClick={handleApply}
          disabled={!hasChanges || loading}
          className="flex-1 rounded-lg px-3 py-2 text-sm font-medium disabled:opacity-40"
          style={{ background: "var(--accent)", color: "#fff" }}
        >
          {loading ? "Applying..." : "Apply"}
        </button>
      </div>
    </div>
  );
}

// Made with Bob
