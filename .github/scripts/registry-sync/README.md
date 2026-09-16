# registry-sync

Keeps the Notion Skill Registry at one row per skill. When a pull request touches a skill under
`plugins/<category>/<plugin>/skills/<skill>/`, the workflow finds that skill's registry row, or
creates it, and leaves one comment on the pull request with the link. A manual reconcile run
checks every skill on `main` against the registry and fixes what differs.

Rule: a skill on `main` has exactly one registry row, and the row says what is on `main`. A row
whose skill left `main` is `Deprecated`. Nothing is ever deleted.

## When it runs

`.github/workflows/registry-sync.yml` runs on every pull request event (opened, edited, reopened,
pushed to, closed) and by hand from the Actions tab (Registry Sync, Run workflow). Manual runs
have a `mode`: `pull request` (give a number) or `reconcile` (the whole repository). Manual runs
are dry runs unless you untick `dry_run`.

A pull request that touches no skill exits with `no skills touched` and no comment.

The same files run in `casper-secret-sauce` and `casper-marketplace`. The script reads the
repository name and writes `Secret Sauce` or `Public Marketplace` into the row's Marketplace
column. Any other repository stops with a message.

## How a row is found

1. The Notion link on the `**Notion page:**` line of the pull request body, if the page exists,
   is not in the trash, and belongs to the registry.
2. Otherwise a search by the skill's frontmatter `name`. None: create. One: update. Two or more:
   fail, a person merges them.

The search is not limited to this repository's marketplace. A skill moved from secret sauce to
the public marketplace keeps its row.

## What is written on a pull request

| Event | Row missing | Row exists |
|---|---|---|
| opened, edited, reopened, pushed to | create: Name, Description, Owner, Status `Needs Documentation`, Marketplace, User Group, Plugin, and the page body below | Status to `For Review` if it was `Beta`, `Standard`, `Not Created`, `Deprecated` or empty, and the old value is remembered. `For Review` and `Needs Documentation` are left alone |
| merged | create with Status `Needs Documentation` and the page body | Name, Plugin, User Group, Status `Beta`. Marketplace if it differs. Description only if it changed in the pull request |
| closed without merge | nothing | Status back to the remembered value, if still `For Review` |
| skill removed, merged | nothing | Status `Deprecated` |
| skill removed, not merged | nothing | nothing |

Page body: a new row gets `How to Install` with the `npx skills add` command, the documentation
headings from `write-skill-documentation` (empty), and a `Source` link to the `SKILL.md`. A row
whose page is empty gets the same headings the next time the sync writes to it. A page with
content is never touched.

Never done: delete a row, write `Standard`, change Owner after create, write `Related Docs/SOPs`,
fill in the documentation.

## Reconcile

`sync.py reconcile` reads every `SKILL.md` in the checkout and every registry row, then fixes the
rows that carry this repository's Marketplace value:

| Found | Done |
|---|---|
| Skill with no row | Row created with Status `Needs Documentation`, Owner from the commit that added the file, and the page body |
| Row with the wrong Plugin, User Group or Marketplace | Fixed |
| Row `Deprecated`, skill on `main` | Status `Beta` |
| Row `Beta`, `Standard` or empty, no skill folder | Status `Deprecated` |
| Row `For Review`, `Needs Documentation` or `Not Created`, no skill folder | Left alone. It may belong to an open pull request |
| Row named like a command (`plugins/*/*/commands/<name>.md`) | Left alone |
| Row for the other marketplace | Ignored |
| `SKILL.md` whose frontmatter cannot be read | Folder name used as the name. Plugin, User Group and Marketplace fixed. No row created |

Description, Owner and every other Status are left as they are. The report is printed to the
log and to the run's summary page. Rows that already match are counted, not listed.

## The comment

One per pull request, edited in place on later runs. One line per skill: what happened, the Notion
link, and any warning. Then a next step. Warnings never fail the job:

