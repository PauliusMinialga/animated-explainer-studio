import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { Play, Code, Sparkles, Video, Loader2, Check, X } from "lucide-react";

const logoNames = ["TechCorp", "DevStudio", "CodeBase", "Synthetix", "NeuralNet", "DataFlow", "CloudOps"];

const demoConcepts = [
  { label: "Recursion.py", topic: "recursion" },
  { label: "BinarySearch.js", topic: "binary_search" },
  { label: "TCP_Handshake.md", topic: "tcp_handshake" },
];

const FAKE_STEPS = [
  "Analyzing concept…",
  "Generating script…",
  "Rendering animation…",
  "Adding voiceover…",
];

const Index = () => {
  const [selected, setSelected] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [fakeStep, setFakeStep] = useState(-1);
  const [doneVideo, setDoneVideo] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const handleConceptClick = (topic: string) => {
    setSelected(topic);
    setDoneVideo(null);
    setGenerating(false);
    setFakeStep(-1);
  };

  const handleGenerate = () => {
    if (!selected || generating) return;
    setGenerating(true);
    setDoneVideo(null);
    setFakeStep(0);

    // Clear any previous timers
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];

    // Walk through fake steps, then show the video
    FAKE_STEPS.forEach((_, i) => {
      const t = setTimeout(() => setFakeStep(i), i * 1200);
      timerRef.current.push(t);
    });

    const finalTimer = setTimeout(() => {
      setGenerating(false);
      setFakeStep(FAKE_STEPS.length);
      // TODO: Replace with real Supabase storage URLs from demo_videos table
      setDoneVideo(`/demo/${selected}.mp4`);
    }, FAKE_STEPS.length * 1200 + 800);
    timerRef.current.push(finalTimer);
  };

  const handleClose = () => {
    timerRef.current.forEach(clearTimeout);
    timerRef.current = [];
    setDoneVideo(null);
    setGenerating(false);
    setFakeStep(-1);
  };

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
            Paste your code or describe a concept — our AI generates beautiful animated
            video explanations in seconds. Learn, teach, and share visually.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              to="/signup"
              className="inline-flex h-12 items-center gap-2 rounded-xl bg-primary px-7 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:bg-primary/90 hover:shadow-xl"
            >
              Try It Free
            </Link>
            <a
              href="#demo"
              className="inline-flex h-12 items-center gap-2 rounded-xl border bg-card px-7 text-sm font-semibold transition-colors hover:bg-secondary"
            >
              <Play className="h-4 w-4" /> Watch Demo
            </a>
          </div>
        </div>

        {/* Prompt box */}
        <div className="mx-auto mt-16 max-w-2xl">
          <div className="peach-glow rounded-2xl p-6 shadow-xl shadow-peach/30">
            <p className="text-sm text-muted-foreground">
              Pick a concept to see it explained by our AI...
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {demoConcepts.map((c) => (
                <button
                  key={c.topic}
                  onClick={() => handleConceptClick(c.topic)}
                  disabled={generating}
                  className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
                    selected === c.topic
                      ? "bg-accent text-accent-foreground ring-2 ring-accent/40"
                      : "bg-accent/20 text-accent hover:bg-accent/30"
                  } disabled:opacity-50`}
                >
                  {c.label}
                </button>
              ))}
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleGenerate}
                disabled={!selected || generating}
                className="inline-flex h-10 items-center gap-2 rounded-xl bg-accent px-5 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90 disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Generating…
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" /> Generate
                  </>
                )}
              </button>
            </div>

            {/* Fake progress steps */}
            {(generating || fakeStep === FAKE_STEPS.length) && !doneVideo && (
              <div className="mt-4 space-y-2 rounded-xl border bg-card p-4">
                {FAKE_STEPS.map((label, i) => {
                  const done = i < fakeStep || fakeStep === FAKE_STEPS.length;
                  const active = i === fakeStep && generating;
                  return (
                    <div key={i} className="flex items-center gap-2">
                      {done ? (
                        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-accent">
                          <Check className="h-3 w-3 text-accent-foreground" />
                        </div>
                      ) : (
                        <div className={`flex h-5 w-5 items-center justify-center rounded-full border-2 ${active ? "border-accent" : "border-muted"}`}>
                          {active && <Loader2 className="h-3 w-3 animate-spin text-accent" />}
                        </div>
                      )}
                      <span className={`text-xs ${done ? "font-medium" : active ? "text-foreground" : "text-muted-foreground"}`}>
                        {label}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Video result */}
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
                <p className="text-sm font-medium">
                  {demoConcepts.find((c) => c.topic === selected)?.label ?? "Demo"} — AI Explanation
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  This is a pre-generated demo. Sign up to create custom videos!
                </p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Demo */}
      <section id="demo" className="bg-secondary/50 px-6 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="font-display text-3xl font-bold">See it in action</h2>
          <p className="mt-3 text-muted-foreground">Watch how CodeViz turns a simple concept into an animated explanation</p>
          <div className="mx-auto mt-10 aspect-video max-w-3xl overflow-hidden rounded-2xl border bg-card shadow-lg">
            <div className="flex h-full items-center justify-center bg-gradient-to-br from-secondary to-muted">
              <div className="flex flex-col items-center gap-3 text-muted-foreground">
                <Play className="h-16 w-16 rounded-full bg-primary p-4 text-primary-foreground" />
                <span className="text-sm font-medium">Demo Video Placeholder</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center font-display text-3xl font-bold">How it works</h2>
          <div className="mt-14 grid gap-8 md:grid-cols-3">
            {[
              { icon: Code, step: "01", title: "Input your code or concept", desc: "Paste a code snippet, describe an algorithm, or link a GitHub repo." },
              { icon: Sparkles, step: "02", title: "AI generates explanation", desc: "Our AI writes a script, creates animations, and adds voiceover — automatically." },
              { icon: Video, step: "03", title: "Watch and share", desc: "Get a polished animated video you can download, embed, or share anywhere." },
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
