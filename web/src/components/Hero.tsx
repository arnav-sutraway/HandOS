import { motion } from "framer-motion";
import { ArrowRight, Github, PlayCircle } from "lucide-react";

type HeroProps = {
  onGoToDemo: () => void;
};

export function Hero({ onGoToDemo }: HeroProps) {
  return (
    <section className="hero">
      <motion.div
        className="hero-copy"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        <div className="eyebrow">Hand Gesture Control</div>
        <h1>Control your cursor with hand movement and click with a pinch gesture.</h1>
        <p>
          HandOS uses on-device computer vision to track a hand from a webcam, map fingertip
          movement to the desktop cursor, and trigger clicks from a pinch gesture.
        </p>
        <div className="hero-actions">
          <button className="primary-button" onClick={onGoToDemo}>
            View Demo
            <PlayCircle size={18} />
          </button>
          <a
            className="secondary-button"
            href="https://github.com/arnav-sutraway/HandOS"
            target="_blank"
            rel="noreferrer"
          >
            View GitHub
            <Github size={18} />
          </a>
          <a className="secondary-button" href="#installation">
            Run Locally
            <ArrowRight size={18} />
          </a>
        </div>
        <div className="hero-meta">
          <span>`python -m handos --no-preview`</span>
          <span>On-device tracking</span>
          <span>Pinch-to-click</span>
          <span>Engine/UI separation</span>
        </div>
      </motion.div>

      <motion.div
        className="hero-panel"
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, delay: 0.1 }}
      >
        <div className="panel-glow" />
        <div className="terminal-card">
          <div className="terminal-bar">
            <span />
            <span />
            <span />
          </div>
          <div className="terminal-body">
            <p>$ handos start --profile calibrated</p>
            <p>&gt; engine.started camera=0</p>
            <p>&gt; gesture.hand_detected handedness=Right</p>
            <p>&gt; gesture.click_triggered status=CLICK</p>
            <p>&gt; fps=29.8 latency_ms=38</p>
          </div>
        </div>
        <div className="hero-stats">
          <div>
            <strong>Local-first</strong>
            <span>On-device camera processing</span>
          </div>
          <div>
            <strong>Threaded</strong>
            <span>Capture, vision, and control loop</span>
          </div>
          <div>
            <strong>Gesture-driven</strong>
            <span>Cursor movement and click input</span>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
