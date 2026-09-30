# Radio Client — engine and build audit

**Audit branch:** `radio-client`  
**Audited commit:** `81f8594d4350e40075dbbfbc166ce5113d2676e3`

## What exists today

- `dist/web/radio/index.html` is the separate Radio-branded interface prototype.
- `build.py` describes a build based on an Eaglercraft 26.2 / Wispcraft single-file HTML input.
- `src/rise.js` and other root-level implementation files are inherited Rise Client code; they are not a clean-room Radio engine.
- `dist/web/index.html` and the payload binaries are checked-in generated output. Their presence does not make the build reproducible from a clean checkout.

## Reproducible-build blockers

The current build script expects these local inputs:

1. `ref/wispcraft-26.2.html` — ignored by Git via `.gitignore`.
2. `../BlueprintMod/blueprint.js` — a sibling dependency outside this repository.

The build script also reads local theme and `theme_extra` assets. Before a build can be reproduced, all required inputs must be accounted for and their versions recorded.

## Permission and licensing gate

There is no root `LICENSE` file on this branch. The README records that the upstream Wispcraft repository has no declared license; this must be checked against the actual upstream repository before relying on it. A missing license is not permission to copy or redistribute the code.

Before publishing a playable build, verify the applicable permissions and notices for the game base, Wispcraft, BlueprintMod, inherited Rise implementation, assets, fonts, skins, and other bundled components. Keep the Radio interface work separate from inherited implementation until reuse rights are established.

## Next implementation milestone

1. Locate the exact Eaglercraft 26.2 / Wispcraft base and its terms.
2. Confirm whether the owner permits the intended local use and public deployment.
3. Obtain the missing build inputs from legitimate sources and record exact versions/hashes.
4. Reproduce a build in a clean environment before changing engine behavior.
5. Connect Radio's settings to actual engine options and measure performance; do not present mock controls as working game settings.

**Current status:** interface prototype only; no independently verified, reproducible Radio game build yet.
