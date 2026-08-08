(function (root) {
  "use strict";

  function canonicalize(locale) {
    if (typeof locale !== "string" || !locale.trim()) return "";
    const cleaned = locale.trim().replace(/_/g, "-");
    try {
      return Intl.getCanonicalLocales(cleaned)[0] || "";
    } catch (_error) {
      return cleaned;
    }
  }

  function localeKey(locale) {
    return canonicalize(locale).toLowerCase();
  }

  function matchLocale(preferences, locales, fallback, aliases) {
    const available = locales
      .map((route) => ({ ...route, canonical: canonicalize(route.code) }))
      .filter((route) => route.canonical && route.url);
    if (!available.length) return "";

    const byCode = new Map(available.map((route) => [localeKey(route.canonical), route]));
    const aliasMap = new Map(
      Object.entries(aliases || {}).map(([key, value]) => [localeKey(key), localeKey(value)]),
    );
    const requested = (preferences || []).map(canonicalize).filter(Boolean);

    for (const preference of requested) {
      const exact = byCode.get(localeKey(preference));
      if (exact) return exact.canonical;
    }

    for (const preference of requested) {
      const alias = aliasMap.get(localeKey(preference)) || aliasMap.get(preference.split("-")[0]);
      const aliased = byCode.get(alias);
      if (aliased) return aliased.canonical;
    }

    for (const preference of requested) {
      const language = preference.split("-")[0].toLowerCase();
      const languageMatch = available.find(
        (route) => route.canonical.split("-")[0].toLowerCase() === language,
      );
      if (languageMatch) return languageMatch.canonical;
    }

    return byCode.get(localeKey(fallback))?.canonical || available[0].canonical;
  }

  function readPreference(storageKey) {
    try {
      return root.localStorage?.getItem(storageKey) || "";
    } catch (_error) {
      return "";
    }
  }

  function savePreference(storageKey, locale) {
    try {
      root.localStorage?.setItem(storageKey, locale);
    } catch (_error) {
      // Language selection still works when storage is unavailable.
    }
  }

  function routeFor(locale, routes) {
    const key = localeKey(locale);
    return routes.find((route) => localeKey(route.code) === key);
  }

  function destinationUrl(url) {
    const destination = new URL(url, root.location.href);
    if (!destination.search && root.location.search) destination.search = root.location.search;
    if (!destination.hash && root.location.hash) destination.hash = root.location.hash;
    return destination.href;
  }

  function navigate(locale, config, replace) {
    const route = routeFor(locale, config.locales || []);
    if (!route) return false;
    const destination = destinationUrl(route.url);
    if (destination === root.location.href) return false;
    root.location[replace ? "replace" : "assign"](destination);
    return true;
  }

  function initialize() {
    const configElement = document.getElementById("locale-routes");
    if (!configElement) return;

    let config;
    try {
      config = JSON.parse(configElement.textContent);
    } catch (_error) {
      return;
    }

    const storageKey = config.storageKey || "app-site-locale";
    const current = canonicalize(config.currentLocale || document.documentElement.lang);
    const selects = [...document.querySelectorAll("[data-locale-switcher]")];

    for (const select of selects) {
      select.value = current;
      select.addEventListener("change", () => {
        const selected = canonicalize(select.value);
        if (!selected) return;
        if (config.rememberSelection !== false) savePreference(storageKey, selected);
        navigate(selected, config, false);
      });
    }

    if (!config.autoRedirect) return;
    const saved = config.rememberSelection === false ? "" : readPreference(storageKey);
    const browserLanguages = root.navigator?.languages?.length
      ? root.navigator.languages
      : [root.navigator?.language].filter(Boolean);
    const preferred = matchLocale(
      saved ? [saved] : browserLanguages,
      config.locales || [],
      config.sourceLocale,
      config.aliases,
    );
    if (preferred && localeKey(preferred) !== localeKey(current)) {
      navigate(preferred, config, true);
    }
  }

  root.AppLocaleRouter = { canonicalize, matchLocale, routeFor };
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", initialize, { once: true });
    } else {
      initialize();
    }
  }
})(typeof window !== "undefined" ? window : globalThis);
