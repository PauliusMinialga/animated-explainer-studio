import { Link, Navigate } from "react-router-dom";
import { Play, Crown } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import PremiumGate from "@/components/PremiumGate";

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
  const { user, loading, isPremium, tier, profile, profileLoading } = useAuth();

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
    profile?.full_name ||
    user.user_metadata?.full_name ||
    user.user_metadata?.name ||
    user.email?.split("@")[0] ||
    "User";
  const email = user.email || "";
  const avatarUrl = profile?.avatar_url || user.user_metadata?.avatar_url;
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
            <p className="text-sm text-muted-foreground">
              {email} ·{" "}
              {isPremium ? (
                <span className="inline-flex items-center gap-1 text-accent">
                  <Crown className="h-3.5 w-3.5" /> Premium
                </span>
              ) : (
                "Free Plan"
              )}
              {profileLoading && " (loading…)"}
            </p>
          </div>
        </div>

        {/* Demo Videos — visible to all */}
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

        {/* Generation History — premium only */}
        <section className="mt-12">
          <h2 className="font-display text-xl font-semibold">Generation History</h2>
          <p className="mt-1 text-sm text-muted-foreground">Your previously generated videos</p>
          <div className="mt-6">
            <PremiumGate inline message="Generation history is a Premium feature">
              <p className="py-8 text-center text-sm text-muted-foreground">
                No generated videos yet. Head to the{" "}
                <Link to="/premium" className="font-medium text-accent hover:underline">
                  generation page
                </Link>{" "}
                to create your first video.
              </p>
            </PremiumGate>
          </div>
        </section>

        {/* Premium Features Upsell — only for free users */}
        {!isPremium && (
          <section className="mt-16">
            <PremiumGate message="Unlock the full power of CodeViz">
              <div className="grid gap-4 sm:grid-cols-2">
                {premiumFeatures.map((f) => (
                  <div key={f} className="rounded-xl border bg-secondary p-4 text-sm font-medium">{f}</div>
                ))}
              </div>
            </PremiumGate>
          </section>
        )}
      </div>
    </div>
  );
};

export default Profile;
