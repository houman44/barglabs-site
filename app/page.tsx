"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";

const fade = {
  initial: { opacity: 0, y: 14 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.18 },
  transition: { duration: 0.42 },
};

const navItems = [
  ["Products", "#products"],
  ["Approach", "#approach"],
  ["Leadership", "#leadership"],
  ["Alfred", "#alfred"],
  ["Cejel", "#cejel"],
  ["Egbert", "#egbert"],
  ["Therasyn", "#therasyn"],
] as const;

type Product = {
  name: string;
  title: string;
  href?: string;
  displayUrl?: string;
  body: string;
};

const products: Product[] = [
  {
    name: "Alfred",
    title: "Operator OS for AI-native studios",
    href: "https://alfred.barglabs.ai",
    displayUrl: "alfred.barglabs.ai",
    body: "An operating surface for AI-native studios: missions, systems, teams, and live operating context in one place.",
  },
  {
    name: "Cejel",
    title: "Trust certificate for AI-written code",
    body: "A free, offline CLI that scores how trustworthy a codebase is — tests, secrets, isolation, CI and audit discipline — and folds your existing scanners (Snyk, Semgrep, OpenSSF Scorecard) into one portable, shareable certificate. Especially useful when AI wrote a lot of the code.",
  },
  {
    name: "Egbert",
    title: "B2B Fintech 3.0 infrastructure",
    href: "https://egbert.io",
    displayUrl: "egbert.io",
    body: "Infrastructure for validating trading strategies and moving them from research to governed paper pilots and production — with explicit risk controls, full attribution, and human oversight.",
  },
  {
    name: "Therasyn",
    title: "Governance & on-prem infrastructure for clinical AI",
    href: "https://therasyn.ai",
    displayUrl: "therasyn.ai",
    body: "Governance and deployment infrastructure for clinical AI in environments where cloud-only isn't an option — academic medical centres, regulated health systems, and pharma research. BAA-bound by design, on-prem capable from day one. Built so health systems can run AI inside their own perimeter, with audit, PHI controls, and required sign-off enforced by construction.",
  },
];

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <motion.section id={id} {...fade} className="scroll-mt-28 py-14 sm:py-18">
      <div className="mb-7 flex items-center gap-4">
        <div className="h-px w-10 bg-white/25" />
        <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          {title}
        </h2>
      </div>
      <div className="space-y-5 text-base leading-8 text-white/72 sm:text-lg">
        {children}
      </div>
    </motion.section>
  );
}

function ProductCard({ product }: { product: Product }) {
  return (
    <article className="flex h-full flex-col rounded-lg border border-white/12 bg-white/[0.035] p-5">
      <div className="text-sm font-medium uppercase tracking-[0.2em] text-sky-200/80">
        {product.name}
      </div>
      <h3 className="mt-4 text-xl font-semibold leading-7 text-white">
        {product.title}
      </h3>
      {product.href ? (
        <a
          href={product.href}
          className="mt-3 inline-flex w-fit items-center gap-1.5 text-sm font-medium text-amber-200 transition hover:text-amber-100"
        >
          {product.displayUrl}
          <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
        </a>
      ) : null}
      <p className="mt-5 text-sm leading-7 text-white/68">{product.body}</p>
    </article>
  );
}

