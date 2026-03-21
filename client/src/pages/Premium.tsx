import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Crown, Download, Loader2, Play } from "lucide-react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import AlgorithmBrowser, { type AlgorithmItem } from "@/components/AlgorithmBrowser";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";

const BACKEND = "http://localhost:8000";

const avatars = [
  { id: "ava1", name: "Nova", emoji: "🤖" },
  { id: "ava2", name: "Sage", emoji: "🧑‍🏫" },
  { id: "ava3", name: "Pixel", emoji: "👾" },
];

const moods = ["Friendly", "Technical", "Energetic", "Calm"];
const levels = ["Beginner", "Advanced", "Expert"];

const premadeConcepts = [
  { id: "recursion", label: "Recursion", file: "/demo/recursion.mp4" },
  { id: "binary_search", label: "Binary Search", file: "/demo/binary_search.mp4" },
  { id: "tcp_handshake", label: "TCP Handshake", file: "/demo/tcp_handshake.mp4" },
  { id: "gradient_descent", label: "Gradient Descent", file: "/demo/gradient_descent.mp4" },
];

const premadeCode = [
  { id: "explain_factorial", label: "Factorial", file: "/demo/explain_factorial.mp4" },
  { id: "explain_dijkstra", label: "Dijkstra", file: "/demo/explain_dijkstra.mp4" },
];

const FAKE_STEPS = [
  "Generating scripts…",
  "Rendering animation…",
  "Adding voiceover…",
  "Finalising video…",
];


