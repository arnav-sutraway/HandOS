type NavbarProps = {
  page: "home" | "demo";
  onNavigate: (page: "home" | "demo") => void;
};

export function Navbar({ page, onNavigate }: NavbarProps) {
  return (
    <header className="navbar">
      <button className="brand" onClick={() => onNavigate("home")}>
        <span className="brand-mark">H</span>
        <div>
          <strong>HandOS</strong>
          <span>Gesture Engine</span>
        </div>
      </button>
      <nav>
        <a href="#features">Overview</a>
        <a href="#goals">Goals</a>
        <a href="#architecture">Architecture</a>
        <a href="#cli">CLI</a>
        <a href="#installation">Install</a>
      </nav>
      <div className="nav-actions">
        <button
          className={page === "home" ? "nav-button active" : "nav-button"}
          onClick={() => onNavigate("home")}
        >
          Home
        </button>
        <button
          className={page === "demo" ? "nav-button active" : "nav-button"}
          onClick={() => onNavigate("demo")}
        >
          Demo
        </button>
      </div>
    </header>
  );
}
