import { Cpu, Gauge, MonitorSmartphone, ShieldCheck } from "lucide-react";
import { ArchitectureDiagram } from "../components/ArchitectureDiagram";
import { CLIReference } from "../components/CLIReference";
import { FeatureCard } from "../components/FeatureCard";
import { Hero } from "../components/Hero";
import { InstallationSteps } from "../components/InstallationSteps";
import { Layout } from "../components/Layout";

type HomePageProps = {
  onGoToDemo: () => void;
};

export function HomePage({ onGoToDemo }: HomePageProps) {
  return (
    <>
      <Hero onGoToDemo={onGoToDemo} />

      <Layout
        id="features"
        eyebrow="Why It Feels Real"
        title="Built like a product, not just a prototype."
        description="The runtime stays native and low-latency while the interface explains the system with product-level clarity."
      >
        <div className="feature-grid">
          <FeatureCard
            icon={<Cpu size={22} />}
            title="Separated Engine"
            description="Camera capture, inference, gesture state, and pointer control now live behind a reusable engine boundary."
          />
          <FeatureCard
            icon={<Gauge size={22} />}
            title="Observable Runtime"
            description="Structured engine events make diagnostics, future desktop GUIs, and test harnesses much easier to build."
          />
          <FeatureCard
            icon={<ShieldCheck size={22} />}
            title="Local-First Privacy"
            description="The core hand tracking loop runs on-device, which is the right tradeoff for camera trust and interaction latency."
          />
          <FeatureCard
            icon={<MonitorSmartphone size={22} />}
            title="Professional Presentation"
            description="The product surface now has a polished landing page, CLI reference, and demo page for showcasing the work."
          />
        </div>
      </Layout>

      <Layout
        id="architecture"
        eyebrow="System Design"
        title="Threaded architecture with a cleaner boundary."
        description="The engine exposes snapshots and events so the CLI, future desktop UI, and tests can all use the same runtime."
      >
        <ArchitectureDiagram />
      </Layout>

      <Layout
        id="cli"
        eyebrow="CLI Reference"
        title="A concise interface for operators and developers."
        description="Keeping the CLI sharp still matters because it is the fastest way to test runtime changes and showcase engineering depth."
      >
        <CLIReference />
      </Layout>

      <Layout
        id="installation"
        eyebrow="Install"
        title="From clone to runtime in minutes."
        description="These are the commands you would surface on the landing page or in docs while the native installer is still in progress."
      >
        <InstallationSteps />
      </Layout>
    </>
  );
}
