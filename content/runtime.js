(() => {
  const fix = globalThis[globalThis.__DYNATRACE_IME_FIX_KEY__];

  if (fix.initialized) {
    return;
  }

  const state = fix.state;
  const { FOLLOW_UP_ENTER_GRACE_MS } = fix.constants;

  fix.handleCompositionStart = (event) => {
    state.composing = true;
    state.lastCompositionEndAt = 0;
    state.lastCompositionTarget = fix.getTargetElement(event.target);
  };

  fix.handleCompositionEnd = (event) => {
    state.composing = false;
    state.lastCompositionEndAt = Date.now();
    state.lastCompositionTarget = fix.getTargetElement(event.target);
  };

  fix.handleBlur = () => {
    state.composing = false;
  };

  fix.handleKeydown = (event) => {
    const eventTime = Date.now();

    if (!fix.shouldSuppressEnter(event, eventTime)) {
      return;
    }

    state.lastSuppressedTarget = fix.getTargetElement(event.target);
    state.suppressFollowUpEnterUntil = eventTime + FOLLOW_UP_ENTER_GRACE_MS;
    fix.stopEvent(event);
  };

  fix.handleKeyup = (event) => {
    if (!fix.isEnterKey(event) || Date.now() > state.suppressFollowUpEnterUntil) {
      return;
    }

    if (!fix.isEditableTarget(event.target)) {
      return;
    }

    if (fix.getTargetElement(event.target) !== state.lastSuppressedTarget) {
      return;
    }

    fix.stopEvent(event);
  };

  window.addEventListener("compositionstart", fix.handleCompositionStart, true);
  window.addEventListener("compositionend", fix.handleCompositionEnd, true);
  window.addEventListener("blur", fix.handleBlur, true);
  window.addEventListener("keydown", fix.handleKeydown, true);
  window.addEventListener("keyup", fix.handleKeyup, true);

  fix.initialized = true;
})();
