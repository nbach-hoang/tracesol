# What changed from the previous hackathon prototype

Reference reviewed: the local `carbon_decision_engine` README, `app.py`, and `carbon_engine.py`. This comparison is based on inspected implementation, not a performance benchmark or a claim about competition results.

| Aspect | Carbon Decision Engine reference | New TraceSol implementation |
|---|---|---|
| Problem fit | Transport trade-offs | Chemistry evidence curation and solubility context |
| Core interaction | Set trip assumptions and rank options | Import, normalize, compare context, inspect sources, annotate, export/reopen |
| Interface | Streamlit input/results layout | Custom responsive research interface with evidence inspector and comparisons |
| Input scope | Included transport-factor table | User CSV import/paste, documented template, edit workflow |
| Traceability | Editable demonstration assumptions | Raw fields, source excerpt/locator, visible conversion, input fingerprint, edit history |
| Uncertainty | Warning that transport factors are illustrative | Missing context prevents disagreement conclusions; different conditions remain separate |
| Decisions | Weighted option ranking | Human decisions with required reasons, kept separate from automated flags |
| Outputs | On-screen results, charts, and existing presentation | CSV, audit JSON, self-contained HTML report, editable workspace, screenshots, judge guide |
| Application dependencies | Streamlit and pandas | Python standard library; no pip packages or API keys |
| Validation added here | No test assessment of prior project conducted | Recorded engine/server and browser checks, including malformed input and hostile markup |
| Submission materials | README and existing PDF presentation | Requirements mapping, copy-ready story, contribution disclosure, screenshots, cover, project brief |

No code was copied from the earlier prototype. TraceSol makes no unsupported real-world performance, publication-validation, or winning-probability claim.
