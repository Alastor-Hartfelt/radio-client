/*
 * Radio Client 26.2 live-engine seam.
 *
 * The wrapper can remain compatible with the existing compiled client while
 * automatically using the real 26.2 Options bridge once the rebuilt engine
 * publishes globalThis.Radio26Options.
 */
(function () {
  'use strict';
  function waitForEngine(invoke, timeout, fallback) {
    var timer;
    return new Promise(function (resolve) {
      timer = setTimeout(function () { resolve(fallback); }, timeout);
      invoke(resolve);
    }).finally(function () { clearTimeout(timer); });
  }
  window.__radioEngine = {
    available: function () {
      try { return !!window.Radio26Options && window.Radio26Options.available() === true; }
      catch (e) { return false; }
    },
    set: function (key, value) {
      try {
        if (!this.available()) return false;
        return window.Radio26Options.set(key, String(value).replace(/^"(.*)"$/, '$1'));
      } catch (e) {
        console.warn('[Radio] live engine option failed:', key, e);
        return false;
      }
    },
    apply: async function (values) {
      var keys = Object.keys(values);
      if (!keys.length || !this.available()) return keys;
      if (!window.Radio26Options.apply) {
        return keys.filter(function (key) { return !this.set(key, values[key]); }, this);
      }
      try {
        var normalized = keys.map(function (key) {
          return String(values[key]).replace(/^"(.*)"$/, '$1');
        });
        var rejected = await waitForEngine(function (resolve) {
          window.Radio26Options.apply(keys, normalized, resolve);
        }, 30000, keys);
        return Array.from(rejected);
      } catch (e) {
        console.warn('[Radio] live engine apply failed', e);
        return keys;
      }
    },
    get: function (key) {
      try {
        if (!this.available()) return null;
        return window.Radio26Options.get(key);
      } catch (e) { return null; }
    },
    canSetResourcePack: function () {
      return this.available() && typeof window.Radio26Options.setResourcePack === 'function';
    },
    setResourcePack: function (enabled) {
      return waitForEngine(function (resolve) {
        window.Radio26Options.setResourcePack(enabled, resolve);
      }, 60000, false);
    },
    reloadResources: function () {
      try {
        if (!this.available() || !window.Radio26Options.reloadResources) return false;
        return window.Radio26Options.reloadResources() === true;
      } catch (e) {
        console.warn('[Radio] live resource reload failed:', e);
        return false;
      }
    }
  };
})();
