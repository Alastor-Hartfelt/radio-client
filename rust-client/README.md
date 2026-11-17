# Radio Client — Minecraft 26.2 Rust/WebAssembly experiment

**Target: existing Radio Client / Eaglercraft Minecraft 26.2.** Minecraft Java 1.21.11 is a separate project.

This branch is an experimental Rust/WASM rewrite of Radio Client. The current code is a browser initialization scaffold only: **not a playable Minecraft client**.

## Architecture

- Preserve the existing Radio Client 26.2 behavior and branding as the compatibility target.
- Rust compiled to WebAssembly for suitable game logic, state, and rendering support.
- Use browser APIs for input, graphics and WebSocket networking.
- Prefer incremental reuse and porting over an unsupported claim that the full Minecraft Java game can be rewritten quickly.
- Keep original `radio-client` branch untouched.
- Do not assume existing Eaglercraft protocol compatibility without implementing and testing it.

## Build scaffold

Install Rust and wasm-pack, then run from `rust-client`:

```sh
wasm-pack build --target web --release
python3 -m http.server 8080
```

Open http://localhost:8080/ if serving from `rust-client`.

## Milestones

1. Compile and browser-test Rust/WASM scaffold.
2. Add graphics, input, and asset loading.
3. Investigate reusable Radio Client 26.2 systems and browser-compatible multiplayer networking.
4. Implement or port rendering, world handling, controls and game systems.
5. Validate actual 26.2 gameplay and server connectivity.

**Status:** Scaffold committed, not yet compiled or browser-tested, no gameplay implemented.
