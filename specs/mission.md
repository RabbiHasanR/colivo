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
- **Members** log daily **meals** (lunch, dinner, guests).
- **Members** add **groceries**; the app shows the live **cost per meal**.
- A **fund keeper** holds the **grocery fund** and gives money to shoppers;
  nobody spends more than they were given.
- **Members** report anything they paid in one **I paid** flow, with a
  required receipt; a **manager** or the **owner** confirms or rejects it.
- A **manager** gives **home fund** money to a member to pay a **bill**.
- The **owner** or a **manager** changes **rent** for the home, a room or a
  member, from a chosen month.
- Every **member** sees their **bill** by purpose; the **owner** or a
  **manager** sees the **monthly statement** for everyone.
- The **owner** or a **manager** closes a **month**: credits and dues carry
  into the next month; a closed month can't be reopened, only corrected.
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
Nagad are recorded manually), transferring ownership, notification settings.

## Who it's for

- **Owner** — the person who runs the home; signs up, sets it up and can do
  everything.
- **Manager** — handles the money day to day: records payments, confirms
  entries, pays bills, closes the month.
- **Fund keeper** — holds the shared grocery cash and gives it to shoppers.
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