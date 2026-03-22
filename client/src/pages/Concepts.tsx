/** Concepts page — browse pre-made code/concept demo videos (no backend generation). */
import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Crown, Download, Loader2, Play } from "lucide-react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import AlgorithmBrowser, { type AlgorithmItem } from "@/components/AlgorithmBrowser";

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

const Concepts = () => {
  const { user, loading, isPremium, profileLoading, refreshProfile } = useAuth();
  const [upgrading, setUpgrading] = useState(false);

  const [mode, setMode] = useState<"concept" | "code">("concept");
  const [selectedPremade, setSelectedPremade] = useState<string | null>(null);
  const [selectedPremadeFile, setSelectedPremadeFile] = useState<string | null>(null);
  const [browserOpen, setBrowserOpen] = useState(false);

  const [generating, setGenerating] = useState(false);
  const [fakeStep, setFakeStep] = useState(-1);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    return () => {
      timerRef.current.forEach(clearTimeout);
    };
  }, []);

  useEffect(() => {
    setSelectedPremade(null);
    setSelectedPremadeFile(null);
  }, [mode]);

  const handleGenerate = () => {
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

        {/* Selected from browser (if not in default list) */}
        {selectedPremade && !activePremadeList.find((i) => i.id === selectedPremade) && (
          <div className="mt-3 flex items-center gap-3 rounded-2xl border-2 border-accent bg-accent/10 p-4 shadow-md shadow-accent/10">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-accent-foreground">
              <Play className="h-4 w-4" />
            </div>
            <span className="text-sm font-semibold">{selectedPremade.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</span>
            <Check className="ml-auto h-5 w-5 text-accent" />
          </div>
        )}

        {/* See more button */}
        <button
          onClick={() => setBrowserOpen(true)}
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-accent transition-colors hover:text-accent/80"
        >
          See more <ChevronDown className="h-4 w-4" />
        </button>

        {/* Algorithm browser dialog */}
        <AlgorithmBrowser open={browserOpen} onClose={() => setBrowserOpen(false)} onSelect={handleBrowserSelect} />

        <div className="mt-8">
          <button
            onClick={handleGenerate}
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

        {/* Upgrade banner — only for free users */}
        {!isPremium && (
          <div className="mt-12 rounded-2xl border border-accent/20 bg-accent/5 p-6 text-center">
            <Crown className="mx-auto h-8 w-8 text-accent" />
            <h3 className="mt-3 font-display text-lg font-semibold">Want custom videos?</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Upgrade to Premium to write your own prompts, choose avatars, and customise mood & level.
            </p>
            <button
              onClick={async () => {
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
              }}
              disabled={upgrading}
              className="mt-4 inline-flex h-10 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90 disabled:opacity-50"
            >
              {upgrading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Crown className="h-4 w-4" />}
              {upgrading ? "Upgrading…" : "Upgrade to Premium"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Concepts;
