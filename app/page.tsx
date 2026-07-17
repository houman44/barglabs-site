"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowUpRight, Moon, Sun } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

const fade = {
  initial: { opacity: 0, y: 14 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.18 },
  transition: { duration: 0.42 },
};

const navItems = [
  ["Products", "#products"],
  ["Story", "#story"],
  ["Approach", "#approach"],
  ["Leadership", "#leadership"],
  ["Cejel", "#cejel"],
  ["Alfred", "#alfred"],
  ["Egbert", "#egbert"],
  ["Therasyn", "#therasyn"],
] as const;

type Product = {
  name: string;
  title: string;
  icon?: string;
  href?: string;
  displayUrl?: string;
  body: string;
};

const products: Product[] = [
  {
    name: "Cejel",
    title: "The evidence-backed trust certificate for code",
    icon: "/cejel-sun-wheel.png",
    body: "A deterministic, offline code-trust scorer that checks the observable engineering signals behind a repository — test integrity, secret hygiene, dependency discipline, isolation, CI, auditability, and whether the code matches its claims. It emits an evidence-backed certificate and report, incorporates SARIF and OpenSSF Scorecard results, and abstains when the source is too thin to assess responsibly.",
  },
  {
    name: "Alfred",
    title: "The company brain that executes — through governed, human-approved actions",
    href: "https://alfred.barglabs.ai",
    displayUrl: "alfred.barglabs.ai",
    body: "The operator OS that runs a studio — or a whole portfolio — on AI, safely: hard isolation between products, governed execution that proposes but never ships on its own, verified memory, and a trust certificate for everything the AI builds. Cloud or fully on-prem.",
  },
  {
    name: "Egbert",
    title: "B2B Fintech 3.0 infrastructure for validating strategies and moving them into governed execution",
    href: "https://egbert.io",
    displayUrl: "egbert.io",
    body: "The governance, provenance, and attestation layer for autonomous systematic trading. Firms bring their strategies and brokers; Egbert adds paper-first validation, explicit risk gates, broker-reconciled execution, kill switches, attribution, and an exportable Strategy Trust Certificate — without becoming the broker, custodian, or source of alpha.",
  },
  {
    name: "Therasyn",
    title: "Governance and on-prem deployment infrastructure for clinical AI",
    href: "https://therasyn.ai",
    displayUrl: "therasyn.ai",
    body: "Governance and deployment infrastructure for clinical AI in environments where cloud-only isn't an option — academic medical centres, regulated health systems, and pharma research. BAA-bound by design, on-prem capable from day one. Built so health systems can run AI inside their own perimeter, with audit, PHI controls, and required sign-off enforced by construction.",
  },
];

function ThemeToggle() {
  function toggleTheme() {
    const currentTheme = document.documentElement.dataset.theme ?? "dark";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";

    document.documentElement.dataset.theme = nextTheme;
    try {
      window.localStorage.setItem("barg-theme", nextTheme);
    } catch {
      // The theme still changes for this visit when storage is unavailable.
    }
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="theme-toggle inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-medium transition"
      aria-label="Toggle light and dark mode"
      title="Toggle light and dark mode"
    >
      <Sun className="theme-icon-light h-4 w-4" aria-hidden="true" />
      <Moon className="theme-icon-dark h-4 w-4" aria-hidden="true" />
      <span className="hidden sm:inline">
        <span className="theme-label-light">Light</span>
        <span className="theme-label-dark">Dark</span>
      </span>
    </button>
  );
}

function Section({
  id,
  title,
  children,
  logo,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
  logo?: React.ReactNode;
}) {
  return (
    <motion.section id={id} {...fade} className="scroll-mt-28 py-14 sm:py-18">
      <div className="mb-7 flex items-center gap-4">
        {logo ?? <div className="theme-line h-px w-10" />}
        <h2 className="theme-text text-2xl font-semibold tracking-tight sm:text-3xl">
          {title}
        </h2>
      </div>
      <div className="theme-copy space-y-5 text-base leading-8 sm:text-lg">
        {children}
      </div>
    </motion.section>
  );
}

