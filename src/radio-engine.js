/*
 * Radio Client 26.2 live-engine seam.
 *
 * The wrapper can remain compatible with the existing compiled client while
 * automatically using the real 26.2 Options bridge once the rebuilt engine
 * publishes globalThis.Radio26Options.
 */
(function () {
  'use strict';
  window.__radioEngine = {
    available: function () {
      try { return !!window.Radio26Options && window.Radio26Options.available() === true; }
      catch (e) { return false; }
    },
    set: function (key, value) {
      try {
        if (!this.available()) return false;
        return window.Radio26Options.set(key, String(value)) === true;
      } catch (e) {
        console.warn('[Radio] live engine option failed:', key, e);
        return false;
      }
    },
    get: function (key) {
      try {
        if (!this.available()) return null;
        return window.Radio26Options.get(key);
      } catch (e) { return null; }
    }
  };
})();
