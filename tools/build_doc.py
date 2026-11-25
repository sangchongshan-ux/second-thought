# -*- coding: utf-8 -*-
"""Builds the A2 report DOCX through the local editor SDK."""
import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import report_text as R

SKILL = r"E:\Autumn class\WorkBuddyAI\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\workbuddy-local-office-edit"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'docs', 'A2_Project_Report_3129594.docx')

COUNTS = R.counts()
GH_USER = os.environ.get('GH_USER', 'USERNAME')
# Word splits URLs, hyphenated compounds and decimals differently from a
# whitespace count, so the figure printed on the cover is the one Word itself
# reports. Measure with tools/wordcount.ps1, then pass it in here.
WORD_BODY = os.environ.get('WORD_BODY')
WORD_ABSTRACT = os.environ.get('WORD_ABSTRACT')
# Cite the root commit, not HEAD: HEAD changes every time the report is rebuilt,
# so the submitted DOCX would cite a commit whose copy of itself is out of date.
try:
    GH_COMMIT = os.environ.get('GH_COMMIT') or subprocess.check_output(
        ['git', 'rev-list', '--max-parents=0', 'HEAD'], cwd=ROOT).decode().strip()[:7]
except Exception:
    GH_COMMIT = 'COMMIT_HASH'


def sub(text):
    return text.replace('USERNAME', GH_USER).replace('COMMIT_HASH', GH_COMMIT)


def call(tool, **kwargs):
    args = [sys.executable, 'edsdk.py', 'call', tool, '--json', json.dumps(kwargs)]
    p = subprocess.run(args, cwd=SKILL, capture_output=True, text=True, encoding='utf-8')
    out = (p.stdout or '') + (p.stderr or '')
    m = re.search(r'"position"\s*:\s*(-?\d+)', out)
    pos = int(m.group(1)) if m else None
    return out.strip(), pos


def md(text, idx, fid):
    out, pos = call('doc_insert_markdown', file_id=fid, idx=idx, markdown=text)
    if pos is None:
        print('WARN no position from markdown insert:', out[:300])
        return idx + len(text)
    return pos


def img(path, idx, fid, w, h):
    out, pos = call('doc_insert_image', file_id=fid, idx=idx, image_path=path, w=w, h=h)
    if pos is None:
        print('WARN no position from image insert:', out[:300])
        return idx
    # close the image's own paragraph, otherwise the caption becomes a run on the
    # same line as the picture and flows to its right when the image is narrow
    out2, p2 = call('doc_insert_paragraph', file_id=fid, idx=pos, level=0, type=0)
    if p2 is None:
        print('WARN no position from paragraph break:', out2[:300])
        return pos
    # p2 points at the break itself, which still belongs to the image paragraph;
    # step past the paragraph mark so the caption lands in the new empty paragraph
    return p2 + 1


