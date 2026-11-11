import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs')
os.makedirs(OUT, exist_ok=True)

INK = '#17232e'
SOFT = '#4a5a68'
MUTED = '#7b8a97'
LINE = '#dde4ea'
ACCENT = '#2c5f80'
ACCENT_SOFT = '#eaf1f6'
AMBER = '#8a6420'
AMBER_SOFT = '#fbf3e2'
GREEN = '#2f6b4f'
GREEN_SOFT = '#e9f4ee'
SANS = "Segoe UI, Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ───────────────────────── system diagram ─────────────────────────
def box(x, y, w, h, title, sub='', kind='impl', fs=17, sfs=12.5):
    fill = {'impl': '#ffffff', 'sim': AMBER_SOFT, 'plan': '#f7f9fa'}[kind]
    stroke = {'impl': ACCENT, 'sim': AMBER, 'plan': MUTED}[kind]
    dash = ' stroke-dasharray="7 5"' if kind == 'plan' else ''
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>']
    ty = y + h / 2 - (6 if sub else 0)
    out.append(f'<text x="{x + w/2}" y="{ty}" text-anchor="middle" font-family="{SANS}" font-size="{fs}" font-weight="600" fill="{INK}">{esc(title)}</text>')
    if sub:
        out.append(f'<text x="{x + w/2}" y="{ty + 17}" text-anchor="middle" font-family="{SANS}" font-size="{sfs}" fill="{SOFT}">{esc(sub)}</text>')
    return ''.join(out)


def band(x, y, w, h, label, align='right'):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#fbfcfd" stroke="{LINE}" stroke-width="1.2"/>'
            f'<text x="{x + w - 16 if align == "right" else x + 16}" y="{y + 22}" text-anchor="{"end" if align == "right" else "start"}" font-family="{SANS}" font-size="13" letter-spacing="1.6" fill="{MUTED}">{esc(label.upper())}</text>')


