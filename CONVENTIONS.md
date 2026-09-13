# QuadriviumPress book conventions

Shared structural baseline for every book repo in the [QuadriviumPress](https://github.com/QuadriviumPress)
organization, enforced (where automatable) by [`scripts/check-repo-compliance.sh`](scripts/check-repo-compliance.sh)
and [`shared-compliance-check.yml`](.github/workflows/shared-compliance-check.yml). Format-specific
detail lives in [`skills/quadrivium-repo-structure/SKILL.md`](skills/quadrivium-repo-structure/SKILL.md).

## Every repo

- `README.md` with an `# Title` heading. No fixed section order is enforced -- the fleet's
  README styles vary (badges, TOC links, "Source and license" sections) more than a rigid
  template would tolerate -- but a book's README should at least say what it is, how to
  build it, and where its content license lives.
- Content license documented at the repo, in a root `LICENSE`/`LICENSE.txt` file or a
  `## License` README section. See [`skills/quadrivium-attribution/SKILL.md`](skills/quadrivium-attribution/SKILL.md)
  for why this is per-repo rather than inherited from `QuadriviumPress/.github`.
- `.github/workflows/ci.yml` that builds on pull requests. New and migrating repos should
  call bindery's reusable workflow rather than reimplementing checkout/setup/build:

  ```yaml
  jobs:
    ci:
      uses: QuadriviumPress/bindery/.github/workflows/ci.yml@main
      with:
        build-command: npm run build   # or: myst build --html, eleventy, ...
  ```
- `.github/workflows/deploy.yml`, for any repo with a `deployedUrl` in the catalog, calling
  the reusable Pages deploy with the format's output directory:

  ```yaml
  on:
    push: { branches: [main] }
    workflow_dispatch:
  jobs:
    deploy:
      uses: QuadriviumPress/bindery/.github/workflows/deploy.yml@main
      with:
        output-dir: _build/html   # MyST; Eleventy/Jekyll use _site
      permissions:
        contents: read
        pages: write
        id-token: write
  ```
- `.github/dependabot.yml` for Node/Python dependency updates -- see
  [`config/dependabot-npm.yml`](config/dependabot-npm.yml) / [`config/dependabot-pip.yml`](config/dependabot-pip.yml)
  for the canonical templates.
- If the repo is Node-based, `package.json` declares `engines.node` (fleet floor: `>=22`,
  matching the `node-version` default in `ci.yml` / `deploy.yml`).

## MyST contract

Every active MyST book additionally provides:

- `package.json` with `private: true`, exact `mystmd@1.10.1`, and `start`,
  `build`, `verify`, and `check` scripts. `verify` runs fast structural,
  conversion, execution, or content checks appropriate to that book; `check`
  is the production-equivalent verification and HTML build.
- `myst.yml` metadata containing `title`, `short_title`, `description`,
  `authors`, `license`, `open_access: true`, `github`, `keywords`, and a
  non-empty `toc`.
- `SOURCES.md` recording the primary source, edition license, and the policy
  for attributing figures and other third-party components.
- Pull-request CI that gates on `verify`/`check`, and a Pages deployment that
  reruns the book's verifier before publishing. Export-, PWA-, and
  notebook-heavy books may keep specialized deployment workflows while using
  the same command contract.

## Adding a book to the catalog

See [`doc/add-book.md`](doc/add-book.md).

## Not yet built

Baton (bindery's counterpart for the [OpenPhysics](https://github.com/OpenPhysics) org)
also has fleet-wide GitHub-settings sync, an off-GitHub GitLab mirror, PR-fan-out tooling,
and generated screenshot thumbnails. Bindery starts without those -- add them the same way
Baton did, incrementally, once there's an actual need across the book fleet, rather than
speculatively porting everything up front.