| Warning | Meaning | Who acts |
|---|---|---|
| link did not resolve / page in the trash / not a registry page | The Notion link was ignored and the row was found by name | Nobody, unless the wrong row was found |
| Skipped `<file>`: ... Fix the frontmatter and push again | `SKILL.md` has no frontmatter, invalid YAML, or no `name`/`description` | The author, or a reviewer, pushes a fix |
| unknown category | A folder under `plugins/` that is not one of the known categories | Add it to `USER_GROUPS` in `classify.py` |
| You ticked X, but this pull request does Y | The change-type box disagrees with the diff. The diff wins | Nobody |
| This row is Secret Sauce. Merging moves it to Public Marketplace | The skill is being promoted. The row moves on merge | Remove the skill from the other repository if it is still there |
| This row was Secret Sauce. It is now Public Marketplace | The promotion happened | Same |

## When the job is red

The comment says what failed. It is never the author's fault or job.

| Failure | Fix | Who |
|---|---|---|
| `NOTION_TOKEN is not set` | Add the repository secret `NOTION_TOKEN` | GitHub admin |
| data source was not found | In Notion, open the Skill Registry, Connections, add `github-registry-sync` | Registry owner |
| gave up after 6 tries | Notion was slow or down. Wait | Nobody |
| Two or more registry rows are named X | Merge the rows in Notion into one | Registry owner |
| X is not a repository the sync knows | The workflow was copied to a repository not listed in `MARKETPLACES` in `registry.py` | Sync owner |
| anything else | A bug. Read the job log | Sync owner |

Then run it again: Actions tab, Registry Sync, Run workflow, mode `pull request`, the pull request
number, `dry_run` off. The next pull request event also runs it again on its own, so a red run on
open is retried on the next push and on merge.

## Run it locally

```bash
set -a; source .env; set +a          # NOTION_TOKEN
uv run --locked --script .github/scripts/registry-sync/sync.py run --pr 34 --dry-run
uv run --locked --script .github/scripts/registry-sync/sync.py reconcile --dry-run
uv run --locked --script .github/scripts/registry-sync/sync.py test
```

`--dry-run` prints every write and the report and sends nothing. Without it, `run --pr` writes to
Notion and posts the comment only with `--post-comment`. `--data-source <id>` points a run at a
copy of the registry. `--repo <owner/name>` picks the marketplace; `reconcile --root <path>` reads
another checkout.

`sync.py` is a PEP 723 script. Python 3.13, `pydantic`, `pyyaml`, pinned in `sync.py.lock`.
Refresh the lock with `uv lock --script sync.py`.

## Export: the registry as telemetry

`sync.py export` publishes the same walk the reconcile does, as telemetry, so the
`claude-telemtery` Logfire dashboard can tell Casper skills from everything else without a
hand-typed list. It writes `telemetry/casper-skills.json` for review and sends one
`registry.skill` log record per skill and command to Logfire under the service
`casper-skill-registry`, plus one `registry.ambiguous` record per generic name and one
`registry.snapshot` summary. The commit SHA is the snapshot id; the dashboard joins on the
newest snapshot per repository.

`.github/workflows/registry-export.yml` runs it on every push to `main` that touches
`plugins/`, `.claude-plugin/`, `telemetry/` or these scripts, and weekly (Logfire records
age out, so the newest snapshot has to be re-sent). It needs the repository secret
`LOGFIRE_WRITE_TOKEN`, a write token for the `claude-telemtery` project. Manual runs are
dry runs unless you untick `dry_run`.

```bash
uv run --locked --script .github/scripts/registry-sync/sync.py export --dry-run   # write the JSON, send nothing
uv run --locked --script .github/scripts/registry-sync/sync.py export --check     # fail if the JSON is stale
LOGFIRE_WRITE_TOKEN=... uv run --locked --script .github/scripts/registry-sync/sync.py export
```

Rows carry: repo, marketplace label and name, plugin and its version, skill (frontmatter
name, or the folder name when the frontmatter cannot be read), kind (`skill` or `command`),
category, user group, path, and origin (`casper` for the two Casper marketplaces, `client`
for anything else). `telemetry/client-plugins.json` lists engagement plugins that live
outside this repository; they are emitted with origin `client` so the dashboard can bucket
client work separately. `AMBIGUOUS_NAMES` in `export.py` holds bare skill names too generic
to attribute when they arrive without a plugin name; any name found under two plugins is
added automatically.

The sender is plain OTLP/HTTP JSON over `urllib`, so `sync.py.lock` is unchanged and
`export_test.py` covers it with a fake transport. `LOGFIRE_BASE_URL` overrides the region
(default `https://logfire-us.pydantic.dev`).
