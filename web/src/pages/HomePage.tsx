import { Camera, Cpu, Gauge, MonitorSmartphone, ShieldCheck, Workflow } from "lucide-react";
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
        eyebrow="Overview"
        title="A local-first desktop gesture control system."
        description="HandOS turns webcam hand tracking into desktop cursor movement and click input with a runtime designed for low latency, privacy, and direct OS control."
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
            title="Clear Controls"
            description="The project includes demo media, CLI usage, installation steps, and a cleaner structure for building a future desktop interface."
          />
        </div>
      </Layout>

      <Layout
        id="goals"
        eyebrow="Core Capabilities"
        title="What HandOS does."
        description="The system captures webcam frames, detects hand landmarks, smooths cursor motion, and recognizes pinch gestures for click input."
      >
        <div className="feature-grid">
          <FeatureCard
            icon={<Camera size={22} />}
            title="Hand Tracking"
            description="MediaPipe landmarks are used to detect a hand in real time and follow fingertip movement across the frame."
          />
          <FeatureCard
            icon={<Workflow size={22} />}
            title="Cursor Mapping"
            description="Index fingertip coordinates are converted into screen coordinates and passed through smoothing before pointer movement."
          />
          <FeatureCard
            icon={<ShieldCheck size={22} />}
            title="Pinch Click"
            description="Thumb and index finger distance is normalized against hand size so pinch gestures can trigger more reliable click input."
          />
          <FeatureCard
            icon={<Gauge size={22} />}
            title="Native Runtime"
            description="All processing happens on-device, which keeps camera data local and avoids the latency of a browser-only control model."
          />
        </div>
      </Layout>

      <Layout
        id="architecture"
        eyebrow="System Design"
        title="Threaded architecture with a reusable engine boundary."
        description="The runtime separates camera capture, vision inference, gesture processing, and UI-facing state so the system stays responsive and easier to extend."
      >
        <ArchitectureDiagram />
      </Layout>

      <Layout
        id="cli"
        eyebrow="CLI Reference"
        title="Run and tune the runtime from the command line."
        description="Camera selection, preview mode, smoothing, and pinch behavior can be adjusted directly from the CLI."
      >
        <CLIReference />
      </Layout>

      <Layout
        id="installation"
        eyebrow="Install"
        title="From clone to local runtime in minutes."
        description="Install the dependencies, start the runtime, and use a webcam to control the cursor with your hand."
      >
        <InstallationSteps />
      </Layout>
    </>
  );
}
