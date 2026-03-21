import { Link } from "react-router-dom";
import { Play, Code, Sparkles, Video } from "lucide-react";

const logoNames = ["TechCorp", "DevStudio", "CodeBase", "Synthetix", "NeuralNet", "DataFlow", "CloudOps"];

const Index = () => (
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

      {/* Prompt box mock */}
      <div className="mx-auto mt-16 max-w-2xl">
        <div className="peach-glow rounded-2xl p-6 shadow-xl shadow-peach/30">
          <p className="text-sm text-muted-foreground">
            Describe a concept to be explained by our AI...
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="inline-flex items-center rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground">
              Recursion.py
            </span>
            <span className="inline-flex items-center rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground">
              BinarySearch.js
            </span>
            <span className="inline-flex items-center rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground">
              TCP_Handshake.md
            </span>
          </div>
          <div className="mt-4 flex items-center gap-3 text-xs text-muted-foreground">
            <span>+</span>
            <span>🌐</span>
            <span className="flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Concierge
            </span>
          </div>
        </div>
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

export default Index;
