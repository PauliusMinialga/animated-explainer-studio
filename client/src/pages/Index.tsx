import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Play, Code, Sparkles, Video, Loader2, Check, X, Github } from "lucide-react";

const logoNames = ["TechCorp", "DevStudio", "CodeBase", "Synthetix", "NeuralNet", "DataFlow", "CloudOps"];

const API_BASE = import.meta.env.VITE_API_URL || "https://vizifi.onrender.com";

const PROGRESS_LABELS: Record<string, string> = {
  "Queued": "Queued…",
  "Ingesting GitHub repo…": "Fetching repository…",
  "Analyzing architecture…": "Analyzing architecture…",
  "Generating storyboard…": "Generating storyboard…",
  "Assembling narration…": "Assembling narration…",
  "Generating scene audio…": "Generating voiceover…",
  "Generating avatar videos…": "Creating avatar…",
  "Enriching prompt…": "Enriching prompt…",
  "Generating scripts…": "Generating animation…",
  "Rendering animation…": "Rendering animation…",
  "Generating avatar & voice…": "Adding voiceover…",
  "Assembling final video…": "Assembling video…",
};

const Index = () => {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [doneVideo, setDoneVideo] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => { if (pollRef.current) clearTimeout(pollRef.current); };
  }, []);

  const handleGenerate = async () => {
    const input = prompt.trim();
    if (!input || generating) return;

    setGenerating(true);
    setProgress("Submitting…");
    setError(null);
    setDoneVideo(null);

    try {
      // Submit job
      const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input, mood: "friendly", level: "beginner", mode: "concept" }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const { job_id } = await res.json();

      // Poll for completion
      const poll = async () => {
        try {
          const r = await fetch(`${API_BASE}/jobs/${job_id}`);
          const data = await r.json();

          setProgress(PROGRESS_LABELS[data.progress] || data.progress || "Processing…");

          if (data.status === "failed") {
            setError(data.error || "Generation failed");
            setGenerating(false);
            return;
          }

          if (data.status === "done") {
            setGenerating(false);
            if (data.job_type === "repo") {
              // Redirect to React Flow player
              navigate(`/repo/${job_id}`);
            } else {
              // Show video inline
              setDoneVideo(data.animation_url || data.final_url);
            }
            return;
          }

          pollRef.current = setTimeout(poll, 2000);
        } catch (err: any) {
          setError(err.message);
          setGenerating(false);
        }
      };

      pollRef.current = setTimeout(poll, 1000);
    } catch (err: any) {
      setError(err.message);
      setGenerating(false);
    }
  };

  const handleClose = () => {
    if (pollRef.current) clearTimeout(pollRef.current);
    setDoneVideo(null);
    setGenerating(false);
    setProgress("");
    setError(null);
  };

  const isGithubUrl = prompt.trim().startsWith("https://github.com/");

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-24">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="font-display text-5xl font-bold leading-tight tracking-tight lg:text-6xl">
            Turn code into animated
            <br />
            <span className="hero-gradient-text">explanations with </span>
            <span className="hero-accent-text">AI</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            Paste a GitHub repo URL or describe a concept — our AI generates beautiful animated
            explanations in seconds. Learn, teach, and share visually.
          </p>
        </div>

        {/* Prompt box */}
        <div className="mx-auto mt-16 max-w-2xl">
          <div className="peach-glow rounded-2xl p-6 shadow-xl shadow-peach/30">
            {/* Input field */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
                  placeholder="https://github.com/user/repo  or  Explain how binary search works"
                  disabled={generating}
                  className="w-full rounded-xl border bg-background px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:opacity-50"
                />
                {isGithubUrl && (
                  <Github className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground/40" />
                )}
              </div>
              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || generating}
                className="inline-flex h-[46px] items-center gap-2 rounded-xl bg-accent px-5 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90 disabled:opacity-50 shrink-0"
              >
                {generating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                {generating ? "Generating…" : "Generate"}
              </button>
            </div>

            {/* Quick examples */}
            <div className="mt-3 flex flex-wrap gap-2">
              {[
                { label: "cal.com", value: "https://github.com/calcom/cal.com" },
                { label: "shadcn/ui", value: "https://github.com/shadcn-ui/ui" },
                { label: "Binary Search", value: "Explain how binary search works step by step" },
              ].map((ex) => (
                <button
                  key={ex.label}
                  onClick={() => { setPrompt(ex.value); setDoneVideo(null); setError(null); }}
                  disabled={generating}
                  className="inline-flex items-center gap-1 rounded-md bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent hover:bg-accent/20 disabled:opacity-50 transition-colors"
                >
                  {ex.value.startsWith("https://github.com") && <Github className="h-3 w-3" />}
                  {ex.label}
                </button>
              ))}
            </div>

            {/* Progress */}
            {generating && (
              <div className="mt-4 flex items-center gap-3 rounded-xl border bg-card p-4">
                <Loader2 className="h-4 w-4 animate-spin text-accent shrink-0" />
                <span className="text-sm text-muted-foreground">{progress}</span>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
          </div>

          {/* Video result (code explanations) */}
          {doneVideo && (
            <div className="mt-6 overflow-hidden rounded-2xl border bg-card shadow-lg">
              <div className="relative aspect-video bg-black">
                <video
                  ref={videoRef}
                  src={doneVideo}
                  className="h-full w-full object-contain"
                  controls
                  autoPlay
                  playsInline
                />
                <button
                  onClick={handleClose}
                  className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-white transition-colors hover:bg-black/80"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="p-4">
                <p className="text-sm font-medium">AI Explanation</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Generated from your prompt. Sign up to save and share!
                </p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* How It Works */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center font-display text-3xl font-bold">How it works</h2>
          <div className="mt-14 grid gap-8 md:grid-cols-3">
            {[
              { icon: Code, step: "01", title: "Input your code or concept", desc: "Paste a code snippet, describe an algorithm, or link a GitHub repo." },
              { icon: Sparkles, step: "02", title: "AI generates explanation", desc: "Our AI analyzes the architecture, writes a script, and creates an interactive walkthrough." },
              { icon: Video, step: "03", title: "Watch and share", desc: "Get a narrated visual explanation you can explore, download, or share." },
            ].map((item) => (
              <div key={item.step} className="group rounded-2xl border bg-card p-8 transition-all hover:shadow-lg">
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
                  <item.icon className="h-6 w-6 text-accent" />
                </div>
                <div className="mb-2 font-display text-xs font-semibold tracking-widest text-accent">{item.step}</div>
                <h3 className="font-display text-lg font-semibold">{item.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Logos */}
      <section className="border-t px-6 py-12">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-center gap-10">
          {logoNames.map((name) => (
            <span key={name} className="font-display text-sm font-bold tracking-wider text-muted-foreground/50 uppercase">
              {name}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Index;
