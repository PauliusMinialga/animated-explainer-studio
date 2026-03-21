import { useEffect, useRef, useState } from "react";
import { Check, Download, Loader2 } from "lucide-react";

const BACKEND = "http://localhost:8000";

const avatars = [
  { id: "ava1", name: "Nova", emoji: "🤖" },
  { id: "ava2", name: "Sage", emoji: "🧑‍🏫" },
  { id: "ava3", name: "Pixel", emoji: "👾" },
  { id: "ava4", name: "Aria", emoji: "🎙️" },
  { id: "ava5", name: "Byte", emoji: "💻" },
  { id: "ava6", name: "Echo", emoji: "🔊" },
];

const moods = ["Friendly", "Technical", "Energetic", "Calm"];
const levels = ["Beginner", "Advanced", "Expert"];

const STEPS = [
  "Generating scripts…",
  "Rendering animation…",
  "Adding voiceover…",
  "Generating avatar…",
];

type Job = {
  job_id: string;
  status: "pending" | "running" | "done" | "failed";
  progress: string | null;
  animation_url: string | null;
  avatar_url: string | null;
  error: string | null;
};

const Premium = () => {
  const [selectedAvatar, setSelectedAvatar] = useState("ava1");
  const [mode, setMode] = useState<"concept" | "code">("code");
  const [mood, setMood] = useState("Friendly");
  const [level, setLevel] = useState("Beginner");
  const [prompt, setPrompt] = useState("");
  const [url, setUrl] = useState("");
  const [job, setJob] = useState<Job | null>(null);
  const [activeStep, setActiveStep] = useState(-1);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const animRef = useRef<HTMLVideoElement>(null);
  const avatarRef = useRef<HTMLVideoElement>(null);

  // Map fake step labels to real progress strings from backend
  const stepForProgress = (progress: string | null) => {
    if (!progress) return -1;
    const p = progress.toLowerCase();
    if (p.includes("script")) return 0;
    if (p.includes("render") || p.includes("animation")) return 1;
    if (p.includes("voice") || p.includes("tts")) return 2;
    if (p.includes("avatar")) return 3;
    if (p.includes("done")) return 4;
    return activeStep;
  };

  const stopPolling = () => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = null;
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setJob(null);
    setActiveStep(0);

    const res = await fetch(`${BACKEND}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt.trim(),
        url: url.trim() || null,
        mode,
        level: level.toLowerCase(),
        mood: mood.toLowerCase(),
      }),
    });

    if (!res.ok) {
      setJob({ job_id: "", status: "failed", progress: null, animation_url: null, avatar_url: null, error: "Failed to start generation." });
      return;
    }

    const initial: Job = await res.json();
    setJob(initial);

    pollRef.current = setInterval(async () => {
      try {
        const poll = await fetch(`${BACKEND}/jobs/${initial.job_id}`);
        const data: Job = await poll.json();
        setJob(data);
        setActiveStep(stepForProgress(data.progress));
        if (data.status === "done" || data.status === "failed") stopPolling();
      } catch {
        stopPolling();
      }
    }, 2500);
  };

  // Sync both videos to play together
  const handlePlay = () => {
    animRef.current?.play();
    avatarRef.current?.play();
  };

  useEffect(() => () => stopPolling(), []);

  const isRunning = job?.status === "pending" || job?.status === "running";
  const isDone = job?.status === "done";
  const isFailed = job?.status === "failed";

  return (
    <div className="px-6 py-12">
      <div className="mx-auto max-w-4xl">
        <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
          ✨ Premium
        </div>
        <h1 className="font-display text-3xl font-bold">Create Your Video</h1>
        <p className="mt-2 text-muted-foreground">Select an avatar, write your prompt, and generate an animated explanation.</p>

        {/* Avatar Selection */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Choose Avatar</h2>
          <div className="mt-4 grid grid-cols-3 gap-4 sm:grid-cols-6">
            {avatars.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelectedAvatar(a.id)}
                className={`relative flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition-all hover:shadow-md ${
                  selectedAvatar === a.id ? "border-accent bg-accent/5 shadow-md" : "border-transparent bg-card"
                }`}
              >
                {selectedAvatar === a.id && (
                  <div className="absolute right-2 top-2 flex h-5 w-5 items-center justify-center rounded-full bg-accent">
                    <Check className="h-3 w-3 text-accent-foreground" />
                  </div>
                )}
                <span className="text-3xl">{a.emoji}</span>
                <span className="text-xs font-medium">{a.name}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Prompt Input */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Your Prompt</h2>
          <div className="mt-4 space-y-4">
            <div className="inline-flex rounded-xl border bg-secondary p-1">
              {(["concept", "code"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`rounded-lg px-5 py-2 text-sm font-medium transition-all ${
                    mode === m ? "bg-card shadow-sm" : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {m === "concept" ? "Concept Mode" : "Code Mode"}
                </button>
              ))}
            </div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={5}
              className="flex w-full rounded-xl border bg-card px-4 py-3 font-mono text-sm outline-none transition-colors focus:ring-2 focus:ring-ring"
              placeholder={mode === "concept"
                ? "Describe a concept, e.g. 'Explain how recursion works with a visual tree diagram'"
                : "Paste a code snippet to be explained visually…\n\ndef factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"}
            />
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex h-11 w-full rounded-xl border bg-card px-4 text-sm outline-none transition-colors focus:ring-2 focus:ring-ring"
              placeholder="Link to GitHub repo or article (optional)"
            />
          </div>
        </section>

        {/* Settings */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Settings</h2>
          <div className="mt-4 grid gap-6 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium">Mood / Intonation</label>
              <div className="flex flex-wrap gap-2">
                {moods.map((m) => (
                  <button key={m} onClick={() => setMood(m)}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      mood === m ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    }`}
                  >{m}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium">Experience Level</label>
              <div className="flex flex-wrap gap-2">
                {levels.map((l) => (
                  <button key={l} onClick={() => setLevel(l)}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      level === l ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    }`}
                  >{l}</button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Generate */}
        <section className="mt-10">
          <button
            onClick={handleGenerate}
            disabled={isRunning || !prompt.trim()}
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-accent px-8 text-sm font-semibold text-accent-foreground shadow-lg shadow-accent/20 transition-all hover:bg-accent/90 disabled:opacity-50 disabled:shadow-none"
          >
            {isRunning && <Loader2 className="h-4 w-4 animate-spin" />}
            {isRunning ? "Generating…" : "Generate Video"}
          </button>

          {/* Progress */}
          {(isRunning || isDone || isFailed) && (
            <div className="mt-6 space-y-3 rounded-xl border bg-card p-6">
              {STEPS.map((label, i) => {
                const done = i < activeStep || isDone;
                const active = i === activeStep && isRunning;
                return (
                  <div key={i} className="flex items-center gap-3">
                    {done ? (
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accent">
                        <Check className="h-3.5 w-3.5 text-accent-foreground" />
                      </div>
                    ) : (
                      <div className={`flex h-6 w-6 items-center justify-center rounded-full border-2 ${active ? "border-accent" : "border-muted"}`}>
                        {active && <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />}
                      </div>
                    )}
                    <span className={`text-sm ${done ? "font-medium" : active ? "text-foreground" : "text-muted-foreground"}`}>{label}</span>
                  </div>
                );
              })}
              {isFailed && (
                <p className="mt-2 text-sm text-destructive">{job?.error ?? "Generation failed."}</p>
              )}
            </div>
          )}

          {/* Dual Video Player */}
          {isDone && job?.animation_url && job?.avatar_url && (
            <div className="mt-6 overflow-hidden rounded-2xl border bg-black">
              <div className="relative aspect-video cursor-pointer" onClick={handlePlay}>
                {/* Main animation */}
                <video
                  ref={animRef}
                  src={`${BACKEND}${job.animation_url}`}
                  className="h-full w-full object-contain"
                  controls={false}
                  playsInline
                />
                {/* Avatar overlay — bottom-right */}
                <video
                  ref={avatarRef}
                  src={`${BACKEND}${job.avatar_url}`}
                  className="absolute bottom-4 right-4 w-1/4 rounded-xl shadow-xl"
                  controls={false}
                  playsInline
                />
                {/* Play hint */}
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 transition-opacity hover:opacity-0">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg">
                    <span className="ml-1 text-2xl">▶</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between border-t p-4">
                <span className="text-sm text-muted-foreground">Generated video</span>
                <a
                  href={`${BACKEND}${job.animation_url}`}
                  download="animation.mp4"
                  className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  <Download className="h-4 w-4" /> Download
                </a>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Premium;


const avatars = [
  { id: "ava1", name: "Nova", emoji: "🤖" },
  { id: "ava2", name: "Sage", emoji: "🧑‍🏫" },
  { id: "ava3", name: "Pixel", emoji: "👾" },
  { id: "ava4", name: "Aria", emoji: "🎙️" },
  { id: "ava5", name: "Byte", emoji: "💻" },
  { id: "ava6", name: "Echo", emoji: "🔊" },
];

const moods = ["Friendly", "Technical", "Energetic", "Calm"];
const levels = ["Beginner", "Advanced", "Expert"];

type GenStep = { label: string; done: boolean };

const Premium = () => {
  const [selectedAvatar, setSelectedAvatar] = useState("ava1");
  const [mode, setMode] = useState<"concept" | "code">("concept");
  const [mood, setMood] = useState("Friendly");
  const [level, setLevel] = useState("Beginner");
  const [prompt, setPrompt] = useState("");
  const [url, setUrl] = useState("");
  const [generating, setGenerating] = useState(false);
  const [done, setDone] = useState(false);
  const [steps, setSteps] = useState<GenStep[]>([]);

  const handleGenerate = () => {
    if (!prompt.trim()) return;
    setGenerating(true);
    setDone(false);
    const stepLabels = ["Generating script...", "Rendering animation...", "Adding voiceover...", "Finalizing video..."];
    setSteps(stepLabels.map((l) => ({ label: l, done: false })));

    stepLabels.forEach((_, i) => {
      setTimeout(() => {
        setSteps((prev) => prev.map((s, j) => (j <= i ? { ...s, done: true } : s)));
        if (i === stepLabels.length - 1) {
          setTimeout(() => {
            setGenerating(false);
            setDone(true);
          }, 800);
        }
      }, (i + 1) * 1200);
    });
  };

  return (
    <div className="px-6 py-12">
      <div className="mx-auto max-w-4xl">
        <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
          ✨ Premium
        </div>
        <h1 className="font-display text-3xl font-bold">Create Your Video</h1>
        <p className="mt-2 text-muted-foreground">Select an avatar, write your prompt, and generate an animated explanation.</p>

        {/* Avatar Selection */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Choose Avatar</h2>
          <div className="mt-4 grid grid-cols-3 gap-4 sm:grid-cols-6">
            {avatars.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelectedAvatar(a.id)}
                className={`relative flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition-all hover:shadow-md ${
                  selectedAvatar === a.id ? "border-accent bg-accent/5 shadow-md" : "border-transparent bg-card"
                }`}
              >
                {selectedAvatar === a.id && (
                  <div className="absolute right-2 top-2 flex h-5 w-5 items-center justify-center rounded-full bg-accent">
                    <Check className="h-3 w-3 text-accent-foreground" />
                  </div>
                )}
                <span className="text-3xl">{a.emoji}</span>
                <span className="text-xs font-medium">{a.name}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Prompt Input */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Your Prompt</h2>
          <div className="mt-4 space-y-4">
            {/* Mode toggle */}
            <div className="inline-flex rounded-xl border bg-secondary p-1">
              {(["concept", "code"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`rounded-lg px-5 py-2 text-sm font-medium transition-all ${
                    mode === m ? "bg-card shadow-sm" : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {m === "concept" ? "Concept Mode" : "Code Mode"}
                </button>
              ))}
            </div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="flex w-full rounded-xl border bg-card px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-ring"
              placeholder={mode === "concept" ? "Describe a concept, e.g. 'Explain how recursion works with a visual tree diagram'" : "Paste a code snippet to be explained visually..."}
            />
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex h-11 w-full rounded-xl border bg-card px-4 text-sm outline-none transition-colors focus:ring-2 focus:ring-ring"
              placeholder="Link to GitHub repo or article (optional)"
            />
          </div>
        </section>

        {/* Settings */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Settings</h2>
          <div className="mt-4 grid gap-6 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium">Mood / Intonation</label>
              <div className="flex flex-wrap gap-2">
                {moods.map((m) => (
                  <button
                    key={m}
                    onClick={() => setMood(m)}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      mood === m ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium">Experience Level</label>
              <div className="flex flex-wrap gap-2">
                {levels.map((l) => (
                  <button
                    key={l}
                    onClick={() => setLevel(l)}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      level === l ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Generate */}
        <section className="mt-10">
          <button
            onClick={handleGenerate}
            disabled={generating || !prompt.trim()}
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-accent px-8 text-sm font-semibold text-accent-foreground shadow-lg shadow-accent/20 transition-all hover:bg-accent/90 disabled:opacity-50 disabled:shadow-none"
          >
            {generating && <Loader2 className="h-4 w-4 animate-spin" />}
            {generating ? "Generating..." : "Generate Video"}
          </button>

          {/* Progress */}
          {(generating || done) && (
            <div className="mt-6 space-y-3 rounded-xl border bg-card p-6">
              {steps.map((s, i) => (
                <div key={i} className="flex items-center gap-3">
                  {s.done ? (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accent">
                      <Check className="h-3.5 w-3.5 text-accent-foreground" />
                    </div>
                  ) : (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full border-2">
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                    </div>
                  )}
                  <span className={`text-sm ${s.done ? "font-medium" : "text-muted-foreground"}`}>{s.label}</span>
                </div>
              ))}
            </div>
          )}

          {/* Video Player */}
          {done && (
            <div className="mt-6 overflow-hidden rounded-2xl border bg-card">
              <div className="flex aspect-video items-center justify-center bg-gradient-to-br from-accent/10 to-secondary">
                <div className="text-center">
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-accent/20">
                    <span className="text-2xl">▶</span>
                  </div>
                  <p className="mt-3 text-sm font-medium">Your video is ready!</p>
                </div>
              </div>
              <div className="flex items-center justify-between border-t p-4">
                <span className="text-sm text-muted-foreground">Generated video · 2:34</span>
                <button className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
                  <Download className="h-4 w-4" /> Download
                </button>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Premium;
