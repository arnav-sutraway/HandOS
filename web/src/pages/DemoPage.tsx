import { motion } from "framer-motion";

export function DemoPage() {
  const base = import.meta.env.BASE_URL;

  return (
    <section className="demo-page">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55 }}
      >
        <div className="eyebrow">Demo</div>
        <h2>See the runtime behavior and core gestures.</h2>
        <p>
          HandOS currently focuses on two core interactions: cursor movement from index fingertip
          tracking and click input from a pinch gesture.
        </p>
      </motion.div>

      <div className="demo-grid">
        <article className="demo-card">
          <h3>Runtime Demo</h3>
          <video
            className="demo-media"
            controls
            muted
            loop
            playsInline
            preload="metadata"
            poster={`${base}handpic.png`}
          >
            <source src={`${base}demo.mp4`} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </article>
        <article className="demo-card">
          <h3>Pinch Click</h3>
          <img className="demo-media" src={`${base}click_demo.gif`} alt="HandOS pinch click demo" />
        </article>
      </div>

      <div className="demo-notes">
        <div>
          <span className="eyebrow">Cursor Control</span>
          <p>The cursor follows tracked hand motion after screen mapping, smoothing, and dead-zone suppression.</p>
        </div>
        <div>
          <span className="eyebrow">Click Gesture</span>
          <p>Clicks are triggered from a pinch state machine designed to reduce accidental activation and improve control stability.</p>
        </div>
      </div>
    </section>
  );
}
