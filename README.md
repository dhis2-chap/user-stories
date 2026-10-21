# User stories

Who uses the Chap modeling platform and the climate data tools, and what they
need to be able to do. One place for the whole team, kept apart from the
product repos so a story can span several of them and be edited without a
release.

The stories are read by tools, so they are YAML with a fixed format. The
`docs-review` plugin in
[dhis2-chap/claude-plugins](https://github.com/dhis2-chap/claude-plugins)
walks each story through the docs as that reader and reports where they get
stuck.

## Files

One file per domain. Each team owns its file.

| File | Domain |
|------|--------|
| `modeling.yaml` | modeling platform: chap-core, chapkit, SDKs, model examples, Modeling App |
| `climate-data.yaml` | climate data: open-climate-service, climate-tools, Climate app (only open-climate-service so far) |
| `cross-domain.yaml` | stories that span domains, for example setting up open-climate-service and chap-core together; owned by both teams |

Add a file when a new domain does not fit any of these.

## Format

Each file is a list of stories:

```yaml
- id: newcomer-first-eval            # unique across all files, kebab-case, never reused
  reader: newcomer model developer   # who, in a few words
  goal: get a first model running and evaluated with `chap eval`
  starts_at:                         # where the reader starts, in order
    - repo: dhis2-chap/chap-core     # org/name on GitHub
      path: docs/external_models/newcomer.md
  done_when:                         # optional: checkable outcomes
    - ...
  jira: [CLIM-374]                   # optional: the Jira issue describing this reader
```

- `id` is how tools and tests refer to a story. Do not rename one; add a new
  story and delete the old one instead.
- `goal` is one sentence. If a story needs more than one goal, split it.
- `starts_at` paths are on the default branch. Directories are allowed.
- `jira` links to the persona or user story in Jira, where the background and
  discussion live. This file holds what can be checked; Jira holds the why.

## Status

The climate stories are copied from the user stories in open-climate-service
`docs/project_description.md`. The modeling stories were drafted from the
structure of the docs and have not been agreed by the team. None has
`done_when` yet. Review them, and add readers that are
missing, for example R model developers, model developers publishing to the
marketplace, and people running the servers.
