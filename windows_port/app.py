import os
import random
import tempfile
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

import easyocr

from comment_sampler import CommentEntry, extract_comments


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET", "rene-fairy-secret")
    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB limit

    allowed_extensions = {"png", "jpg", "jpeg", "webp"}

    reader_holder = {"reader": None}

    def get_reader() -> easyocr.Reader:
        if reader_holder["reader"] is None:
            reader_holder["reader"] = easyocr.Reader(["ch_tra", "en"], gpu=False)
        return reader_holder["reader"]

    def is_allowed(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            files = request.files.getlist("images")
            sample_count_raw = request.form.get("sample_count", "").strip()

            if not files or all(f.filename == "" for f in files):
                flash("請至少選擇一張蓋樓截圖。")
                return redirect(url_for("index"))

            try:
                sample_count = int(sample_count_raw)
                if sample_count <= 0:
                    raise ValueError
            except ValueError:
                flash("抽出名額請填寫大於 0 的數字。")
                return redirect(url_for("index"))

            valid_uploads = [f for f in files if f and f.filename and is_allowed(f.filename)]
            if not valid_uploads:
                flash("僅支援 JPG、PNG、WEBP 影像格式。")
                return redirect(url_for("index"))

            with tempfile.TemporaryDirectory() as tmpdir:
                temp_paths = []
                for index, upload in enumerate(valid_uploads, start=1):
                    filename = secure_filename(upload.filename) or f"image_{index}.png"
                    temp_path = Path(tmpdir) / filename
                    upload.save(temp_path)
                    temp_paths.append(temp_path)

                reader = get_reader()
                all_comments: list[CommentEntry] = []
                missing_comments: list[str] = []
                for path in temp_paths:
                    comments = extract_comments(path, reader, min_conf=0.3, line_gap=130.0)
                    if not comments:
                        missing_comments.append(path.name)
                    all_comments.extend(comments)

            if not all_comments:
                flash("沒有辨識到留言，請確認截圖清晰度或重新上傳。")
                return redirect(url_for("index"))

            # 以帳號 + 留言內容去除完全相同的重複紀錄
            unique_map: dict[tuple[str, str], CommentEntry] = {}
            for comment in all_comments:
                key = (comment.username, comment.comment)
                unique_map[key] = comment
            unique_comments = list(unique_map.values())

            if sample_count > len(unique_comments):
                flash(f"共有 {len(unique_comments)} 則有效留言，已自動調整為抽出 {len(unique_comments)} 位。")
                sample_count = len(unique_comments)

            winners = random.sample(unique_comments, sample_count) if sample_count else []

            return render_template(
                "index.html",
                winners=winners,
                warnings=missing_comments,
            )

        return render_template("index.html", winners=None, warnings=None)

    return app


app = create_app()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="啟動 Rene 的抽獎器服務")
    parser.add_argument("--host", default="0.0.0.0", help="監聽的主機位址，預設 0.0.0.0")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 5000)),
        help="監聽的連接埠號，預設讀取 PORT 環境變數或 5000",
    )
    parser.add_argument(
        "--no-debug",
        action="store_true",
        help="停用 Flask debug 與自動重載模式",
    )
    args = parser.parse_args()

    app.run(
        debug=not args.no_debug,
        host=args.host,
        port=args.port,
    )
