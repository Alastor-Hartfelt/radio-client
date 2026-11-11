/*
 * Radio Client 26.2 engine bridge.
 *
 * This class is intended for the 26.2/Eagler source build. The current
 * single-file wrapper can use the browser seam in src/radio-engine.js as soon
 * as this class is compiled into the engine.
 */
package net.minecraft.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.server.level.ParticleStatus;
import net.minecraft.server.packs.repository.PackRepository;
import org.teavm.jso.JSBody;
import org.teavm.jso.JSFunctor;
import org.teavm.jso.JSObject;

public final class RadioOptionsBridge {
    private RadioOptionsBridge() {
    }

    private static final String RADIO_PACK = "file/rise_active";
    private static KeyMapping modMenuKey;

    public static void install() {
        Options options = Minecraft.getInstance().options;
        if (modMenuKey == null) {
            // Native Controls owns remapping, conflict highlighting, reset and saving.
            String name = "Radio Client Mod Menu";
            InputConstants.Key saved = options.eaglerResolveSavedKeyMapping(name);
            modMenuKey = new KeyMapping(name, InputConstants.Type.KEYSYM, 344, KeyMapping.Category.MISC);
            if (!options.eaglerRegisterKeyMappings(List.of(modMenuKey), Collections.singletonList(saved))) {
                throw new IllegalStateException("Could not register Radio mod-menu keybind");
            }
        }
        install0(RadioOptionsBridge::getOption, RadioOptionsBridge::applyOptions,
                RadioOptionsBridge::setResourcePack, RadioOptionsBridge::reloadResources);
    }

    private static boolean canOpenModMenu() {
        var screen = Minecraft.getInstance().gui.screen();
        // Do not intercept typing or the Controls screen while it captures a new binding.
        return screen == null || screen instanceof TitleScreen || screen instanceof PauseScreen;
    }

    public static boolean handleModMenuKey(int action, KeyEvent event) {
        if (action != 1 || modMenuKey == null || !canOpenModMenu() || !modMenuKey.matches(event)) return false;
        openModMenu();
        return true;
    }

    public static boolean handleModMenuMouse(int action, int button) {
        if (action != 1 || modMenuKey == null || !canOpenModMenu()
                || !modMenuKey.matches(InputConstants.Type.MOUSE.getOrCreate(button))) return false;
        openModMenu();
        return true;
    }

    @JSBody(script = "window.dispatchEvent(new Event('radio-open-mod-menu'));")
    public static native void openModMenu();

    @JSBody(script = "return !!(window.rise && window.rise.mods.passwordHider === true);")
    private static native boolean passwordHiderEnabled();

    public static boolean isMaskedLogin(String command) {
        return passwordStart(command) >= 0;
    }

    public static String maskLoginPassword(String command, String text, int offset) {
        int start = passwordStart(command);
        if (start < 0 || start - offset >= text.length()) return text;
        int visible = Math.max(0, start - offset);
        return text.substring(0, visible) + "*".repeat(text.length() - visible);
    }

    private static int passwordStart(String command) {
        if (!passwordHiderEnabled()) return -1;
        String prefix = "/login";
        int start = 0;
        while (start < command.length() && Character.isWhitespace(command.charAt(start))) start++;
        int end = start + prefix.length();
        if (end >= command.length() || !command.regionMatches(true, start, prefix, 0, prefix.length())
                || !Character.isWhitespace(command.charAt(end))) return -1;
        return end + 1;
    }