const Premium = () => {
  const { user, loading, isPremium, profileLoading } = useAuth();

  // Premium controls
  const [selectedAvatar, setSelectedAvatar] = useState("ava1");
  const [mode, setMode] = useState<"concept" | "code">("concept");
  const [mood, setMood] = useState("Friendly");
  const [level, setLevel] = useState("Beginner");
  const [prompt, setPrompt] = useState("");
  const [url, setUrl] = useState("");

  const [selectedPremade, setSelectedPremade] = useState<string | null>(null);
  const [selectedPremadeFile, setSelectedPremadeFile] = useState<string | null>(null);
  const [browserOpen, setBrowserOpen] = useState(false);

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [fakeStep, setFakeStep] = useState(-1);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [premiumRequestSent, setPremiumRequestSent] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  // ── Free user: fake generation ──
  const handleFreeGenerate = () => {
    if (!selectedPremade || generating) return;
    const list = mode === "code" ? premadeCode : premadeConcepts;
    const item = list.find((c) => c.id === selectedPremade);
    const file = item?.file ?? selectedPremadeFile;
    if (!file) return;

    setGenerating(true);
    setVideoUrl(null);
    setFakeStep(0);
    setPremiumRequestSent(false);

    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];

    FAKE_STEPS.forEach((_, i) => {
      const t = setTimeout(() => setFakeStep(i), i * 1200);
      timerRef.current.push(t);
    });

    const finalTimer = setTimeout(() => {
      setGenerating(false);
      setFakeStep(FAKE_STEPS.length);
      setVideoUrl(file);
    }, FAKE_STEPS.length * 1200 + 800);
    timerRef.current.push(finalTimer);
  };

  const handleBrowserSelect = (item: AlgorithmItem) => {
    setSelectedPremade(item.id);
    setSelectedPremadeFile(item.file);
  };


  const handlePremiumGenerate = async () => {
    if (!prompt.trim() || generating) return;

    const payload = {
      prompt: prompt.trim(),
      url: url.trim() || null,
      mode,
      avatar: selectedAvatar,
      mood: mood.toLowerCase(),
      level: level.toLowerCase(),
      user_id: user?.id,
    };

    console.log("[GenerateVideo] Request payload:", JSON.stringify(payload, null, 2));

    setGenerating(true);
    setVideoUrl(null);
    setFakeStep(0);
    setPremiumRequestSent(false);

    try {
      // Store the request in Supabase so the team can pick it up
      const { error } = await supabase.from("video_requests").insert({
        user_id: user!.id,
        topic: prompt.trim(),
        mood: mood.toLowerCase(),
        level: level.toLowerCase(),
        avatar: selectedAvatar,
        status: "pending",
      });

      if (error) {
        console.error("Failed to save video request:", error);
        toast({ title: "Error", description: "Failed to submit request. Please try again.", variant: "destructive" });
        setGenerating(false);
        setFakeStep(-1);
        return;
      }

      // Walk through fake progress while backend works
      FAKE_STEPS.forEach((_, i) => {
        const t = setTimeout(() => setFakeStep(i), i * 1500);
        timerRef.current.push(t);
      });

      const doneTimer = setTimeout(() => {
        setGenerating(false);
        setFakeStep(FAKE_STEPS.length);
        setPremiumRequestSent(true);
        toast({ title: "Request submitted!", description: "Your video is being generated. We'll notify you when it's ready." });
      }, FAKE_STEPS.length * 1500 + 500);
      timerRef.current.push(doneTimer);
    } catch {
      setGenerating(false);
      setFakeStep(-1);
      toast({ title: "Error", description: "Something went wrong.", variant: "destructive" });
    }
  };

  const handleClose = () => {
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];
    setVideoUrl(null);
    setGenerating(false);
    setFakeStep(-1);
    setPremiumRequestSent(false);
  };

  useEffect(() => {
    return () => timerRef.current.forEach(clearTimeout);
  }, []);

  // Reset premade selection when mode changes (free only)
  useEffect(() => {
    setSelectedPremade(null);
  }, [mode]);

  if (loading || profileLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  const activePremadeList = mode === "code" ? premadeCode : premadeConcepts;

  // ── FREE USER LAYOUT ──
  if (!isPremium) {
    return (
      <div className="px-6 py-12">
        <div className="mx-auto max-w-3xl">
          {/* Header */}
          <h1 className="font-display text-3xl font-bold">Explore Video Explanations</h1>
          <p className="mt-2 text-muted-foreground">
            Pick a topic below and watch an AI-generated animated explanation.
          </p>

          {/* Category tabs */}
          <div className="mt-8 flex gap-2">
            {(["concept", "code"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`rounded-full px-5 py-2 text-sm font-semibold transition-all ${
                  mode === m
                    ? "bg-accent text-accent-foreground shadow-md shadow-accent/20"
                    : "bg-secondary text-muted-foreground hover:text-foreground"
                }`}
              >
                {m === "concept" ? "📚 Concepts" : "💻 Code"}
              </button>
            ))}
          </div>

          {/* Premade video grid */}
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {activePremadeList.map((item) => (
              <button
                key={item.id}
                onClick={() => setSelectedPremade(item.id)}
                disabled={generating}
                className={`group flex items-center gap-4 rounded-2xl border-2 p-5 text-left transition-all ${
                  selectedPremade === item.id
                    ? "border-accent bg-accent/10 shadow-md shadow-accent/10"
                    : "border-transparent bg-card hover:border-accent/30 hover:shadow-sm"
                } disabled:opacity-50`}
              >
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl transition-colors ${
                    selectedPremade === item.id
                      ? "bg-accent text-accent-foreground"
                      : "bg-secondary text-muted-foreground group-hover:bg-accent/10 group-hover:text-accent"
                  }`}
                >
                  <Play className="h-5 w-5" />
                </div>
                <div>
                  <span className="font-semibold">{item.label}</span>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {mode === "concept" ? "Animated concept breakdown" : "Step-by-step code walkthrough"}
                  </p>
                </div>
                {selectedPremade === item.id && (
                  <Check className="ml-auto h-5 w-5 shrink-0 text-accent" />
                )}
              </button>
            ))}
          </div>

          {/* Generate button */}
          <div className="mt-8">
            <button
              onClick={handleFreeGenerate}
              disabled={generating || !selectedPremade}
              className="inline-flex h-12 items-center gap-2 rounded-xl bg-accent px-8 text-sm font-semibold text-accent-foreground shadow-lg shadow-accent/20 transition-all hover:bg-accent/90 disabled:opacity-50 disabled:shadow-none"
            >
              {generating && <Loader2 className="h-4 w-4 animate-spin" />}
              {generating ? "Generating…" : "Generate Video"}
            </button>
          </div>

          {/* Progress steps */}
          {(generating || fakeStep === FAKE_STEPS.length) && !videoUrl && (
            <div className="mt-6 space-y-3 rounded-xl border bg-card p-6">
              {FAKE_STEPS.map((label, i) => {
                const done = i < fakeStep || fakeStep === FAKE_STEPS.length;
                const active = i === fakeStep && generating;
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
            </div>
          )}

          {/* Video player */}
          {videoUrl && (
            <div className="mt-6 overflow-hidden rounded-2xl border bg-card shadow-lg">
              <div className="relative aspect-video bg-black">
                <video ref={videoRef} src={videoUrl} className="h-full w-full object-contain" controls autoPlay playsInline />
              </div>
              <div className="flex items-center justify-between p-4">
                <p className="text-sm font-medium">
                  {activePremadeList.find((c) => c.id === selectedPremade)?.label ?? "Video"} — AI Explanation
                </p>
                <a
                  href={videoUrl}
                  download
                  className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  <Download className="h-4 w-4" /> Download
                </a>
              </div>
            </div>
          )}

          {/* Upgrade banner */}
          <div className="mt-12 rounded-2xl border border-accent/20 bg-accent/5 p-6 text-center">
            <Crown className="mx-auto h-8 w-8 text-accent" />
            <h3 className="mt-3 font-display text-lg font-semibold">Want custom videos?</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Upgrade to Premium to write your own prompts, choose avatars, and customise mood & level.
            </p>
            <a
              href="/premium"
              className="mt-4 inline-flex h-10 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90"
            >
              <Crown className="h-4 w-4" /> Upgrade to Premium
            </a>
          </div>
        </div>
      </div>
    );
  }

  // ── PREMIUM USER LAYOUT ──
  return (
    <div className="px-6 py-12">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
            <Crown className="h-3.5 w-3.5" /> Premium
          </div>
        </div>
        <h1 className="mt-2 font-display text-3xl font-bold">Create Your Video</h1>
        <p className="mt-2 text-muted-foreground">
          Select an avatar, write your prompt, and generate an animated explanation.
        </p>

        {/* Avatar Selection */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">Choose Avatar</h2>
          <div className="mt-4 grid grid-cols-3 gap-4">
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

        {/* Prompt Section */}
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
              placeholder={
                mode === "concept"
                  ? "Describe a concept, e.g. 'Explain how recursion works with a visual tree diagram'"
                  : "Paste a code snippet to be explained visually…\n\ndef factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"
              }
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

        {/* Generate Button */}
        <section className="mt-10">
          <button
            onClick={handlePremiumGenerate}
            disabled={generating || !prompt.trim()}
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-accent px-8 text-sm font-semibold text-accent-foreground shadow-lg shadow-accent/20 transition-all hover:bg-accent/90 disabled:opacity-50 disabled:shadow-none"
          >
            {generating && <Loader2 className="h-4 w-4 animate-spin" />}
            {generating ? "Generating…" : "Generate Video"}
          </button>

          {/* Progress steps */}
          {(generating || fakeStep === FAKE_STEPS.length) && !premiumRequestSent && (
            <div className="mt-6 space-y-3 rounded-xl border bg-card p-6">
              {FAKE_STEPS.map((label, i) => {
                const done = i < fakeStep || fakeStep === FAKE_STEPS.length;
                const active = i === fakeStep && generating;
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
            </div>
          )}

          {/* Request submitted */}
          {premiumRequestSent && (
            <div className="mt-6 rounded-xl border border-accent/30 bg-accent/5 p-6 text-center">
              <Check className="mx-auto h-10 w-10 text-accent" />
              <h3 className="mt-3 font-display text-lg font-semibold">Request Submitted</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Your video generation request has been queued. You'll be notified when it's ready.
              </p>
              <button
                onClick={handleClose}
                className="mt-4 inline-flex h-10 items-center rounded-xl border px-5 text-sm font-medium transition-colors hover:bg-secondary"
              >
                Create Another
              </button>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Premium;
