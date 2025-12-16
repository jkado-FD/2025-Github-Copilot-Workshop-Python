from pomodoro import create_app

app = create_app()


if __name__ == "__main__":
    # 開発用: `python app.py` で起動できるようにする
    # NOTE: VS Codeのターミナル/ツールでバックグラウンド実行する際、
    # Flaskのreloader（debug=True）はプロセスが二重化して停止/切断扱いになることがあるため無効化。
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
