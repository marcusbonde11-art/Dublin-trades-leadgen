# CLAUDE.md

Project memory for Claude sessions working in this repo. Read this first; it
replaces needing to rediscover context each run. Keep it short and current:
when a run teaches something that the next run should know, add it under
**Lessons learned** in the same commit.

## What this is

A paced, compliant cold-outreach pipeline for small owner-operated HVAC and
plumbing shops within 20 miles of Dublin, OH. Claude researches leads and
writes **Gmail drafts**; Marcus reviews and sends them himself. Overview and
diagram: `README.md`.

## Hard rules (never break)

- **Never send email.** Create drafts only. The one exception is the summary
  or alert email to Marcus himself (marcusbonde11@gmail.com).
- Caps come from `config.yaml → pacing`: at most 10 new first-touch drafts and
  25 total per week. The pacing guard is: new drafts = 10 minus the rows still
  `Drafted`, and never below 0.
- Only use email addresses the business publishes itself, on its own site or
  its own business profile. Never guessed, broker or third-party-only
  addresses (`docs/compliance.md`).
- `Do-not-contact` and `Bounced` are permanent. Check status, address **and
  domain** before drafting.
- Every first-touch email follows `docs/tone-guide.md`: under ~120 words,
  plain text, the standard no-pressure closing (rule 7), and the CAN-SPAM
  footer with the postal address.
- If anything is unclear or broken, draft nothing and email Marcus a short note.

## Where state lives

| What | Source of truth |
|---|---|
| Lead statuses, thread IDs, history | Google Sheet `1KVkBKzi4XFJtNQ1ySj7DWp4tAMojxOUZoFXxIM1qtTg`, tab `Pipeline` (thread ID in column T) |
| Settings, caps, label IDs, Make IDs | `config.yaml` |
| Weekly procedure (step by step) | `docs/weekly-routine.md` |
| What each past run did | `batches/` (newest file = latest state; read it before starting a run) |
| Discovery cache, screen results | `data/discovered.csv`, `data/raw_places.json` (gitignored) |
| Per-lead research | `data/research/<place_id>.json` |
| Reply watcher | Make scenario 6446669 (blueprint in `make/`) |

The Sheet beats anything written in `batches/`. Batch files are a log, not
live state.

## Tools and access

- **Sheet:** go through the Make tool *LeadGen – Sheets API* (6446598).
- **Gmail:** use the Gmail connector. After you create a draft, add labels
  `Label_21` (To Review) and `Label_22` (Active), and store the **thread ID**
  on the row, because the reply watcher matches on it.
- **Make free plan:** at most 2 active scenarios, the watcher (6446669) and
  the Sheets tool (6446598). To use *LeadGen – Gmail API* (6446597), turn the
  watcher off first and back on afterward.
- **Places API:** key in env `GOOGLE_PLACES_API_KEY`, never committed. The
  `discover.py` cap is 120 requests per run. Without a key, use
  `python scripts/discover.py --from-cache` to re-screen. Use `--towns "A,B"`
  to search towns outside `territory.towns`.

## Run log conventions

- One file per run in `batches/`: `YYYY-MM-DD-batch-NN.md` for drafting runs
  and `YYYY-MM-DD-discovery-NN.md` for discovery-only runs. Numbering is
  shared and increments across both kinds.
- Each file ends with a **Pipeline after this run** line of status counts.
- Commit messages: `Batch NN: <what happened>` / `Discovery NN: ...`.

## Lessons learned

- **Business websites can't be fetched from the cloud container** (network
  policy). Research comes from the web search index plus public profiles, so
  flag owner names from third-party sources. In that case greet with "Hi
  there" and tell Marcus to check greetings.
- The Places API key has returned 403 in some runs. If so, fall back to search
  and note it in the batch file. Don't stall the run.
- **The town-branded network:** Hilliard-Dublin, Westerville, Bexley, Delaware,
  New Albany, Gahanna and Lewis Center-Powell "Heating & Cooling" / "Plumbing &
  Drain" brands share the `inbound@` email format, one site template and the
  614-344-68xx phone block. Treat them as one company and disqualify the
  duplicates.
- The Waterworks owns Wolfe & Sons and The Comfortworks, so it's
  disqualified. Heating & Cooling Doctors is a Columbus Comfort brand.
- SewerQuest shares an address with The Local Plumber. Hold it until that
  thread resolves.
- Most shops don't publish an email. Expect a large `No email - call/visit`
  bucket, which is normal and not a failure.
