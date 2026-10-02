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

The browser wrapper in `src/radio-engine.js` automatically uses that API when
the rebuilt engine provides it.

## Engine hookup

The 26.2 source build must call:

```java
RadioOptionsBridge.install();
```

after `Minecraft.options` has been constructed. In the vanilla 26.2
constructor, the safe insertion point is immediately after the existing
`this.options.save();` during startup.

This keeps the bridge absent from the old compiled client until the real 26.2
engine is rebuilt, so the existing client remains usable while the source
engine is being integrated.
