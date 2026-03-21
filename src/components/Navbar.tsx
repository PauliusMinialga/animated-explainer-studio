import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();
  const isLoggedIn = false; // Mock auth state

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
            <Link
              to="/profile"
              className={`transition-colors hover:text-foreground ${location.pathname === "/profile" ? "text-foreground" : "text-muted-foreground"}`}
            >
              Profile
            </Link>
          </div>

          <div className="flex items-center gap-3">
            {isLoggedIn ? (
              <Link
                to="/profile"
                className="inline-flex h-9 items-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                Dashboard
              </Link>
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
