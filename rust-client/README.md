# Radio Client — Minecraft Java 1.21.11 Rust/WebAssembly rewrite

**Target Minecraft version: Java Edition 1.21.11.**

This branch is an experimental independent Rust/WASM rewrite. The current code is a browser initialization scaffold **only**; it is not yet a Minecraft renderer, playable game, or working multiplayer client.

## Architecture decision

- Rust compiled to WebAssembly for game state, protocol handling, simulation and client logic.
- Browser JavaScript glue only where required for DOM, input, graphics and WebSocket APIs.
- Start with WebGL2 for wider browser compatibility; consider WebGPU as an optional future backend.
- Implement the Minecraft Java 1.21.11 protocol, not the older 1.12.2 or 26.2 protocols.
- Browser WebSocket connections require a compatible WebSocket-to-Minecraft gateway/proxy; browsers cannot directly open raw Minecraft TCP sockets.
- Keep the existing Java-based Radio Client untouched on its original branch.
- Reuse third-party crates only after checking version compatibility and licenses; do not assume Android-native Starling code works in browsers.

## Build locally

Install Rust and wasm-pack:

```sh
cd rust-client
wasm-pack build --target web --release
python3 -m http.server 8080
```

Open http://localhost:8080/rust-client/ from the repository root.

## Development milestones

1. CI builds and smoke-tests the browser WASM scaffold.
2. WebGL2 renderer, input and asset-loading foundations.
3. Protocol 1.21.11 codec, packet framing, compression, login/configuration/play state machine, and WebSocket gateway support.
4. Chunk decoding and rendering, player controls, physics, entities, inventory and GUI.
5. Connect to an authorized 1.21.11 test server; verify actual gameplay and performance.

Do not claim multiplayer support or browser playability until these milestones are implemented and tested.
