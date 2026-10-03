# MyST textbook review ledger

Started 2026-09-29. Scope: the 17 active `format: myst`, `isBook: true`
entries in `structure/repos.json`. The starter template and other book formats
are excluded. Review every student-facing page in each book's `myst.yml` table
of contents. This ledger tracks daily batches; individual findings and edits
belong in each book's `reviews/editorial-review.md` once work starts there.

## Repeatable inventory

Run `python3 scripts/audit-myst-fleet.py` from Bindery for a feature and page
summary, or add `--json` for page-level findings with line numbers. The audit
is read-only. It reports missing or truncated alternative text and unlisted
content candidates; a human must check context. Each book's `npm run verify`
and `npm run check` remain the authoritative project checks.

Initial inventory: 499 table-of-contents pages and approximately 2.05 million
raw Markdown words. The audit flagged 352 image descriptions for review,
chiefly raw HTML images in `opticsTextbook` and `musicTheory`. No TOC paths were
missing and no conventional content files were unlisted. Five books currently
have PDF and DOCX scripts; three have H5P scripts. These capabilities remain
content-driven rather than universal requirements.

| Book | TOC pages | Editorial pages reviewed | Status |
| --- | ---: | ---: | --- |
| `quantumComputingForTheQuantumCurious` | 11 | 11 | Editorial pass complete; local PDF export added; [book report](../../quantumComputingForTheQuantumCurious/reviews/editorial-review.md) |
| `modernPhysicsLab` | 21 | 21 | Editorial pass complete; [book report](../../modernPhysicsLab/reviews/editorial-review.md) |
| `musicTheory` | 126 | 0 | Pending; raw HTML image descriptions |
| `opticsTextbook` | 32 | 25 | In progress; [book report](../../opticsTextbook/reviews/editorial-review.md) |
| `physicsOfWaves` | 17 | 0 | Pending |
| `thermodynamics` | 25 | 0 | Pending |
| `variationalPrinciples` | 25 | 0 | Pending |
| `principlesOfMechanics` | 12 | 0 | Pending |
| `universityPhysicsIClassicalMechanics` | 15 | 0 | Pending |
| `modernClassicalMechanics` | 38 | 0 | Pending |
| `quantumMechanics` | 13 | 0 | Pending |
| `physicsOfMusic` | 21 | 0 | Pending |
| `dynamicsTextbook` | 28 | 0 | Pending |
| `energyAndHumanAmbitions` | 33 | 0 | Pending |
| `atomicPhysicsForEveryone` | 15 | 0 | Pending |
| `modernPhysics` | 19 | 0 | Pending |
| `understandingMusicTheory` | 48 | 0 | Pending |

## Daily batches

- **2026-09-29:** Added the read-only fleet audit and focused tests. Reviewed
  all 11 quantum-computing TOC pages. Corrected explanations of classical
  versus quantum uncertainty, energy levels, probability amplitudes,
  measurement, interference, photon sources, Stern–Gerlach experiments, BB84,
  gates, entanglement, teleportation, and algorithmic complexity. Updated
  worksheet instructions and figure descriptions; the fleet audit now flags
  zero weak image descriptions in this book. The book verifier and strict
  MyST site-content build pass. Full HTML/link verification is restricted by
  this environment; details are in the book report.
