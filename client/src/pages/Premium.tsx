import { useEffect, useRef, useState } from "react";
import { Check, Crown, Download, Loader2, Lock, Play } from "lucide-react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
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

/** Overlay badge shown on locked sections for free users */
const LockedOverlay = ({ label }: { label: string }) => (
  <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-card/70 backdrop-blur-[2px]">
    <div className="flex items-center gap-2 rounded-full bg-muted px-4 py-2 text-xs font-semibold text-muted-foreground">
      <Lock className="h-3.5 w-3.5" />
      {label}
    </div>
  </div>
);

const Premium = () => {
  const { user, loading, isPremium, profileLoading } = useAuth();

  // Premium controls
  const [selectedAvatar, setSelectedAvatar] = useState("ava1");
  const [mode, setMode] = useState<"concept" | "code">("concept");
  const [mood, setMood] = useState("Friendly");
  const [level, setLevel] = useState("Beginner");
  const [prompt, setPrompt] = useState("");
  const [url, setUrl] = useState("");

  // Free user: premade selection
  const [selectedPremade, setSelectedPremade] = useState<string | null>(null);

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
    if (!item) return;

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
      setVideoUrl(item.file);
    }, FAKE_STEPS.length * 1200 + 800);
    timerRef.current.push(finalTimer);
  };

  // ── Premium user: real request ──
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

  return (
    <div className="px-6 py-12">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="flex items-center gap-3">
          {isPremium && (
            <div className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
              <Crown className="h-3.5 w-3.5" /> Premium
            </div>
          )}
        </div>
        <h1 className="mt-2 font-display text-3xl font-bold">Create Your Video</h1>
        <p className="mt-2 text-muted-foreground">
          {isPremium
            ? "Select an avatar, write your prompt, and generate an animated explanation."
            : "Pick a premade concept or code explanation to watch. Upgrade to unlock custom generation."}
        </p>

        {/* ── Avatar Selection — locked for free ── */}
        <section className="relative mt-10">
          {!isPremium && <LockedOverlay label="Premium — Upgrade to choose an avatar" />}
          <h2 className="font-display text-lg font-semibold">Choose Avatar</h2>
          <div className={`mt-4 grid grid-cols-3 gap-4 ${!isPremium ? "pointer-events-none opacity-40" : ""}`}>
            {avatars.map((a) => (
              <button
                key={a.id}
                onClick={() => isPremium && setSelectedAvatar(a.id)}
                disabled={!isPremium}
                className={`relative flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition-all hover:shadow-md ${
                  selectedAvatar === a.id && isPremium ? "border-accent bg-accent/5 shadow-md" : "border-transparent bg-card"
                }`}
              >
                {selectedAvatar === a.id && isPremium && (
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

        {/* ── Prompt / Premade Section ── */}
        <section className="mt-10">
          <h2 className="font-display text-lg font-semibold">
            {isPremium ? "Your Prompt" : "Choose a Video"}
          </h2>
          <div className="mt-4 space-y-4">
            {/* Mode toggle — free users can switch between concept/code premade lists */}
            <div className="relative inline-block">
              {!isPremium && (
                <div className="absolute -right-2 -top-2 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-muted">
                  <Lock className="h-3 w-3 text-muted-foreground" />
                </div>
              )}
              <div className={`inline-flex rounded-xl border bg-secondary p-1 ${!isPremium ? "opacity-50 pointer-events-none" : ""}`}>
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
            </div>

            {isPremium ? (
              /* Premium: free-form input */
              <>
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
              </>
            ) : (
              /* Free: premade video buttons */
              <>
                <div className="relative">
                  <textarea
                    disabled
                    rows={3}
                    className="flex w-full cursor-not-allowed rounded-xl border bg-card px-4 py-3 font-mono text-sm opacity-40 outline-none"
                    placeholder="Custom prompts are a Premium feature…"
                  />
                </div>
                <div className="relative">
                  <input
                    disabled
                    type="url"
                    className="flex h-11 w-full cursor-not-allowed rounded-xl border bg-card px-4 text-sm opacity-40 outline-none"
                    placeholder="GitHub link — Premium only"
                  />
                </div>
                <div>
                  <p className="mb-3 text-sm font-medium text-muted-foreground">
                    Select a premade {mode === "code" ? "code" : "concept"} video:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {activePremadeList.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => setSelectedPremade(item.id)}
                        disabled={generating}
                        className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-all ${
                          selectedPremade === item.id
                            ? "border-accent bg-accent/10 text-accent shadow-sm"
                            : "bg-card text-muted-foreground hover:border-accent/40 hover:text-foreground"
                        } disabled:opacity-50`}
                      >
                        <Play className="h-3.5 w-3.5" />
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </section>

        {/* ── Settings — locked for free ── */}
        <section className="relative mt-10">
          {!isPremium && <LockedOverlay label="Premium — Upgrade to customise mood & level" />}
          <h2 className="font-display text-lg font-semibold">Settings</h2>
          <div className={`mt-4 grid gap-6 sm:grid-cols-2 ${!isPremium ? "pointer-events-none opacity-40" : ""}`}>
            <div>
              <label className="mb-2 block text-sm font-medium">Mood / Intonation</label>
              <div className="flex flex-wrap gap-2">
                {moods.map((m) => (
                  <button key={m} onClick={() => isPremium && setMood(m)} disabled={!isPremium}
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
                  <button key={l} onClick={() => isPremium && setLevel(l)} disabled={!isPremium}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      level === l ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    }`}
                  >{l}</button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── Generate Button ── */}
        <section className="mt-10">
          <button
            onClick={isPremium ? handlePremiumGenerate : handleFreeGenerate}
            disabled={generating || (isPremium ? !prompt.trim() : !selectedPremade)}
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-accent px-8 text-sm font-semibold text-accent-foreground shadow-lg shadow-accent/20 transition-all hover:bg-accent/90 disabled:opacity-50 disabled:shadow-none"
          >
            {generating && <Loader2 className="h-4 w-4 animate-spin" />}
            {generating ? "Generating…" : "Generate Video"}
          </button>

          {/* Progress steps */}
          {(generating || fakeStep === FAKE_STEPS.length) && !videoUrl && !premiumRequestSent && (
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

          {/* Premium: request submitted confirmation */}
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

          {/* Free: video player */}
          {videoUrl && (
            <div className="mt-6 overflow-hidden rounded-2xl border bg-card shadow-lg">
              <div className="relative aspect-video bg-black">
                <video
                  ref={videoRef}
                  src={videoUrl}
                  className="h-full w-full object-contain"
                  controls
                  autoPlay
                  playsInline
                />
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
        </section>
      </div>
    </div>
  );
};

export default Premium;
