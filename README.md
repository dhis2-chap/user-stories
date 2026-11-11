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
| `modeling.yaml` | modeling platform: chap-core, chapkit, SDKs, model examples |
| `modeling-app.yaml` | people using the Modeling App in a country: setting up evaluations, judging them |
| `climate-data.yaml` | climate data: open-climate-service, climate-tools, Climate app (only open-climate-service so far) |
| `cross-domain.yaml` | stories that span domains, for example setting up open-climate-service and chap-core together; owned by both teams |

Add a file when a new domain does not fit any of these.

## Format

Each file is a list of stories:

```yaml
- id: newcomer-first-eval            # unique across all files, kebab-case, never reused
  reader: newcomer model developer   # who, in a few words
  goal: get a first model running and evaluated with `chap eval`
  why: ...                           # optional: what the reader gets from reaching the goal
  context: ...                       # optional: what the reader already has and knows
  status: current                    # current, planned or proposed
  starts_at:                         # where the reader starts, in order
    - repo: dhis2-chap/chap-core     # org/name on GitHub
      path: docs/external_models/newcomer.md
  done_when:                         # optional: checkable outcomes
    - ...
  jira: [CLIM-374]                   # optional: the Jira issue describing this reader
  notes: >-                          # optional: context for the team, free text
    why this story is here, what is still open, how to read it
```

- `id` is how tools and tests refer to a story. Do not rename one; add a new
  story and delete the old one instead.
- `goal` is one sentence. If a story needs more than one goal, split it.
- `why` is one clause on what the reader gets from reaching the goal, or what
  goes wrong today without it. Optional: leave it out when the goal says it
  already. Tools read it to judge whether a reader has really reached the
  goal; the full background stays in Jira.
- `context` says what the reader already has and knows when they start, for
  example "has a DHIS2 instance", "knows R, not Docker" or "at a workshop with
  a trainer". Optional. Tools read it, so it belongs here rather than in
  `notes`.
- `done_when` lists what must be true when the reader has reached the goal,
  as outcomes someone can check, not steps. For example, for a scheduled
  import: "values for yesterday are in DHIS2 for every org unit" and "the
  import runs again the next night without manual steps". Without it, the
  goal sentence is the only test. docs-review counts a story as reached only
  when every item holds.
- `status` is `current` when the story should work today, `planned` when it
  is where we want to get to, and `proposed` when someone has suggested the
  story and the team has not decided yet (see "Proposing a change"). Stories
  are permanent: a story is not closed when it works, it stays and should keep
  working. Tools that check stories, such as docs-review and tests, only use
  `current` stories and skip `planned` and `proposed` ones. Change a story to
  `current` when the work that makes it true is done. A `proposed` story
  becomes `current` or `planned` when the team accepts it, and is deleted if
  the team drops it; it is not kept with a rejected status.
- `starts_at` paths are on the default branch. Directories are allowed. It is
  required for `current` stories. For `planned` and `proposed` stories it may
  be empty or left out when nobody knows yet where the reader starts.
- `jira` links to the persona or user story in Jira, where the background and
  discussion live. This file holds what can be checked, plus the one-line
  `why`; Jira holds the longer reasoning.
- `notes` is free text for the team: where the story came from, what is
  still undecided, and anything a reader of the YAML should know. Tools ignore
  it. Keep it to a few sentences; longer discussion goes in Jira. For
  `proposed` stories it is required: say who asked for the story and why.

## Readers

`readers.yaml` lists the readers the stories are written for: a key, a name,
one line of description, and the evidence the description rests on (Jira
persona issues, meeting notes). It is a draft from 2026-11-10 that merges the
reader names used in the story files, for the team to agree on. Until then
`reader` in a story is free text; once the list is agreed, `reader` should be
one of the keys and the check below will require it.

## Checks

`check_stories.py` checks the story files against the rules above: required
fields, kebab-case unique ids, one-sentence goals, valid statuses, `starts_at`
on every `current` story, `notes` on every `proposed` story, and the shapes of
`starts_at`, `done_when` and `jira`. It also lists, as a note, the `current`
stories that have no `done_when` yet. It runs in CI on every push and pull
request (`.github/workflows/check.yml`). To run it locally:

```sh
pip install pyyaml && python3 check_stories.py
```

## Proposing a change

Anyone can propose a new story or a change to an existing one. Two ways:

- **Pull request**, for a concrete proposal. Add the story to the file for its
  domain with `status: proposed`, a new `id`, a `reader`, a one-sentence `goal`
  and `notes` saying who asked for it and why. `starts_at`, `done_when` and
  `jira` are welcome but not required. To change an existing story, edit it and
  explain the change in the pull request. Keep one proposal per pull request so
  each can be discussed on its own.
- **Issue**, for an idea that is not ready to be a story yet, or a question
  about an existing story. No YAML needed: the "Story idea" issue form asks for
  the reader, what they need to do, why, and where the idea came from.

The team goes through proposals at its team meeting. An accepted proposal is
merged (or, if it was an issue, written up as a story) and gets `status:
current` or `planned`. A proposal the team drops is closed with a reason, and
a `proposed` story already in the files is deleted. Proposals may sit in the
files as `proposed` until they are discussed.

## Status

The climate stories are copied from the user stories in open-climate-service
`docs/project_description.md`. The modeling stories were drafted from the
structure of the docs and have not been agreed by the team. The Modeling App
and cross-domain stories were added on 2026-11-06 from the capacity-building
meeting notes (user roles in the Modeling App) and from the installation
needs, for discussion at the team meeting the week after. Landing the final set of
stories is tracked under CLIM-1780: CLIM-1844 (collect earlier work and
sources), CLIM-1846 (brainstorm candidates), CLIM-1845 (climate team review)
and then CLIM-1491 (final selection).

Open for that discussion:

- Reader names: `readers.yaml` is a draft list of seven readers merged from
  the names in the files. Agree on it, then switch `reader` to the keys.
- `done_when` is missing on most `current` stories. The plan is to write it
  for them and then make it required; see the review in chap-first-brain,
  `Human-AI-collaboration/Reports/26-11-10_theUserStoriesFormatFollows.md`.
- The install story starts on chap.dhis2.org and sends the reader on to the
  DHIS2 install docs. The entry page is a guess.
- `operator-upgrade-stack` is `current` on the assumption that upgrading is
  documented; check.
- `caps-pipeline` was set to `planned` on 2026-11-10 because it had no
  `starts_at`; it goes back to `current` when the CAPS docs exist.
- The Google Doc linked from CLIM-430 has more Modeling App stories that have
  not been read yet.
- Still missing: R model developers, model developers publishing to the
  marketplace.
