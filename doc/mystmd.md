## Result

  Using “pure MyST” to mean that MyST is the primary site generator—rather than Eleventy, Jekyll, or an OpenStax CNXML
  pipeline—I found:

  - 12 active MyST textbooks recorded in Bindery’s repository catalog (bindery/structure/repos.json).
  - 1 additional MyST textbook, quantumMechanics, which is deployed but not yet catalogued.
  - opiniatedMystmdBookTemplate, which is a template rather than a textbook.

  All 13 use mystmd@1.10.1 and build HTML into _build/html. Under a stricter definition of “pure” that excludes
  extensions, four are enhanced MyST projects:

  - modernPhysics: custom simulation/export plugins.
  - opticsTextbook: substantial JavaScript validation, export, and PWA post-processing.
  - modern-classical-mechanics: executable Jupytext/Python content.
  - quantumMechanics: PWA post-processing.

  The other nine are comparatively plain MyST books.

  ## Survey

   Textbook            Practices worth adopting                          Most important gaps
  ━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   modernPhysics       Best overall engineering model: consistent        Highly customized and too complex to impose as
                       chapter structure, learning objectives,           the minimum; not yet using Bindery reusable
                       summaries, problems and worked solutions;         workflows.
                       simulations in every chapter; explicit alt
                       text; per-chapter attribution; generated
                       figures; extensive tests; link checking;
                       student/instructor PDF variants, DOCX and
                       chapter offprints. See its README
                       (modernPhysics/README.md) and project
                       validator (modernPhysics/scripts/validate-
                       project.mjs).
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   opticsTextbook      Richest reusable QA toolbox: Markdown/style/      No conventional ci.yml; several validation
                       grammar/spelling, reference, image and alt-       steps are continue-on-error, so they report
                       text validators; Jest tests; security audit;      problems without blocking a merge. Validation
                       PWA/offline support; image optimization; PDF      uses Node 20 while deployment uses 22.
                       and per-chapter exports. See opticsTextbook/      private: true is absent. Bindery calls it
                       package.json and alt-text validator               original, while its README calls it a fork/
                       (opticsTextbook/scripts/validation/validate-      adaptation—provenance needs a deliberate
                       alt-text.js).                                     resolution.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   physicsOfWaves      Strong conversion verifier for structure,         No Node engine or Dependabot; little chapter-
                       labels, cross-references, footnotes, equations    level objective/summary scaffolding.
                       and images; explicit alt text on all 258
                       figure directives; substantial problem sets.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   thermodynamics      Excellent converted-book conventions: 96          No Node engine or Dependabot; large source PDF
                       exercise directives, collapsible answers, OCR/    committed directly; limited consistent
                       hunspell checks, source-count verification,       learning outcomes and summaries.
                       directive-fence checks and explicit figure alt
                       text.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   variationalPrinc    Very strong advanced reference book, with         No Node engine or Dependabot; no learning
   iples               chapter summaries/exercises, 1,591 labelled       objectives; QA is conversion-oriented rather
                       equations, cross-reference verification and       than pedagogical.
                       explicit alt text.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   PrinciplesOfMech    Strong exercise density—114 exercise              No active verifier; no explicit alt text on
   anics               directives—and proper bibliography/DOI            roughly 286 figure directives; sparse MyST
                       metadata.                                         description/keywords; no Node engine or
                                                                         Dependabot.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   UniversityPhysic    Consistent examples, summaries, problems and      Sparse project metadata; figures generally
   sIClassicalMecha    worked solutions; structural/figure verifier;     lack explicit :alt:; no Node engine or
   nics                clear maintenance documentation.                  Dependabot.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   modern-             Best computational pedagogy: Jupytext-authored    Needs a content-specific structural validator
   classical-          executable lessons, strict execution during       and a clearer source/asset attribution ledger.
   mechanics           every build, activities, projects, homework,
                       applications and inclusive historical context.
                       Also has PDF/DOCX exports. See modern-
                       classical-mechanics/myst.yml.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   Dynamics_Textboo    Best conversion-integrity verifier: source-       Current CI fails because 152 image files are
   k                   page coverage, checksums, figures, labels,        orphaned; deployment is manual-only; myst.yml
                       references, problems/solutions, malformed         lacks github. The latest CI failure is
                       LaTeX, conversion artifacts and orphaned          reproducible locally.
                       assets. Pedagogically strong active-learning
                       design, summaries, practice problems,
                       experiments, videos and eight notebooks. See
                       Dynamics_Textbook/scripts/verify_book.py.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   EnergyAndHumanAm    Excellent whole-book architecture: “how to use    Source-coverage QA silently skips when build/
   bitions             this book,” problems in every chapter,            document.json is absent—as it is in a clean
                       selected answers, math/chemistry primers,         clone. Deploy installs MyST globally rather
                       notation, glossary and detailed image             than using npm ci. No Node engine or
                       attribution. All 202 figure directives have       Dependabot.
                       explicit alt text.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   QuantumComputing    Accessible conceptual progression,                Fails Bindery’s license-documentation check
   ForTheQuantumCur    experimental motivation and a dedicated           even though the license appears in myst.yml;
   ious                worksheet chapter.                                no active verifier; sparse metadata; most
                                                                         images lack usable alt text.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   AtomicPhysicsFor    Strong general-audience orientation, learning     Same license-documentation failure; no active
   Everyone            goals in most substantive chapters and 64         verifier; sparse metadata; figures generally
                       exercise directives.                              lack alt text.
  ──────────────────  ────────────────────────────────────────────────  ────────────────────────────────────────────────
   quantumMechanics    Promising new pedagogical model: experiment-      Not in Bindery; currently an incomplete local
                       first/spins-first progression, explicit           draft with modified and untracked chapters;
                       learning objectives, frequent worked examples,    its verifier only checks that a few files and
                       concept checks, summaries and exercises. It       metadata fields exist. Assessment is therefore
                       inherits a reproducible Node 22/PWA structure     provisional.
                       from the opinionated template.

  ## Best exemplars by dimension

  There is no single repo that should simply be copied everywhere:

  - Overall engineering and structured textbook pedagogy: modernPhysics.
  - Reusable validation code, PWA and delivery tooling: opticsTextbook.
  - Computational and project-based learning: modern-classical-mechanics.
  - Active-learning and multimodal material: Dynamics_Textbook.
  - Conversion fidelity: Dynamics_Textbook, then thermodynamics.
  - Accessibility in existing content: modernPhysics, physicsOfWaves, thermodynamics, variationalPrinciples,
    Dynamics_Textbook, and EnergyAndHumanAmbitions.

  - Attribution/provenance: modernPhysics, Dynamics_Textbook, and EnergyAndHumanAmbitions.
  - Clean starter architecture: opiniatedMystmdBookTemplate (opiniatedMystmdBookTemplate/README.md).

  ## Recommended future unified model

  I would use a small universal baseline plus optional capability profiles.

  The universal baseline should require:

  1. private: true, Node >=22, exact mystmd@1.10.1, a committed lockfile, and standard start, build, verify, and check
     scripts.

  2. Complete MyST metadata: description, keywords, author, license, open_access, short_title, github, HTTPS URL and
     accessible logo text.

  3. A real verify command checking TOC files, duplicate/dangling labels, missing/orphaned images, explicit alt text,
     malformed directives and license/provenance documentation.

  4. PR CI running npm ci → verify → strict build → link check; deployment should repeat verification before publishing.
  5. Dependabot for npm and GitHub Actions.
  6. A content-license document plus separate code/tooling licensing where relevant.
  7. A recommended—not compulsory—chapter pattern: learning outcomes, motivation/application, worked examples, concept
     checks, summary, graduated problems and answers or hints.

  Optional profiles should add specialized behavior without burdening every book:

  - conversion-source: source manifest, checksums, OCR checks and fidelity thresholds.
  - executable: Python/Jupytext environment and executed strict builds.
  - interactive: simulation directives with keyboard-accessible and print fallbacks.
  - pwa: offline/installable delivery.
  - exports: PDF, student/instructor editions, DOCX and release artifacts.
  - generated-figures: reproducible figure sources and regeneration tests.

  Bindery should record these profiles and a verifyCommand in the catalog. That would let fleet health test each book
  appropriately without pretending every MyST book has identical needs.

  One caution: none of the 12 catalogued books currently calls Bindery’s reusable workflows. Before migrating them, the
  shared workflows should absorb the strongest existing features—strict/link builds, executable-notebook setup, export
  extensions and current action versions. Otherwise “unification” would reduce QA in the best repositories.

  As of September 13, 2026, the primary Pages deployments are generally successful; the clear current exception is
  Dynamics_Textbook CI. I made no repository changes during this survey.