- **2026-09-30:** Built and validated a 107-page PDF from the edited quantum
  MyST source using a local XeLaTeX template. Corrected figure option blocks,
  table targets and references, and worksheet cells revealed by print output;
  added a verifier check for the markup patterns. Quantum verifier and strict
  site build pass. Reviewed all six `modernPhysicsLab` front-matter pages.
  Corrected safety guidance, uncertainty and fitting explanations, the Python
  number-formatting example, and report schedule and rubric inconsistencies.
  The lab verifier and 21-page strict site build pass. Its index remains
  provisional until the 14 experiments have been checked against the
  schedule's promises. The quantum PDF is currently a local artifact, not a
  site download. Continued with lab Experiments 1–2: corrected the
  interferometer's precision promise and conditional ether-model sensitivity,
  and fixed the speed-of-light handout's cable-offset interpretation and
  single-delay formula in its schematic. Their figures were inspected. The
  lab verifier and strict site build still pass; 8 of 21 pages now reviewed.
  Experiment 3 required a new practical-range analysis: a noise threshold
  cannot define the beta endpoint because it changes with counting time. The
  procedure now requires a measured thick-absorber floor and a terminal
  linear-rate fit; its concept figure, uncertainty guidance, safety controls,
  and exercises were revised. The source code and SVG agree. The lab verifier
  and strict site build pass; 9 of 21 pages now reviewed.
  Experiment 4's noninteger slit ratio invalidated the blanket fringe-count
  formula and its missing-order question. Corrected the rule, repaired camera
  and wedge imaging methods, and fixed the schedule's mistaken “film
  thickness” claim. The lab verifier and strict site build pass; 10 of 21
  pages now reviewed.
  Experiment 5's Rayleigh figure used a slit profile rather than the
  circular-aperture Airy pattern; the corrected plot gives a 26.5% central
  dip. The diffraction and disc procedures now distinguish transmission and
  reflection layouts, and an absent Blu-ray spot is no longer treated as a
  measured pitch bound. The lab verifier and strict site build pass; 11 of
  21 pages now reviewed.
  Experiment 6's LED fit now distinguishes a voltage proxy from an exact band
  gap; its tungsten-lamp fit reports an effective electrical-power exponent,
  since the recorded $VI$ also covers conduction and possible gas losses. The
  unsupported 10% $h$ promise, fixed negative-intercept claim, and lamp
  spectrometer figure were corrected. The lab verifier and strict site build
  pass; 12 of 21 pages now reviewed.
  Experiment 7 now treats the EDU-QE1 as a laser and mount source for a
  separately supplied double-slit analog, measures path bias from one-slit
  powers instead of deriving it from analyzer angle, and uses a calibrated
  screen or scanning detector. Its corrected schematic includes 45° input
  preparation; the complementarity plot states its ideal assumptions. Laser
  class, orthogonal-analyzer sum, $C_{60}$ grating reasoning, delayed choice,
  and photon-counting claims were corrected. The lab verifier and strict
  21-page site build pass; 13 of 21 pages now reviewed, or 24 of 499 fleet
  pages.
  Experiment 8's FTIR page now fits only the optical thick-gap tail, checks
  the beam profile and ring geometry, and treats the exact quantum barrier
  transmission separately from its thick-barrier limit. The above-barrier
  code denominator and the $E=V_0$ case were corrected; the prism schematic
  now sends light to the hypotenuse and shows the proper ports. Both figures,
  the numerical example, the verifier, and the strict site build were checked.
  The lab now has 14 of 21 pages reviewed, or 25 of 499 fleet pages.
  Experiment 9 now uses a square-cross-section cavity and follows a
  specified degenerate pair through partition detuning. The analysis
  fits sound speed with independently measured dimensions, since a fit
  of speed and all dimensions together cannot identify their absolute
  scale. It distinguishes acoustic mode triples from distinct peaks,
  corrects the density-of-states trend, and treats Chladni plates as a
  different bending-wave system. Both figures and the index promise were
  revised. The verifier and strict 21-page site build pass; 15 of 21 lab
  pages and 26 of 499 fleet pages have been reviewed.
  Experiment 10 now uses an instrument-specific reflective-grating path
  and calibration model, with mercury and helium lines assigned distinct
  roles. The analysis separates observed Balmer centers from the simple
  Rydberg model, propagates common calibration uncertainty, and treats
  precision and reduced-mass claims conditionally. Both figures and the
  index promise were revised. The verifier and strict 21-page site build
  pass; 16 of 21 lab pages and 27 of 499 fleet pages have been reviewed.
  Experiment 11's visible sodium method now reconstructs 3p, 5s, and 4d
  energies from assigned lines and uses an independently tabulated
  ionization limit for state-specific quantum defects. The D splitting,
  weak-line targets, resolution checks, potassium option, and two figures
  were corrected; an impossible n=3 f level was removed. The verifier
  and strict 21-page site build pass; 17 of 21 lab pages and 28 of 499
  fleet pages have been reviewed.
  Experiment 12 now uses solvent-matched references and corrected detector
  response for absorption/emission comparisons. Its analysis distinguishes
  absorbance from emission density when changing to wavenumbers and makes
  mirror symmetry and vibronic-spacing conclusions conditional on evidence.
  The UV controls, apparatus schematic, and optional lifetime/quantum-yield
  methods were revised. Both figures, the verifier, and strict site build
  passed; 18 of 21 lab pages and 29 of 499 fleet pages have been reviewed.
  Experiment 13's half-life run now spans the stated 15 minutes and fits
  raw interval counts with a Poisson likelihood that includes measured
  background. The counting comparison accounts for Gaussian bin probability
  and fitted degrees of freedom, and the attenuation result is marked
  effective when scattered photons enter the GM tube. The figures, verifier,
  and strict site build passed; 19 of 21 lab pages and 30 of 499 fleet
  pages have been reviewed.
  Experiment 14 now distinguishes vertical muon intensity from integrated
  flux, counts achievable with the illustrative two-tube setup, and a
  conditional time-dilation calculation from a one-altitude measurement.
  The finite-acceptance code and rotated-frame schematic were corrected;
  the two-GM-tube stopped-muon lifetime promise was removed. The index
  schedule now matches all 14 experiments. The verifier, strict 21-page
  site build, and figure checks passed. All 21 lab pages are reviewed,
  bringing the fleet count to 32 of 499.
