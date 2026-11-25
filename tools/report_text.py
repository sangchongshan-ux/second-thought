# -*- coding: utf-8 -*-
"""Report text for A2. Kept here so the word counts can be checked before the DOCX is built."""

ABSTRACT = """Students who use ChatGPT for coursework cannot tell whether they could solve the same problem alone, and self-reports do not predict unaided performance (Stojanov et al., 2024). Second Thought replaces the self-report with an observed behaviour. It presents three problems whose obvious answer is wrong and records how much help the learner requests before answering. Help is a ladder: level 1 restates the question, level 2 names the relation, level 3 performs one step; no level gives the answer. A rule set over attempts, time and lure matches chooses the rung and tells the learner why. Reflection opens on submission, not on a timer. The summary reports unaided solves, supported solves, deepest level and time, then states what they cannot support: one sitting is not ability, and prediction needs a delayed retest. The prototype is a static page with no network calls and opt-in logging; hints are authored and the selector is rule-based. Model-generated hints, a tutor view and the retest are designed but not built."""

SECTIONS = [
    ("1. The problem", [
        """Assignment 1 found mixed evidence: performance rises while mental effort falls (Deng et al., 2025), engagement rises with passive procrastination (Lo et al., 2024), and over-reliance accompanies weaker critical thinking (Zhai et al., 2024). The gap is not whether ChatGPT helps. It is that reliance varies — Stojanov et al. (2024) found five profiles — and no study links a profile to performance after the tool is removed. Self-report cannot close that gap, because it asks students to estimate the very capacity under test. The design question is therefore not whether ChatGPT helps, but how to observe what a learner does without the tool. Second Thought measures behaviour: three lure-based problems, the help requested, and the pattern reported instead of a self-assessment."""
    ]),
    ("2. Design rationale", [
        """The central decision is that help is a ladder, not an answer: level 1 restates the question, level 2 names the relation, level 3 performs one step, none states the result. This follows G10 (scope services when in doubt) and G9 (support efficient correction) in Amershi et al. (2019), but the reason is methodological: a system that supplies answers would reproduce the dependency it observes, so the record would describe the system, not the learner. Initiative stays with the learner — the system never pushes a hint, the mixed-initiative pattern in which the human initiates. Because the learner chooses the depth reached, it is evidence about the person.""",
        """The selector is three ordered rules, not a model: a lure match asks for level 2, two wrong attempts for level 3, otherwise the ladder starts at 1. Deterministic rules let records be compared across learners; a stochastic selector would let identical behaviour produce different levels. The cost is coarse adaptation — a rung is chosen, not a wording.""",
        """Items are cognitive-reflection problems whose intuitive answer is wrong, giving the checker a specific misconception to name. A lure match names the trap — 1.10 and 1.00 invite a subtraction not asked for — rather than saying wrong. This came from development, not literature: the Week 7 rule flagged 419 of 569 half-second intervals, so it fired on almost everything and said nothing about which moment mattered. This came from development experience rather than the literature. Feedback that separates one error from another has the same property as a flag that separates one moment from another: it informs only if it can vary.""",
        """Timing is the third decision. Reflection opens when a problem is submitted, not on a clock: a timer interrupts mid-reasoning and changes the variable under observation, since persistence is what is measured. G3 (time services based on context) states the guideline; the instrument supplies the reason to follow it.""",
        """The summary reports four counts and then what they cannot support — G2 (make clear how well the system can do what it can do) turned on its own output. Week 7 made this concrete: one 284-second recording produced 417 or 478 flags depending only on two settings I chose. A number without its conditions reads as a verdict, and a reliance profile has that property, which is why the limits sentence belongs to the measurement, not optional copy.""",
        """Privacy is the fifth decision. Failure is sensitive, so logging is opt-in before the session rather than a default discovered later, and the record can be exported or deleted. G17 (provide global controls) is the guideline.""",
        """The Week 7 guideline review was the feedback stage. It returned two amber findings: prompts timed to a clock (G3), and a profile shown without a claim-support statement (G2). Both are now decisions above, not notes in a document.""",
        """Two things were cut. A keyword matcher scored free-text justifications but rewarded phrasing, not reasoning, so justifications are stored, not judged. Scope is one sitting of three items: enough to show the interaction, not to claim anything about a person."""
    ]),
    ("3. System diagram", [
        """The diagram separates what the interface offers from the rules deciding it. There is no backend: the page is the system, state sits in localStorage, and no request leaves the device. The dashed branch is the selector — model-generated hints would change wording inside a rung, not the ladder."""
    ]),
    ("4. Storyboards", [
        """Three walkthroughs: a lure answer, a request for the answer, and the session end."""
    ])
]

TABLE = [
    ["Design choice", "Why it suits the problem", "Evidence", "Status"],
    ["Hint ladder, no answers", "Measures the learner, not the system", "G10, G9 (Amershi et al., 2019); A1 gap", "Implemented"],
    ["Lure-specific feedback", "Names the misconception", "Item design; Week 7 flag exercise", "Implemented"],
    ["Reflection at submission", "Does not interrupt measured persistence", "G3; Week 7 timing review", "Implemented"],
    ["Limits statement in summary", "Stops counts reading as ability", "G2; Week 7 comparison counts", "Implemented"],
    ["Opt-in logging, export, delete", "Failure is sensitive; control must be explicit", "G17; A1 ethics", "Implemented"],
    ["Model-generated hints", "Adapts wording, not only level", "Not yet evaluated", "Planned"],
]

CLOSING = [
    ("5. Repository and development evidence", [
        """The repository is at github.com/USERNAME/second-thought and the prototype commit is COMMIT_HASH. The stack is plain HTML, CSS and JavaScript: no framework, build step or network call, and state in localStorage. The README carries the project status (implemented, simulated, planned), a development record naming the changes made while walking the interaction, and the AI-assistance statement. The rule set and hint text are what to check against the screenshots."""
    ]),
    ("6. AI assistance", [
        """Claude (WorkBuddy) drafted the CSS, hint text and a first README. I set the interaction model, chose the items, wrote the limits statement and checked each output by running the page. The hint-escalation bug and the reflection-timing change came out of that checking, not out of the generated code. The argument, the guideline mapping and the limits claim are mine."""
    ])
]

CAPTIONS = [
    "Figure 1. System diagram: solid implemented, amber selector simulated, dashed planned.",
    "Figure 2. A lure answer, one hint, then reflection.",
    "Figure 3. An answer request refused; level 3 stops at one step.",
    "Figure 4. Summary limits, export and delete.",
    "Figure 5. The hint ladder as built.",
    "Figure 6. The summary as built.",
]


def words(text):
    import re
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def counts():
    a = words(ABSTRACT)
    body = sum(words(p) for _, paras in SECTIONS for p in paras)
    body += sum(words(h) for h, _ in SECTIONS)
    table = sum(words(c) for row in TABLE for c in row)
    closing = sum(words(p) for _, paras in CLOSING for p in paras)
    closing += sum(words(h) for h, _ in CLOSING)
    main = body + table + closing
    return {"abstract": a, "main": main, "total": a + main, "table": table}


if __name__ == "__main__":
    print(counts())
