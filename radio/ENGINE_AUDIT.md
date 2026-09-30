# Radio Client — engine and build audit

**Audit branch:** `radio-client`  
**Audit updated:** 2026-09-30

## What exists today

- `dist/web/radio/index.html` is the separate Radio-branded interface prototype.
- The existing Rise `build.py` expects an Eaglercraft 26.2 / Wispcraft single-file HTML input.
- `src/rise.js` and other root-level implementation files are inherited Rise Client code; they are not a clean-room Radio engine.
- `dist/web/index.html` and the payload binaries are checked-in generated output. Their presence does not make the build reproducible from a clean checkout.

## Candidate base: user's Eaglercraft 26.2 fork

The user owns https://github.com/Alastor-Hartfelt/eaglercraft-26.2. Its `index.html` is reported by GitHub as 75,576,620 bytes (about 75.6 MB decimal). The README describes it as “minecraft 26.2 in the browser” and credits `o_xer`.

The repository is a fork of https://github.com/3lit3-Pl4y3r/eaglercraft-26.2. The visible parent history shows:
- An initial `index.html` upload on 2026-09-15.
- A README credit update on 2026-09-21.
- The README attribution is only “credits to o_xer”; it does not provide a source URL, license terms, or redistribution permission.

GitHub reports no recognized license for either repository. The parent repository's visible root contains only `README.md` and `index.html`, and its issue list currently has no entries. These facts do not establish who owns all components in the bundled HTML or what upstream reuse rights apply.

Because the user owns the fork, there is no need to seek permission from the owner of the user's own fork. The remaining questions are provenance and rights for the original bundled HTML and any upstream components, plus whether it is compatible with the existing build pipeline.

This is a promising candidate for compatibility testing, but it has **not** been established that this HTML is the specific Wispcraft build expected by Rise's build script, or that it is a drop-in replacement for `ref/wispcraft-26.2.html`.

## What the Eaglercraft 26.2 patcher README clarifies

The supplied patcher documentation describes a **source patcher and project exporter**, not a complete game source/build distribution. It explicitly says the export omits the game build and important inputs.

Key requirements and limitations described in that documentation:
- Building the patcher GUI requires JDK 17; its JAR is generated locally rather than included.
- A Normal standalone HTML build requires the appropriate source project and additional pinned inputs. The documented pipeline lists an official 26.2 client JAR, Vineflower 1.12.0, Java 17, a pinned source patch bundle, a pinned project skeleton, Java 25, Node/npm, and authorized resource packs/EPKs as applicable.
- The source patch archive contains Mojang-derived Java changes and is omitted from the export. Other inputs such as decompiled game source, assets, resource overlays, media, project skeleton archives, and third-party mod binaries are also omitted.
- The README says the source folder has no license file and does not grant permission to reuse the code or external inputs.
- The maintainer's estimate for a full standalone HTML build is about 30 minutes on a capable PC; a recorded build took 41 minutes 46 seconds. The docs recommend 16 GiB RAM or more and say the current linker needs at least a 10 GiB build budget plus a system reserve.

This means the patcher folder alone is **not enough to recreate the game HTML**. It does provide a documented path if the complete, compatible source workspace and authorized pinned inputs are available. The patcher is also a different pipeline from Rise's current HTML-patching build script, so we should not assume the outputs or injection anchors match.

## Reproducible-build blockers

The current Rise build script expects these local inputs:

1. `ref/wispcraft-26.2.html` — ignored by Git via `.gitignore`.
2. `../BlueprintMod/blueprint.js` — a sibling dependency outside this repository.

It also expects a particular embedded `eag-inline-assets` block, a known boot-script anchor, and several local theme/`theme_extra` assets. The supplied Eaglercraft patcher docs do not establish that the user's HTML has these exact markers. We need to inspect the HTML structure or run a compatibility check before adapting the script.

## Permission and licensing gate

There is no root `LICENSE` file on the Radio branch, and GitHub reports no recognized license metadata for the candidate Eaglercraft repositories. The supplied patcher documentation itself says it grants no reuse permission. A missing license is not permission to copy or redistribute upstream code.

Before publishing a playable Radio build, verify the applicable permissions and notices for the game base, source patch bundle, Wispcraft, BlueprintMod, inherited Rise implementation, assets, fonts, skins, and other bundled components. Keep the independent Radio interface separate from inherited implementation until reuse rights are established.

## Next implementation milestone

1. Identify the original source/project behind the bundled HTML and clarify the `o_xer` attribution.
2. Check whether the user's HTML contains the exact payload and boot markers Rise's script requires.
3. If compatible, prototype a minimal build-script adaptation on `radio-client` only; otherwise choose between using the documented source-project pipeline (if all inputs are available and authorized) or adapting Radio to the HTML's actual structure.
4. Record exact input versions/hashes and reproduce the build in a clean environment before changing engine behavior.
5. Connect Radio's settings to actual engine options and measure performance; do not present mock controls as working game settings.

While source inputs or permissions remain unresolved, continue with independently authored Radio UI, documentation, and non-game-specific tooling.

**Current status:** interface prototype plus a candidate 26.2 HTML and a documented patcher workflow; no independently verified, reproducible Radio game build yet.


## Compatibility probe added (2026-09-30)

A read-only probe now lives at `radio/check_engine_compat.py`. It checks the literal payload, boot, module, icon, decoder, and WASM-worker anchors that the current `build.py` expects. It also validates the inline asset block's base64 length against its declared size.

A manual GitHub Actions workflow at `.github/workflows/check-radio-engine.yml` downloads the candidate HTML from the user's `eaglercraft-26.2` repository into the runner's temporary directory and runs the probe. It does not commit or publish the downloaded HTML. Trigger it from the repository's Actions tab on branch `radio-client`.

**Important:** the workflow has been added but has not yet been run. A passing probe would only establish anchor compatibility, not a successful full build or a browser launch. If anchors differ, adapt the build approach based on the actual HTML structure instead of running the existing patcher blindly.
