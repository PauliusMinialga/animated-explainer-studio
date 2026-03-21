import { Link, Navigate } from "react-router-dom";
import { Play, Lock, Crown } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const demoVideos = [
  { title: "Recursion Explained", duration: "2:34", color: "from-accent/20 to-accent/5" },
  { title: "Binary Search Animation", duration: "1:58", color: "from-blue-100 to-blue-50" },
  { title: "TCP Handshake", duration: "3:12", color: "from-orange-100 to-orange-50" },
];

const premiumFeatures = [
  "Custom avatar selection",
  "Custom prompt templates",
  "Mood & intonation settings",
  "Experience level tuning",
  "Priority rendering",
];

const Profile = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const displayName =
    user.user_metadata?.full_name ||
    user.user_metadata?.name ||
    user.email?.split("@")[0] ||
    "User";
  const email = user.email || "";
  const avatarUrl = user.user_metadata?.avatar_url;
  const initials = displayName
    .split(" ")
    .map((w: string) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="px-6 py-12">
      <div className="mx-auto max-w-4xl">
        {/* User Header */}
        <div className="flex items-center gap-4">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={displayName}
              className="h-16 w-16 rounded-full object-cover"
            />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-accent/10 font-display text-xl font-bold text-accent">
              {initials}
            </div>
          )}
          <div>
            <h1 className="font-display text-2xl font-bold">{displayName}</h1>
            <p className="text-sm text-muted-foreground">{email} · Free Plan</p>
          </div>
        </div>

        {/* Example Videos */}
        <section className="mt-12">
          <h2 className="font-display text-xl font-semibold">Example Videos</h2>
          <p className="mt-1 text-sm text-muted-foreground">Watch pre-rendered demo explanations</p>
          <div className="mt-6 grid gap-6 sm:grid-cols-3">
            {demoVideos.map((v) => (
              <div key={v.title} className="group cursor-pointer overflow-hidden rounded-2xl border bg-card transition-all hover:shadow-lg">
                <div className={`flex aspect-video items-center justify-center bg-gradient-to-br ${v.color}`}>
                  <Play className="h-10 w-10 rounded-full bg-primary/90 p-2.5 text-primary-foreground opacity-80 transition-opacity group-hover:opacity-100" />
                </div>
                <div className="p-4">
                  <h3 className="text-sm font-semibold">{v.title}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">{v.duration}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Locked Premium Section */}
        <section className="mt-16">
          <div className="relative overflow-hidden rounded-2xl border bg-card p-8">
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-card/80 backdrop-blur-[2px]">
              <Lock className="h-8 w-8 text-muted-foreground" />
              <h3 className="mt-3 font-display text-lg font-semibold">Premium Features</h3>
              <p className="mt-1 text-sm text-muted-foreground">Unlock the full power of CodeViz</p>
              <Link
                to="/premium"
                className="mt-5 inline-flex h-11 items-center gap-2 rounded-xl bg-accent px-6 text-sm font-semibold text-accent-foreground transition-colors hover:bg-accent/90"
              >
                <Crown className="h-4 w-4" /> Upgrade to Premium
              </Link>
            </div>
            <div className="grid gap-4 opacity-40 sm:grid-cols-2">
              {premiumFeatures.map((f) => (
                <div key={f} className="rounded-xl border bg-secondary p-4 text-sm font-medium">{f}</div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Profile;
