# Installed skills — sources

Downloaded 2026-11-05. Copied unmodified from upstream; each folder keeps the upstream license.

| Skill | Upstream | Commit | License |
|---|---|---|---|
| sector-overview | anthropics/financial-services · plugins/vertical-plugins/equity-research/skills/sector-overview | 6056506 | Apache-2.0 |
| dcf-model | anthropics/financial-services · plugins/agent-plugins/model-builder/skills/dcf-model | 6056506 | Apache-2.0 |
| comps-analysis | anthropics/financial-services · plugins/agent-plugins/market-researcher/skills/comps-analysis | 6056506 | Apache-2.0 |
| humanizer | blader/humanizer (SKILL.md, README, CHANGELOG, LICENSE) | 0ef9fe5 | MIT |
| literature-review | K-Dense-AI/scientific-agent-skills · skills/literature-review | a25cf9e | MIT |
| citation-management | K-Dense-AI/scientific-agent-skills · skills/citation-management | a25cf9e | MIT |
| statement-of-purpose | Haadhi76/SOP_Consultant · skills/statement-of-purpose (added 2026-11-05) | 5522a87 | MIT |
| statement-coach | mohitagw15856/pm-claude-skills · skills/statement-coach (added 2026-11-05) | f7c90bc | MIT |

## Optional dependencies
- dcf-model: `pip install -r .claude/skills/dcf-model/requirements.txt` (for scripts/validate_dcf.py)
- citation-management / literature-review: Python 3.9+ with `requests`; Google Scholar search needs `scholarly`.
  Optional keys: NCBI_API_KEY, OPENALEX_API_KEY; literature-review AI diagrams need OPENROUTER_API_KEY; PDF export needs Pandoc + XeLaTeX.
