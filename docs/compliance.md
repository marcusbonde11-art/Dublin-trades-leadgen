# Compliance & sustainability safeguards

This is cold B2B email in the US, which is legal under the CAN-SPAM Act when
the rules below are followed. This is a practical checklist, not legal advice.

## CAN-SPAM checklist (every commercial email)

- [x] Accurate From / Reply-To: sent from Marcus's own Gmail.
- [x] Subject line is not deceptive (no fake "Re:", no false urgency).
- [x] Identifies the sender plainly: name, what he does.
- [x] Valid physical postal address in the footer (`config.yaml → sender.postal_address`).
- [x] Clear way to opt out ("reply 'no thanks'") and honored immediately.
  The law allows 10 business days; the reply watcher marks opt-outs
  `Do-not-contact` automatically within ~4 hours.
- [x] No purchased lists, no harvested/guessed addresses.

## Data rules

- Only **business** contact addresses the business **publishes itself**
  (its own website or its own business profile). No guessing patterns like
  firstname@domain, no data-broker addresses, no personal addresses found on
  third-party sites.
- If no published email exists, the lead is marked `No email - call/visit`.
  Those are better handled by phone or in person anyway.
- Research uses public business information only (website, Google business
  profile, reviews). Nothing about individual customers is stored beyond what
  appears in a public review, and reviews are used only to understand the
  business's pain points.

## Pacing & reputation

- Nothing is sent automatically. Drafts sit in Gmail until Marcus hits send.
- Hard caps in `config.yaml`: 10 new drafts per week, 25 total drafts per week.
- Max 2 follow-ups, then the lead is closed.
- Sending ~2-3 per day (Tue-Thu mornings) keeps volume well under anything
  that looks like bulk mail and protects the Gmail account's reputation.
- The territory is small (~70 qualified shops). Owners talk. Quality over
  volume, always.

## Sticky suppression

- `Do-not-contact` is permanent. The watcher never changes it back, and the
  weekly routine never drafts to a row with that status, to its email, or to
  its domain.
- `Bounced` addresses are never reused.

## Later, when volume grows

- Move sending to a custom domain (Google Workspace) with SPF, DKIM, and DMARC.
- Keep personal Gmail for personal mail.
