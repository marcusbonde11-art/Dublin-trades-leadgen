# Dublin Trades Lead Gen

A paced, personalized, compliant outreach pipeline for small HVAC and plumbing
businesses around Dublin, Ohio.

**You only review drafts and hit send.** The system handles everything else.

## How it works

```
 Google Places API ──► discovery (scripts/discover.py) ──► Google Sheet "Pipeline" (status: New)
                                                              │
 Monday 7:50am ET: Claude routine (docs/weekly-routine.md)    │
   research → qualify → write → Gmail DRAFT (Outreach/To Review) ─► row: Drafted + thread_id
                                                              │
 You: read, edit, send (spread over Tue-Thu)                  │
                                                              ▼
 Make: "LeadGen – Reply & Sent Watcher", every 4h, 8am-8pm ET
   • your sent outreach   → row: Sent (+ date)  → follow-ups drafted when due
   • their reply          → row: Replied, thread starred, ALERT EMAIL to you
   • opt-out ("no thanks")→ row: Do-not-contact (permanent), alert email
   • bounce / auto-reply  → logged, no alert
```

### How a reply is recognized

Matching is on the **Gmail thread ID** stored in the Sheet (column T) when the
draft is created. Each run, the watcher:

1. reads the tracked thread IDs from the Sheet (1 operation),
2. lists recent messages that aren't yet processed (1 operation),
3. keeps only messages whose thread ID is tracked (the filter is free),
4. processes each match, then labels it `Outreach/Processed` so it's never
   handled twice.

Everything else in the inbox is ignored. A weekly backup sweep, run by the
Monday routine, catches replies that arrive outside the thread, matched by
exact email address or by custom domain (never by gmail.com/yahoo.com).

## Where things live

| Thing | Where |
|---|---|
| Pipeline tracker | Google Sheet **Dublin Trades – Lead Pipeline** (`Summary` + `Pipeline` tabs) |
| Drafts to review | Gmail label **Outreach/To Review** |
| Reply alerts | Gmail, subject starts with **[Lead reply]** |
| Reply watcher | Make.com → *LeadGen – Reply & Sent Watcher (every 4h)* (blueprint in `make/`) |
| Sheet/Gmail helpers | Make.com tools *LeadGen – Sheets API*, *LeadGen – Gmail API* |
| Weekly drafting | Claude scheduled routine, *Dublin LeadGen – Monday batch* |
| Settings & caps | `config.yaml` |
| Rules | `docs/compliance.md`, `docs/tone-guide.md`, `docs/weekly-routine.md` |

## Your weekly routine (~30 min)

1. Monday: open Gmail → **Outreach/To Review**. Read each draft and edit anything
   that doesn't sound like you.
2. Send 2-3 per day, Tue-Thu mornings. Delete any draft you don't like, then set
   that row to `Disqualified` in the Sheet.
3. When a **[Lead reply]** email arrives, reply personally. Update the row to
   `Meeting` / `Won` / `Lost` when it changes.
4. Glance at the **No email - call/visit** rows. Those shops are worth a call.

## Operations budget (Make free plan)

- Watcher: 4 runs a day × ~3 operations + ~6 per actual email ≈ **400-500 per month**.
- The free plan allows **2 active scenarios**: the watcher and *LeadGen – Sheets API*.
  *LeadGen – Gmail API* stays off unless needed (see `docs/weekly-routine.md`).

## Discovery

```bash
pip install requests pyyaml
GOOGLE_PLACES_API_KEY=... python scripts/discover.py            # live (≤120 API calls)
python scripts/discover.py --from-cache                          # re-screen without API calls
GOOGLE_PLACES_API_KEY=... python scripts/place_details.py <place_id> ...
```

The API key is never committed. Keep it in an environment variable.
