/*
 * Radio Client 26.2 engine bridge.
 *
 * This class is intended for the 26.2/Eagler source build. The current
 * single-file wrapper can use the browser seam in src/radio-engine.js as soon
 * as this class is compiled into the engine.
 */
package net.minecraft.client;

import org.teavm.jso.JSBody;

public final class RadioOptionsBridge {
    private RadioOptionsBridge() {
    }

    public static void install() {
        install0();
    }

    public static boolean setOption(String key, String value) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft == null || minecraft.options == null) return false;
        Options o = minecraft.options;
        try {
            switch (key) {
                case "renderDistance": o.renderDistance().set(Integer.valueOf(value)); break;
                case "simulationDistance": o.simulationDistance().set(Integer.valueOf(value)); break;
                case "maxFps": o.framerateLimit().set(Integer.valueOf(value)); break;
                case "gamma": o.gamma().set(Double.valueOf(value)); break;
                case "guiScale": o.guiScale().set(Integer.valueOf(value)); break;
                case "enableVsync": o.enableVsync().set(Boolean.valueOf(value)); break;
                case "bobView": o.bobView().set(Boolean.valueOf(value)); break;
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
            o.save();
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    public static String getOption(String key) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft == null || minecraft.options == null) return null;
        Options o = minecraft.options;
        try {
            switch (key) {
                case "renderDistance": return String.valueOf(o.renderDistance().get());
                case "simulationDistance": return String.valueOf(o.simulationDistance().get());
                case "maxFps": return String.valueOf(o.framerateLimit().get());
                case "gamma": return String.valueOf(o.gamma().get());
                case "guiScale": return String.valueOf(o.guiScale().get());
                case "enableVsync": return String.valueOf(o.enableVsync().get());
                case "bobView": return String.valueOf(o.bobView().get());
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

    public static boolean available() {
        return true;
    }

    @JSBody(script =
        "globalThis.Radio26Options = globalThis.Radio26Options || {};" +
        "globalThis.Radio26Options.set = function(k,v) { return RadioOptionsBridge.setOption(k,String(v)); };" +
        "globalThis.Radio26Options.get = function(k) { return RadioOptionsBridge.getOption(k); };" +
        "globalThis.Radio26Options.available = function() { return RadioOptionsBridge.available(); };")
    private static native void install0();
}