function ProductSection({
  id,
  title,
  children,
  href,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
  href?: string;
}) {
  return (
    <Section id={id} title={title}>
      {children}
      {href ? (
        <p>
          <a
            href={href}
            className="inline-flex items-center gap-2 font-medium text-amber-200 transition hover:text-amber-100"
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
    <div className="min-h-screen bg-[#0b0d0f] text-white">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-[#0b0d0f]/88 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-5 px-5 py-4 sm:px-6">
          <a href="#" className="flex items-center gap-3" aria-label="Barg Labs home">
            <Image
              src="/barg-icon.png"
              alt=""
              width={34}
              height={34}
              className="rounded-md"
              priority
            />
            <div>
              <div className="text-sm font-semibold tracking-tight text-white">
                Barg Labs
              </div>
              <div className="text-[11px] uppercase tracking-[0.22em] text-white/45">
                Applied AI products
              </div>
            </div>
          </a>

          <nav className="hidden items-center gap-5 text-sm text-white/60 lg:flex">
            {navItems.map(([label, href]) => (
              <a key={href} href={href} className="transition hover:text-white">
                {label}
              </a>
            ))}
          </nav>

          <a
            href="mailto:team@barglabs.ai"
            className="rounded-md bg-white px-4 py-2 text-sm font-medium text-[#0b0d0f] transition hover:bg-white/88"
          >
            Contact
          </a>
        </div>
      </header>

      <main>
        <section className="border-b border-white/10">
          <div className="mx-auto grid min-h-[calc(100vh-73px)] max-w-6xl content-center gap-12 px-5 py-16 sm:px-6 lg:grid-cols-[1fr_360px] lg:py-20">
            <motion.div {...fade} className="max-w-3xl">
              <div className="mb-7 inline-flex items-center gap-3 text-xs font-medium uppercase tracking-[0.24em] text-sky-200/80">
                <span className="h-px w-8 bg-sky-200/45" />
                Alfred. Cejel. Egbert — Fintech 3.0. Therasyn.
              </div>

              <h1 className="text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl">
                Barg Labs
              </h1>

              <div className="mt-8 max-w-2xl space-y-5 text-lg leading-8 text-white/74">
                <p>
                  The company centers on four product lines:{" "}
                  <span className="font-semibold text-white">Alfred</span>, the
                  operator OS for AI-native studios;{" "}
                  <span className="font-semibold text-white">Cejel</span>, a trust
                  certificate for AI-written code;{" "}
                  <span className="font-semibold text-white">Egbert</span>, our
                  B2B Fintech 3.0 infrastructure platform;{" "}
                  and <span className="font-semibold text-white">Therasyn</span>,
                  governance and on-prem infrastructure for clinical AI.
                </p>
              </div>
            </motion.div>

            <motion.div
              {...fade}
              className="self-end rounded-lg border border-white/12 bg-white/[0.035] p-5"
            >
              <Image
                src="/barg-icon.png"
                alt="Barg Labs"
                width={92}
                height={92}
                className="rounded-lg"
                priority
              />
              <p className="mt-6 text-sm leading-7 text-white/68">
                Applied AI products for studios, markets, and regulated health
                systems.
              </p>
            </motion.div>
          </div>
        </section>

        <div className="mx-auto max-w-6xl px-5 sm:px-6">
          <motion.section id="products" {...fade} className="scroll-mt-28 py-14 sm:py-18">
            <div className="mb-8 flex items-end justify-between gap-6">
              <div>
                <div className="mb-4 h-px w-10 bg-white/25" />
                <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                  Products
                </h2>
              </div>
              <p className="hidden max-w-md text-sm leading-6 text-white/48 md:block">
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

          <Section id="approach" title="Approach">
            <p>
              Barg Labs builds applied AI products around real operating
              constraints: who is using the system, where the data lives, what
              has to be reviewed, and what must remain under human control.
            </p>
            <p>
              The work is product-led rather than demo-led. Each surface is
              designed for a specific audience and an environment where
              reliability, legibility, and iteration matter.
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
            id="alfred"
            title="Alfred"
            href="https://alfred.barglabs.ai"
          >
            <p>
              Alfred is the operator OS for AI-native studios: a working surface
              for missions, product lines, system state, and the decisions that
              keep a studio moving.
            </p>
            <p>
              It is built for teams that need their operating context close to
              the work itself, with structure around what is being built, why it
              matters, and what needs attention next.
            </p>
            <p>
              Live operator surface available at{" "}
              <a
                href="https://alfred.barglabs.ai"
                className="font-medium text-amber-200 transition hover:text-amber-100"
              >
                alfred.barglabs.ai
              </a>
              .
            </p>
          </ProductSection>

          <ProductSection id="cejel" title="Cejel">
            <p>
              Cejel is a trust certificate for AI-written code: a free, offline
              command-line tool that scores the engineering signals that tell you
              whether to trust a repository - tests, secret hygiene, isolation,
              claim-vs-reality, and CI and audit discipline - and prints a portable
              certificate.
            </p>
            <p>
              Rather than competing with the scanner you already run, Cejel
              aggregates them. Pipe in SARIF from Snyk, Semgrep, or CodeQL, plus
              OpenSSF Scorecard, and get one shareable, rubric-scored certificate
              over all of them, with every contributing tool attributed. It is
              especially useful when AI wrote a lot of the code - exactly when trust
              can't be eyeballed.
            </p>
            <p>
              Open-source and source-available. Runs fully offline, with no signup
              and no model call.
            </p>
          </ProductSection>

          <ProductSection id="egbert" title="Egbert" href="https://egbert.io">
            <p>
              Egbert is Barg Labs' B2B Fintech 3.0 infrastructure platform for
              validating trading strategies and moving them from research to
              governed paper pilots and production, with explicit risk controls
              and human oversight.
            </p>
            <p>
              It is designed for real execution, monitoring, and controlled
              rollout, so strategy work can move from analysis into action
              without becoming an opaque black box.
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
            <div className="rounded-lg border border-white/12 bg-white/[0.035] px-6 py-9 text-center sm:px-10">
              <h2 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Contact Barg Labs
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-white/68">
                For product conversations, partnerships, or early access,
                contact the team directly.
              </p>
              <a
                href="mailto:team@barglabs.ai"
                className="mt-7 inline-flex items-center gap-2 rounded-md bg-white px-5 py-3 text-sm font-medium text-[#0b0d0f] transition hover:bg-white/88"
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