def arrow(x1, y1, x2, y2, label='', dash=False, lx=None, ly=None, curve=None, anchor='middle'):
    d = f'M {x1} {y1} L {x2} {y2}' if not curve else f'M {x1} {y1} Q {curve[0]} {curve[1]} {x2} {y2}'
    dash_attr = ' stroke-dasharray="6 5"' if dash else ''
    out = [f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.5"{dash_attr} marker-end="url(#ah)"/>']
    if label:
        out.append(f'<text x="{lx if lx is not None else (x1+x2)/2}" y="{ly if ly is not None else (y1+y2)/2 - 6}" '
                   f'text-anchor="{anchor}" font-family="{SANS}" font-size="13" fill="{SOFT}">{esc(label)}</text>')
    return ''.join(out)


def system_diagram():
    W, H = 1020, 680
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{SANS}">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="30" y="36" font-family="{SANS}" font-size="22" font-weight="700" fill="{INK}">Second Thought — system diagram</text>',
         f'<text x="30" y="57" font-family="{SANS}" font-size="14" fill="{MUTED}">Solid = implemented · amber = simulated (rule-based) · dashed = planned. Arrows read left to right, then down.</text>']

    # learner
    s.append(f'<rect x="60" y="82" width="200" height="48" rx="24" fill="{ACCENT_SOFT}" stroke="{ACCENT}" stroke-width="1.4"/>')
    s.append(f'<text x="160" y="111" text-anchor="middle" font-size="17" font-weight="600" fill="{INK}">Learner</text>')

    # interface band
    s.append(band(60, 146, 900, 96, 'Interface · one page, no network calls'))
    s.append(box(60, 176, 200, 56, 'Contract', 'rules · logging toggle', fs=17, sfs=12.5))
    s.append(box(290, 176, 200, 56, 'Problem card', 'prompt · answer · check', fs=17, sfs=12.5))
    s.append(box(520, 176, 200, 56, 'Hint ladder', 'levels 1-3, learner-paced', fs=17, sfs=12.5))
    s.append(box(750, 176, 200, 56, 'Summary', 'profile + limits', fs=17, sfs=12.5))

    # logic band
    s.append(band(60, 272, 900, 200, 'Decision logic'))
    s.append(box(290, 306, 200, 58, 'Answer checker', 'parse · compare · unit', fs=17, sfs=12.5))
    s.append(box(520, 306, 200, 58, 'Hint selector', 'attempts · time · lure', 'sim', fs=17, sfs=12.5))
    s.append(box(60, 402, 200, 50, 'Model hints', 'planned', 'plan', fs=16, sfs=12))

    # data band
    s.append(band(60, 498, 900, 104, 'Local data · this browser only', 'left'))
    s.append(box(290, 528, 430, 56, 'Session log', 'attempts · hints · reflections · export · delete', fs=17, sfs=12.5))
    s.append(box(750, 528, 200, 56, 'Profile builder', 'counts to label', fs=17, sfs=12.5))

    # flows
    s.append(arrow(160, 130, 160, 174))                                  # learner -> contract
    s.append(arrow(260, 204, 288, 204))                                  # contract -> problem
    s.append(arrow(390, 232, 390, 304, 'answer', lx=398, ly=274))        # problem -> checker
    s.append(arrow(490, 335, 518, 335))
    s.append(arrow(620, 304, 620, 234, 'level 1-3', lx=628, ly=274))     # selector -> ladder
    s.append(arrow(262, 427, 516, 427, 'generated text', dash=True, lx=390, ly=418))  # planned -> selector
    s.append(arrow(340, 364, 340, 526, 'attempts', lx=348, ly=452))
    s.append(arrow(700, 364, 700, 526, 'hint levels', lx=708, ly=452))
    s.append(arrow(720, 556, 748, 556))                                  # log -> profile
    s.append(arrow(762, 526, 762, 234, 'profile + limits', lx=772, ly=390, anchor='start'))

    s.append('</svg>')
    return ''.join(s)


# ───────────────────────── storyboards ─────────────────────────
def frame(x, y, w, h, n, header, lines, accents):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#ffffff" stroke="{LINE}" stroke-width="1.4"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="12" fill="#f7f9fa"/>',
           f'<rect x="{x}" y="{y+18}" width="{w}" height="12" fill="#f7f9fa"/>',
           f'<circle cx="{x+w-16}" cy="{y+15}" r="9" fill="{ACCENT}"/>',
           f'<text x="{x+w-16}" y="{y+19}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{n}</text>',
           f'<text x="{x+14}" y="{y+19}" font-size="12.5" letter-spacing="0.8" fill="{MUTED}">{esc(header.upper())}</text>']
    cy = y + 52
    for ln in lines:
        out.append(f'<rect x="{x+14}" y="{cy}" width="{w-28-ln.get("short",0)}" height="7" rx="3.5" fill="#e7ecf0"/>')
        cy += 17
    for a in accents:
        top, hgt, text, kind = a['top'], a['h'], a['text'], a.get('kind', 'info')
        fill = {'info': ACCENT_SOFT, 'warn': AMBER_SOFT, 'ok': GREEN_SOFT}[kind]
        stroke = {'info': '#cfdfea', 'warn': '#eddfc2', 'ok': '#cfe4d9'}[kind]
        tc = {'info': ACCENT, 'warn': AMBER, 'ok': GREEN}[kind]
        out.append(f'<rect x="{x+14}" y="{y+top}" width="{w-28}" height="{hgt}" rx="7" fill="{fill}" stroke="{stroke}"/>')
        for i, t in enumerate(text):
            out.append(f'<text x="{x+24}" y="{y+top+18+i*14}" font-size="12" fill="{tc}">{esc(t)}</text>')
    return ''.join(out)


def storyboard(title, subtitle, frames, fname):
    W, H = 1020, 500
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{SANS}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="30" y="34" font-size="21" font-weight="700" fill="{INK}">{esc(title)}</text>',
         f'<text x="30" y="54" font-size="14" fill="{MUTED}">{esc(subtitle)}</text>']
    xs = [30, 360, 690]
    for i, f in enumerate(frames):
        s.append(frame(xs[i], 76, 300, 300, i + 1, f['header'], f['lines'], f['accents']))
        if i < 2:
            s.append(f'<path d="M {xs[i]+304} 226 L {xs[i]+352} 226" stroke="{MUTED}" stroke-width="1.5" marker-end="url(#a2)"/>')
        s.append(f'<text x="{xs[i]}" y="{400}" font-size="15" font-weight="700" fill="{INK}">{esc(f["caption"])}</text>')
        for j, line in enumerate(f['desc']):
            s.append(f'<text x="{xs[i]}" y="{419+j*15}" font-size="13" fill="{SOFT}">{esc(line)}</text>')
    s.insert(1, f'<defs><marker id="a2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker></defs>')
    s.append('</svg>')
    open(os.path.join(OUT, fname), 'w', encoding='utf-8').write(''.join(s))


open(os.path.join(OUT, 'system-diagram.svg'), 'w', encoding='utf-8').write(system_diagram())

