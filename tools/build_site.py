#!/usr/bin/env python3
"""Build the Open Semantic Agent website into docs/ (GitHub Pages from main:/docs, at https://opensemanticagent.org).

Static HTML only (.nojekyll), so nothing builds on GitHub. Pages:
  /               home
  /spec/          spec/SPEC.md rendered
  /schemas/*.json the JSON Schemas, at the paths their $id names
  /privacy/       privacy policy (MCP directories ask for one)
Other files already in docs/ (the one-pager, images) are left alone and served as they are.

Links between pages are relative, so the site also works without the custom domain.
DOMAIN below is written to docs/CNAME; set it to None to serve without a custom domain.

Run: python3 tools/build_site.py   (needs: pip install markdown)
"""
import html
import json
import pathlib
import re
import shutil

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent

DOCS = ROOT / "docs"
REPO = "https://github.com/opensemanticagent/opensemanticagent"
DOMAIN = "opensemanticagent.org"
SPEC_VERSION = "0.2"
GENERATED = ["index.html", "spec", "schemas", "privacy", "favicon.svg", ".nojekyll", "CNAME"]

LOGO = """<svg viewBox="0 0 56 56" width="{s}" height="{s}" role="img" aria-label="Open Semantic Agent logo">
<rect width="56" height="56" rx="14" fill="#15233B"/>
<path d="M10 28h36" stroke="#F4F6F9" stroke-width="3" stroke-linecap="round"/>
<path d="M18 28c0-7 4-12 10-12M18 28c0 7 4 12 10 12" stroke="#2BB3A5" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="28" cy="16" r="3.5" fill="#2BB3A5"/><circle cx="28" cy="40" r="3.5" fill="#2BB3A5"/>
<circle cx="40" cy="28" r="4" fill="#E08A2E"/><circle cx="12" cy="28" r="3" fill="#F4F6F9"/></svg>"""

CSS = """
:root{--fg:#15233B;--muted:#56637A;--accent:#0E7C72;--accent2:#B0570A;--bg:#fff;--soft:#F4F6F9;--code:#F1F4F8;--line:#DCE2EB}
@media (prefers-color-scheme:dark){:root{--fg:#E7ECF4;--muted:#9AA8BE;--accent:#4FC7B9;--accent2:#F0A35A;--bg:#0F1724;--soft:#172235;--code:#1B2840;--line:#2A3850}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{border-bottom:1px solid var(--line)}header .in,main{max-width:900px;margin:0 auto;padding:14px 20px}
header .in{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
a.brand{display:flex;gap:10px;align-items:center;font-weight:700;color:var(--fg);text-decoration:none;margin-right:auto}
nav{display:flex;gap:16px;flex-wrap:wrap}nav a{color:var(--muted);text-decoration:none;font-size:15px}nav a:hover{color:var(--accent)}
h1,h2,h3{line-height:1.25}h1{font-size:2rem}h2{margin-top:2.2rem;padding-bottom:.3rem;border-bottom:1px solid var(--line)}
a{color:var(--accent)}code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.92em}
pre{background:var(--code);padding:14px;border-radius:8px;overflow:auto}pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;display:block;overflow:auto;font-size:.95em}th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
blockquote{margin:0;padding-left:14px;border-left:3px solid var(--line);color:var(--muted)}
footer{max-width:900px;margin:40px auto;padding:16px 20px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
.hero{padding:28px 0 8px}.hero h1{font-size:2.4rem;margin:.2em 0}.hero p.lead{font-size:1.2rem;color:var(--muted);max-width:44em}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}
.btn{display:inline-block;padding:10px 16px;border-radius:8px;text-decoration:none;font-weight:600;border:1px solid var(--line);color:var(--fg)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.flow{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0}
.step{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:14px}
.step b{display:block;font-size:1.05rem}.step small{color:var(--muted)}
.step .tag{font:600 12px/1 ui-monospace,Menlo,monospace;letter-spacing:.06em;color:var(--accent)}
.step.paid .tag{color:var(--accent2)}
@media (max-width:640px){.flow{grid-template-columns:1fr}.hero h1{font-size:1.9rem}}
"""

NAV = [("", "Home"), ("spec/", "Spec"), ("schemas/envelope.schema.json", "Schemas"), ("privacy/", "Privacy")]


def shell(depth, title, body_html, description):
    up = "../" * depth
    nav = "".join(f'<a href="{up}{h}">{t}</a>' for h, t in NAV[1:]) + f'<a href="{REPO}">GitHub</a>'
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title>'
            f'<meta name="description" content="{html.escape(description)}">'
            f'<link rel="icon" href="{up}favicon.svg" type="image/svg+xml"><style>{CSS}</style></head><body>'
            f'<header><div class="in"><a class="brand" href="{up or "./"}">{LOGO.format(s=28)}Open Semantic Agent</a>'
            f'<nav>{nav}</nav></div></header><main>{body_html}</main>'
            f'<footer>Open Semantic Agent spec {SPEC_VERSION} (draft) · Apache-2.0 · <a href="{REPO}">Source</a></footer>'
            f'</body></html>\n')


