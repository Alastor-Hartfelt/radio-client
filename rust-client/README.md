# Radio Client 26.2 — Rust browser rewrite

**Target:** Radio Client / Eaglercraft Minecraft 26.2. The Minecraft 1.21.11 Rust project is separate.

**Status:** Experimental scaffold only. Not yet compiled, browser-tested, or playable.

## Chosen architecture

- **Rust + WebAssembly** for portable client logic.
- **wgpu / WebGPU** as the primary browser 3D rendering backend.
- **WebGL2 fallback** where supported by the chosen wgpu version, for devices or browsers without working WebGPU.
- **JavaScript/TypeScript browser shell** for startup, compatibility checks, input and browser APIs.
- **WebSocket multiplayer transport**, subject to implementing/testing compatibility with the existing Radio/Eagler 26.2 network protocol.

WebGPU is not universally available and does not guarantee higher FPS than WebGL2. Test performance and renderer behavior on target devices before making performance claims.

## Build existing scaffold

Install Rust and wasm-pack, then from `rust-client`:

```sh
wasm-pack build --target web --release
python3 -m http.server 8080
```

Open http://localhost:8080/.

## Implementation roadmap

1. CI build and smoke test of current Rust/WASM scaffold.
2. Add a minimal wgpu renderer with WebGPU-first adapter selection and a supported WebGL2 fallback.
3. Add assets, input, and frame scheduling.
4. Port/reimplement 26.2 world, gameplay, and compatible WebSocket networking.
5. Verify actual multiplayer playability and benchmark mobile and desktop browsers.

Keep the original `radio-client` branch unchanged. Do not claim that a Rust renderer alone makes Minecraft playable.
