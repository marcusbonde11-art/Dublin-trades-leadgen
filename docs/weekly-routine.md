# Weekly drafting routine (runs Monday ~7:50am ET)

This is the exact procedure the scheduled Claude routine follows. It is also
the manual runbook if you ever run a batch by hand.

## Hard rules

- **Never send email.** Only create Gmail drafts. Marcus reviews and sends.
- Respect caps from `config.yaml`: ≤10 new first-touch drafts, ≤25 total drafts.
- Never draft to a row whose status is `Do-not-contact`, `Bounced`,
  `Disqualified`, `Replied`, `Meeting`, `Won`, `Lost`, or `Closed - no response`,
  and never to an email/domain that appears on any `Do-not-contact` row.
- Only use emails the business publishes itself (see `docs/compliance.md`).
- If anything is unclear or broken, draft nothing and email Marcus a short note.

## Tools

- **Sheet:** "Dublin Trades – Lead Pipeline" (ID `1KVkBKzi4XFJtNQ1ySj7DWp4tAMojxOUZoFXxIM1qtTg`), tab `Pipeline`.
  Read/write it through the Make tool **LeadGen – Sheets API** (scenario 6446598).
- **Gmail:** the Gmail connector (create drafts, add labels, search). If the
  connector is unavailable, the Make tool **LeadGen – Gmail API** (6446597) can
  be activated temporarily. Deactivate the reply watcher first because of the
  free plan's 2-active-scenario limit, then restore the watcher afterward.
- **Research:** Google Places API (`scripts/place_details.py`, key in env
  `GOOGLE_PLACES_API_KEY`), web search, and business websites if the network
  policy allows.

## Steps

1. **Health check.** Confirm the Make scenario "LeadGen – Reply & Sent Watcher"
   (6446669) is active and its last runs succeeded. If it isn't, say so in
   the summary email.
2. **Backup reply sweep.** For every row in `Sent` / `Follow-up * sent`, search
   Gmail for messages from that exact address (or, for custom domains, that
   domain) in the last 8 days that are *not* in the tracked thread. For any
   hit, set the row to `Replied` (or `Do-not-contact` if it's an opt-out), log
   it in `history`, and email Marcus an alert.
3. **Follow-ups due.** Business days since `first_sent`:
   - status `Sent` and ≥5 → draft follow-up 1 as a reply in the same thread;
     set `Follow-up 1 drafted`.
   - status `Follow-up 1 sent` and ≥12 → draft follow-up 2; set `Follow-up 2 drafted`.
   - status `Follow-up 2 sent` and ≥5 business days after follow-up 2 →
     set `Closed - no response`.
4. **New batch.** Pacing guard first: count rows still in `Drafted` (written
   but not sent yet). New drafts this week = 10 minus that count (never below 0),
   so unsent drafts never pile up past 10. If the result is 0, skip this step
   and say so in the summary. Otherwise take `New` rows ordered by distance
   until that many drafts exist (or the total cap is hit). For each:
   - Research: Places details (reviews, hours), website/search for owner name,
     services, how customers book, after-hours coverage, review themes.
   - Qualify: owner-operated, not a franchise or acquired brand, active, fits
     HVAC/plumbing. Otherwise set `Disqualified` with a reason.
   - Email: only a published business address. None → `No email - call/visit`.
   - Score fit 0-10 (automation opportunity + size + proximity). Below 6 →
     `Researched`, not drafted.
   - Write the email per `docs/tone-guide.md`. It must end with the standard
     no-pressure closing line from rule 7, not a sales pitch. Create the Gmail
     draft, then add labels `Outreach/To Review` (Label_21) and
     `Outreach/Active` (Label_22) to the draft message.
   - Write back to the row: fit_score, contact_name, contact_email,
     email_source, personalization_hook, research_notes, draft_id,
     **thread_id** (required, because the reply watcher matches on it), status
     `Drafted`, next_action `Review & send`, and a history line.
5. **Summary email to Marcus** (subject `[LeadGen] Monday batch – N drafts ready`):
   the list of drafts with one line each on the angle, follow-ups drafted,
   any backup-sweep hits, disqualified leads and why, and the no-email list
   for calls.
