---
name: quadrivium-pwa
description: Add or repair offline support, install manifests, and service workers in QuadriviumPress MyST books. Use for PWA setup or stale content and cache interference between books on the shared Pages domain.
---

# Offline book support

Start with `opiniatedMystmdBookTemplate/scripts/setup-pwa.mjs` and
`pwa/service-worker.js`. `modernPhysics` has the same scope isolation plus
book-specific H5P handling. Copy only the capabilities the target needs;
PWA exceptions belong in the book's `AGENTS.md`.

## Build and asset paths

PWA setup runs after the HTML build, writes into `_build/html`, and reads
project metadata from `myst.yml`. The starter generates the manifest and
192/512 pixel regular and maskable PNG icons from `images/logo.svg`, copies
`offline.html` and `service-worker.js`, and injects registration and manifest
tags into the built HTML. A book may have its own asset names and theme.

Normalize `BASE_URL` to a path with leading and trailing slashes:
`/` locally or `/<repo>/` on Pages. Manifest `start_url`, manifest `scope`,
registration scope, icon URLs, and offline URLs must agree. Copy the worker
to the root of the book's output, so it can control the book's pages.
Use the book's own subject mark and existing branding for icons.

## Cache isolation is required on the shared origin

Every book on `quadriviumpress.com` shares CacheStorage. A worker must only
read and delete caches belonging to its own installation scope. The starter
and current books derive cache names from a book identifier and the full
registration scope:

```js
const base = new URL(self.registration.scope);
const VERSION = 'v2'; // Follow the target book's versioning.
const CACHE_PREFIX = `book-slug:${encodeURIComponent(base.href)}:`;
const STATIC_CACHE = `${CACHE_PREFIX}static-${VERSION}`;
const PAGE_CACHE = `${CACHE_PREFIX}pages-${VERSION}`;
```

On activation, delete obsolete caches only if their name starts with this
`CACHE_PREFIX`. Read from explicitly opened scope caches; a global
`caches.match()` can return another book's response. Do not globally delete
unrecognized caches, including when migrating away from old generic names.

Handle only GET requests with the same origin and a pathname under
`base.pathname`. Construct offline URLs relative to `base`, preserving the
trailing slash that separates `/book/` from `/book-other/`.

## Returning readers and offline fallback

MyST chapter JSON, configuration, and CSS can keep stable URLs across builds.
The current worker fetches with `cache: 'no-cache'` while online and caches
successful responses. On network failure, it checks only this installation's
page/static caches and serves the offline page for navigation. Storage quota
failures must not prevent a successful online response reaching the reader.

When validating a PWA change, cover a project base path and two installations
on one origin: one worker's activation must preserve the other's caches.
Also check that a changed chapter response reaches a returning reader and
that cached pages remain available offline. Follow the target book's existing
checks rather than assuming an HTML build exercises service worker behavior.