- **2026-09-30–10-01:** Began the 32-page optics book. Reviewed its preface,
  Chapter 1, and Chapter 1 problems. Corrected the relativistic wavelength
  and photon-flux arithmetic, Newton's rings phase, refractive-index scope,
  UV descriptions, and historical speed measurement. Inspected and described
  all six Chapter 1 figures. The verifier passes all 181 tests and the strict
  MyST site build passes all 32 pages. Optics audit findings fell from 152 to
  146; the fleet count was 35 of 499. Chapter 2 was next.
- **2026-10-01:** Reviewed optics Chapter 2 and its problem page. Corrected
  the stationary optical-path formulation, phase-index timing, single-surface
  focal sign, camera $f$-number, numerical aperture and Airy width, and the
  two-lens transfer matrix and focal coordinates. Rebuilt two figures from
  vector sources to repair the conic directrix and pupil labels. Inspected
  and described all 23 figures on these pages. The verifier passes all 181
  tests, the strict 32-page site build passes, and optics audit findings are
  down to 123. The fleet count is 37 of 499.
  Reviewed Chapter 3 and its problems. Corrected the reduced-eye model,
  camera and eye anatomy, magnifier and finite-tube microscope formulas,
  telescope focus, and the field-of-view exercise's eye dimensions. The
  planar-interface problem now states its negative-index premise. All 16
  figures on these pages were inspected and described. The verifier passes
  181 tests, the strict site build passes, and optics audit findings are
  down to 107. The fleet count is 39 of 499.
  Reviewed Chapter 4 and its problems. Corrected the Jones rotation and
  eigenvector equations, circular-basis coefficients, full-wave filter
  arrangement, and the mirror-return exercise's polarizer angle and scope.
  All six figures on these pages were inspected and described. The verifier
  passes 181 tests, the strict site build passes, and optics audit findings
  are down to 101. The fleet count is 41 of 499.
  Reviewed Chapter 5 and its problems. Corrected the pulse derivative,
  cylindrical far-field limit, Poynting factor, circular-field phasor, and
  low-speed Doppler signs. Repaired exercises on a traveling pulse,
  unequal-amplitude nodes, Gaussian beams, radar reflection, and stationary
  interference fringes. Both pages contain no figures. The verifier passes
  181 tests and the strict site build passes. The fleet count is 43 of 499.