function ProductCard({ product }: { product: Product }) {
  return (
    <article className="theme-border theme-surface flex h-full flex-col rounded-lg border p-5">
      <div className="flex min-h-14 items-start justify-between gap-4">
        <div className="theme-kicker pt-1 text-sm font-medium uppercase tracking-[0.2em]">
          {product.name}
        </div>
        {product.icon ? (
          <Image
            src={product.icon}
            alt=""
            width={56}
            height={56}
            className="h-14 w-14 object-contain"
          />
        ) : null}
      </div>
      <h3 className="theme-text mt-3 text-xl font-semibold leading-7">
        {product.title}
      </h3>
      {product.href ? (
        <a
          href={product.href}
          className="theme-link mt-3 inline-flex w-fit items-center gap-1.5 text-sm font-medium transition"
        >
          {product.displayUrl}
          <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
        </a>
      ) : null}
      <p className="theme-copy-soft mt-5 text-sm leading-7">{product.body}</p>
    </article>
  );
}

function ProductSection({
  id,
  title,
  children,
  href,
  logo,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
  href?: string;
  logo?: React.ReactNode;
}) {
  return (
    <Section id={id} title={title} logo={logo}>
      {children}
      {href ? (
        <p>
          <a
            href={href}
            className="theme-link inline-flex items-center gap-2 font-medium transition"
          >
            {href.replace("https://", "")}
            <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
          </a>
        </p>
      ) : null}
    </Section>
  );
}

