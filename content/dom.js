(() => {
  const fix = globalThis[globalThis.__DYNATRACE_IME_FIX_KEY__];
  const editableInputTypes = new Set([
    "text",
    "search",
    "url",
    "tel",
    "email",
    "password",
    "number",
  ]);

  fix.getTargetElement = (target) => {
    if (target instanceof Element) {
      return target;
    }

    return target instanceof Node ? target.parentElement : null;
  };

  fix.isEditableTarget = (target) => {
    const element = fix.getTargetElement(target);

    if (!element) {
      return false;
    }

    if (element instanceof HTMLTextAreaElement) {
      return !element.readOnly && !element.disabled;
    }

    if (element instanceof HTMLInputElement) {
      const type = (element.type || "text").toLowerCase();

      return editableInputTypes.has(type) && !element.readOnly && !element.disabled;
    }

    return element.isContentEditable;
  };

  fix.stopEvent = (event) => {
    event.preventDefault();
    event.stopImmediatePropagation();
    event.stopPropagation();
  };
})();
