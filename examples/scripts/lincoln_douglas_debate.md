---
mode: raw-gpt
---

```eval
resolution = ask('What resolution would you like to debate? E.g. "In a democracy, a free press ought to prioritize objectivity over advocacy."')
```

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far: nothing yet.

The Affirmative will now present its Affirmative Constructive arguments in favor of the resolution.

- The Affirmative and Negative will both use markdown wherever possible
- After the Affirmative Constructive arguments are complete, the Negative will not yet continue

Affirmative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative will now cross examine the Affirmative.

- The Affirmative and Negative will both use markdown wherever possible
- The Negative will ask at least 3 questions in the cross examination, and the Affirmative will answer each of those questions before the Negative asks the next one
- After the Negative's cross examination is complete, the Negative will not yet continue

Negative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative conducted the following cross examination of the Affirmative:

{{ answers[1] }}

The Negative will now present their Negative Constructive arguments.

- The Affirmative and Negative will both use markdown wherever possible
- After the Negative's constructive arguments are complete, the Affirmative will not yet continue

Negative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative conducted the following cross examination of the Affirmative:

{{ answers[1] }}

The Negative presented the Negative Constructive arguments as follows:

{{ answers[2] }}

The Affirmative will now cross examine the Negative.

- The Affirmative and Negative will both use markdown wherever possible
- The Affirmative will ask at least 3 questions in the cross examination, and the Negative will answer each of those questions before the Affirmative asks the next one
- After the Affirmative's cross examination is complete, the Affirmative will not yet continue

Affirmative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative conducted the following cross examination of the Affirmative:

{{ answers[1] }}

The Negative presented the Negative Constructive arguments as follows:

{{ answers[2] }}

The Affirmative conducted the following cross examination of the Negative:

{{ answers[3] }}

The Affirmative will now present the First Affirmative Rebuttal

- The Affirmative and Negative will both use markdown wherever possible
- After the Affirmative's rebuttal is complete, the Negative will not yet continue

Affirmative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative conducted the following cross examination of the Affirmative:

{{ answers[1] }}

The Negative presented the Negative Constructive arguments as follows:

{{ answers[2] }}

The Affirmative conducted the following cross examination of the Negative:

{{ answers[3] }}

The Affirmative presented the First Affirmative Rebuttal:

{{ answers[4] }}

The Negative will now present the Negative Rebuttal

- The Affirmative and Negative will both use markdown wherever possible
- After the Negative's rebuttal is complete, the Affirmative will not yet continue

Negative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative conducted the following cross examination of the Affirmative:

{{ answers[1] }}

The Negative presented the Negative Constructive arguments as follows:

{{ answers[2] }}

The Affirmative conducted the following cross examination of the Negative:

{{ answers[3] }}

The Affirmative presented the First Affirmative Rebuttal:

{{ answers[4] }}

The Negative presented the Negative Rebuttal:

{{ answers[5] }}

The Affirmative will now present the Second Affirmative Rebuttal

- The Affirmative and Negative will both use markdown wherever possible

Affirmative:

---

Lincoln–Douglas Debate

Resolution: {{ resolution }}

What has happened so far:

The Affirmative has presented the Affirmative Constructive arguments as follows:

{{ answers[0] }}

The Negative conducted the following cross examination of the Affirmative:

{{ answers[1] }}

The Negative presented the Negative Constructive arguments as follows:

{{ answers[2] }}

The Affirmative conducted the following cross examination of the Negative:

{{ answers[3] }}

The Affirmative presented the First Affirmative Rebuttal:

{{ answers[4] }}

The Negative presented the Negative Rebuttal:

{{ answers[5] }}

The Affirmative presented the Second Affirmative Rebuttal:

{{ answers[6] }}

The Judge will now decide the outcome of the debate

:> The Judge has decided in favor of the
