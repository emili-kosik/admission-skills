# Security

## Reporting a vulnerability

Report privately through GitHub **Security Advisories** on this repository
(Security → "Report a vulnerability", or
<https://github.com/emili-kosik/admission-skills/security/advisories/new>).
You'll get an acknowledgment within 7 days. Please allow up to 90 days for
a fix before public disclosure.

In scope: anything that makes the plugin exfiltrate workspace data, execute
unintended commands, or mislead a family in a way that damages an application
(e.g., a data-poisoning path into the bundled datasets).

## Design properties

- **Runtime is dependency-free.** User-facing scripts are Python stdlib only;
  hooks are Node stdlib only. There is no `npm install` or `pip install` in
  any user path, hence no supply-chain surface beyond Claude Code itself.
  (`pyproject.toml`'s dev extras are maintainer/CI-only.)
- **Hook commands are fixed strings** — `node "${CLAUDE_PLUGIN_ROOT}/…"`
  with no user-controlled interpolation; hook scripts read their input from
  stdin JSON only.
- **Hooks fail closed for integrity, open for availability**: the essay-draft
  guard blocks writes on match; every other hook exits 0 on any internal
  error so a corrupted workspace can never break sessions.
- **Network calls go to a fixed allowlist of hosts**: `api.data.gov`,
  `educationdata.urban.org`, `api.careeronestop.org`,
  `raw.githubusercontent.com` (refresh), plus whatever WebFetch/WebSearch the
  operator's own Claude Code session permits. Scripts never fetch URLs taken
  from workspace data.
- **Dataset refresh validates before replacing**: `refresh_data.py` requires
  every downloaded file to parse as JSON and carry `_meta` before it lands
  in `CLAUDE_PLUGIN_DATA`; bundled files remain as fallback.
- **Tests run fully offline** — CI cannot be made to depend on, or leak to,
  external services (socket use fails the suite).

## Threat notes for contributors

The bundled datasets are an integrity-critical input: a malicious "deadline
correction" PR is an attack on families' applications. Dataset changes must
come from the build tools against primary sources, pass the anchor-fact
tests (`tests/test_datasets.py`), and be reviewed by a maintainer — never
hand-edited silently.
