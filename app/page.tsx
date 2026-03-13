"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

const fade = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 },
  transition: { duration: 0.45 },
};

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <motion.section {...fade} className="mb-20">
      <h2 className="mb-6 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
        {title}
      </h2>
      <div className="space-y-4 text-base leading-8 text-white/70 sm:text-lg">
        {children}
      </div>
    </motion.section>
  );
}

function Surface({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.02)] backdrop-blur-sm">
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

      <header className="sticky top-0 z-50 border-b border-white/10 bg-neutral-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-5">
          <div>
            <div className="text-base font-semibold tracking-tight text-white">Barg Labs</div>
            <div className="text-xs uppercase tracking-[0.24em] text-white/40">Founder</div>
          </div>

          <a
            href="mailto:founder@barglabs.ai"
            className="inline-flex items-center rounded-full bg-white px-4 py-2 text-sm font-medium text-neutral-950 transition hover:bg-white/90"
          >
            Contact
          </a>
        </div>
      </header>

      <main className="relative mx-auto max-w-3xl px-6 py-20 sm:py-24">
        <motion.section {...fade} className="mb-24">
          <p className="text-sm uppercase tracking-[0.24em] text-emerald-200/80">
            Founder
          </p>

          <h1 className="mt-4 text-5xl font-semibold tracking-tight text-white sm:text-6xl">
            Building governed agentic systems for markets.
          </h1>

          <div className="mt-8 max-w-3xl space-y-5 text-lg leading-8 text-white/72">
            <p>
              I’m building Barg Labs to explore a question that feels increasingly important:
            </p>
            <p className="text-white/88">
              What does it look like for machines to operate inside markets responsibly?
            </p>
            <p>
              AI is rapidly expanding what parts of complex workflows can be automated. But most real-world systems — especially markets — still lack the infrastructure required to safely operate autonomous systems.
            </p>
          </div>
        </motion.section>

        <Section title="The problem">
          <p>
            Today, most AI trading systems fall into one of three categories:
          </p>
          <ul className="space-y-3 pl-5 text-white/70 marker:text-white/40 list-disc">
            <li>Black-box models with little operational control</li>
            <li>Research pipelines disconnected from execution</li>
            <li>Automation systems without governance or safety layers</li>
          </ul>
          <p>
            Markets require something different: systems that can act autonomously, but only within explicit rules, policies, and risk boundaries.
          </p>
        </Section>

        <Section title="What I’m building">
          <p>
            Barg Labs is focused on building infrastructure for governed agentic systems in markets.
          </p>
          <p>
            Instead of chasing fully autonomous trading agents, the focus is on building runtimes that allow machines to participate in markets inside strict operational guardrails.
          </p>
          <p>
            Think of it as a control plane for machine-assisted market operations.
          </p>
        </Section>

        <motion.section {...fade} className="mb-20">
          <h2 className="mb-6 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
            What exists today
          </h2>

          <div className="space-y-5">
            <Surface>
              <p className="text-base leading-7 text-white/70 sm:text-lg">
                A live-capable prediction market runtime with ingestion, evaluation,
                sizing logic, execution, monitoring, and rollout systems.
              </p>
            </Surface>

            <Surface>
              <p className="text-base leading-7 text-white/70 sm:text-lg">
                A second FX runtime with signal generation, Kelly sizing, and execution infrastructure.
              </p>
            </Surface>

            <Surface>
              <p className="text-base leading-7 text-white/70 sm:text-lg">
                Canary rollout systems, shadow evaluation paths, monitoring, reconciliation, and rollback infrastructure.
              </p>
            </Surface>
          </div>
        </motion.section>

        <Section title="Current focus">
          <p>
            The initial wedge is prediction markets — a rapidly growing market category that still lacks mature operational infrastructure.
          </p>
          <p>
            The immediate goal is disciplined validation: proving a narrow strategy path under real conditions using strict risk boundaries and controlled rollouts.
          </p>
        </Section>

        <motion.section {...fade}>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-10 text-center sm:px-10">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Building quietly.
            </h2>

            <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-white/70 sm:text-lg">
              If you&apos;re interested in the ideas behind Barg Labs or want to follow the work, feel free to reach out.
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

