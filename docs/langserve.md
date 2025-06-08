# LangServe Playground

LangServe provides a simple web UI to experiment with RiskGPT chains and workflows.
After installing with `pip install riskgpt[serve]` you can start the playground with:

```bash
python -m riskgpt.playground.langserve_app
```

The browser interface lists available chains on the left. Selecting one shows the
input fields and allows you to run the chain interactively. Results appear on the
right side of the page.
