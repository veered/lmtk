In the following conversation, you will pretend to be a natural language programming language. Each request will ask for something and you will return the result and only the result.

Respond "Yes" if you understand.

***

```
{{get_web(params.url)}}
```

Summarize the above web page in the following format:

### Background
Should contain general information about the website itself. This doesn't necessarily relate to the current content of the text. It's meant to be about the publisher themselves.

### Key Takeaways
This should be 3 bullet points about the most important, interesting or unusual parts of the web page.

### Other Takeaways
This should be the main summary of the web page. It should not include things already mentioned in "Background" or "Key Takeaways". It should only contain things that are specific to the web page, not the web site as a whole. Ideally break things into Markdown lists. Should be no more than 200 words.

---
