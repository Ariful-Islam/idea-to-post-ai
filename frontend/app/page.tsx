"use client";

import { useState } from "react";

type Post = {
  id: number;
  created_at: string;
  input_text: string;
  hook: string;
  body: string;
  hashtags: string[];
  cta?: string | null;
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [idea, setIdea] = useState("");
  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleGenerate() {
    if (idea.trim().length < 3) {
      setError("Please enter at least a few words.");
      return;
    }
    setLoading(true);
    setError(null);
    setPost(null);
    setCopied(false);
    try {
      const res = await fetch(`${API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Request failed (${res.status})`);
      }
      setPost(await res.json());
    } catch (e: any) {
      setError(e.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function handleCopy() {
    if (!post) return;
    const text = formatPostText(post);
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Idea → Post</h1>
        <p className="mt-2 text-slate-600">
          Drop a rough idea. Get a polished post with a hook, hashtags, and CTA.
        </p>
      </header>

      <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
        <label htmlFor="idea" className="block text-sm font-medium text-slate-700">
          Your idea
        </label>
        <textarea
          id="idea"
          className="mt-2 w-full resize-none rounded-lg border border-slate-300 p-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
          rows={5}
          placeholder="e.g. Launching a habit tracker app that pairs you with a friend for accountability."
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          maxLength={1000}
        />
        <div className="mt-1 flex justify-between text-xs text-slate-400">
          <span>{idea.length}/1000</span>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-3 inline-flex w-full items-center justify-center rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Generating…" : "Generate post"}
        </button>

        {error && (
          <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 ring-1 ring-red-200">
            {error}
          </p>
        )}
      </section>

      {post && (
        <section className="mt-6 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Your post
            </h2>
            <button
              onClick={handleCopy}
              className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
            >
              {copied ? "Copied!" : "Copy all"}
            </button>
          </div>

          <div className="mt-4 space-y-4">
            <Field label="Hook" value={post.hook} />
            <Field label="Body" value={post.body} />
            {post.hashtags.length > 0 && (
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Hashtags
                </p>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {post.hashtags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {post.cta && <Field label="Call to action" value={post.cta} />}
          </div>
        </section>
      )}
    </main>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 whitespace-pre-wrap text-slate-800">{value}</p>
    </div>
  );
}

function formatPostText(p: Post): string {
  const lines = [p.hook, "", p.body];
  if (p.cta) lines.push("", p.cta);
  if (p.hashtags.length) {
    lines.push("", p.hashtags.map((t) => `#${t}`).join(" "));
  }
  return lines.join("\n").trim();
}