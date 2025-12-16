import json
import unittest
from pathlib import Path

import quickjs


ROOT = Path(__file__).resolve().parents[1]
CORE_JS = ROOT / "static" / "js" / "pomodoro_core.js"


def js_state(ctx: quickjs.Context, expr: str) -> dict:
    """JS式の評価結果（state）をJSONとして受け取りdictにする。"""
    s = ctx.eval(expr)
    if not isinstance(s, str):
        raise TypeError(f"Expected JSON string, got {type(s)}")
    return json.loads(s)


class PomodoroCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx = quickjs.Context()
        ctx.eval(CORE_JS.read_text(encoding="utf-8"))
        cls.ctx = ctx

    def test_start_sets_running_and_end_at(self):
        state = js_state(self.ctx, "PomodoroCore.serialize(PomodoroCore.initialState())")
        self.assertEqual(state["status"], "idle")

        started = js_state(
            self.ctx,
            "PomodoroCore.serialize(PomodoroCore.reducer(PomodoroCore.initialState(), {type:'START', nowMs: 1000}))",
        )
        self.assertEqual(started["status"], "running")
        self.assertEqual(started["mode"], "focus")
        self.assertEqual(started["remainingSec"], 25 * 60)
        self.assertEqual(started["endAtMs"], 1000 + 25 * 60 * 1000)

    def test_pause_freezes_remaining(self):
        # Start at now=0 then pause at 10s
        paused = js_state(
            self.ctx,
            "PomodoroCore.serialize(PomodoroCore.reducer(" 
            "PomodoroCore.reducer(PomodoroCore.initialState(), {type:'START', nowMs: 0})," 
            "{type:'PAUSE', nowMs: 10000}))",
        )
        self.assertEqual(paused["status"], "paused")
        # 25:00 - 10s = 24:50
        self.assertEqual(paused["remainingSec"], 25 * 60 - 10)
        self.assertIsNone(paused["endAtMs"])

    def test_tick_auto_transitions_focus_to_break(self):
        # Start and then tick at end
        started = js_state(
            self.ctx,
            "PomodoroCore.serialize(PomodoroCore.reducer(PomodoroCore.initialState(), {type:'START', nowMs: 0}))",
        )
        end_at = started["endAtMs"]
        self.assertIsInstance(end_at, int)

        transitioned = js_state(
            self.ctx,
            f"PomodoroCore.serialize(PomodoroCore.reducer({json.dumps(started)}, {{type:'TICK', nowMs: {end_at}}}))",
        )
        self.assertEqual(transitioned["status"], "running")
        self.assertEqual(transitioned["mode"], "break")
        self.assertEqual(transitioned["remainingSec"], 5 * 60)
        self.assertEqual(transitioned["endAtMs"], end_at + 5 * 60 * 1000)

    def test_double_tick_does_not_double_transition(self):
        started = js_state(
            self.ctx,
            "PomodoroCore.serialize(PomodoroCore.reducer(PomodoroCore.initialState(), {type:'START', nowMs: 0}))",
        )
        end_at = started["endAtMs"]

        first = js_state(
            self.ctx,
            f"PomodoroCore.serialize(PomodoroCore.reducer({json.dumps(started)}, {{type:'TICK', nowMs: {end_at}}}))",
        )
        # 同じnowMsで2回TICKしても、endAtMsが更新されるため再遷移しない
        second = js_state(
            self.ctx,
            f"PomodoroCore.serialize(PomodoroCore.reducer({json.dumps(first)}, {{type:'TICK', nowMs: {end_at}}}))",
        )
        self.assertEqual(first["mode"], "break")
        self.assertEqual(second["mode"], "break")
        self.assertEqual(second["endAtMs"], first["endAtMs"])


if __name__ == "__main__":
    unittest.main()