    private static void applyOptions(String[] keys, String[] values, ApplyResult result) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft == null || minecraft.options == null || keys.length != values.length) {
            result.complete(keys);
            return;
        }
        // Options.save() can use Eagler's async filesystem. Run it on the client loop.
        minecraft.schedule(() -> {
            List<String> rejected = new ArrayList<>();
            Options options = minecraft.options;
            for (int i = 0; i < keys.length; i++) {
                if (!applyOption(options, keys[i], values[i])) rejected.add(keys[i]);
            }
            try {
                if (rejected.size() < keys.length) options.save();
            } catch (RuntimeException e) {
                result.complete(keys);
                return;
            }
            result.complete(rejected.toArray(String[]::new));
        });
    }

    private static boolean applyOption(Options o, String key, String value) {
        try {
            switch (key) {
                case "renderDistance": o.renderDistance().set(Integer.valueOf(value)); break;
                case "simulationDistance": o.simulationDistance().set(Integer.valueOf(value)); break;
                case "maxFps": o.framerateLimit().set(Integer.valueOf(value)); break;
                case "gamma": o.gamma().set(Double.valueOf(value)); break;
                case "guiScale": o.guiScale().set(Integer.valueOf(value)); break;
                case "enableVsync": o.enableVsync().set(Boolean.valueOf(value)); break;
                case "bobView": o.bobView().set(Boolean.valueOf(value)); break;
                case "inactivityFpsLimit":
                    o.inactivityFpsLimit().set(
                        "minimized".equalsIgnoreCase(value)
                            ? InactivityFpsLimit.MINIMIZED
                            : InactivityFpsLimit.AFK
                    );
                    break;
                case "renderClouds":
                    if ("false".equalsIgnoreCase(value) || "off".equalsIgnoreCase(value))
                        o.cloudStatus().set(CloudStatus.OFF);
                    else if ("fast".equalsIgnoreCase(value))
                        o.cloudStatus().set(CloudStatus.FAST);
                    else
                        o.cloudStatus().set(CloudStatus.FANCY);
                    break;
                case "textureFiltering":
                    switch (value) {
                        case "0": o.textureFiltering().set(TextureFilteringMethod.NONE); break;
                        case "1": o.textureFiltering().set(TextureFilteringMethod.RGSS); break;
                        case "2": o.textureFiltering().set(TextureFilteringMethod.ANISOTROPIC); break;
                        default: return false;
                    }
                    break;
                case "attackIndicator":
                    switch (value) {
                        case "0": o.attackIndicator().set(AttackIndicatorStatus.OFF); break;
                        case "1": o.attackIndicator().set(AttackIndicatorStatus.CROSSHAIR); break;
                        case "2": o.attackIndicator().set(AttackIndicatorStatus.HOTBAR); break;
                        default: return false;
                    }
                    break;
                case "particles":
                    switch (value) {
                        case "0": o.particles().set(ParticleStatus.ALL); break;
                        case "1": o.particles().set(ParticleStatus.DECREASED); break;
                        case "2": o.particles().set(ParticleStatus.MINIMAL); break;
                        default: return false;
                    }
                    break;
                case "eaglerPerformanceCounters":
                    o.showPerformanceCounters().set(Boolean.valueOf(value));
                    break;
                case "toggleSprint": o.toggleSprint().set(Boolean.valueOf(value)); break;
                case "toggleCrouch": o.toggleCrouch().set(Boolean.valueOf(value)); break;
                case "ao": o.ambientOcclusion().set(Boolean.valueOf(value)); break;
                case "cloudRange": o.cloudRange().set(Integer.valueOf(value)); break;
                case "weatherRadius": o.weatherRadius().set(Integer.valueOf(value)); break;
                case "entityShadows": o.entityShadows().set(Boolean.valueOf(value)); break;
                case "cutoutLeaves": o.cutoutLeaves().set(Boolean.valueOf(value)); break;
                case "improvedTransparency": o.improvedTransparency().set(Boolean.valueOf(value)); break;
                case "vignette": o.vignette().set(Boolean.valueOf(value)); break;
                case "menuBackgroundBlurriness": o.menuBackgroundBlurriness().set(Integer.valueOf(value)); break;
                case "mipmapLevels": o.mipmapLevels().set(Integer.valueOf(value)); break;
                case "biomeBlendRadius": o.biomeBlendRadius().set(Integer.valueOf(value)); break;
                case "chunkSectionFadeInTime": o.chunkSectionFadeInTime().set(Double.valueOf(value)); break;
                case "entityDistanceScaling": o.entityDistanceScaling().set(Double.valueOf(value)); break;
                case "prioritizeChunkUpdates":
                    o.prioritizeChunkUpdates().set(PrioritizeChunkUpdates.values()[Integer.parseInt(value)]);
                    break;
                case "syncChunkWrites": o.syncWrites = Boolean.parseBoolean(value); break;
                case "graphicsPreset":
                    if (!"custom".equals(value)) return false;
                    o.graphicsPreset().set(GraphicsPreset.CUSTOM);
                    break;
                case "rawMouseInput": o.rawMouseInput().set(Boolean.valueOf(value)); break;
                case "pauseOnLostFocus": o.pauseOnLostFocus = Boolean.valueOf(value); break;
                case "showAutosaveIndicator": o.showAutosaveIndicator().set(Boolean.valueOf(value)); break;
                case "reducedDebugInfo": o.reducedDebugInfo().set(Boolean.valueOf(value)); break;
                case "damageTiltStrength": o.damageTiltStrength().set(Double.valueOf(value)); break;
                case "fovEffectScale": o.fovEffectScale().set(Double.valueOf(value)); break;
                case "screenEffectScale": o.screenEffectScale().set(Double.valueOf(value)); break;
                case "hideLightningFlashes": o.hideLightningFlash().set(Boolean.valueOf(value)); break;
                default: return false;
            }
            return true;
        } catch (RuntimeException e) {
            return false;
        }
    }

    public static String getOption(String key) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft == null || minecraft.options == null) return null;
        Options o = minecraft.options;
        try {
            switch (key) {
                case "radioModMenuKey": return modMenuKey == null ? null : modMenuKey.saveString();
                case "renderDistance": return String.valueOf(o.renderDistance().get());
                case "simulationDistance": return String.valueOf(o.simulationDistance().get());
                case "maxFps": return String.valueOf(o.framerateLimit().get());
                case "gamma": return String.valueOf(o.gamma().get());
                case "guiScale": return String.valueOf(o.guiScale().get());
                case "enableVsync": return String.valueOf(o.enableVsync().get());
                case "bobView": return String.valueOf(o.bobView().get());
                case "inactivityFpsLimit": return o.inactivityFpsLimit().get() == InactivityFpsLimit.MINIMIZED ? "minimized" : "afk";
                case "renderClouds":
                    switch (o.cloudStatus().get()) {
                        case OFF: return "false";
                        case FAST: return "fast";
                        default: return "true";
                    }
                case "textureFiltering":
                    switch (o.textureFiltering().get()) {
                        case NONE: return "0";
                        case RGSS: return "1";
                        default: return "2";
                    }
                case "attackIndicator":
                    switch (o.attackIndicator().get()) {
                        case OFF: return "0";
                        case CROSSHAIR: return "1";
                        default: return "2";
                    }
                case "particles":
                    switch (o.particles().get()) {
                        case ALL: return "0";
                        case DECREASED: return "1";
                        default: return "2";
                    }
                case "eaglerPerformanceCounters": return String.valueOf(o.showPerformanceCounters().get());
                case "toggleSprint": return String.valueOf(o.toggleSprint().get());
                case "toggleCrouch": return String.valueOf(o.toggleCrouch().get());
                case "ao": return String.valueOf(o.ambientOcclusion().get());
                case "cloudRange": return String.valueOf(o.cloudRange().get());
                case "weatherRadius": return String.valueOf(o.weatherRadius().get());
                case "entityShadows": return String.valueOf(o.entityShadows().get());
                case "cutoutLeaves": return String.valueOf(o.cutoutLeaves().get());
                case "improvedTransparency": return String.valueOf(o.improvedTransparency().get());
                case "vignette": return String.valueOf(o.vignette().get());
                case "menuBackgroundBlurriness": return String.valueOf(o.menuBackgroundBlurriness().get());
                case "mipmapLevels": return String.valueOf(o.mipmapLevels().get());
                case "biomeBlendRadius": return String.valueOf(o.biomeBlendRadius().get());
                case "chunkSectionFadeInTime": return String.valueOf(o.chunkSectionFadeInTime().get());
                case "entityDistanceScaling": return String.valueOf(o.entityDistanceScaling().get());
                case "prioritizeChunkUpdates": return String.valueOf(o.prioritizeChunkUpdates().get().ordinal());
                case "syncChunkWrites": return String.valueOf(o.syncWrites);
                case "graphicsPreset": return o.graphicsPreset().get().getSerializedName();
                case "rawMouseInput": return String.valueOf(o.rawMouseInput().get());
                case "pauseOnLostFocus": return String.valueOf(o.pauseOnLostFocus);
                case "showAutosaveIndicator": return String.valueOf(o.showAutosaveIndicator().get());
                case "reducedDebugInfo": return String.valueOf(o.reducedDebugInfo().get());
                case "damageTiltStrength": return String.valueOf(o.damageTiltStrength().get());
                case "fovEffectScale": return String.valueOf(o.fovEffectScale().get());
                case "screenEffectScale": return String.valueOf(o.screenEffectScale().get());
                case "hideLightningFlashes": return String.valueOf(o.hideLightningFlash().get());
                default: return null;
            }
        } catch (Throwable t) {
            return null;
        }
    }

    public static boolean reloadResources() {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft == null) return false;
        try {
            minecraft.schedule(minecraft::reloadResourcePacks);
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    private static void setResourcePack(boolean enabled, PackResult result) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft == null || minecraft.options == null) {
            result.complete(false);
            return;
        }
        minecraft.schedule(() -> {
            try {
                PackRepository packs = minecraft.getResourcePackRepository();
                packs.reload();
                if (enabled && !packs.isAvailable(RADIO_PACK)) {
                    result.complete(false);
                    return;
                }
                List<String> selected = new ArrayList<>(packs.getSelectedIds());
                selected.removeIf(RadioOptionsBridge::isRadioPack);
                if (enabled) selected.add(RADIO_PACK);
                packs.setSelected(selected);
                minecraft.reloadResourcePacks().whenComplete((ignored, error) -> {
                    if (error != null || packs.getSelectedIds().contains(RADIO_PACK) != enabled) {
                        result.complete(false);
                        return;
                    }
                    try {
                        Options o = minecraft.options;
                        o.resourcePacks.removeIf(RadioOptionsBridge::isRadioPack);
                        o.incompatibleResourcePacks.removeIf(RadioOptionsBridge::isRadioPack);
                        if (enabled) o.resourcePacks.add(RADIO_PACK);
                        o.save();
                        result.complete(true);
                    } catch (RuntimeException e) {
                        result.complete(false);
                    }
                });
            } catch (RuntimeException e) {
                result.complete(false);
            }
        });
    }

    private static boolean isRadioPack(String id) {
        return id.startsWith("file/rise_");
    }

    @JSFunctor public interface OptionGetter extends JSObject { String get(String key); }
    @JSFunctor public interface OptionsApply extends JSObject { void apply(String[] keys, String[] values, ApplyResult result); }
    @JSFunctor public interface ApplyResult extends JSObject { void complete(String[] rejected); }
    @JSFunctor public interface PackSetter extends JSObject { void set(boolean enabled, PackResult result); }
    @JSFunctor public interface PackResult extends JSObject { void complete(boolean success); }
    @JSFunctor public interface ResourceReloader extends JSObject { boolean reload(); }

    @JSBody(params = {"get", "apply", "setResourcePack", "reloadResources"}, script =
        "globalThis.Radio26Options = { get: get, apply: apply, setResourcePack: setResourcePack,"
        + " set: function(k,v) { return new Promise(function(done) {"
        + " apply([k], [String(v)], function(rejected) { done(rejected.length === 0); }); }); },"
        + " reloadResources: reloadResources, modMenuKeybind: true, nativePauseMods: true, passwordHider: true,"
        + " available: function() { return true; } };")
    private static native void install0(OptionGetter get, OptionsApply apply,
            PackSetter setResourcePack, ResourceReloader reloadResources);
}
