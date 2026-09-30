# Radio Client — independent scaffold

Radio Client is being developed as a distinct client project, with original branding and UI. This directory is an **independent interface prototype**, not a playable Minecraft client.

## Status

- [x] Original black-and-red UI direction and Radio emblem
- [x] Responsive navigation and working browser-only interface preferences
- [x] Clearly marked performance-setting placeholders (no fake FPS claims)
- [ ] Select an engine/base whose license permits the intended use
- [ ] Establish reproducible source/build inputs
- [ ] Implement engine-connected settings
- [ ] Test Eaglercraft 26.2 compatibility and measure performance
- [ ] Verify all licenses and notices before public redistribution

## Important separation

The repository still contains inherited Rise Client files elsewhere. Those files are **not** a clean-room implementation and must not be treated as cleared for redistribution. Keep the independent Radio scaffold in `radio/` and do not copy inherited implementation code into it unless the relevant permissions are verified.

## Run / preview

When deployed with `dist/web` as the static output directory, open `/radio/`. The preview uses the Radio logo asset hosted in this repository's public raw-content URL. If this project is moved to a new repository, update the logo URL to the new asset path.

## Design principles

1. Original Radio branding and interface.
2. Performance changes must be measured on the connected engine.
3. No fake FPS counters or controls that imply an engine feature is already implemented.
4. No public playable distribution until the base engine and included components are license-checked.
