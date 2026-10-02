# Radio Client 26.2 engine patch

The live-settings problem exists because the current wrapper can write
`_eaglercraftX.g`, but that is persistent storage, not the already-running
Minecraft `Options` object.

## Bridge

`RadioOptionsBridge.java` is the 26.2-side bridge. It uses the real 26.2
`Options` / `OptionInstance` APIs and publishes:

- `Radio26Options.set(key, value)`
- `Radio26Options.get(key)`
- `Radio26Options.available()`
- `Radio26Options.reloadResources()`

The browser wrapper in `src/radio-engine.js` automatically uses that API when
the rebuilt engine provides it.

## Automatic source hookup

After `eagler-patcher create-dev` produces the authenticated 26.2 workspace,
run:

```bash
python3 scripts/install-radio-bridge.py /path/to/eagler-26_2
```

The helper copies the bridge into `net/minecraft/client` and inserts:

```java
RadioOptionsBridge.install();
```

immediately after the existing `this.options.save();` constructor call.

Generated/decompiled Minecraft sources stay in the local build workspace and
are not committed to this repository.

The 26.2 skeleton already supplies TeaVM JSO as a compile-time dependency.
TeaVM's upstream Maven repository currently lists 0.16.0-dev releases through
2026-10-01. citeturn0search2

This keeps the old compiled client usable until the real 26.2 engine is rebuilt,
while making the source-build integration repeatable.