storyboard(
    'Storyboard 1 — Stuck, then unstuck',
    'One learner, three frames. The system never states the answer; it names the trap and hands back the next step.',
    [
        {'header': 'problem 1', 'caption': '1 · The obvious answer',
         'desc': ['Types £0.10, the answer the item is', 'built to attract.'],
         'lines': [{'short': 40}, {'short': 90}, {'short': 20}],
         'accents': [{'top': 150, 'h': 62, 'kind': 'warn',
                      'text': ['Not yet. £0.10 is the answer most', 'people give first: the numbers invite', 'a subtraction that is not asked for.']}]},
        {'header': 'problem 1 · hint', 'caption': '2 · Asks for the next step',
         'desc': ['One click. The rule engine picks', 'level 2 because the lure was hit.'],
         'lines': [{'short': 60}, {'short': 30}],
         'accents': [{'top': 118, 'h': 76, 'kind': 'warn',
                      'text': ['Hint 2 of 3 · strategy', 'Name the ball b. The bat is b + 1.00.', 'Together they make 1.10 — one equation.']},
                     {'top': 210, 'h': 40, 'kind': 'info', 'text': ['[ I need more than this ]']}]},
        {'header': 'problem 1 · solved', 'caption': '3 · Finishes it, then reflects',
         'desc': ['The prompt appears at the boundary,', 'not while they are still working.'],
         'lines': [{'short': 100}, {'short': 70}],
         'accents': [{'top': 118, 'h': 54, 'kind': 'ok',
                      'text': ['Correct. You got there with hint 2.', 'Solved with support · recorded.']},
                     {'top': 190, 'h': 74, 'kind': 'info',
                      'text': ['What made this easier or harder', 'than it looked?', '[ Save and continue ]']}]}
    ],
    'storyboard-1.svg')

storyboard(
    'Storyboard 2 — Asking for the answer',
    'What happens when the request is "just tell me". The ladder has a floor: level 3 still leaves the last step to the learner.',
    [
        {'header': 'problem 2', 'caption': '1 · Tries to get the answer',
         'desc': ['Types a sentence instead of a value.', 'The checker only parses a number.'],
         'lines': [{'short': 20}, {'short': 70}],
         'accents': [{'top': 118, 'h': 58, 'kind': 'info',
                      'text': ['"just give me the answer"', 'Type a number — digits only is fine,', 'units are optional.']}]},
        {'header': 'problem 2 · hint 3', 'caption': '2 · Reaches the last rung',
         'desc': ['Level 3 does one step with them', 'and stops. No answer is produced.'],
         'lines': [{'short': 50}],
         'accents': [{'top': 118, 'h': 84, 'kind': 'warn',
                      'text': ['Hint 3 of 3 · worked step', 'The machines work in parallel. Adding', 'machines raises output per minute; it does', 'not shorten the time one widget takes.']},
                     {'top': 212, 'h': 38, 'kind': 'info', 'text': ['[ Hide hint ]']}]},
        {'header': 'problem 2 · solved', 'caption': '3 · Still has to commit',
         'desc': ['They answer 5. The summary will', 'record the depth they needed.'],
         'lines': [{'short': 80}, {'short': 40}],
         'accents': [{'top': 118, 'h': 54, 'kind': 'ok',
                      'text': ['Correct. You got there with hint 3.', 'Deepest hint level: 3 of 3']}]}
    ],
    'storyboard-2.svg')

storyboard(
    'Storyboard 3 — Ending, and taking the data back',
    'The summary is where a study instrument usually over-claims. Here the limits sit in the same card as the numbers.',
    [
        {'header': 'summary', 'caption': '1 · The profile, with its limits',
         'desc': ['Numbers first, then a fixed statement', 'of what they cannot support.'],
         'lines': [{'short': 10}],
         'accents': [{'top': 92, 'h': 46, 'kind': 'info',
                      'text': ['Solved without help 1/3 · with hints 2/3', 'Deepest hint level 3 of 3']},
                     {'top': 148, 'h': 58, 'kind': 'warn',
                      'text': ['Carried by the last step', 'This is not a measure of your ability.', 'It cannot say how you would do tomorrow.']}]},
        {'header': 'summary · detail', 'caption': '2 · Checks the record',
         'desc': ['Per-problem attempts, deepest hint,', 'time and outcome.'],
         'lines': [{'short': 60}, {'short': 30}, {'short': 80}],
         'accents': [{'top': 150, 'h': 54, 'kind': 'info',
                      'text': ['1  2 attempts  hint 2  38s  with support', '2  1 attempt   hint 3  26s  with support', '3  2 attempts  none    44s  unaided']}]},
        {'header': 'summary · data', 'caption': '3 · Exports or deletes',
         'desc': ['One JSON file, or remove it from', 'this device. No copy is kept elsewhere.'],
         'lines': [{'short': 40}],
         'accents': [{'top': 118, 'h': 74, 'kind': 'info',
                      'text': ['[ Export session JSON ]', '[ Delete this session ]', '[ Start a new set ]']}]}
    ],
    'storyboard-3.svg')

print('wrote diagram + 3 storyboards')
