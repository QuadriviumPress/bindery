---
name: quadrivium-myst-presentation
description: How QuadriviumPress MyST chapters present exercises, callouts, and labels. Read before adding a problem, worked example, figure, or admonition. The starter copy is opiniatedMystmdBookTemplate.
---

# MyST presentation

New chapter prose follows this contract. The sample pages in
`opiniatedMystmdBookTemplate` (`chapters/ch-01-getting-started.md` and
`chapters/ch-02-interactive-content.md`) are the copy to imitate. Simulation
embeds and tab sets stay in
[`quadrivium-myst-directives`](../quadrivium-myst-directives/SKILL.md).

Use backtick fences. Chapter files for new work are `chapters/ch-NN-slug.md`.

## Callouts

| Directive | Role |
| --- | --- |
| `{note}` | Learning objectives and pointers to external resources |
| `{important}` | Laws, principles, and key equations |
| `{tip}` | Strategy and shortcuts |
| `{warning}` | Common mistakes and sign or unit pitfalls |

```{note}
State what the reader should be able to do after the chapter.
```

## Labels

- Equations: `eq:` prefix, then a chapter token and a name, as `eq:starter:energy`
- Figures: `fig:` prefix, the same way, as `fig:starter:logo`
- Exercises: `ex:` prefix, as `ex:starter:energy`
- Solutions: `sol:` prefix, as `sol:starter:energy`

Cross-reference equations with `{eq}` and figures with `{ref}`. Give every
figure alternative text.

## Exercises

Problems are `{exercise}` directives. Hide the worked answer in a `{solution}`
dropdown bound to that exercise label.

```{exercise}
:label: ex:starter:energy

A system emits a photon. Which quantity in {eq}`eq:starter:energy` sets the
energy scale?
```

```{solution} ex:starter:energy
:label: sol:starter:energy
:class: dropdown

The energy is proportional to the square of the speed of light.
```

A converted textbook may keep the source's problem markup when changing it
would rewrite the source's pedagogy. That exception belongs in the book's
`AGENTS.md` under **Presentation gap**, not in a one-off directive invented
for a single chapter.
