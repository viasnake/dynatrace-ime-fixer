# Dynatrace IME Enter Fix

Manifest V3 extension for Dynatrace apps pages that suppresses accidental `Enter` submissions during IME composition.

## Support Matrix

- Browsers: Chrome, Firefox
- Operating systems: Windows, macOS
- Target pages: `https://*.apps.dynatrace.com/*`

## Project Principles

This repository follows UNIX-style design:

- one responsibility per module
- explicit event I/O boundaries
- small composable units
- minimal runtime dependencies and tooling

The content script is split into focused files under `content/` instead of one monolithic script.

## Runtime Architecture

- `manifest.json`: MV3 registration and browser-specific metadata
- `content/namespace.js`: shared namespace bootstrap
- `content/core.js`: immutable behavior constants, runtime state, and suppression decision rules
- `content/dom.js`: event target normalization, editable target checks, and event-stop helper
- `content/runtime.js`: composition and keyboard handlers, listener wiring, and idempotent initialization
- `archive/content-modules-v1/`: archived pre-consolidation 8-module content script layout
- `archive/content.legacy.js`: archived monolithic pre-refactor implementation

## Behavior

The extension starts at `document_start`, runs in all matching frames, and listens in capture phase.

If the key is `Enter`, the event is suppressed only when both of these are true:

- target is an editable field (`input`, `textarea`, or `contenteditable`)
- at least one IME condition is true:
  - composition is currently active (`compositionstart` observed)
  - browser reports active composition (`event.isComposing === true`)
  - browser emits a late `Enter` right after `compositionend` on the same element

Suppression uses:

- `event.preventDefault()`
- `event.stopImmediatePropagation()`
- `event.stopPropagation()`

It also blocks a short follow-up `keyup` window for `Enter` to cover UIs that submit on key release.

## Install (Unpacked)

### Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select this repository directory

### Firefox

1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on...**
3. Select `manifest.json` in this repository

## Package for Release

Install runtime tools with mise first:

```bash
mise install
```

Tool versions are pinned in `.mise.toml`.

Run from repository root:

```bash
npm run package
```

Output is generated under `dist/`.

To build a single browser archive:

```bash
npm run package:chrome
npm run package:firefox
```

## CI/CD

GitHub Actions is used for build verification and release artifact publishing.

- CI workflow (`.github/workflows/ci.yml`)
  - triggers: pull request to `master`, push to `master`, manual run
  - builds Chrome and Firefox ZIP artifacts
  - uploads `dist/*.zip` as workflow artifacts
- Release workflow (`.github/workflows/release.yml`)
  - triggers: push to `master`, manual run
  - runs `semantic-release` to determine the next version from commit messages
  - updates `manifest.json` version, builds ZIP artifacts, and publishes GitHub Release assets

Release operation requires Conventional Commits.

Examples:

- `fix: prevent duplicate Enter suppression after compositionend`
- `feat: support additional editable target detection`
- `feat!: change event suppression timing`
- `feat: ...` with `BREAKING CHANGE:` footer for major releases

No manual tag creation is required.

Note: lint/typecheck/test jobs are not configured in this repository yet.

Both CI and Release workflows use `jdx/mise-action` and `.mise.toml` to align tool versions with local development.

## Manual Verification Matrix

Run all checks on each target combination:

- Chrome + Windows
- Chrome + macOS
- Firefox + Windows
- Firefox + macOS

For each cell:

1. Open a page under `https://*.apps.dynatrace.com/*`
2. Reload the page after loading the extension
3. Focus a target input field
4. Type Japanese text with IME
5. Press `Enter` during composition
6. Confirm composition commits without unintended submit
7. Confirm normal `Enter` works outside composition
8. Confirm behavior right after `compositionend`
9. If target UI is in an iframe, confirm behavior there as well

## Firefox Publishing Notes

- `browser_specific_settings.gecko.id`: `dynatrace-ime-fixer@alflag.org`
- `browser_specific_settings.gecko.strict_min_version`: `109.0`
- `browser_specific_settings.gecko.data_collection_permissions.required`: `none`

## Release Management

- Version source of truth: `semantic-release` (Conventional Commits)
- `manifest.json` version is synchronized during the release prepare step
- History management: git commit log and GitHub Releases
- No `CHANGELOG.md` is maintained in this repository

## Security and Privacy

- No remote calls, telemetry, or data collection
- Reads key and composition events only to prevent accidental submit behavior
- No background script, popup, or options page
- No additional extension permissions

## License

Apache License 2.0.
