# Pomodoro Webアプリ：アーキテクチャ案（Flask + HTML/CSS/JavaScript）

## 目的
- PomodoroタイマーWebアプリを、**シンプルな1ページ構成**で実装する。
- タイマーの正確性（リロード/スリープ/タブ復帰時の復元）と、**ユニットテストのしやすさ**を重視する。

## 基本方針（重要）
- **タイマーの主担当はブラウザ（JavaScript）**
  - 秒刻みのカウントダウンやUI更新はクライアント側で行う。
  - サーバ側で秒刻み処理（バックグラウンドジョブ等）は行わない。
- **Flaskは「画面配信 + 設定/履歴の保存API」**に集中
  - HTMLは1ページ（`/`）で配信。
  - 永続化はSQLiteで十分（単一ユーザー/学習用途前提）。
- **正確性は `end_at` によって担保**
  - 実行中は「終了予定時刻 `end_at`」を状態として保持し、残り時間は `end_at - Date.now()` で再計算する。
  - タブが非アクティブでも復元しやすく、テスト時も「時刻注入」で検証しやすい。

## 全体アーキテクチャ

### 役割分担
- ブラウザ（Front-end）
  - タイマー状態（`idle/running/paused`）とモード（`focus/break`）を管理
  - `end_at` ベースで残り時間を算出し、UIへ反映
  - 設定の読み込み/更新、セッション完了時の履歴送信
- Flask（Back-end）
  - 画面（テンプレート）配信
  - 設定の保存/取得API
  - セッション履歴の保存API
- SQLite
  - 設定と履歴を保存

### 状態管理（推奨）
- クライアント（LocalStorage）
  - 実行中のセッション状態：`mode`、`end_at`、`paused_remaining_ms` 等
  - リロード後も復元可能
- サーバ（SQLite）
  - ユーザー設定（Focus/Break時間など）
  - 完了したセッション履歴（監査・集計用）

## バックエンド設計（Flask）

### アプリ構成：アプリファクトリ
- `create_app()` を採用し、テスト時に設定と依存関係を差し替え可能にする。
- `TestingConfig` で `TESTING=True`、DBをインメモリまたは一時ファイルに切替可能にする。

### レイヤ分離（テスト容易性のため）
- Route（Controller）
  - 入力バリデーション → Service呼び出し → JSON/HTMLを返す
- Service（業務ロジック）
  - 設定取得/更新、履歴保存のユースケース
  - RepositoryとClockを引数で受け取り（DI）
- Repository（永続化）
  - SQLite操作（SQL/CRUD）を隔離

### 「時間」の注入（Clockパターン）
- `datetime.utcnow()` 等をロジック内で直接呼ばず、`clock.now()` を経由。
- テストでは `FakeClock` で固定時刻にでき、境界条件の検証が容易。

### API（必要最小限）
- `GET /`
  - 1ページUIを配信（初期設定を埋め込む or フロントがAPI取得）
- `GET /api/settings`
  - 現在設定を返す
- `PUT /api/settings`
  - 設定を更新
- `POST /api/sessions`
  - セッション完了時に履歴を保存

#### 推奨ペイロード例（概要）
- settings
  - `focus_minutes`, `break_minutes`, （必要なら）`long_break_minutes`, `cycles`
- sessions
  - `type`（`focus`/`break`）, `started_at`, `ended_at`, `completed`（true/false）

※実装開始前に、UIモックに合わせて「必要な項目だけ」に絞る。

## フロントエンド設計（HTML/CSS/JavaScript）

### 基本構成
- `templates/index.html`：画面（1ページ）
- `static/css/app.css`：スタイル
- `static/js/app.js`：状態管理・タイマー・API呼び出し

### ユニットテストしやすいJS設計
- タイマーの状態遷移を **純粋関数（reducer）** で実装
  - 例：`nextState = reducer(state, action)`
  - DOM更新、`setInterval`、`fetch`、`localStorage` は薄いアダプタ層へ分離
- 時刻とタイマーを注入（TimeProvider/TimerProvider）
  - `Date.now()` を直接呼ばず、`time.now()` を介す
  - `setInterval` もラップし、テストではフェイクタイマーで制御

### 正確性のキー：end_at
- 実行中は `end_at` を状態に保持
- 表示更新は `remaining = end_at - now` の再計算
- 一時停止は `paused_remaining_ms` を保持し、再開時に `end_at = now + paused_remaining_ms`

## ディレクトリ案（最小）
- `app.py`（or `pomodoro/app.py`）
- `templates/index.html`
- `static/css/app.css`
- `static/js/app.js`
- `db.py`（SQLite初期化/接続管理）
- `services.py`
- `repositories.py`
- `config.py`（Configクラス）

※規模が小さい間はファイルを増やしすぎず、責務が混ざり始めたら分割する。

## テスト戦略（最小で効果が高いもの）

### バックエンド
- Flask `test_client()` でAPIの契約テスト
  - `/api/settings` 正常系・異常系（必須不足/型不正）
  - `/api/sessions` 正常系・異常系
- Repository差し替え（Fake/InMemory）でサービスのユニットテスト
- `FakeClock` で時刻境界（0秒到達/日付跨ぎなど）を検証

### フロントエンド
- reducerのユニットテスト（状態×アクションの組合せ）
- “復元”テスト：`end_at` がある状態での残り時間再計算
- “二重送信防止”テスト：0秒到達時に履歴保存が1回だけ起きる

## 実装の進め方（推奨順）
1. Flask `create_app()` と `/` のテンプレ配信
2. フロントの状態管理（reducer + end_at）を実装し、UI更新を完成
3. `/api/settings` 実装（UIと接続）
4. `/api/sessions` 実装（完了時に履歴保存）
5. バックエンドのAPIテスト、フロントのreducerテストを追加
