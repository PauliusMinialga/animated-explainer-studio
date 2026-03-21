/**
 * Repo Explainer page — fetches a job by ID and renders the React Flow walkthrough.
 * Route: /repo/:jobId
 */
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Loader2, ArrowLeft } from "lucide-react";
import RepoPlayer from "@/components/repo-explainer/RepoPlayer";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface JobData {
  job_id: string;
  status: string;
  progress: string;
  job_type: string | null;
  architecture: any;
  storyboard: any;
  narration: any;
  tts_script: any;
  error: string | null;
}

export default function RepoExplainer() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<JobData | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  // Still running
  if (job && (job.status === "pending" || job.status === "running")) {
    return (
      <div className="flex h-[80vh] flex-col items-center justify-center gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-blue-400" />
        <p className="text-sm text-white/60">{job.progress}</p>
      </div>
    );
  }

  // If this is a code job (not repo), show message
  if (job?.job_type === "code") {
    return (
      <div className="flex h-[80vh] flex-col items-center justify-center gap-4">
        <p className="text-white/60 text-sm">This is a code explanation job — view the video instead.</p>
        {job.animation_url && (
          <a href={job.animation_url} className="text-blue-400 underline text-xs" target="_blank" rel="noopener">
            Watch animation
          </a>
        )}
      </div>
    );
  }

  // Repo job done — render player
  if (job?.architecture && job?.storyboard && job?.narration) {
    return (
      <div className="h-[calc(100vh-80px)]">
        <RepoPlayer
          architecture={job.architecture}
          storyboard={job.storyboard}
          narration={job.narration}
        />
      </div>
    );
  }

  return (
    <div className="flex h-[80vh] items-center justify-center">
      <p className="text-white/40 text-sm">No data available</p>
    </div>
  );
}
