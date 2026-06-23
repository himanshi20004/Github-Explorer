import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from flask import Flask, request, jsonify
from flask_cors import CORS

from fetcher import fetch_repo_files
from vector_store import RepoVectorStore
from agent import answer_question, generate_repo_summary

app = Flask(__name__)
CORS(app)

# In-memory session store (single user / demo)
session = {
    "vector_store": None,
    "summary": "",
    "owner": "",
    "repo": "",
    "files_count": 0,
}


@app.route("/api/load", methods=["POST"])
def load_repo():
    """Fetch repo, embed files, build FAISS index."""
    data = request.json
    github_url = data.get("url", "").strip()

    if not github_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        files, owner, repo = fetch_repo_files(github_url)
        if not files:
            return jsonify({"error": "No readable files found in this repository."}), 400

        vs = RepoVectorStore()
        vs.build(files)

        summary = generate_repo_summary(files, owner, repo)

        session["vector_store"] = vs
        session["summary"] = summary
        session["owner"] = owner
        session["repo"] = repo
        session["files_count"] = len(files)

        return jsonify({
            "success": True,
            "owner": owner,
            "repo": repo,
            "files_indexed": len(files),
            "summary": summary,
        })

    except Exception as e:
        print(f"[Error] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ask", methods=["POST"])
def ask():
    """Answer a question about the loaded repo."""
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
    app.run(debug=True, port=5000)