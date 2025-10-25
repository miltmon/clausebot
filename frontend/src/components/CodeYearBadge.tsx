import { CODE_LABEL } from "@/lib/codeMeta";

interface CodeYearBadgeProps {
  className?: string;
}

export default function CodeYearBadge({ className = "" }: CodeYearBadgeProps) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[11px] 
                      border-emerald-200 text-emerald-700 bg-emerald-50 ${className}`}>
      Updated for {CODE_LABEL}
    </span>
  );
}