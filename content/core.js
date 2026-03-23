(() => {
  const fix = globalThis[globalThis.__DYNATRACE_IME_FIX_KEY__];

  fix.constants = Object.freeze({
    ENTER_KEY: "Enter",
    COMPOSITION_END_GRACE_MS: 120,
    FOLLOW_UP_ENTER_GRACE_MS: 250,
  });

  fix.state = {
    composing: false,
    lastCompositionEndAt: 0,
    lastCompositionTarget: null,
    lastSuppressedTarget: null,
    suppressFollowUpEnterUntil: 0,
  };

  const state = fix.state;
  const { ENTER_KEY, COMPOSITION_END_GRACE_MS } = fix.constants;

  fix.isEnterKey = (event) => event.key === ENTER_KEY;

  fix.isImeActive = (event) => state.composing || event.isComposing;

  fix.isDelayedEnterOnSameTarget = (target, eventTime) => {
    if (state.lastCompositionEndAt === 0) {
      return false;
    }

    if (eventTime - state.lastCompositionEndAt > COMPOSITION_END_GRACE_MS) {
      return false;
    }

    return fix.getTargetElement(target) === state.lastCompositionTarget;
  };

  fix.shouldSuppressEnter = (event, eventTime) => {
    if (!fix.isEnterKey(event)) {
      return false;
    }

    if (!fix.isEditableTarget(event.target)) {
      return false;
    }

    return fix.isImeActive(event) || fix.isDelayedEnterOnSameTarget(event.target, eventTime);
  };
})();
