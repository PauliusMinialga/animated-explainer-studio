import { useEffect, useRef, useState, useCallback } from "react";
import { Check, Crown, Download, Loader2, X } from "lucide-react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";

const avatars = [
  { id: "c3po", name: "C-3PO", image: "/c3po.jpg", position: "center" },
  { id: "super_man", name: "Super Man", image: "/super_man.jpg", position: "top" },
  { id: "wonder_woman", name: "Wonder Woman", image: "/wonder_woman.jpg", position: "top" },
];

const moods = ["Friendly", "Technical", "Energetic", "Calm"];
const levels = ["Beginner", "Advanced", "Expert"];

// Real pipeline statuses → step index + label
const STATUS_STEPS = [
  { status: "pending", label: "Queuing request…" },
  { status: "generating_script", label: "Generating script with AI…" },
  { status: "rendering", label: "Rendering animation…" },
  { status: "adding_voiceover", label: "Adding avatar voiceover…" },
  { status: "finalizing", label: "Finalizing video…" },
] as const;

const POLL_INTERVAL = 3000;
const POLL_TIMEOUT = 5 * 60 * 1000; // 5 minutes

const Premium = () => {
  const { user, loading, isPremium, profileLoading } = useAuth();

  // Premium controls
  const [selectedAvatar, setSelectedAvatar] = useState("c3po");
  const [mode, setMode] = useState<"concept" | "code">("concept");
  const [mood, setMood] = useState("Friendly");
  const [level, setLevel] = useState("Beginner");
  const [prompt, setPrompt] = useState("");
  const [url, setUrl] = useState("");

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [fakeStep, setFakeStep] = useState(-1);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  // Real polling state (premium)
  const [requestId, setRequestId] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollStartRef = useRef<number>(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  // Stop polling helper
  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  // Poll for status updates
  const startPolling = useCallback((reqId: string) => {
    pollStartRef.current = Date.now();

    pollRef.current = setInterval(async () => {
      // Timeout check
      if (Date.now() - pollStartRef.current > POLL_TIMEOUT) {
        stopPolling();
        setGenerating(false);
        setCurrentStatus(null);
        toast({
          title: "Taking longer than expected",
          description: "Your video is still being processed. Check back later on your profile.",
        });
        return;
      }

      const { data, error } = await supabase
        .from("video_requests")
        .select("status, error_message")
        .eq("id", reqId)
        .maybeSingle();

      if (error || !data) return;

      setCurrentStatus(data.status);

      if (data.status === "completed") {
        stopPolling();
        // Fetch the generated video
        const { data: videoData } = await supabase
          .from("generated_videos")
          .select("video_url")
          .eq("request_id", reqId)
          .maybeSingle();

        setGenerating(false);
        if (videoData?.video_url) {
          setVideoUrl(videoData.video_url);
          toast({ title: "🎉 Video ready!", description: "Your video has been generated." });
        } else {
          toast({ title: "Video completed", description: "Video processed but URL not available yet." });
        }
      } else if (data.status === "failed") {
        stopPolling();
        setGenerating(false);
        setErrorMessage(data.error_message || "An unknown error occurred.");
        toast({
          title: "Generation failed",
          description: data.error_message || "Something went wrong.",
          variant: "destructive",
        });
      }
    }, POLL_INTERVAL);
  }, [stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
      timerRef.current.forEach(clearTimeout);
    };
  }, [stopPolling]);

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

  const handleUpgrade = async () => {
    if (!user || upgrading) return;
    setUpgrading(true);
    const { error } = await supabase
      .from("profiles")
      .update({ tier: "premium" })
      .eq("user_id", user.id);
    if (error) {
      toast({ title: "Error", description: "Upgrade failed. Please try again.", variant: "destructive" });
    } else {
      await refreshProfile();
      toast({ title: "🎉 Welcome to Premium!", description: "You now have full access to custom video generation." });
    }
    setUpgrading(false);
  };

  // ── Premium user: real generation ──
  const handlePremiumGenerate = async () => {
    const isPromptMode = mode === "concept";
    if (isPromptMode ? !prompt.trim() : !url.trim()) return;
    if (generating) return;

    setGenerating(true);
    setVideoUrl(null);
    setRequestId(null);
    setCurrentStatus(null);
    setErrorMessage(null);

    try {
      const { data, error } = await supabase.functions.invoke("generate-video", {
        body: {
          topic: isPromptMode ? prompt.trim() : url.trim(),
          mode: isPromptMode ? "prompt" : "repo",
          avatar: selectedAvatar,
          mood: mood.toLowerCase(),
          level: level.toLowerCase(),
          github_url: url.trim() || null,
        },
      });

      if (error) {
        throw new Error(error.message || "Failed to invoke edge function");
      }

      const reqId = data?.request_id;
      if (!reqId) {
        throw new Error("No request_id returned");
      }

      setRequestId(reqId);
      setCurrentStatus("pending");
      startPolling(reqId);
      toast({ title: "Request submitted!", description: "Your video is being generated." });
    } catch (err: any) {
      setGenerating(false);
      toast({
        title: "Error",
        description: err.message || "Something went wrong.",
        variant: "destructive",
      });
    }
  };

  const handleCancel = () => {
    stopPolling();
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];
    setVideoUrl(null);
    setGenerating(false);
    setFakeStep(-1);
    setRequestId(null);
    setCurrentStatus(null);
    setErrorMessage(null);
  };

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

  // Compute current step index for the real pipeline
  const currentStepIndex = currentStatus
    ? STATUS_STEPS.findIndex((s) => s.status === currentStatus)
    : -1;

  if (!isPremium) return <Navigate to="/concepts" replace />;

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
                disabled={generating}
                className={`relative flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition-all hover:shadow-md ${
                  selectedAvatar === a.id ? "border-accent bg-accent/5 shadow-md" : "border-transparent bg-card"
                } disabled:opacity-50`}
              >
                {selectedAvatar === a.id && (
                  <div className="absolute right-2 top-2 flex h-5 w-5 items-center justify-center rounded-full bg-accent">
                    <Check className="h-3 w-3 text-accent-foreground" />
                  </div>
                )}
                <img src={a.image} alt={a.name} className="h-16 w-16 rounded-full object-cover" style={{ objectPosition: a.position }} />
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
                  onClick={() => !generating && setMode(m)}
                  className={`rounded-lg px-5 py-2 text-sm font-medium transition-all ${
                    mode === m ? "bg-card shadow-sm" : "text-muted-foreground hover:text-foreground"
                  } ${generating ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  {m === "concept" ? "Prompt Mode" : "Repo Mode"}
                </button>
              ))}
            </div>
            {mode === "concept" ? (
              <>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">Prompt</label>
                  <p className="mb-2 text-xs text-muted-foreground">Paste a concept description or a code snippet to animate.</p>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={6}
                    disabled={generating}
                    className="flex w-full rounded-xl border bg-card px-4 py-3 font-mono text-sm outline-none transition-colors focus:ring-2 focus:ring-ring disabled:opacity-50"
                    placeholder={"Explain how recursion works with a visual tree diagram\n\ndef factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"}
                  />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium">GitHub Link <span className="text-muted-foreground font-normal">(optional)</span></label>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={generating}
                    className="flex h-11 w-full rounded-xl border bg-card px-4 text-sm outline-none transition-colors focus:ring-2 focus:ring-ring disabled:opacity-50"
                    placeholder="https://github.com/user/repo"
                  />
                </div>
              </>
            ) : (
              <div>
                <label className="mb-1.5 block text-sm font-medium">Repository Link</label>
                <p className="mb-2 text-xs text-muted-foreground">Paste a GitHub repo URL — we'll analyze the code and generate a visual walkthrough.</p>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={generating}
                  className="flex h-11 w-full rounded-xl border bg-card px-4 text-sm outline-none transition-colors focus:ring-2 focus:ring-ring disabled:opacity-50"
                  placeholder="https://github.com/user/repo"
                />
              </div>
            )}
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
                  <button key={m} onClick={() => !generating && setMood(m)}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      mood === m ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    } ${generating ? "opacity-50 cursor-not-allowed" : ""}`}
                  >{m}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium">Experience Level</label>
              <div className="flex flex-wrap gap-2">
                {levels.map((l) => (
                  <button key={l} onClick={() => !generating && setLevel(l)}
                    className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                      level === l ? "border-accent bg-accent/10 text-accent" : "bg-card text-muted-foreground hover:text-foreground"
                    } ${generating ? "opacity-50 cursor-not-allowed" : ""}`}
                  >{l}</button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Generate Button */}
        <section className="mt-10">
          <div className="flex items-center gap-3">
            <button
              onClick={handlePremiumGenerate}
              disabled={generating || (mode === "concept" ? !prompt.trim() : !url.trim())}
              className="inline-flex h-12 items-center gap-2 rounded-xl bg-accent px-8 text-sm font-semibold text-accent-foreground shadow-lg shadow-accent/20 transition-all hover:bg-accent/90 disabled:opacity-50 disabled:shadow-none"
            >
              {generating && <Loader2 className="h-4 w-4 animate-spin" />}
              {generating ? "Generating…" : "Generate Video"}
            </button>

            {generating && (
              <button
                onClick={handleCancel}
                className="inline-flex h-12 items-center gap-2 rounded-xl border px-5 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                <X className="h-4 w-4" /> Cancel
              </button>
            )}
          </div>

          {/* Real-time progress steps */}
          {generating && currentStatus && (
            <div className="mt-6 space-y-3 rounded-xl border bg-card p-6">
              {STATUS_STEPS.map((step, i) => {
                const done = i < currentStepIndex || currentStatus === "completed";
                const active = i === currentStepIndex && currentStatus !== "completed" && currentStatus !== "failed";
                const upcoming = i > currentStepIndex;
                return (
                  <div key={step.status} className="flex items-center gap-3">
                    {done ? (
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-accent">
                        <Check className="h-3.5 w-3.5 text-accent-foreground" />
                      </div>
                    ) : active ? (
                      <div className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-accent">
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />
                      </div>
                    ) : (
                      <div className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-muted" />
                    )}
                    <span className={`text-sm ${done ? "font-medium" : active ? "text-foreground" : "text-muted-foreground"}`}>
                      {step.label}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Error state */}
          {errorMessage && !generating && (
            <div className="mt-6 rounded-xl border border-destructive/30 bg-destructive/5 p-6">
              <h3 className="font-display text-lg font-semibold text-destructive">Generation Failed</h3>
              <p className="mt-2 text-sm text-muted-foreground">{errorMessage}</p>
              <button
                onClick={handleCancel}
                className="mt-4 inline-flex h-10 items-center rounded-xl border px-5 text-sm font-medium transition-colors hover:bg-secondary"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Video player */}
          {videoUrl && !generating && (
            <div className="mt-6 overflow-hidden rounded-2xl border bg-card shadow-lg">
              <div className="relative aspect-video bg-black">
                <video ref={videoRef} src={videoUrl} className="h-full w-full object-contain" controls autoPlay playsInline />
              </div>
              <div className="flex items-center justify-between p-4">
                <p className="text-sm font-medium">Your Generated Video</p>
                <div className="flex items-center gap-3">
                  <a
                    href={videoUrl}
                    download
                    className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                  >
                    <Download className="h-4 w-4" /> Download
                  </a>
                  <button
                    onClick={handleCancel}
                    className="inline-flex h-9 items-center rounded-lg border px-4 text-sm font-medium transition-colors hover:bg-secondary"
                  >
                    Create Another
                  </button>
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Premium;
