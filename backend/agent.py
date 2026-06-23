import os
import re
from groq import Groq
from langsmith import traceable
from vector_store import RepoVectorStore

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


@traceable(name="repo_qa_agent")
def answer_question(
    question: str,
    vector_store: RepoVectorStore,
    repo_summary: str,
    owner: str,
    repo: str,
) -> dict:
    chunks = vector_store.search(question, k=6)
    context_parts = []
    sources = []

    for c in chunks:
        context_parts.append(f"### {c['path']}\n```\n{c['content'][:800]}\n```")
        if c["path"] not in sources:
            sources.append(c["path"])

    context = "\n\n".join(context_parts)

    system_prompt = f"""You are RepoMind, an expert code analyst. Answer questions about GitHub repositories.

Repository: {owner}/{repo}
Summary: {repo_summary}

OUTPUT RULES — NEVER break these:
- Output ONLY the final answer. Zero thinking. Zero reasoning steps. Zero meta-commentary.
- Begin your response with ## Overview immediately.
- Always use this exact markdown structure:

## Overview
2-3 sentence direct answer.

## How It Works
Step-by-step explanation referencing specific files and functions.

## Key Files & Their Roles
| File | Role |
|------|------|
| `file.py` | What it does |

## Architecture Notes
Design patterns, data flow, important decisions.

EXTRA FORMATTING RULES:
- If asked about file/folder structure, always render it as a code block with tree format using └──, ├──, │ characters.
- Use **bold** for important terms.
- Use `inline code` for ALL file names, function names, variables, class names.
- Use bullet points for lists of 3+ items.
- Keep sections tight — no padding sentences."""

    user_prompt = f"""Question: {question}

Relevant code:
{context}

Answer now. Start with ## Overview immediately. No thinking."""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=1500,
        
    )

    answer = response.choices[0].message.content

    # Scrub any leaked thinking no matter what
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
    answer = re.sub(
        r"(Here'?s?\s+(a\s+)?thinking\s+process.*?(?=##))",
        "", answer, flags=re.DOTALL | re.IGNORECASE
    )
    answer = re.sub(
        r"(\*{0,2}(Self-Correction|Output Generation|Proceeds?|Draft|Verification"
        r"|Step \d|Note:|Wait,|Let me|I will|I'll ensure).*?\n)",
        "", answer, flags=re.IGNORECASE
    )
    answer = answer.strip()
    if not answer.startswith("#"):
        # Find first ## and slice from there
        idx = answer.find("##")
        if idx != -1:
            answer = answer[idx:]

    return {"answer": answer, "sources": sources}


@traceable(name="generate_repo_summary")
def generate_repo_summary(files: list[dict], owner: str, repo: str) -> str:
    priority_files = ["README.md", "readme.md", "package.json", "pyproject.toml",
                      "setup.py", "main.py", "app.py", "index.js", "index.ts"]

    overview_content = []
    for fname in priority_files:
        for f in files:
            if f["path"].lower().endswith(fname.lower()) or f["path"] == fname:
                overview_content.append(f"### {f['path']}\n{f['content'][:1000]}")
                break

    file_list = "\n".join(f"- {p}" for p in [f["path"] for f in files][:60])

    prompt = f"""Analyze this GitHub repository: {owner}/{repo}

Files:
{file_list}

Key contents:
{''.join(overview_content[:3000])}

Reply with ONLY 3 sentences. No preamble. No labels. Just the sentences.
Cover: what it does, tech stack, architecture."""

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=200,
        
    )
    return response.choices[0].message.content.strip()