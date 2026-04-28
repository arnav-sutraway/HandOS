import { motion } from "framer-motion";

const nodes = [
  { title: "Camera Thread", detail: "Bounded frame queue" },
  { title: "Vision Thread", detail: "MediaPipe inference" },
  { title: "Gesture Engine", detail: "Kalman, dead-zone, pinch state" },
  { title: "CLI / GUI", detail: "Preview, settings, orchestration" },
];

export function ArchitectureDiagram() {
  return (
    <motion.div
      className="architecture-grid"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.55 }}
    >
      {nodes.map((node, index) => (
        <div className="architecture-node" key={node.title}>
          <span className="architecture-index">0{index + 1}</span>
          <h3>{node.title}</h3>
          <p>{node.detail}</p>
        </div>
      ))}
    </motion.div>
  );
}
