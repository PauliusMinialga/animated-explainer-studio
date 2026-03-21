/**
 * Custom React Flow node for architecture components.
 * Visual style varies by component type and highlight state.
 */
import { memo } from "react";
import { Handle, Position, type NodeProps } from "reactflow";

const TYPE_COLORS: Record<string, { bg: string; border: string; icon: string }> = {
  frontend: { bg: "bg-blue-900/80", border: "border-blue-400", icon: "🖥️" },
  backend: { bg: "bg-emerald-900/80", border: "border-emerald-400", icon: "⚙️" },
  database: { bg: "bg-amber-900/80", border: "border-amber-400", icon: "🗄️" },
  service: { bg: "bg-purple-900/80", border: "border-purple-400", icon: "🔌" },
  library: { bg: "bg-cyan-900/80", border: "border-cyan-400", icon: "📦" },
  config: { bg: "bg-gray-800/80", border: "border-gray-400", icon: "⚙️" },
  cli: { bg: "bg-orange-900/80", border: "border-orange-400", icon: "💻" },
  module: { bg: "bg-indigo-900/80", border: "border-indigo-400", icon: "📁" },
};

export interface ComponentNodeData {
  label: string;
  type: string;
  responsibility: string;
  highlighted: boolean;
  dimmed: boolean;
}

function ComponentNode({ data }: NodeProps<ComponentNodeData>) {
  const colors = TYPE_COLORS[data.type] || TYPE_COLORS.module;

  return (
    <div
      className={`
        rounded-xl border-2 px-4 py-3 shadow-lg backdrop-blur-sm
        transition-all duration-500 ease-out min-w-[140px] max-w-[200px]
        ${colors.bg} ${colors.border}
        ${data.highlighted ? "ring-2 ring-white/60 scale-105 shadow-white/20" : ""}
        ${data.dimmed ? "opacity-30 scale-95" : "opacity-100"}
      `}
    >
      <Handle type="target" position={Position.Top} className="!bg-white/40 !w-2 !h-2" />
      <Handle type="source" position={Position.Bottom} className="!bg-white/40 !w-2 !h-2" />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm">{colors.icon}</span>
        <span className="text-sm font-semibold text-white truncate">{data.label}</span>
      </div>
      {data.responsibility && !data.dimmed && (
        <p className="text-[10px] leading-tight text-white/60 line-clamp-2">
          {data.responsibility}
        </p>
      )}
    </div>
  );
}

export default memo(ComponentNode);