export default function Page() {
  return (
    <div className="theme-page min-h-screen transition-colors duration-300">
      <header className="theme-border theme-header sticky top-0 z-50 border-b backdrop-blur-xl transition-colors duration-300">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-5 px-5 py-4 sm:px-6">
          <a href="#" className="flex items-center gap-3" aria-label="Barg Labs home">
            <Image
              src="/barg-icon-mark.png"
              alt=""
              width={34}
              height={34}
              className="rounded-md"
              priority
            />
            <div>
              <div className="theme-text text-sm font-semibold tracking-tight">
                Barg Labs
              </div>
              <div className="theme-copy-subtle text-[11px] uppercase tracking-[0.22em]">
                Consequential AI
              </div>
            </div>
          </a>

          <nav className="theme-nav hidden items-center gap-5 text-sm lg:flex">
            {navItems.map(([label, href]) => (
              <a key={href} href={href} className="transition">
                {label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <ThemeToggle />
            <a
              href="mailto:team@barglabs.ai"
              className="theme-primary rounded-md px-4 py-2 text-sm font-medium transition"
            >
              Contact
            </a>
          </div>
        </div>
      </header>

      <main>
        <section className="theme-border border-b">
          <div className="mx-auto grid min-h-[calc(100vh-73px)] max-w-6xl content-center gap-12 px-5 py-16 sm:px-6 lg:grid-cols-[1fr_360px] lg:py-20">
            <motion.div {...fade} className="max-w-3xl">
              <div className="theme-kicker mb-7 inline-flex items-center gap-3 text-xs font-medium uppercase tracking-[0.24em]">
                <span className="theme-accent-line h-px w-8" />
                Barg Labs · Evidence before action.
              </div>

              <h1 className="theme-text max-w-4xl text-5xl font-semibold tracking-tight sm:text-6xl lg:text-7xl">
                Built for consequential AI.
              </h1>

              <div className="theme-copy-strong mt-8 max-w-2xl space-y-5 text-lg leading-8">
                <p>
                  Evidence, governance, and execution infrastructure for AI
                  operating in code, companies, markets, and clinical systems.
                </p>
              </div>
            </motion.div>

            <motion.div
              {...fade}
              className="theme-border theme-surface self-end rounded-lg border p-5"
            >
              <Image
                src="/barg-icon-mark.png"
                alt="Barg Labs"
                width={92}
                height={92}
                className="rounded-lg"
                priority
              />
              <p className="theme-copy-soft mt-6 text-sm leading-7">
                Evidence before action. Trust is designed into every product,
                workflow, and deployment boundary.
              </p>
            </motion.div>
          </div>
        </section>

        <div className="mx-auto max-w-6xl px-5 sm:px-6">
          <motion.section id="products" {...fade} className="scroll-mt-28 py-14 sm:py-18">
            <div className="mb-8 flex items-end justify-between gap-6">
              <div>
                <div className="theme-line mb-4 h-px w-10" />
                <h2 className="theme-text text-2xl font-semibold tracking-tight sm:text-3xl">
                  Products
                </h2>
              </div>
              <p className="theme-copy-subtle hidden max-w-md text-sm leading-6 md:block">
                Four focused surfaces, each built around a concrete operating
                environment.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {products.map((product) => (
                <ProductCard key={product.name} product={product} />
              ))}
            </div>
          </motion.section>

          <motion.section id="story" {...fade} className="scroll-mt-28 py-14 sm:py-18">
            <Card className="theme-border overflow-hidden py-0 shadow-none">
              <CardContent className="grid p-0 lg:grid-cols-[0.72fr_1.28fr]">
                <div className="theme-border border-b p-6 sm:p-8 lg:border-r lg:border-b-0">
                  <div className="theme-kicker text-xs font-medium uppercase tracking-[0.22em]">
                    Our story
                  </div>
                  <h2 className="theme-text mt-5 max-w-sm text-3xl font-semibold tracking-tight sm:text-4xl">
                    One thesis, unfolding across four products.
                  </h2>
                  <p className="theme-copy-subtle mt-8 text-sm font-medium uppercase tracking-[0.18em]">
                    Evidence before action.
                  </p>
                </div>

                <div className="theme-copy space-y-5 p-6 text-base leading-8 sm:p-8 sm:text-lg">
                  <p>
                    We began Barg Labs by building a systematic trading
                    application. Markets made the requirements unusually clear:
                    every decision needed evidence, every action needed
                    attribution, and risk had to remain under explicit human
                    control.
                  </p>
                  <p className="theme-text text-xl font-medium leading-8 sm:text-2xl">
                    We discovered that the hardest problem was not making AI more
                    capable. It was making AI trustworthy enough to act.
                  </p>
                  <p>
                    That insight became the foundation of Barg Labs. Egbert
                    applies it to systematic trading. Cejel verifies the code AI
                    produces. Alfred governs AI execution across a company.
                    Therasyn brings the same controls to clinical environments
                    where data, deployment, and accountability cannot be
                    compromised.
                  </p>
                  <p>
                    Today, Barg Labs builds infrastructure for consequential AI —
                    systems whose actions matter and therefore must be observable,
                    governed, and verifiable.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          <Section id="approach" title="Approach">
            <p>
              Barg Labs builds infrastructure for consequential AI around real
              operating constraints: who is using the system, where the data
              lives, what has to be reviewed, and what must remain under human
              control.
            </p>
            <p>
              The work is evidence-led rather than demo-led. Across code,
              companies, markets, and clinical systems, AI actions should be
              observable, governed, attributable, and verifiable before they are
              trusted.
            </p>
          </Section>

          <Section id="leadership" title="Leadership">
            <p>
              Barg Labs is led by Houman Azimi-Nejadi, a software engineer and
              founder with more than 25 years of experience building complex
              software systems across multiple domains.
            </p>
            <p>
              The company works closely with expert collaborators across product,
              clinical, market, and web systems as each product line moves from
              focused surface to live deployment.
            </p>
          </Section>

          <ProductSection
            id="cejel"
            title="Cejel"
            logo={
              <Image
                src="/cejel-sun-wheel.png"
                alt="Cejel"
                width={48}
                height={48}
                className="h-12 w-12 object-contain"
              />
            }
          >
            <p>
              Cejel is a deterministic, offline trust certificate for code. It
              examines the observable engineering signals behind a repository —
              test integrity, secret hygiene, dependency discipline, isolation,
              CI, auditability, and whether the code matches its claims — then
              produces an evidence-backed certificate and report.
            </p>
            <p>
              Cejel complements the scanners teams already use. It can incorporate
              SARIF output and OpenSSF Scorecard results into one portable view,
              with contributing evidence clearly attributed. When a repository is
              unreadable or the available source is too thin, Cejel abstains
              instead of presenting a misleading score.
            </p>
            <p>
              It runs fully offline with no signup, telemetry, or model call,
              making it useful for AI-written code, acquisitions, inherited
              systems, and regulated environments where the source cannot leave
              the team's perimeter.
            </p>
          </ProductSection>

          <ProductSection
            id="alfred"
            title="Alfred"
            href="https://alfred.barglabs.ai"
          >
            <p>
              Alfred is the company brain that executes — the operator OS that
              runs a company, or a whole portfolio, on AI, safely. As agents do
              more of the building and operating, the blocker is trust; Alfred is
              the layer that makes it safe.
            </p>
            <p>
              It runs on hard per-product isolation (one product's secrets never
              touch another's), governed execution (agents open reviewed changes
              and run operations but never merge, deploy, or leak, with a full
              audit trail), and verified memory that only trusts what a real
              outcome proved. Cejel, its trust certificate, verifies what the AI
              builds before it ships.
            </p>
            <p>
              Cloud or fully on-prem — including on a local model — so a regulated
              studio can run everything inside its own walls.
            </p>
            <p>
              Live operator surface available at{" "}
              <a
                href="https://alfred.barglabs.ai"
                className="theme-link font-medium transition"
              >
                alfred.barglabs.ai
              </a>
              .
            </p>
          </ProductSection>

          <ProductSection
            id="egbert"
            title="Egbert"
            href="https://egbert.io"
          >
            <p>
              Egbert is the governance, provenance, and attestation layer for
              autonomous systematic trading. Firms bring their strategies and
              brokers; Egbert provides the deployment, risk, execution, and
              analytics discipline they would otherwise have to build internally.
            </p>
            <p>
              Strategies move through walk-forward evidence, paper deployment,
              explicit risk gates, and governed promotion review. Every machine
              decision carries its signal origin, execution state, kill-switch
              scope, and broker-reconciled outcome in an append-only audit trail.
            </p>
            <p>
              The result is an exportable Strategy Trust Certificate for allocator
              diligence and governance review. Customer-hosted and on-prem
              deployment are available for qualified engagements; live-certified
              execution is currently FX-only, while CFD remains shadow and paper.
            </p>
          </ProductSection>

          <ProductSection id="therasyn" title="Therasyn" href="https://therasyn.ai">
            <p>
              Therasyn is governance and on-prem infrastructure for clinical AI
              in environments where cloud-only isn't viable - academic medical
              centres, hospital systems, pharma clinical research, and any
              setting bound by BAA + state law + sovereign-data requirements.
            </p>
            <p>
              It is BAA-bound and on-prem capable from day one. Health systems
              run AI inside their own perimeter - with audit trails, PHI
              controls, and required sign-off enforced by construction - over
              multimodal clinical records (genomics, pathology, radiology,
              notes), without that data ever leaving the institution.
            </p>
            <p>
              For Therasyn the binding constraint is never "does the technology
              work" - it is "can the technology live where the data has to
              live." Therasyn is built for exactly that constraint.
            </p>
          </ProductSection>

          <motion.section {...fade} className="py-14 sm:py-18">
            <div className="theme-border theme-surface rounded-lg border px-6 py-9 text-center sm:px-10">
              <h2 className="theme-text text-2xl font-semibold tracking-tight sm:text-3xl">
                Contact Barg Labs
              </h2>
              <p className="theme-copy-soft mx-auto mt-4 max-w-2xl text-base leading-7">
                For product conversations, partnerships, or early access,
                contact the team directly.
              </p>
              <a
                href="mailto:team@barglabs.ai"
                className="theme-primary mt-7 inline-flex items-center gap-2 rounded-md px-5 py-3 text-sm font-medium transition"
              >
                team@barglabs.ai
                <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
              </a>
            </div>
          </motion.section>
        </div>
      </main>
    </div>
  );
}