def main():
    out, _ = call('create_doc')
    fid = re.search(r'file_id=([\w\-]+)', out).group(1)
    print('doc', fid)

    if WORD_BODY and WORD_ABSTRACT:
        wc_body, wc_abs = int(WORD_BODY), int(WORD_ABSTRACT)
        wc_total = wc_body + wc_abs
        print('word count from Word:', wc_abs, '+', wc_body, '=', wc_total)
    else:
        wc_body, wc_abs, wc_total = COUNTS['main'], COUNTS['abstract'], COUNTS['total']
        print('word count from script (run tools/wordcount.ps1 to replace with Word figures)')

    header = (
        "# Second Thought: measuring help-seeking instead of asking about it\n\n"
        "**Assignment 2 — Project Report**\n\n"
        "桑崇善 · Student 3129594\n\n"
        f"Intelligent Interactive Systems · {datetime.date.today():%d %B %Y}\n\n"
        f"Word count: **{wc_total:,}** (abstract {wc_abs}, main report {wc_body:,}, table included). "
        "Captions and references are excluded, as the brief specifies.\n\n"
        "Repository: github.com/" + GH_USER + "/second-thought\n\n"
        "## Abstract\n\n"
        + R.ABSTRACT + "\n"
    )
    idx = md(header, 0, fid)

    for heading, paras in R.SECTIONS:
        block = "## " + heading + "\n\n" + "\n\n".join(paras) + "\n"
        if heading.startswith("2."):
            block += "\n**Table 1.** Design choices, the problem each answers, the evidence behind it, and status.\n\n"
            rows = ["| " + " | ".join(R.TABLE[0]) + " |", "| --- | --- | --- | --- |"]
            rows += ["| " + " | ".join(r) + " |" for r in R.TABLE[1:]]
            block += "\n".join(rows) + "\n"
        idx = md(block, idx, fid)
        if heading.startswith("2."):
            out, _ = call('doc_list_tables', file_id=fid)
            m = re.search(r'"table_id"\s*:\s*"([^"]+)"', out)
            if m:
                out2, _ = call('doc_set_table_properties', file_id=fid, table_id=m.group(1),
                               mode='manual', col_widths_dxa=[2100, 2700, 2300, 1500],
                               cell_v_align='top')
                print('table widths:', out2[:120])
            else:
                print('WARN table id not found:', out[:200])
        if heading.startswith("3."):
            idx = img(os.path.join(ROOT, 'docs', 'system-diagram.png'), idx, fid, 600, 400)
            idx = md("*" + R.CAPTIONS[0] + "*\n", idx, fid)
        if heading.startswith("4."):
            for n, (f, cap) in enumerate([
                ('storyboard-1.png', R.CAPTIONS[1]),
                ('storyboard-2.png', R.CAPTIONS[2]),
                ('storyboard-3.png', R.CAPTIONS[3]),
            ], start=2):
                idx = img(os.path.join(ROOT, 'docs', f), idx, fid, 600, 294)
                idx = md(f"*{cap}*\n", idx, fid)

    closing = ""
    for heading, paras in R.CLOSING:
        closing += "## " + heading + "\n\n" + "\n\n".join(sub(p) for p in paras) + "\n\n"

    closing += "## References\n\n"
    refs = [
        "Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P.N., Inkpen, K., Teevan, J., Kikin-Gil, R. and Horvitz, E. (2019) ‘Guidelines for human-AI interaction’, in *Proceedings of CHI 2019*. Glasgow: ACM, pp. 1–13.",
        "Deng, R., Jiang, M., Yu, X., Lu, Y. and Liu, S. (2025) ‘Does ChatGPT enhance student learning? A systematic review and meta-analysis of experimental studies’, *Computers & Education*, 227, article 105224.",
        "Lo, C.K., Hew, K.F. and Jong, M.S.-y. (2024) ‘The influence of ChatGPT on student engagement: A systematic review and future research agenda’, *Computers & Education*, 219, article 105100.",
        "Stojanov, A., Liu, Q. and Koh, J.H.L. (2024) ‘University students’ self-reported reliance on ChatGPT for learning: A latent profile analysis’, *Computers and Education: Artificial Intelligence*, 6, article 100243.",
        "Zhai, C., Wibowo, S. and Li, L.D. (2024) ‘The effects of over-reliance on AI dialogue systems on students’ cognitive abilities: A systematic review’, *Smart Learning Environments*, 11, article 28.",
    ]
    closing += "\n\n".join(refs) + "\n"

    idx = md(closing, idx, fid)

    # reference lists are set tight: drop the inter-entry gap so the list closes on
    # the same page instead of stranding one line on a page of its own
    for ref in refs:
        out, _ = call('doc_find', file_id=fid, text=ref[:18])
        m = re.search(r'"begin"\s*:\s*(\d+)\s*,\s*"end"\s*:\s*(\d+)', out)
        if m:
            call('doc_modify_paragraph', file_id=fid,
                 ranges=[{'begin': int(m.group(1)), 'end': int(m.group(2))}],
                 spacing_after=0)
        else:
            print('WARN reference not found:', ref[:30])

    # appendix: the built interface. Start it on a fresh page via the heading's own
    # "page break before" — an inserted break character would leave a blank page behind.
    idx = md("## Appendix: the interface as built\n", idx, fid)
    out, _ = call('doc_find', file_id=fid, text='Appendix: the interface as built')
    m = re.search(r'"begin"\s*:\s*(\d+)\s*,\s*"end"\s*:\s*(\d+)', out)
    if m:
        out2, _ = call('doc_modify_paragraph', file_id=fid,
                       ranges=[{'begin': int(m.group(1)), 'end': int(m.group(2))}],
                       page_break_before=True)
        print('page break before:', out2[:120])
    else:
        print('WARN heading range not found:', out[:200])
    idx = img(os.path.join(ROOT, 'docs', 'screenshots', '04-hint.png'), idx, fid, 496, 349)
    idx = md("*" + R.CAPTIONS[4] + "*\n", idx, fid)
    idx = img(os.path.join(ROOT, 'docs', 'screenshots', '06-summary.png'), idx, fid, 496, 349)
    idx = md("*" + R.CAPTIONS[5] + "*\n", idx, fid)

    # A section heading must not sit alone at the foot of a page while its
    # figure starts the next one. Word's own heading styles keep with next;
    # the SDK inserts plain paragraphs, so set the property explicitly.
    for h in ('1. The problem', '2. Design rationale', '3. System diagram',
              '4. Storyboards', '5. Repository and development evidence',
              'References',
              'Three walkthroughs: a lure answer'):
        out, _ = call('doc_find', file_id=fid, text=h)
        m = re.search(r'"begin"\s*:\s*(\d+)\s*,\s*"end"\s*:\s*(\d+)', out)
        if not m:
            print('WARN heading not found:', h)
            continue
        out2, _ = call('doc_modify_paragraph', file_id=fid,
                       ranges=[{'begin': int(m.group(1)), 'end': int(m.group(2))}],
                       keep_with_next=True)
        print('keep_with_next', h, ':', 'ok' if '"message"' in out2 else out2[:120])

    # A single reference entry must not break across two pages.
    for ref in ('Amershi, S.', 'Deng, R.', 'Lo, C.K.', 'Stojanov, A.', 'Zhai, C.'):
        out, _ = call('doc_find', file_id=fid, text=ref)
        m = re.search(r'"begin"\s*:\s*(\d+)\s*,\s*"end"\s*:\s*(\d+)', out)
        if not m:
            print('WARN reference not found:', ref)
            continue
        out2, _ = call('doc_modify_paragraph', file_id=fid,
                       ranges=[{'begin': int(m.group(1)), 'end': int(m.group(2))}],
                       keep_together=True)
        print('keep_together', ref, ':', 'ok' if '"message"' in out2 else out2[:120])

    out, _ = call('save_file', file_id=fid, file_path=OUT)
    print('saved:', out[:200])
    print('exists:', os.path.exists(OUT), os.path.getsize(OUT) if os.path.exists(OUT) else 0)


if __name__ == '__main__':
    main()
