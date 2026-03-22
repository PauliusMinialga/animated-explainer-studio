/**
 * Concept / Algorithm Explainer page — plays a single-scene Manim animation video.
 * Route: /concept/:jobId
 */
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Loader2, ArrowLeft, Download } from "lucide-react";
import { API_BASE } from "@/lib/utils";
import { getCookingMessage } from "@/lib/cooking-messages";

const COOKING_ROTATE_INTERVAL = 4000;

interface JobData {
  job_id: string;
  status: string;
  progress: string;
  job_type: string | null;
  animation_url: string | null;
  final_url: string | null;
  tts_script: { intro: string; info: string; outro: string } | null;
  error: string | null;
}

export default function ConceptAlgoExplainer() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<JobData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cookingTick, setCookingTick] = useState(0);

  // Rotate cooking message while waiting
  const isWaiting = !!job && (job.status === "pending" || job.status === "running");
  useEffect(() => {
    if (!isWaiting) return;
    const id = setInterval(() => setCookingTick((t) => t + 1), COOKING_ROTATE_INTERVAL);
    return () => clearInterval(id);
  }, [isWaiting]);

  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/jobs/${jobId}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: JobData = await res.json();
        if (cancelled) return;
        setJob(data);

        if (data.status === "pending" || data.status === "running") {
          setTimeout(poll, 2000);
        }
      } catch (err: any) {
        if (!cancelled) setError(err.message);
      }
    };

    poll();
    return () => { cancelled = true; };
  }, [jobId]);

  // Loading state
  if (!job && !error) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-white/40" />
      </div>
    );
  }

  // Error state
  if (error || job?.status === "failed") {
    return (
      <div className="flex h-[80vh] flex-col items-center justify-center gap-4">
        <p className="text-red-400 text-sm">{error || job?.error || "Job failed"}</p>
        <Link to="/" className="text-xs text-white/40 hover:text-white/60 flex items-center gap-1">
          <ArrowLeft className="h-3 w-3" /> Back to home
        </Link>
      </div>
    );
  }

  // Still running — show fun cooking messages
  if (job && (job.status === "pending" || job.status === "running")) {
    return (
      <div className="flex h-[80vh] flex-col items-center justify-center gap-4">
        <div className="relative">
          <div className="h-14 w-14 animate-spin rounded-full border-4 border-white/10 border-t-blue-400" />
          <span className="absolute inset-0 flex items-center justify-center text-xl">🧑‍🍳</span>
        </div>
        <p className="text-sm text-white/70 transition-all duration-300">
          {getCookingMessage(job.progress, cookingTick)}
        </p>
        <p className="text-[11px] text-white/30">This usually takes 1–2 minutes</p>
      </div>
    );
  }

  // Done — play video
  const videoUrl = job?.final_url || job?.animation_url;
  if (videoUrl) {
    return (
      <div className="flex h-[calc(100vh-80px)] flex-col items-center justify-center gap-6 bg-gray-950 px-4">
        <div className="w-full max-w-4xl overflow-hidden rounded-2xl border border-white/10 bg-black shadow-2xl">
          <div className="relative aspect-video">
            <video
              src={videoUrl}
              controls
              autoPlay
              playsInline
              className="h-full w-full object-contain"
            />
          </div>
          <div className="flex items-center justify-between border-t border-white/10 px-6 py-4">
            <p className="text-sm font-medium text-white/70">Concept Explanation</p>
            <div className="flex items-center gap-3">
              <a
                href={`${API_BASE}/download/${jobId}`}
                download
                className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 transition-colors"
              >
                <Download className="h-4 w-4" /> Download Video
              </a>
              <Link
                to="/"
                className="flex items-center gap-1.5 rounded-lg border border-white/20 px-4 py-2 text-sm font-medium text-white/70 hover:bg-white/10 transition-colors"
              >
                <ArrowLeft className="h-4 w-4" /> Back
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[80vh] items-center justify-center">
      <p className="text-white/40 text-sm">No video available</p>
    </div>
  );
}