- **2026-10-01:** Reviewed optics Chapter 6 and its problems. Replaced the inconsistent Fabry–Perot derivation, corrected coherence and solar-disk visibility, repaired propagation delays and polarization guidance, and finished the cavity exercise. Inspected and described all 17 figures on these pages. The verifier passes 181 tests, the strict 32-page site build passes, and optics audit findings are down to 84, with zero findings on reviewed pages. The fleet count is 45 of 499.

- **2026-10-01:** Reviewed optics Chapter 7 and its problems. Corrected the diffraction spectrum, Fresnel and Fraunhofer conditions, Airy and imaging formulas, finite-grating approximations, and the stellar visibility exercise. Inspected and described all 26 figures on the pair of pages. The verifier passes 181 tests, the strict site build passes, and optics audit findings are down to 58, with zero findings on reviewed pages. The fleet count is 47 of 499.

- **2026-10-02:** Reviewed optics Chapter 8 and its problems. Corrected laser linewidth and focusing arithmetic, Einstein coefficient example and units, cavity mirror geometry, transverse-mode terms, and pump mechanisms. Inspected and described all 19 chapter figures, and replaced the population plot with a reproducible, correctly labeled version. The verifier passes 181 tests, the strict site build passes, and optics audit findings are down to 39, with zero findings on reviewed pages. The fleet count is 49 of 499.

- **2026-10-02:** Reviewed optics Chapter 9 and its problems. Rebuilt the phase-contrast derivation, clarified confocal pinhole and fluorescence operation, and corrected near-field descriptions that referred to nonexistent image panels. Inspected and described all five figures. Repaired underdetermined microscope exercises. The verifier passes 181 tests, the strict site build passes, and optics audit findings are down to 34, with zero findings on reviewed pages. The fleet count is 51 of 499.

- **2026-10-02:** Reviewed optics Chapter 10 and its problems. Corrected index contrast, mode cutoff, modal-delay and chromatic-dispersion equations, and several component descriptions. Inspected and described all 21 figures, regenerated the mirror-waveguide delay plot, and made the coupling-loss exercise dimensionally defined. The verifier passes 181 tests, the strict site build passes, and optics audit findings are down to 13, with zero findings on reviewed pages. The fleet count is 53 of 499.

- **2026-10-03:** Reviewed optics Chapter 11 and its problem page. Corrected the focal-coordinate and magnification equations, separated the lensmaker and imaging equations, distinguished afocal from telecentric systems, and fixed the principal-plane propagation sign and problem-set transformation direction. Inspected and described all 13 figures. Symbolic matrix multiplication, the 181-test verifier, and the strict 32-page site build pass. The optics image audit now has zero findings. The fleet count is 55 of 499.
  Reviewed Appendix A on complex numbers. Corrected the distinction between the real-field time average and complex-amplitude modulus, the extinction-coefficient notation, the total-internal-reflection coefficient, and absorbing-slab arithmetic. Its interference exercises now state intensity with physical units. The verifier and strict site build pass; 24 of 32 optics pages and 56 of 499 fleet pages are reviewed.
  Reviewed Appendix B on matrix multiplication. Corrected the stated
  order of transformations, aligned its $(y,\theta)^T$ convention with
  Chapter 11, repaired wave-plate rotation formulas and the telescope
  and beam-expander examples, and completed the practice solutions.
  Symbolic examples, the verifier, and strict site build pass. The
  reviewed counts are now 25 of 32 optics pages and 57 of 499 fleet pages.

## Next batch

Continue `opticsTextbook` with its appendices in TOC order, then prioritize the flagged
image-description work in `musicTheory`. Assess a print handout export for
the now-reviewed `modernPhysicsLab` and plan how the quantum PDF will be
published if a site download is desired. Update each reviewed-page count only
after reading the complete page and checking its substantive edits.
