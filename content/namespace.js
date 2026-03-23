(() => {
  const namespaceKey = "__DYNATRACE_IME_FIX__";
  globalThis.__DYNATRACE_IME_FIX_KEY__ = namespaceKey;

  if (globalThis[namespaceKey]) {
    return;
  }

  globalThis[namespaceKey] = {
    initialized: false,
  };
})();
