/**
 * Problem bank for Second Thought.
 *
 * Each problem is a Cognitive Reflection Test style item: it has an answer that
 * looks obvious and is wrong ("lure"), and a correct answer that needs one
 * deliberate step. That structure is why the item is useful here: the system can
 * tell the difference between "guessed the obvious thing" and "worked it out",
 * which a self-report questionnaire cannot.
 *
 * answer   - accepted correct values (normalised numbers)
 * lure     - the intuitive wrong answer the item is designed to attract
 * hints    - three escalating levels: restate / strategy / worked step
 */
(function (root) {
  'use strict';

  const PROBLEMS = [
    {
      id: 'bat-ball',
      prompt:
        'A bat and a ball cost £1.10 in total. The bat costs £1.00 more than the ball. ' +
        'How much does the ball cost, in pounds?',
      unit: '£',
      answer: [0.05],
      lure: 0.1,
      lureNote:
        '£0.10 is the answer most people give first: the numbers 1.10 and 1.00 invite a subtraction, ' +
        'and the subtraction is not what the question asks for.',
      hints: [
        'Re-read the second sentence. The bat costs £1.00 *more than* the ball — more than what? ' +
          'What are the two quantities you actually have to relate?',
        'Name the ball b. Then the bat is b + 1.00, and together they make 1.10. ' +
          'Write that as one equation in b before you answer.',
        'Test the intuitive answer: if the ball were £0.10 the bat would be £1.10, and the total would be ' +
          '£1.20 — too much. Now adjust b downwards until the total lands on £1.10.'
      ]
    },
    {
      id: 'machines',
      prompt:
        'If 5 machines take 5 minutes to make 5 widgets, how many minutes would 100 machines take ' +
        'to make 100 widgets?',
      unit: 'min',
      answer: [5],
      lure: 100,
      lureNote:
        '100 scales the machines and the widgets together, so the time stays the same. ' +
        'The number that changes is output per minute, not minutes per widget.',
      hints: [
        'The question asks about 100 machines, but the rate that matters is per machine. ' +
          'What does one machine produce, and in how long?',
        'Five machines make five widgets in five minutes, so each machine makes one widget in five minutes. ' +
          'Work out how long one machine needs per widget before you scale up.',
        'The machines work in parallel. Adding machines increases how much is made in a given time; ' +
          'it does not shorten the time one widget takes.'
      ]
    },
    {
      id: 'lily',
      prompt:
        'A patch of lily pads on a lake doubles in size every day. It takes 48 days to cover the whole lake. ' +
        'How many days does it take to cover half the lake?',
      unit: 'days',
      answer: [47],
      lure: 24,
      lureNote:
        'Halving the days assumes the patch grows at a constant rate. It doubles, so the half-covered ' +
        'state is one doubling before the end, not halfway through the time.',
      hints: [
        'The patch doubles every day. Instead of counting forwards from day one, start at day 48 ' +
          'and step backwards.',
        'On day 48 the lake is full. The patch doubled between day 47 and day 48. ' +
          'What must it have covered on day 47 for that doubling to fill the lake?',
        'Work backwards one day only: the day before the lake is full is the day it is half full, ' +
          'because the next doubling completes it.'
      ]
    }
  ];

  /** Parse a free-text answer into a number, accepting £/p and trailing units. */
  function parseAnswer(raw) {
    if (typeof raw !== 'string') return null;
    let s = raw.trim().toLowerCase().replace(/,/g, '');
    if (!s) return null;
    const pence = /^£?\s*([0-9]*\.?[0-9]+)\s*p(ence)?$/.exec(s);
    if (pence) return parseFloat(pence[1]) / 100;
    s = s.replace(/£|\$|minutes?|mins?|days?|pounds?/g, '').trim();
    const n = parseFloat(s);
    return Number.isFinite(n) ? n : null;
  }

  function isCorrect(problem, value) {
    if (value === null) return false;
    return problem.answer.some(a => Math.abs(a - value) < 1e-9);
  }

  function isLure(problem, value) {
    if (value === null || problem.lure === undefined) return false;
    return Math.abs(problem.lure - value) < 1e-9;
  }

  root.ProblemBank = { PROBLEMS, parseAnswer, isCorrect, isLure };
})(typeof window !== 'undefined' ? window : globalThis);