def md_to_html(text):
    # Repo-relative links (README/SPEC style) point at GitHub, since only some files are on the site.
    text = re.sub(r"\]\((?!https?://|#|mailto:)([^)]+)\)",
                  lambda m: f"]({REPO}/blob/main/{m.group(1).lstrip('./')})", text)
    return markdown.markdown(text, extensions=["tables", "fenced_code", "toc", "sane_lists"])


def write(path, depth, title, body_html, description):
    out = DOCS / path / "index.html" if path else DOCS / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(shell(depth, title, body_html, description), encoding="utf-8")


HOME = """
<section class="hero">
<h1>Messages delivered by meaning</h1>
<p class="lead">Open Semantic Agent (OSA) is an open spec for publish/subscribe that routes each message by what
it is about, not only by its topic. It runs the free and cheap checks first and calls an AI model only when they are
unsure, under a budget you set.</p>
<div class="cta"><a class="btn primary" href="spec/">Read the spec</a>
<a class="btn" href="{repo}">GitHub</a></div>
</section>

<h2 id="how">How a message is routed</h2>
<div class="flow">
<div class="step"><span class="tag">CHECK 1 · FREE</span><b>Topic match</b><small>Plain topic patterns, in microseconds. Most traffic stops here.</small></div>
<div class="step"><span class="tag">CHECK 2 · CHEAP</span><b>Similarity</b><small>Embeddings compare the message with what each subscriber said it wants.</small></div>
<div class="step paid"><span class="tag">CHECK 3 · PAID</span><b>AI judge</b><small>Only for the unsure cases, with token budgets and a skip rule when they run out.</small></div>
</div>
<p>Every decision writes an audit record you can explain and replay. Topics marked <code>strict</code> never reach a model.</p>

<h2 id="implement">Implement it</h2>
<p>The spec defines the message envelope, the subscription manifest, the three-check decision engine, audit records,
and the agent interfaces (MCP tools, HTTP, Server-Sent Events, WebSocket and A2A). JSON Schemas and routing test
vectors let you check an implementation against it.</p>
<p>Your AI assistant can read the spec and check documents against the schemas through a small MCP server:</p>
<pre><code>uvx open-semantic-agent</code></pre>

<h2 id="compare">What it adds to a broker</h2>
{table}

<h2 id="read">Read</h2>
<ul>
<li><a href="spec/">Specification {spec}</a> (draft)</li>
<li>JSON Schemas: <a href="schemas/envelope.schema.json">envelope</a>, <a href="schemas/subscription.schema.json">subscription</a>,
<a href="schemas/audit.schema.json">audit</a>, <a href="schemas/stream.schema.json">stream</a></li>
<li><a href="{repo}/tree/main/conformance/fixtures">Conformance test vectors</a></li>
</ul>

<h2 id="contribute">Contribute</h2>
<p>Source, issues and discussions are on <a href="{repo}">GitHub</a>. The spec is Apache-2.0.</p>
"""

PRIVACY = """# Privacy policy

*Last updated: {date}*

This policy covers this website, opensemanticagent.org.

- **No cookies, no analytics, no forms.** The site is static pages and does not collect anything about you.
- **Hosting.** The pages are served by GitHub Pages. GitHub may keep standard server logs; see the
  [GitHub privacy statement](https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement).
- **The spec.** Open Semantic Agent is a specification, not a service. Software that implements it is run by whoever
  deploys it, under their own privacy terms.

## Contact

Questions or concerns: open an issue at [{repo}]({repo}/issues).
"""


def readme_table():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"^\| Conventional broker.*?(?=\n\n)", readme, re.S | re.M)
    return markdown.markdown(m.group(0), extensions=["tables"]) if m else ""


def main():
    import datetime
    for name in GENERATED:  # rebuild only what this script owns
        p = DOCS / name
        shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").write_text("")
    if DOMAIN:
        (DOCS / "CNAME").write_text(DOMAIN + "\n")
    (DOCS / "favicon.svg").write_text(LOGO.format(s=56) + "\n")

    write("", 0, "Open Semantic Agent: pub/sub that routes by meaning",
          HOME.format(repo=REPO, spec=SPEC_VERSION, table=readme_table()),
          "Open Semantic Agent (OSA): an open spec for pub/sub that routes messages by meaning, under AI budgets.")
    write("spec", 1, f"Specification {SPEC_VERSION} · Open Semantic Agent",
          md_to_html((ROOT / "spec" / "SPEC.md").read_text(encoding="utf-8")),
          f"The Open Semantic Agent (OSA) specification, version {SPEC_VERSION} (draft).")
    date = datetime.date.today().isoformat()
    write("privacy", 1, "Privacy policy · Open Semantic Agent", md_to_html(PRIVACY.format(date=date, repo=REPO)),
          "Privacy policy for opensemanticagent.org: no cookies, no analytics.")

    sdir = DOCS / "schemas"
    sdir.mkdir()
    for src in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = json.loads(src.read_text())
        assert schema["$id"].endswith("/schemas/" + src.name), f"$id mismatch in {src.name}"
        (sdir / src.name).write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
    print("site built in", DOCS)


if __name__ == "__main__":
    main()
