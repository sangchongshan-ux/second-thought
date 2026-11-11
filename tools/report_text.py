# -*- coding: utf-8 -*-
"""Report text for A2. Kept here so the word counts can be checked before the DOCX is built."""

ABSTRACT = """Students who use ChatGPT to finish coursework cannot easily say whether they could have solved the same problem alone, and asking them produces self-reports that do not predict unaided performance (Stojanov et al., 2024). Second Thought replaces the self-report with an observed behaviour. It presents three problems whose obvious answer is wrong, and records how much help the learner asks for before answering. Help is a three-level ladder: level 1 restates the question, level 2 names the relationship to set up, level 3 performs one step. No level states the answer. The level offered is chosen by a rule set over attempt count, time on task and whether the answer matched the item's lure, and the interface tells the learner which rule fired. A reflection prompt opens when a problem is submitted, never on a timer. The session summary reports problems solved unaided, problems solved with support, deepest hint level and time, and then states in the same card what those numbers cannot support: they describe one sitting, not ability, and cannot predict a later unaided attempt without a delayed retest. The prototype is one static page with no network calls; logging is opt-out before the session and the record can be exported or deleted. Current scope is a working interaction with authored hint text and a rule-based selector; model-generated hints, a tutor view and the retest are designed but not built."""

SECTIONS = [
    ("1. The problem", [
        """Assignment 1 found that evidence on ChatGPT and learning is mixed because the outcome measures differ: academic performance rises while mental effort falls (Deng et al., 2025), engagement rises alongside passive procrastination (Lo et al., 2024), and over-reliance is associated with weaker critical thinking (Zhai et al., 2024). The gap is narrower than whether ChatGPT is good for learning. It is that reliance is heterogeneous — Stojanov et al. (2024) found five profiles — and that no study connects a profile to what a student can do once the tool is removed. Self-report cannot close that gap, because it asks students to estimate the very capacity under test. Second Thought therefore measures behaviour rather than belief: it gives three problems whose obvious answer is wrong, records how much help the learner asks for, and reports that pattern instead of a self-assessment."""
    ]),
    ("2. Design rationale", [
        """The central decision is that help is a ladder rather than an answer. Level 1 restates the question, level 2 names the relationship to set up, level 3 performs a single step; no level states the result. This follows G10 (scope services when in doubt) and G9 (support efficient correction) in Amershi et al. (2019), but the reason is methodological as much as interactional. A system that supplies answers would reproduce the dependency it is trying to observe, and the record would then describe the system rather than the learner. Initiative also stays with the learner: the system never pushes a hint, which is the mixed-initiative pattern in which the human initiates and the system responds. Because the depth reached is chosen, it is evidence about the person.""",
        """The selector is three ordered rules rather than a model: a lure match asks for level 2, two or more wrong attempts ask for level 3, otherwise the ladder starts at 1. Deterministic rules were chosen because the record may later be compared across learners; a stochastic selector would let identical behaviours produce different levels. The cost is that the adaptation is coarse — it chooses a rung, not a wording.""",
        """The second decision is that the items are cognitive-reflection problems whose intuitive answer is wrong. That structure gives the checker something free text cannot: a specific misconception to answer. When an answer matches the item's lure the feedback names the trap — the numbers 1.10 and 1.00 invite a subtraction that is not asked for — instead of saying wrong. This came from development experience rather than the literature. The Week 7 activity recorded a rule that flagged 419 of 569 half-second intervals; because it fired on almost everything, it said nothing about which moment mattered. Feedback that separates one error from another has the same property as a flag that separates one moment from another: it only informs if it can vary.""",
        """The third decision is timing. The reflection prompt opens when a problem is submitted, not on a clock. A timer interrupts mid-reasoning, and here an interruption changes the variable being measured, because persistence is the thing under observation. G3 (time services based on context) states the guideline; the instrument supplies the reason to follow it.""",
        """The fourth decision concerns what the summary claims. It reports four counts and then, in the same card, what they cannot support. That is G2 (make clear how well the system can do what it can do) turned on the system's own output. The Week 7 exercise made the failure concrete: the same 284-second recording produced 417 or 478 flags depending only on two settings I chose. A number shown without its conditions is read as a verdict, and a reliance profile has exactly that property, which is why the limits sentence is part of the measurement rather than optional copy.""",
        """The fifth decision is privacy. The system records failure, which is sensitive, so logging is opt-in before the session rather than a default discovered afterwards, and the record can be exported or deleted. G17 (provide global controls) is the guideline.""",
        """The Week 7 guideline review served as the feedback stage. It returned two amber findings against this project: prompts timed to a clock rather than to context (G3), and a profile shown without a statement of how well it could support a claim (G2). Both are now decisions above rather than notes in a document.""",
        """Two things were cut. Free-text justifications were to be scored by a keyword matcher; it rewarded phrasing rather than reasoning, so justifications are stored but not judged. The scope is one sitting of three items: enough to show the interaction, not enough to claim anything about a person."""
    ]),
    ("3. System diagram", [
        """The diagram separates what the interface offers from the rules that decide it. The dashed branch points at the selector: model-generated hints would change the wording inside a rung, not the ladder."""
    ]),
    ("4. Storyboards", [
        """Three walkthroughs: a wrong intuitive answer, a request for the answer, and the end of the session."""
    ])
]

TABLE = [
    ["Design choice", "Why it suits the problem", "Evidence", "Status"],
    ["Hint ladder, no answers", "Keeps the measure about the learner, not the system", "G10, G9 (Amershi et al., 2019); A1 gap", "Implemented"],
    ["Lure-specific feedback", "Turns a wrong answer into a misconception signal", "Item design; Week 7 flag exercise", "Implemented"],
    ["Reflection at submission", "Does not interrupt the persistence being measured", "G3; Week 7 timing review", "Implemented"],
    ["Limits statement in summary", "Stops counts being read as ability", "G2; Week 7 comparison counts", "Implemented"],
    ["Opt-in logging, export, delete", "The data records failure, so control must be explicit", "G17; A1 ethics", "Implemented"],
    ["Model-generated hints", "Would adapt wording, not only level", "Not yet evaluated", "Planned"],
]

CLOSING = [
    ("5. Repository and development evidence", [
        """The repository is at github.com/USERNAME/second-thought and the prototype commit is COMMIT_HASH. The README carries the project status (implemented, simulated, planned), the stack, the two commands needed to run it, a development record naming the two faults found while walking the interaction, and the AI-assistance statement. The rule set and the hint text are the parts a reader should check against the screenshots: they are short, and they determine what the learner actually sees."""
    ]),
    ("6. AI assistance", [
        """Claude (WorkBuddy) drafted the CSS, the hint text and a first README. I set the interaction model, chose the items, wrote the limits statement and checked each output by running the page. The hint-escalation bug and the reflection-timing change came out of that checking. The argument, the guideline mapping and the claims about what the summary can support are mine."""
    ])
]

CAPTIONS = [
    "Figure 1. System diagram. Solid boxes are implemented, the amber box is the rule-based selector, dashed is planned. Arrows read left to right, then down.",
    "Figure 2. Storyboard 1 — a wrong intuitive answer, one hint request, then the reflection prompt at the boundary.",
    "Figure 3. Storyboard 2 — a request for the answer is refused; level 3 does one step and stops.",
    "Figure 4. Storyboard 3 — the summary states its own limits, and the record can be exported or deleted.",
    "Figure 5. The hint ladder and the summary as built.",
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
