# Radio Client

Radio Client is the black-and-red edition of the Rise Client project, targeting Eaglercraft **26.2** (Wasm-GC).

## Direction

- **Theme:** near-black panels, dark crimson surfaces, red highlights and a restrained glow.
- **Performance:** preserve the existing performance work instead of replacing it with a new client architecture.
- **Features:** retain Rise's existing video settings, mod menu, HUD options, cosmetic skins, low-end-device mode, payload caching and WebAssembly caching where possible.
- **Compatibility:** Eaglercraft 26.2 only.

## Current branch status

The `radio-client` branch contains the Radio UI palette and source/build branding updates. The checked-in web build is still the previously generated build until the project can be rebuilt and tested.

## Build inputs currently needed

The build script expects these files outside the normal tracked source tree:

- `ref/wispcraft-26.2.html`
- `../BlueprintMod/blueprint.js`

The `ref/` directory is intentionally gitignored, and the BlueprintMod file is a sibling dependency. As a result, a clean checkout alone is not yet enough to reproduce the build.

## Licensing and redistribution

The project owner has confirmed that the required permission to publish this build has been obtained. Keep the permission record and follow any attribution or notice conditions that came with it. This confirmation is specific to the project’s deployment; it does not automatically license unrelated forks or third-party components for other uses.

## Original project

This branch is based on Rise Client. Its existing optimization and feature code is being preserved as the Radio Client foundation.
