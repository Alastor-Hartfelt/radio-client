# Radio Client — engine and build audit

**Audit branch:** `radio-client`  
**Audit updated:** 2026-09-30

## What exists today

- `dist/web/radio/index.html` is the separate Radio-branded interface prototype.
- The existing Rise `build.py` expects an Eaglercraft 26.2 / Wispcraft single-file HTML input.
- `src/rise.js` and other root-level implementation files are inherited Rise Client code; they are not a clean-room Radio engine.
- `dist/web/index.html` and the payload binaries are checked-in generated output. Their presence does not make the build reproducible from a clean checkout.

## Newly identified candidate base

The user-provided repository https://github.com/Alastor-Hartfelt/eaglercraft-26.2 contains an `index.html` reported by GitHub as 75,576,620 bytes (about 75.6 MB decimal), and a short README saying “minecraft 26.2 in the browser” with credit to `o_xer`.

This is a promising lead for locating the intended 26.2 browser build. However:
- It is a fork of `3lit3-Pl4y3r/eaglercraft-26.2`.
- GitHub reports no recognized license for either repository.
- The repository contains only `README.md` and `index.html` on its main branch.
- It has not been established that this HTML is the specific Wispcraft build expected by Rise's build script, or that it is a drop-in replacement for `ref/wispcraft-26.2.html`.

**Do not automatically copy this HTML into the Radio repository or redistribute it.** First confirm the source project's permissions and inspect whether the existing build pipeline can consume it without modifying or misrepresenting the original engine.

## Reproducible-build blockers

The current build script expects these local inputs:

1. `ref/wispcraft-26.2.html` — ignored by Git via `.gitignore`.
2. `../BlueprintMod/blueprint.js` — a sibling dependency outside this repository.

The build script also reads local theme and `theme_extra` assets. Before a build can be reproduced, all required inputs must be accounted for and their versions recorded.

## Permission and licensing gate

There is no root `LICENSE` file on the Radio branch. The candidate Eaglercraft 26.2 repository also has no recognized license metadata. A missing license is not permission to copy or redistribute code.

Before publishing a playable build, verify the applicable permissions and notices for the game base, Wispcraft, BlueprintMod, inherited Rise implementation, assets, fonts, skins, and other bundled components. Keep the Radio interface work separate from inherited implementation until reuse rights are established.

## Next implementation milestone

1. Inspect the candidate base's source history and upstream attribution.
2. Confirm whether the owner permits the intended local use and public deployment.
3. Determine whether this HTML can be used as the engine input or whether a source/buildable version is needed.
4. Obtain missing build inputs from legitimate sources and record exact versions/hashes.
5. Reproduce a build in a clean environment before changing engine behavior.
6. Connect Radio's settings to actual engine options and measure performance; do not present mock controls as working game settings.

**Current status:** interface prototype plus a promising candidate engine file; no independently verified, reproducible Radio game build yet.
