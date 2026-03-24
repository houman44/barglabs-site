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
            <a href="#safety" className="transition hover:text-white">Safety</a>
            <a href="#onboarding" className="transition hover:text-white">How I Work</a>
          </nav>

          <a
            href="mailto:team@barglabs.ai"
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
              I’m building Barg Labs around a simpler question:
            </p>

            <p className="text-white/90">
              How do you turn a trading idea into a live strategy without handing control to a black box?
            </p>

            <p>
              Barg Labs is not a generic AI tool or a retail trading platform. It is a system for running trading strategies in real markets with real execution, explicit risk controls, and hands-on oversight. The goal is simple: help people run strategies automatically, safely, and with clear control over what the system is allowed to do.
            </p>

            <p>
              The product is called <span className="font-semibold text-white">Egbert</span>.
            </p>
          </div>
        </motion.section>

        <Section id="background" title="Background">
          <p>
            I have spent more than 25 years working as a software engineer, building and operating complex software systems across multiple domains.
          </p>

          <p>
            Over the past several years my work has focused on what happens when software moves from analysis into action. That means less interest in demos and more interest in whether a system can behave predictably when it is live, exposed to real conditions, and responsible for real outcomes.
          </p>

          <p>
            Markets made that problem especially clear. Many products talk about intelligence or automation, but far fewer are designed to run strategies safely and reliably once money is actually at risk.
          </p>
        </Section>

        <Section id="why" title="Why Barg Labs">
          <p>
            Barg Labs emerged from a practical belief: if someone has a real trading idea, they should be able to turn it into a live strategy without stitching together a research stack, an execution engine, and a risk layer on their own.
          </p>

          <p>
            I’m building the system to do exactly that. A strategy can be defined clearly, deployed into real markets, and run automatically with risk controls, monitoring, and human review built in from the start.
          </p>

          <p>
            This is not a black box. It is designed so the user understands the rules, sees how the strategy behaves, and stays in control while the system handles execution and day-to-day operation.
          </p>
        </Section>

        <Section id="safety" title="Safety first">
          <p>
            Safety over profit is a product decision here, not a disclaimer added at the end. Every strategy is deployed with explicit risk limits, controlled exposure, and a kill switch before it is allowed to run.
          </p>

          <p>
            The system is designed to prevent blowups, not chase activity for its own sake. Position sizing, exposure boundaries, monitoring, and stop conditions exist so a strategy stays legible and bounded even when markets move unexpectedly.
          </p>

          <p>
            The user retains control at all times. Strategies can be reviewed, adjusted, paused, or shut down entirely, and nothing is treated as untouchable once it is live.
          </p>
        </Section>

        <motion.section id="systems" {...fade} className="mb-24 scroll-mt-24">
          <div className="mb-8 flex items-end justify-between gap-4">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Live today
            </h2>
            <p className="hidden text-sm text-white/45 md:block">Real execution before broad rollout.</p>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            <Surface>
              <p className="text-base leading-7 text-white/75 sm:text-lg">
                The system is live and running real strategies rather than sitting in a research environment. It is built for actual execution, monitoring, and controlled rollout.
              </p>
            </Surface>

            <Surface>
              <p className="text-base leading-7 text-white/75 sm:text-lg">
                It already supports multiple market workflows, with live work today in prediction markets and FX and a path to extend the same operating model across other markets.
              </p>
            </Surface>

            <Surface>
              <p className="text-base leading-7 text-white/75 sm:text-lg">
                Early users are already using it in collaboration with me, which means the product is being shaped by real deployment constraints, not hypothetical ones.
              </p>
            </Surface>
          </div>
        </motion.section>

        <motion.section id="onboarding" {...fade} className="mb-24 scroll-mt-24">
          <div className="mb-8 flex items-end justify-between gap-4">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              How I work with users
            </h2>
            <p className="hidden text-sm text-white/45 md:block">Hands-on onboarding, limited access.</p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Surface>
              <h3 className="text-lg font-semibold text-white">
                Manual onboarding
              </h3>
              <p className="mt-2 text-white/70">
                Early users are onboarded directly by me. We start small, define the strategy carefully, and set the limits before anything is allowed to run.
              </p>
            </Surface>

            <Surface>
              <h3 className="text-lg font-semibold text-white">
                Deployed together
              </h3>
              <p className="mt-2 text-white/70">
                I work with each user to turn an idea into a live strategy. We review the rules, the risk boundaries, and the expected behavior together so the system is understandable before it is automated.
              </p>
            </Surface>

            <Surface>
              <h3 className="text-lg font-semibold text-white">
                Iterative collaboration
              </h3>
              <p className="mt-2 text-white/70">
                After launch, we refine it collaboratively. We look at how it behaves in practice, tighten what needs tightening, and expand only when the system has earned more room.
              </p>
            </Surface>
          </div>
        </motion.section>

        <Section id="fit" title="Who this is for">
          <p>
            Barg Labs is for people who already have strategy ideas and want automation without losing control of how those ideas are expressed in the market.
          </p>

          <p>
            The best early users are willing to start small, work through the rules carefully, and improve the strategy through real feedback rather than trying to skip straight to full autonomy.
          </p>

          <p>
            If you want guided autopilot trading with clear boundaries and direct access to the person building the system, this is the right kind of fit.
          </p>
        </Section>

        <motion.section {...fade}>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-10 text-center shadow-[0_10px_30px_rgba(0,0,0,0.22)] sm:px-10">
            <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Working with a small number of users.
            </h2>

            <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-white/70 sm:text-lg">
              If this resonates, reach out. I’m onboarding a small number of users directly and working with them hands-on from strategy definition through live deployment and iteration.
            </p>

            <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <a
                href="mailto:team@barglabs.ai"
                className="inline-flex items-center rounded-full bg-white px-6 py-3 text-sm font-medium text-neutral-950 transition hover:bg-white/90"
              >
                Work with the founder
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
              <a
                href="https://egbert.io/app"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center rounded-full border border-white/20 bg-white/[0.06] px-6 py-3 text-sm font-medium text-white transition hover:border-white/30 hover:bg-white/[0.10]"
              >
                Create an Egbert account
                <ArrowRight className="ml-2 h-4 w-4" />
              </a>
            </div>
          </div>
        </motion.section>
      </main>
    </div>
  );
}