─ Worked for 8m 52s ────────────────────────────────────────────────────────────────────────────────────────────────────


› can you focus on the first six bullet points


• I’m interpreting “first six” as the first six items in the proposed universal baseline, leaving pedagogy aside for
  now.

  ## 1. Standard package.json

  Target:

  - private: true
  - engines.node: ">=22"
  - mystmd: "1.10.1"
  - Scripts: start, build, verify, check
  - Committed package-lock.json
  - npm ci in automation

  Current state:

  - Every book pins mystmd@1.10.1 and has a lockfile.
  - opticsTextbook lacks private: true.
  - Only modernPhysics, modern-classical-mechanics, and Dynamics_Textbook fully declare a Node 22 floor among the
    catalogued books.

  - opticsTextbook allows Node 20 and actually validates on Node 20 while deploying on Node 22.
  - Most converted books lack engines.node.
  - Script names are inconsistent: some use verify, some check, and others expose no validation command.

  Recommended contract:

  {
    "private": true,
    "engines": {
      "node": ">=22"
    },
    "scripts": {
      "start": "myst start",
      "build": "myst build --html",
      "verify": "...book-specific checks...",
      "check": "npm run verify && myst build --html --strict --check-links"
    },
    "devDependencies": {
      "mystmd": "1.10.1"
    }
  }

  verify should remain book-specific; check should become the predictable fleet-wide entry point.

  ## 2. Complete MyST and catalog metadata

  Required MyST fields should be:

  - title
  - short_title
  - description
  - authors
  - license
  - open_access: true
  - github
  - keywords
  - toc

  Recommended site metadata:

  - logo
  - logo_dark, when relevant
  - logo_alt
  - logo_text
  - GitHub action link
  - Source/original-edition action link for adaptations

  Main gaps:

   Repo                                               Metadata gap
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PrinciplesOfMechanics                              No description, keywords, or accessible logo metadata
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   UniversityPhysicsIClassicalMechanics               No description, keywords, or accessible logo metadata
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   Dynamics_Textbook                                  Missing github and keywords
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   QuantumComputingForTheQuantumCurious               No description, keywords, or accessible logo metadata
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   AtomicPhysicsForEveryone                           No description, keywords, or accessible logo metadata
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   physicsOfWaves, thermodynamics,                    Good core metadata, but little or no accessible branding metadata
   variationalPrinciples, EnergyAndHumanAmbitions
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   opticsTextbook                                     Good metadata, but catalog provenance conflicts with its README
  ─────────────────────────────────────────────────  ───────────────────────────────────────────────────────────────────
   quantumMechanics                                   Good MyST metadata, but absent from Bindery

  Bindery should also normalize all deployed URLs to HTTPS and add quantumMechanics. The provenance classification of
  opticsTextbook needs review because Bindery (bindery/structure/repos.json) calls it original while its README
  describes an adaptation of the TU Delft textbook.

  ## 3. A common verification contract

  The fleet should standardize what npm run verify means without requiring identical implementations.

  Minimum checks:

  1. Every TOC entry exists.
  2. Labels are unique.
  3. Internal references resolve.
  4. Referenced images exist.
  5. Unreferenced/orphaned images are reported.
  6. Every meaningful image has explicit alt text.
  7. Directive fences and Markdown structure are balanced.
  8. Required MyST metadata is present.
  9. Content license and provenance documentation exist.
  10. Common conversion artifacts or invalid characters are absent.

  Existing code to reuse:

  - Dynamics verifier (Dynamics_Textbook/scripts/verify_book.py): strongest source-fidelity, label, reference, image,
    problem/solution and LaTeX checking.

  - Optics validators (opticsTextbook/scripts/validation): best modular validators, especially accessibility and style.
  - Modern Physics validator and tests (modernPhysics/scripts/validate-project.mjs): strongest metadata/plugin/export
    testing.

  - physicsOfWaves, thermodynamics, and variationalPrinciples: useful conversion-artifact and reference checks.

  Important current weaknesses:

  - PrinciplesOfMechanics, QuantumComputingForTheQuantumCurious, and AtomicPhysicsForEveryone have no active package-
    level verifier.

  - quantumMechanics only checks a few files and metadata fields.
  - modern-classical-mechanics executes notebooks strictly but lacks structural content checks.
  - EnergyAndHumanAmbitions skips source-coverage checks in a clean clone because build/document.json is absent.
  - Dynamics_Textbook correctly fails verification because 152 images are currently orphaned. This is evidence that the
    verifier is useful, not that it should be weakened.

  A shared scripts/verify-base.mjs or small internal package could implement universal checks, with each book adding its
  own conversion or execution checks.

  ## 4. Unified CI and deployment

  None of the 12 catalogued MyST books currently calls Bindery’s reusable workflows.

  The desired pattern is:

  Pull request
    → npm ci
    → npm run verify
    → npm run build -- --strict --check-links

  Push to main
    → repeat verification/build
    → upload _build/html
    → deploy Pages

  Before migrating books, Bindery’s reusable CI (bindery/.github/workflows/ci.yml) and deployment workflow
  (bindery/.github/workflows/deploy.yml) should be expanded to support:

  - A standard check-command, preferably npm run check.
  - Strict and link-checked MyST builds.
  - Executable notebook setup.
  - Optional hunspell.
  - Optional generated-figure checks.
  - Optional post-build/PWA steps.
  - Optional export artifact retrieval.
  - Current GitHub Action versions.

  Book-specific workflows such as exports, figures and security scans should remain separate extension workflows.

  Immediate anomalies:

  - Dynamics_Textbook deployment is manual-only.
  - EnergyAndHumanAmbitions deploys using a global MyST installation.
  - opticsTextbook has no conventional ci.yml; several validators are non-blocking.
  - PrinciplesOfMechanics, QuantumComputingForTheQuantumCurious, and AtomicPhysicsForEveryone only test whether MyST
    builds.

  ## 5. Dependabot

  Only four catalogued MyST books currently have Dependabot:

  - modernPhysics
  - opticsTextbook
  - modern-classical-mechanics
  - Dynamics_Textbook

  Every Node-based book should receive the canonical npm and GitHub Actions configuration from Bindery. Python
  dependency updates should be enabled only for repositories that actually maintain a requirements.txt or
  pyproject.toml.

  A monthly grouped schedule is probably appropriate for stable books:

  version: 2
  updates:
    - package-ecosystem: npm
      directory: /
      schedule:
        interval: monthly
      groups:
        myst:
          patterns:
            - mystmd
            - "@myst-theme/*"

    - package-ecosystem: github-actions
      directory: /
      schedule:
        interval: monthly

  opticsTextbook currently includes a pip updater even though its active tooling is JavaScript; that should be checked
  before using its configuration as a model.

  ## 6. License and provenance

  Every myst.yml names a content license, but that is not yet enough to satisfy Bindery’s repository-level policy.

  Current failures:

  - QuantumComputingForTheQuantumCurious
  - AtomicPhysicsForEveryone

  Both need a root license document or a clear README license section.

  A stronger unified standard would use:

  - LICENSE-CONTENT.md: edition content license.
  - LICENSE-CODE: scripts, plugins, templates and build tooling.
  - SOURCES.md: chapter-level source and interactive-resource attribution.
  - provenance.md: conversion/source-edition history when applicable.
  - Image-level attribution ledger for third-party figures.

  Best examples:

  - modernPhysics: detailed chapter-level modernPhysics/SOURCES.md.
  - Dynamics_Textbook: explicit provenance (Dynamics_Textbook/provenance.md), upstream acknowledgement, and separate
    notebook/video licensing.

  - EnergyAndHumanAmbitions: dedicated image-attribution material.
  - modern-classical-mechanics: actual root content license.

  The distinction between content and code is especially important for quantumMechanics: its root LICENSE covers the
  inherited template code, while the README assigns CC BY-SA to the textbook content.

  ## Suggested order

  1. Add missing metadata, Node engines, private: true, license sections and Dependabot. These are low-risk mechanical
     changes.

  2. Establish the common verify/check command contract.
  3. Extract shared validators from Dynamics, Optics and Modern Physics.
  4. Upgrade Bindery’s reusable workflows to preserve those capabilities.
  5. Migrate simple books first.
  6. Migrate executable, PWA and export-heavy books only after the extension hooks exist.
