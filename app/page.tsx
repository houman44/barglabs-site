"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

const fade = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 },
  transition: { duration: 0.45 },
};

function Section({ title, children, id }: { title: string; children: React.ReactNode; id?: string }) {
  return (
    <motion.section id={id} {...fade} className="mb-24 scroll-mt-24">
      <h2 className="mb-6 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
        {title}
      </h2>
      <div className="space-y-5 text-base leading-8 text-white/70 sm:text-lg">
        {children}
      </div>
    </motion.section>
  );
}

function Surface({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 shadow-[0_10px_30px_rgba(0,0,0,0.22)] backdrop-blur-sm transition duration-300 hover:-translate-y-1 hover:border-white/15 hover:bg-white/[0.06]">
      {children}
    </div>
  );
}

export default function Page() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-[-8rem] top-[-4rem] h-72 w-72 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute right-[-8rem] top-[20%] h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute bottom-[-6rem] left-[35%] h-72 w-72 rounded-full bg-orange-500/10 blur-3xl" />
      </div>

      <header className="sticky top-0 z-50 border-b border-white/10 bg-neutral-950/70 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <div>
            <div className="text-base font-semibold tracking-tight text-white">Barg Labs</div>
            <div className="text-xs uppercase tracking-[0.24em] text-white/40">Founder</div>
          </div>

          <nav className="hidden items-center gap-6 text-sm text-white/60 md:flex">
            <a href="#background" className="transition hover:text-white">Background</a>
            <a href="#why" className="transition hover:text-white">Why Barg Labs</a>
            <a href="#systems" className="transition hover:text-white">Systems</a>
            <a href="#notes" className="transition hover:text-white">Notes</a>
          </nav>

          <a
            href="mailto:founder@barglabs.ai"
            className="inline-flex items-center rounded-full bg-white px-4 py-2 text-sm font-medium text-neutral-950 transition hover:bg-white/90"
          >
            Contact
          </a>
        </div>
      </header>

      <main className="relative mx-auto max-w-4xl px-6 py-20 sm:py-24">
        <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_at_center,black_38%,transparent_78%)]" />

        <motion.section {...fade} className="mb-24">
          <div className="inline-flex rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs uppercase tracking-[0.22em] text-emerald-200/80 shadow-sm shadow-black/20">
            Founder
          </div>

          <h1 className="mt-6 text-5xl font-semibold tracking-tight text-white sm:text-6xl">
            Houman Azimi-Nejadi
          </h1>

          <p className="mt-3 text-lg text-white/60">
            Founder, Barg Labs
          </p>

          <div className="mt-8 max-w-3xl space-y-5 text-lg leading-8 text-white/75">
            <p>
              I’m building Barg Labs to explore a question that feels increasingly important:
            </p>

            <p className="text-white/90">
              What does it look like for machines to operate inside markets responsibly?
            </p>

            <p>
              Artificial intelligence is rapidly expanding what parts of complex workflows can be automated. But most real-world systems — especially markets — still lack the infrastructure required to safely operate autonomous systems.
            </p>
          </div>
        </motion.section>

        <Section id="background" title="Background">
          <p>
            I have spent more than 25 years working as a software engineer, building and operating complex software systems across multiple domains.
          </p>

          <p>
            Over the past several years my work has increasingly focused on artificial intelligence and machine learning. I completed professional certification in AI and ML through Imperial College London and have been exploring how these technologies behave in real-world operational systems rather than purely research environments.
          </p>

          <p>
            Through this work I became increasingly skeptical of much of the narrative around AI trading. Many systems marketed as AI-driven trading rely on thin abstractions, opaque models, or automation without meaningful operational discipline.
          </p>
        </Section>

        <Section id="why" title="Why Barg Labs">
          <p>
            Barg Labs emerged from the belief that the next generation of intelligent systems in markets will require more than better models.
          </p>

          <p>
            They will require infrastructure — systems that allow machine reasoning and automation to operate inside explicit risk boundaries, operational controls, and observable workflows.
          </p>

          <p>
            Instead of pursuing full autonomy, the focus is on <strong>governed agentic systems</strong> — systems that can reason, act, and adapt while remaining auditable, controllable, and constrained by policy.
          </p>
        </Section>

        <motion.section id="systems" {...fade} className="mb-24 scroll-mt-24">
          <div className="mb-8 flex items-end justify-between gap-4">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Systems built so far
            </h2>
            <p className="hidden text-sm text-white/45 md:block">Operational proof before scale.</p>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            <Surface>
              <p className="text-base leading-7 text-white/75 sm:text-lg">
                A live-capable prediction market runtime supporting ingestion, evaluation, sizing logic, execution, monitoring, and rollout systems.
              </p>
            </Surface>

            <Surface>
              <p className="text-base leading-7 text-white/75 sm:text-lg">
                A second FX runtime with signal generation, Kelly sizing logic, and execution infrastructure.
              </p>
            </Surface>

            <Surface>
              <p className="text-base leading-7 text-white/75 sm:text-lg">
                Operational infrastructure including canary deployments, shadow evaluation paths, monitoring systems, and rollback controls.
              </p>
            </Surface>
          </div>
        </motion.section>

        <motion.section id="notes" {...fade} className="mb-24 scroll-mt-24">
          <div className="mb-8 flex items-end justify-between gap-4">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Notes from the lab
            </h2>
            <p className="hidden text-sm text-white/45 md:block">Early essays and working ideas.</p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Surface>
              <h3 className="text-lg font-semibold text-white">
                Why most AI trading systems fail
              </h3>
              <p className="mt-2 text-white/70">
                Many systems described as AI trading platforms are primarily research pipelines connected to execution engines. Without governance layers, monitoring, and operational discipline, intelligent systems quickly become difficult to trust in real market environments.
              </p>
            </Surface>

            <Surface>
              <h3 className="text-lg font-semibold text-white">
                Markets need governed agents
              </h3>
              <p className="mt-2 text-white/70">
                Intelligent agents operating in markets must function within clear policy boundaries. The future likely belongs not to unconstrained autonomy but to systems that balance reasoning ability with explicit operational control.
              </p>
            </Surface>

            <Surface>
              <h3 className="text-lg font-semibold text-white">
                Prediction markets as proving grounds
              </h3>
              <p className="mt-2 text-white/70">
                Prediction markets provide a unique environment for testing machine-assisted decision systems: clear outcomes, probabilistic signals, and real incentives. They represent a natural early wedge for exploring governed agentic systems.
              </p>
            </Surface>
          </div>
        </motion.section>

        <motion.section {...fade}>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-10 text-center shadow-[0_10px_30px_rgba(0,0,0,0.22)] sm:px-10">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Building quietly.
            </h2>

            <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-white/70 sm:text-lg">
              If you're interested in the ideas behind Barg Labs or would like to follow the work, feel free to reach out.
            </p>

            <div className="mt-8">
              <a
                href="mailto:founder@barglabs.ai"
                className="inline-flex items-center rounded-full bg-white px-6 py-3 text-sm font-medium text-neutral-950 transition hover:bg-white/90"
              >
                Contact the founder
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </div>
          </div>
        </motion.section>
      </main>
    </div>
  );
}

