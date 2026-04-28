import { motion } from "framer-motion";

export function DemoPage() {
  return (
    <section className="demo-page">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55 }}
      >
        <div className="eyebrow">Demo Surface</div>
        <h2>Show the interaction before people install the runtime.</h2>
        <p>
          These are the 2 core interactions of HandOS: cursor movement and pinch click. More complex gestures and visualizations can be added later, but this is the heart of the experience.
        </p>
      </motion.div>

      <div className="demo-grid">
        <article className="demo-card">
          <h3>Cursor Movement</h3>
          <img src="/demo.gif" alt="HandOS cursor movement demo" />
        </article>
        <article className="demo-card">
          <h3>Pinch Click</h3>
          <img src="/click_demo.gif" alt="HandOS pinch click demo" />
        </article>
      </div>

      {/*
      <div className="demo-notes">
        <div>
          <span className="eyebrow">Presentation angle</span>
          <p>Lead with privacy, low latency, and accessibility instead of calling the core runtime a SaaS.</p>
        </div>
        <div>
          <span className="eyebrow">Future extension</span>
          <p>Add a browser-only visualization mode here later if you want a lightweight shareable demo without OS control.</p>
        </div>
      </div>
       */}
    </section>
  );
}
