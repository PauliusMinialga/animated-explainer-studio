import { Link, useLocation, useNavigate } from "react-router-dom";
import { LogOut, User } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, loading, signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
    navigate("/");
  };

  // Get display name and initials from user metadata
  const displayName =
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    user?.email?.split("@")[0] ||
    "User";
  const initials = displayName
    .split(" ")
    .map((w: string) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
  const avatarUrl = user?.user_metadata?.avatar_url;

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="font-display text-xl font-bold tracking-tight">
            Code<span className="hero-accent-text">Viz</span>
          </span>
        </Link>

        <div className="flex items-center gap-8">
          <div className="hidden items-center gap-6 text-sm font-medium sm:flex">
            <Link
              to="/"
              className={`transition-colors hover:text-foreground ${location.pathname === "/" ? "text-foreground" : "text-muted-foreground"}`}
            >
              Home
            </Link>
            {user && (
              <Link
                to="/profile"
                className={`transition-colors hover:text-foreground ${location.pathname === "/profile" ? "text-foreground" : "text-muted-foreground"}`}
              >
                Profile
              </Link>
            )}
          </div>

          <div className="flex items-center gap-3">
            {loading ? (
              <div className="h-9 w-20 animate-pulse rounded-lg bg-muted" />
            ) : user ? (
              <>
                <Link
                  to="/profile"
                  className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-secondary"
                >
                  {avatarUrl ? (
                    <img
                      src={avatarUrl}
                      alt={displayName}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/10 text-xs font-bold text-accent">
                      {initials}
                    </div>
                  )}
                  <span className="hidden text-sm font-medium sm:inline">
                    {displayName}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="inline-flex h-9 items-center gap-2 rounded-lg border px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Log out</span>
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                >
                  Log in
                </Link>
                <Link
                  to="/signup"
                  className="inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
