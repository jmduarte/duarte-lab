#!/usr/bin/env python3
"""Fill in missing paper metadata in _data/papers.yml from INSPIRE-HEP.

Usage:
    python3 scripts/fetch_papers.py           # fill in what's missing
    python3 scripts/fetch_papers.py --check   # exit 1 if anything is missing
    python3 scripts/fetch_papers.py --diff    # report where our text differs
                                              # from the official abstract

Only entries that are missing `title:` or `abstract:` are touched. Existing
values are never overwritten: several abstracts on the site are deliberately
trimmed versions of the official one, and we don't want a re-run to silently
revert those edits. Use --diff to see those differences on purpose.

Requires PyYAML (pip install pyyaml).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
PAPERS = REPO / '_data' / 'papers.yml'
API = 'https://inspirehep.net/api'
UA = 'duarte-lab-site/1.0 (https://github.com/jmduarte/duarte-lab)'
FIELDS = 'titles,abstracts,arxiv_eprints,dois'

# The order keys appear in for each entry in _data/papers.yml: identifiers,
# then what's shown, then the links. Anything not listed here is kept and
# appended after these.
KEY_ORDER = ('arxiv', 'doi', 'title', 'image', 'image_width', 'embed',
             'abstract', 'links')


class Folded(str):
    """A string emitted as a folded YAML block scalar.

    Abstracts contain LaTeX (\\(, \\mathrm). In double-quoted YAML a backslash
    is an escape character, so forcing block style keeps the math intact.
    """


yaml.add_representer(
    Folded,
    lambda d, v: d.represent_scalar('tag:yaml.org,2002:str', str(v), style='>'),
)


def tex_to_mathjax(text: str) -> str:
    """Convert $...$ / $$...$$ to the \\(...\\) / \\[...\\] MathJax expects.

    The site loads MathJax 2 with the stock TeX-MML-AM_CHTML config, whose
    default inline delimiter is \\(...\\) -- `$...$` is NOT enabled, so an
    unconverted abstract would render literal dollar signs.
    """
    text = re.sub(r'\$\$(.+?)\$\$', r'\\[\1\\]', text, flags=re.S)
    text = re.sub(r'(?<!\\)\$(.+?)(?<!\\)\$', r'\\(\1\\)', text, flags=re.S)
    return text


def fetch(entry: dict) -> dict | None:
    """Look up one record on INSPIRE by arXiv id or DOI."""
    if entry.get('arxiv'):
        url = f"{API}/arxiv/{entry['arxiv']}?fields={FIELDS}"
    elif entry.get('doi'):
        url = f"{API}/doi/{entry['doi']}?fields={FIELDS}"
    else:
        return None

    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get('metadata', {})
    except urllib.error.HTTPError as e:
        print(f'  ! HTTP {e.code} for {url}', file=sys.stderr)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f'  ! {type(e).__name__}: {e} for {url}', file=sys.stderr)
    return None


def pick_abstract(meta: dict) -> str | None:
    """Prefer arXiv's abstract, else the longest one on the record."""
    abstracts = meta.get('abstracts') or []
    if not abstracts:
        return None
    for a in abstracts:
        if a.get('source', '').lower() == 'arxiv' and a.get('value'):
            return a['value']
    return max((a.get('value', '') for a in abstracts), key=len) or None


def pick_title(meta: dict) -> str | None:
    titles = meta.get('titles') or []
    return titles[0].get('title') if titles else None


def load():
    """Return (header_comment, entries). PyYAML drops comments, so the
    leading comment block is preserved verbatim and re-emitted on write."""
    raw = PAPERS.read_text()
    header, body = [], []
    for line in raw.splitlines(keepends=True):
        (header if not body and line.lstrip().startswith('#') else body).append(line)
    return ''.join(header), yaml.safe_load(''.join(body)) or []


def canonical(entry: dict) -> dict:
    """Rebuild an entry with its keys in the order papers.yml uses.

    Without this, keys filled in by this script land wherever dict insertion
    put them -- a hand-written entry listing `links:` before the script adds
    `title:`/`abstract:` ends up with those two dangling at the end, which
    reads nothing like the entries around it.

    Keys not in KEY_ORDER are kept (appended) rather than dropped, so adding
    a new field to papers.yml doesn't silently lose it on the next run.
    """
    out = {k: entry[k] for k in KEY_ORDER if k in entry}
    out.update({k: v for k, v in entry.items() if k not in KEY_ORDER})
    return out


def dump(header: str, entries: list) -> None:
    out = []
    for e in entries:
        e = canonical(e)
        if isinstance(e.get('abstract'), str):
            e['abstract'] = Folded(e['abstract'])
        out.append(e)
    body = yaml.dump(out, sort_keys=False, allow_unicode=True,
                     width=100, default_flow_style=False)
    PAPERS.write_text(header + body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='exit non-zero if any entry is missing metadata')
    ap.add_argument('--diff', action='store_true',
                    help='report entries whose abstract differs from INSPIRE')
    args = ap.parse_args()

    header, entries = load()

    if args.check:
        bad = [e for e in entries if not e.get('title') or not e.get('abstract')]
        for e in bad:
            print(f'missing metadata: {e.get("arxiv") or e.get("doi") or e}')
        print(f'{len(entries)} entries, {len(bad)} incomplete')
        return 1 if bad else 0

    if args.diff:
        differing = 0
        for e in entries:
            if not (e.get('arxiv') or e.get('doi')):
                continue
            meta = fetch(e)
            time.sleep(1)
            if not meta:
                continue
            upstream = pick_abstract(meta)
            if not upstream:
                continue
            ours = ' '.join((e.get('abstract') or '').split())
            theirs = ' '.join(tex_to_mathjax(upstream).split())
            if ours != theirs:
                differing += 1
                print(f'\n--- {e.get("arxiv") or e.get("doi")}: {e.get("title", "")[:70]}')
                print(f'    ours    ({len(ours):5d} chars): {ours[:110]}...')
                print(f'    inspire ({len(theirs):5d} chars): {theirs[:110]}...')
        print(f'\n{differing} entries differ from the official abstract '
              f'(expected -- many are deliberately trimmed)')
        return 0

    filled = skipped = 0
    for e in entries:
        if e.get('title') and e.get('abstract'):
            continue
        ident = e.get('arxiv') or e.get('doi')
        if not ident:
            print(f'  - no arxiv/doi, needs manual title/abstract: '
                  f'{e.get("title") or e.get("image") or "<unknown>"}')
            skipped += 1
            continue
        print(f'  fetching {ident} ...')
        meta = fetch(e)
        time.sleep(1)  # be polite to INSPIRE
        if not meta:
            skipped += 1
            continue
        if not e.get('title'):
            t = pick_title(meta)
            if t:
                # titles carry math too, e.g. "... at $\sqrt{s}$ = 13 TeV"
                e['title'] = tex_to_mathjax(t)
        if not e.get('abstract'):
            a = pick_abstract(meta)
            if a:
                e['abstract'] = tex_to_mathjax(a)
        filled += 1

    if filled:
        dump(header, entries)
        print(f'updated {PAPERS.relative_to(REPO)}: filled {filled} entr'
              f'{"y" if filled == 1 else "ies"}')
    else:
        print('nothing to fill -- every entry already has a title and abstract')
    if skipped:
        print(f'{skipped} entr{"y" if skipped == 1 else "ies"} skipped')
    return 0


if __name__ == '__main__':
    sys.exit(main())
