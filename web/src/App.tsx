import { useState } from "react";
import { Footer } from "./components/Footer";
import { Navbar } from "./components/Navbar";
import { DemoPage } from "./pages/DemoPage";
import { HomePage } from "./pages/HomePage";

export function App() {
  const [page, setPage] = useState<"home" | "demo">("home");

  return (
    <div className="app-shell">
      <div className="ambient ambient-left" />
      <div className="ambient ambient-right" />
      <Navbar page={page} onNavigate={setPage} />
      <main>{page === "home" ? <HomePage onGoToDemo={() => setPage("demo")} /> : <DemoPage />}</main>
      <Footer />
    </div>
  );
}
