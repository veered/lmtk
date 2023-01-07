---
mode: raw-gpt
---

```eval
topic = ask('What statement would you like to debate?')
```

Topic: {{ topic }}

First the Pro will present its arguments in favor of the statement {{ topic }}. The Pro will use markdown wherever possible. The Con will not present its arguments yet.

Pro:

---

Topic: {{ topic }}

The Pro has already presented the argument
{{ answers[0] }}

The Con will now present its argument. The Con will use markdown wherever possible. The Con will also reply to specific Pro arguments where possible.

Con:

---

Topic: {{ topic }}

The Pro has presented the argument
{{ answers[0] }}

The Con has presented the argument
{{ answers[1] }}

The Judge will now decide if the Pro or Con has made a stronger argument:

:> The Judge decides in favor of
