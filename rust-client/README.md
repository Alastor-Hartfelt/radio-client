# Radio Client Rust/WebAssembly rewrite

This is an **initial scaffold**, not a playable Minecraft client. It does not yet implement rendering, Minecraft protocol, assets, authentication, or multiplayer.

## Build locally

Install Rust and wasm-pack, then:

```sh
cd rust-client
wasm-pack build --target web --release
python3 -m http.server 8080
```

Open http://localhost:8080/rust-client/ from the repository root.

## Milestones
1. Compile and serve Rust/WASM in a browser.
2. Add a GPU renderer, input handling, and asset loading.
3. Implement world/chunk representation and protocol-compatible network transport.
4. Implement player movement, collision, entities, inventory, and gameplay.
5. Validate actual multiplayer connections against a permitted test server.

Keep the existing Java-based Radio Client on its original branch. No claim of gameplay or server compatibility is made until tested.
