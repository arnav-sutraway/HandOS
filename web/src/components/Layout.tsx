import { ReactNode } from "react";
import { motion } from "framer-motion";

type LayoutProps = {
  eyebrow?: string;
  title: string;
  description: string;
  children: ReactNode;
  id?: string;
};

export function Layout({ eyebrow, title, description, children, id }: LayoutProps) {
  return (
    <section className="section" id={id}>
      <motion.div
        className="section-header"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.55 }}
      >
        {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
        <h2>{title}</h2>
        <p>{description}</p>
      </motion.div>
      {children}
    </section>
  );
}
