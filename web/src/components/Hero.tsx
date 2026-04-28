import { motion } from "framer-motion";
import { ArrowRight, PlayCircle } from "lucide-react";

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
        <div className="eyebrow">Local-First Gesture Runtime</div>
        <h1>Turn a computer vision prototype into a product people can trust.</h1>
        <p>
          HandOS combines a native gesture engine with a polished presentation layer, giving you
          low-latency cursor control, privacy-first processing, and a credible product story.
        </p>
        <div className="hero-actions">
          <button className="primary-button" onClick={onGoToDemo}>
            View Demo
            <PlayCircle size={18} />
          </button>
          <a className="secondary-button" href="#installation">
            Install Runtime
            <ArrowRight size={18} />
          </a>
        </div>
        <div className="hero-meta">
          <span>`python -m handos --no-preview`</span>
          <span>Local processing only</span>
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
            <strong>On-device</strong>
            <span>Computer vision loop</span>
          </div>
          <div>
            <strong>Threaded</strong>
            <span>Capture and inference queues</span>
          </div>
          <div>
            <strong>Observable</strong>
            <span>Structured engine events</span>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
