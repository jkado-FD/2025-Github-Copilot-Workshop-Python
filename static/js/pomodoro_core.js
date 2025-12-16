/*
  Pomodoro Core (Phase 1)
  - DOMに依存しない純粋ロジック
  - reducer(state, action) は純粋関数（副作用なし）
  - テストはPython+quickjsで実行
*/

(function (global) {
  "use strict";

  var DURATIONS_SEC = {
    focus: 25 * 60,
    break: 5 * 60,
  };

  function initialState() {
    return {
      mode: "focus", // 'focus' | 'break'
      status: "idle", // 'idle' | 'running' | 'paused'
      remainingSec: DURATIONS_SEC.focus,
      endAtMs: null,
    };
  }

  function clampNonNegInt(n) {
    var x = Math.floor(n);
    return x < 0 ? 0 : x;
  }

  function computeRemainingSec(nowMs, endAtMs) {
    // end_atベースで残秒を再計算（タブ復帰/スリープ後もズレにくい）
    var remainingMs = endAtMs - nowMs;
    return clampNonNegInt(Math.ceil(remainingMs / 1000));
  }

  function otherMode(mode) {
    return mode === "focus" ? "break" : "focus";
  }

  function resetForMode(state, mode) {
    return {
      mode: mode,
      status: "idle",
      remainingSec: DURATIONS_SEC[mode],
      endAtMs: null,
    };
  }

  function startFrom(state, nowMs) {
    var baseRemaining = state.remainingSec;

    // idleで0秒などの場合、モードのデフォルト時間に戻してから開始
    if (state.status === "idle" && (!baseRemaining || baseRemaining <= 0)) {
      baseRemaining = DURATIONS_SEC[state.mode];
    }

    return {
      mode: state.mode,
      status: "running",
      remainingSec: baseRemaining,
      endAtMs: nowMs + baseRemaining * 1000,
    };
  }

  function pauseFrom(state, nowMs) {
    var remaining = computeRemainingSec(nowMs, state.endAtMs);
    return {
      mode: state.mode,
      status: "paused",
      remainingSec: remaining,
      endAtMs: null,
    };
  }

  function tickFrom(state, nowMs) {
    // running時のみ処理
    if (state.status !== "running" || state.endAtMs == null) return state;

    var remaining = computeRemainingSec(nowMs, state.endAtMs);

    if (remaining > 0) {
      return {
        mode: state.mode,
        status: "running",
        remainingSec: remaining,
        endAtMs: state.endAtMs,
      };
    }

    // 0秒到達: 自動遷移（Focus→Break / Break→Focus）
    var nextMode = otherMode(state.mode);
    var nextDuration = DURATIONS_SEC[nextMode];

    // 二重遷移防止: ここでendAtを更新するので、同一nowMsでtickが複数回呼ばれても再遷移しない
    return {
      mode: nextMode,
      status: "running",
      remainingSec: nextDuration,
      endAtMs: nowMs + nextDuration * 1000,
    };
  }

  function reducer(state, action) {
    if (!state) state = initialState();
    if (!action || !action.type) return state;

    if (action.type === "SET_MODE") {
      if (state.status === "running") return state; // 実行中の切替はしない（仕様を単純化）
      if (action.mode !== "focus" && action.mode !== "break") return state;
      return resetForMode(state, action.mode);
    }

    if (action.type === "RESET") {
      return resetForMode(state, state.mode);
    }

    if (action.type === "START") {
      if (state.status === "running") return state;
      return startFrom(state, action.nowMs);
    }

    if (action.type === "PAUSE") {
      if (state.status !== "running" || state.endAtMs == null) return state;
      return pauseFrom(state, action.nowMs);
    }

    if (action.type === "TICK") {
      return tickFrom(state, action.nowMs);
    }

    // Warn in development if an unknown action type is received
    if (typeof console !== "undefined" && console.warn) {
      console.warn("[PomodoroCore] Unknown action type:", action.type, action);
    }

    return state;
  }

  function formatMMSS(totalSec) {
    var s = clampNonNegInt(totalSec);
    var mm = String(Math.floor(s / 60)).padStart(2, "0");
    var ss = String(s % 60).padStart(2, "0");
    return mm + ":" + ss;
  }

  function serialize(state) {
    return JSON.stringify(state);
  }

  global.PomodoroCore = {
    DURATIONS_SEC: DURATIONS_SEC,
    initialState: initialState,
    reducer: reducer,
    computeRemainingSec: computeRemainingSec,
    formatMMSS: formatMMSS,
    serialize: serialize,
  };
})(this);
