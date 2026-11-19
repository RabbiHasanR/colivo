# Colivo — Mission

> Meal rate, rent, bills, members, bazar — manage any mess, hostel, PG or
> shared flat.

## What it is

Colivo is a web and mobile app for people who share a **home**: a mess,
hostel, PG or shared flat. Members log their own **meals**, **groceries** and
**payments**; the app works out each member's **bill** from the
**cost per meal**, **rent** and **utility bills**, and keeps the **home fund**
and **grocery fund** honest. The **owner** or a **manager** closes each
**month** in one step, and every balance carries forward.

## Why it exists

Shared homes run their money in a spreadsheet that one person maintains by
hand. Balances get miscalculated, nobody can see their own bill, and money
handed over without proof leads to arguments every month. Colivo replaces the
spreadsheet: everyone logs their own entries, every payment needs a receipt,
and the maths is done the same way every time.

## Scope (v1 — Focused MVP)

In scope:

- An **owner** signs up, which creates their **home**, and adds **members**
  by phone or email.
- Anyone logs in with a phone or email and a one-time code.
- The **owner** sets up **rooms**, **rent**, **home rules** (deposit months,
  notice period, rent-gap policy) and **bills**.
- The **owner** or a **manager** keeps the home's **contacts**: landlord,
  cook, internet and other providers, with several phones and emails,
  documents and their history; each bill can name who it is paid to.
- The **owner** or a **manager** can set an optional **estimate** for any
  bill (once for every month, or changed for one month); members see their
  share from the 1st, the actual bill replaces it, and any difference after
  close is adjusted next month.
- **Members** log daily **meals** per session (breakfast, lunch, dinner, as
  the home sets them), with their own **guests** counted separately. The
  **owner** or a **manager** adds **home guests** and **confirms** each
  session after it is cooked; only confirmed meals count, and members can't
  change a session once it is confirmed or the day is over.
- **Members** add **groceries**; the app shows the live **cost per meal**.
  One entry can be paid partly from a fund and partly from the member's own
  pocket.
- The **grocery fund** and **home fund** can be held by several people at
  once (the **owner**, any **manager**, and **fund keepers** chosen per
  fund). The app shows how much each one holds; cash paid to a person or
  handed over counts once they confirm it, and nobody spends more than they
  hold or were given.
- **Members** report anything they paid in one **I paid** flow, with a
  required receipt; a **manager** or the **owner** confirms or rejects it.
  A payment can mix a shared source with the member's own pocket; only the
  pocket part is credited.
- Anything bought for the home can be **returned** or exchanged on its
  original entry, so the home pays only for what it kept. Members send
  **corrections** of their own confirmed entries for a **manager** or the
  **owner** to confirm; confirmed money is never overwritten. Non-food
  **household** items are a bill, not groceries.
- A **refund** to a member counts only once they confirm they received it.
- A **manager** gives **home fund** money to a member to pay a **bill**.
- The **owner** or a **manager** changes **rent** for the home, a room or a
  member, from a chosen month.
- Every **member** sees their **bill** by purpose; the **owner** or a
  **manager** sees the **monthly statement** for everyone.
- The **owner** or a **manager** closes a **month**: member credits and
  dues, **home fund** and **grocery fund** cash, money still with shoppers
  and unpaid bills carry into the next month; unpaid bills are never charged
  to members twice; a closed month can't be reopened, only corrected.
- **Members** pay a **deposit** on joining, give **notice** to leave, and get
  a **final settlement**; past members stay on record.
- Every role has an **inbox**; members can **message** each other.
- Edits and deletes need a reason and are kept in **history** (soft delete).
- Responsive **web** first, then a **mobile** app on the same API.

Out of scope for v1 (revisit later): a person in more than one home, short-
notice waiver voting, whole-home move-out with landlord deposit settlement,
PDF/Excel export and WhatsApp sharing, meal cut-off times and default meal
patterns, reminders, grocery shopping roster, Bangla and other languages,
currencies other than ৳ (BDT), split methods other than meal-based groceries
(flatshare, bills-only, paying guest), payment gateway integration (bKash and
Nagad are recorded manually), transferring ownership, notification settings,
custom funds (repair, festival; shape agreed 19 Nov 2026).

## Who it's for

- **Owner** — the person who runs the home; signs up, sets it up and can do
  everything.
- **Manager** — handles the money day to day: records payments, confirms
  entries, pays bills, closes the month. A home can have several.
- **Fund keeper** — holds cash for the grocery fund, the home fund or both,
  and gives it to shoppers or bill payers. A fund can have several.
- **Member** — everyone who lives there (all roles are members too); logs
  meals and groceries, reports payments, sees their own bill.

## Stakeholder goals this serves

- **Rabbi Hasan (builder; owner and manager of the first home):** replace
  the flat's monthly spreadsheet; handle any mess scenario through home rules
  (deposit months, notice period, rent changes, rent gaps); make the app
  usable by other homes, with worldwide use later.

## Success looks like

- October 2026 replayed in Colivo gives the same balances as the spreadsheet,
  to the paisa.
- One full month runs in Colivo with no spreadsheet.
- Every member logs their own meals and payments; the manager no longer types
  them in.
- Closing a month takes under 10 minutes.
- Every payment has a receipt, so "who paid what" is never argued about.

See the build order in [roadmap.md](roadmap.md) and the technical rules in
[tech-stack.md](tech-stack.md).
