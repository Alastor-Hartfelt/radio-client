#!/usr/bin/env python3
"""Install the Radio Client 26.2 JavaScript bridge into a generated Eagler source tree.

This is deliberately a post-decompile source step: generated Minecraft sources are
never committed to the Radio Client repository.
"""
from pathlib import Path
import argparse
import re
import shutil

HERE = Path(__file__).resolve().parent.parent
BRIDGE = HERE / "engine-patch" / "RadioOptionsBridge.java"

def find_java_root(workspace: Path) -> Path:
    candidates = [
        workspace / "game" / "src" / "main" / "java",
        workspace / "src" / "main" / "java",
    ]
    for root in candidates:
        if (root / "net" / "minecraft").is_dir():
            return root
    raise SystemExit("Could not find generated Java source root")

def install_password_hider(client: Path) -> None:
    bridge = "net.minecraft.client.RadioOptionsBridge"
    patches = {
        "screens/ChatScreen.java": [
            (
                "FormattedCharSequence formatChat(final String text, final int offset) {",
                f"\n        String masked = {bridge}.maskLoginPassword(this.input.getValue(), text, offset);"
                "\n        if (masked != text) return FormattedCharSequence.forward(masked, Style.EMPTY);",
            ),
            (
                "protected MutableComponent createNarrationMessage() {",
                "\n                String value = this.getValue();"
                f"\n                if ({bridge}.isMaskedLogin(value)) {{"
                f"\n                    return Component.literal({bridge}.maskLoginPassword(value, value, 0));"
                "\n                }",
            ),
            (
                "if (addToRecent) {",
                f"if (addToRecent && !{bridge}.isMaskedLogin(msg)) {{",
            ),
            (
                "if (this.shouldDiscardDraft() || StringUtils.isBlank(this.initial)) {",
                f"if (this.shouldDiscardDraft() || StringUtils.isBlank(this.initial) || {bridge}.isMaskedLogin(this.initial)) {{",
            ),
        ],
        "components/CommandSuggestions.java": [
            (
                "String command = this.input.getValue();",
                f"\n        if ({bridge}.isMaskedLogin(command)) {{"
                "\n            this.close();"
                "\n            this.currentParseIsCommand = true;"
                "\n            return;"
                "\n        }",
            ),
        ],
    }
    for relative, hooks in patches.items():
        path = client / "gui" / relative
        source = path.read_text(encoding="utf-8")
        for anchor, code in hooks:
            # For insertions the anchor remains in the generated code.
            replacement = anchor + code if code.startswith("\n") else code
            if replacement in source:
                continue
            if source.count(anchor) != 1:
                raise SystemExit(f"{path.name} has no unique password hider anchor: {anchor}")
            source = source.replace(anchor, replacement, 1)
        path.write_text(source, encoding="utf-8")
        print(f"patched {path}")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path, help="generated 26.2/Eagler workspace")
    args = ap.parse_args()
    workspace = args.workspace.resolve()
    java_root = find_java_root(workspace)
    client = java_root / "net" / "minecraft" / "client"
    minecraft = client / "Minecraft.java"
    target = client / "RadioOptionsBridge.java"
    if not minecraft.is_file():
        raise SystemExit(f"Missing generated source: {minecraft}")
    if not BRIDGE.is_file():
        raise SystemExit(f"Missing bridge source: {BRIDGE}")
    source = minecraft.read_text(encoding="utf-8")
    marker = "RadioOptionsBridge.install();"
    if marker not in source:
        anchor = "this.options.save();"
        if anchor not in source:
            raise SystemExit("Minecraft.java has no expected this.options.save(); anchor")
        source = source.replace(anchor, anchor + "\n\t\tRadioOptionsBridge.install();", 1)
        minecraft.write_text(source, encoding="utf-8")
        print(f"patched {minecraft}")
    else:
        print(f"already patched {minecraft}")
    shutil.copy2(BRIDGE, target)
    print(f"installed {target}")

    # Run inside the native window check, before normal screen/game input dispatch.
    for filename, method, hook in [
        ("KeyboardHandler.java", "private void keyPress(", "RadioOptionsBridge.handleModMenuKey(action, event)"),
        ("MouseHandler.java", "private void onButton(", "RadioOptionsBridge.handleModMenuMouse(action, rawButtonInfo.button())"),
    ]:
        path = client / filename
        text = path.read_text(encoding="utf-8")
        call = f"if ({hook}) return;"
        if call not in text:
            anchor = "this.minecraft.getFramerateLimitTracker().onInputReceived();"
            start = text.index(method)
            pos = text.index(anchor, start)
            if pos - start > 500:
                raise SystemExit(f"{filename} has no expected native input anchor")
            pos += len(anchor)
            path.write_text(text[:pos] + "\n            " + call + text[pos:], encoding="utf-8")
            print(f"patched {path}")

    pause_screen = client / "gui" / "screens" / "PauseScreen.java"
    text = pause_screen.read_text(encoding="utf-8")
    action = "net.minecraft.client.RadioOptionsBridge.openModMenu()"
    if action not in text:
        start = text.index("private void createPauseMenu()")
        anchor = re.search(r"^([ \t]+)gridLayout\.arrangeElements\(\);$", text[start:], re.M)
        if anchor is None:
            raise SystemExit("PauseScreen.java has no expected pause grid layout anchor")
        pos = start + anchor.start()
        indent = anchor[1]
        button = (
            f'{indent}helper.addChild(Button.builder(Component.literal("Mods"),\n'
            f"{indent}    button -> {action}).width(204).build(), 2);\n"
        )
        pause_screen.write_text(text[:pos] + button + text[pos:], encoding="utf-8")
        print(f"patched {pause_screen}")

    install_password_hider(client)

if __name__ == "__main__":
    main()
