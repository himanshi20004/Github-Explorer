import os
import json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

from fetcher import fetch_repo_files
from vector_store import RepoVectorStore
from agent import answer_question, generate_repo_summary

app = Flask(__name__)
CORS(app)

session = {
    "vector_store": None,
    "summary": "",
    "owner": "",
    "repo": "",
    "files_count": 0,
}


@app.route("/api/load", methods=["POST"])
def load_repo():
    data = request.json
    github_url = data.get("url", "").strip()
    if not github_url:
        return jsonify({"error": "No URL provided"}), 400

    def generate():
        try:
            yield f"data: {json.dumps({'status': 'Fetching files from GitHub...'})}\n\n"
            files, owner, repo = fetch_repo_files(github_url)
            if not files:
                yield f"data: {json.dumps({'error': 'No readable files found'})}\n\n"
                return

            yield f"data: {json.dumps({'status': f'Embedding {len(files)} files...'})}\n\n"
            vs = RepoVectorStore()
            vs.build(files)

            yield f"data: {json.dumps({'status': 'Generating summary...'})}\n\n"
            summary = generate_repo_summary(files, owner, repo)

            session["vector_store"] = vs
            session["summary"] = summary
            session["owner"] = owner
            session["repo"] = repo
            session["files_count"] = len(files)

            yield f"data: {json.dumps({'success': True, 'owner': owner, 'repo': repo, 'files_indexed': len(files), 'summary': summary})}\n\n"
        except Exception as e:
            print(f"[Error] {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/ask", methods=["POST"])
def ask():
    if session["vector_store"] is None:
        return jsonify({"error": "No repository loaded. Please load a repo first."}), 400

    data = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        result = answer_question(
            question=question,
            vector_store=session["vector_store"],
            repo_summary=session["summary"],
            owner=session["owner"],
            repo=session["repo"],
        )
        return jsonify(result)
    except Exception as e:
        print(f"[Error] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "loaded": session["vector_store"] is not None,
        "repo": f"{session['owner']}/{session['repo']}" if session["owner"] else None,
        "files_indexed": session["files_count"],
        "summary": session["summary"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)