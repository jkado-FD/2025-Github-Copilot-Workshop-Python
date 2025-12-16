(() => {
  "use strict";

  if (!window.PomodoroCore) {
    console.warn("PomodoroCore が見つかりません（pomodoro_core.js の読み込みを確認してください）");
    return;
  }

  const modeLabel = document.getElementById("modeLabel");
  const timeLabel = document.getElementById("timeLabel");
  const startPauseButton = document.getElementById("startPauseButton");
  const resetButton = document.getElementById("resetButton");
  const modeFocusButton = document.getElementById("modeFocus");
  const modeBreakButton = document.getElementById("modeBreak");

  if (!modeLabel || !timeLabel || !startPauseButton || !resetButton || !modeFocusButton || !modeBreakButton) {
    console.warn("必須要素が見つかりません（index.html を確認してください）");
    return;
  }

  const core = window.PomodoroCore;

  /** @type {{state: any, intervalId: number|null}} */
  const runtime = {
    state: core.initialState(),
    intervalId: null,
  };

  function setActiveModeTab(mode) {
    const isFocus = mode === "focus";
    modeFocusButton.classList.toggle("tab--active", isFocus);
    modeBreakButton.classList.toggle("tab--active", !isFocus);
    modeFocusButton.setAttribute("aria-selected", isFocus ? "true" : "false");
    modeBreakButton.setAttribute("aria-selected", !isFocus ? "true" : "false");
  }

  function render() {
    const s = runtime.state;
    modeLabel.textContent = s.mode === "focus" ? "Focus" : "Break";
    timeLabel.textContent = core.formatMMSS(s.remainingSec);
    setActiveModeTab(s.mode);

    if (s.status === "running") {
      startPauseButton.textContent = "Pause";
    } else if (s.status === "paused") {
      startPauseButton.textContent = "Resume";
    } else {
      startPauseButton.textContent = "Start";
    }
  }

  function stopInterval() {
    if (runtime.intervalId != null) {
      window.clearInterval(runtime.intervalId);
      runtime.intervalId = null;
    }
  }

  function ensureInterval() {
    if (runtime.intervalId != null) return;
    runtime.intervalId = window.setInterval(() => {
      dispatch({ type: "TICK", nowMs: Date.now() });
      // runningでなくなったら停止
      if (runtime.state.status !== "running") stopInterval();
    }, 250);
  }

  function dispatch(action) {
    runtime.state = core.reducer(runtime.state, action);
    render();
  }

  startPauseButton.addEventListener("click", () => {
    const s = runtime.state;
    const nowMs = Date.now();
    if (s.status === "running") {
      dispatch({ type: "PAUSE", nowMs });
      stopInterval();
      return;
    }
    dispatch({ type: "START", nowMs });
    ensureInterval();
  });

  resetButton.addEventListener("click", () => {
    dispatch({ type: "RESET" });
    stopInterval();
  });

  modeFocusButton.addEventListener("click", () => {
    dispatch({ type: "SET_MODE", mode: "focus" });
  });

  modeBreakButton.addEventListener("click", () => {
    dispatch({ type: "SET_MODE", mode: "break" });
  });

  render();
})();
