# Colivo: Mess, Hostel & Flat Manager

> Meal rate, rent, bills, members, bazar — manage any mess, hostel, PG or shared flat

Nov 12, 2026 · @Rabbi @ Spordium

## 1. Project overview

Mess Manager is a shared-home web app that replaces the monthly shared-home spreadsheet: members log meals, groceries and payments, and the system calculates every member's bill, the central fund and what is still owed to the landlord and providers. This version follows SRS v1.0.0-PROD (12 Nov 2026), which adds balanced utility redistribution, a per-category override ledger and a grocery fund, plus home-specific rules for deposit and notice period so the app fits any home.

**Problem today.** The October and November 2026 meal-track spreadsheets work, but only the manager can maintain them. Members send meal counts and bKash screenshots in chat, the manager re-types them, and one wrong cell breaks the cost per meal or someone's balance. Custom utility deals are handled by hand, so the utility total is easily under- or over-recovered.

**Vision.** A single ledger every member trusts: anyone can trace how the cost per meal, rent and utility shares were calculated, the books always balance, and month close takes minutes instead of an evening.

### Goals

| # | Goal | How we measure it |
| --- | --- | --- |
| G1 | Remove manual calculation | Recalculating October 2026 gives Rabbi Hasan +৳293.65 and Hijam Shusil +৳3,713.77, matching the sheet |
| G2 | Books always balance | Every month, member charges + bills to pay = total home expenditure (shared cost invariant) |
| G3 | Let members self-serve | Members log their own meals and check their own balance without asking the manager |
| G4 | Keep the fund honest | Home fund and grocery fund cash shown by the app equal the cash each holder (owner, managers, fund keepers, shoppers) actually has |
| G5 | Fast month close | Close the month and roll balances over in under 10 minutes |

### Scope

- **In scope (v1):** one home per account, rooms and members, configurable expense categories, per-member per-category overrides with balanced redistribution, daily meal grid per meal session (breakfast, lunch, dinner, as the home sets them) with member guests, home guests and daily confirmation by the owner or a manager, home contacts (landlord, cook, internet and other providers) with their history, grocery purchases and grocery fund top-ups, utility and rent bills, member payments and refunds, prior-month balance import and rollover (member balances, fund cash and unpaid bills), optional estimated bills, split-funded entries (shared fund plus own pocket), rent revisions (home-wide, per room or per member, up or down, with effective dates), configurable home rules (deposit months, notice period, short-notice policy), deposit ledger, leave notice and final settlement, dashboard and monthly statement.
- **Out of scope (v1):** multiple homes per account, short-notice waiver votes, whole-home move-out and landlord deposit settlement screens, bKash/Nagad gateway integration, cook salary payroll, grocery inventory, native mobile apps (the web app is mobile-first; Flutter app later).

### Words used in the app

The app uses plain words that people understand in any country. The earlier South Asian words can come back later as an optional word pack (see Release plan).

| Word in the app | What it means | Earlier name |
| --- | --- | --- |
| Home | The shared flat or house; one per account in the MVP | Mess, flat |
| Owner | The person who signed up and created the home; can do everything | Super admin |
| Manager | Runs the money day to day | Manager |
| Fund keeper | A member chosen to hold cash for the grocery fund or the home fund; a home can have several | Bazar box keeper |
| Holder | Anyone holding a fund's cash: the owner, a manager or one of that fund's fund keepers | — |
| Handover | Fund cash passed from one holder to another | — |
| Groceries | Food shopping that counts toward the cost per meal | Bazar |
| Grocery fund | Shared cash kept aside for grocery shopping | Bazar box |
| Home fund | Money held for rent and bills by the owner, managers or home fund keepers | Mess fund, cash in hand |
| Cost per meal | Grocery spending ÷ billable meals (BR-2) | Meal rate |
| Meal session | One meal of the day the home serves: breakfast, lunch or dinner; each home picks its own and how many meals each counts as | — |
| Guest meal | A meal for a member's own guest; counted and charged to that member | Guest meal |
| Home guest | A guest of the whole home (not of one member); cooked for, but not charged to anyone directly | — |
| Cook for | How many plates to cook for a session: members, their guests and home guests | — |
| Contact | A person or company the home deals with: landlord, cook, internet, electricity or gas provider, caretaker | — |
| Deposit | Rent a member pays before moving in; pays their last months' rent | Advance rent |
| Landlord deposit | One-time money paid to the landlord when the home was rented | Landlord advance |
| Credit | A positive balance carried into next month | Deposit (in balances) |
| Refund | Money the home pays back to a member | Refund |
| Return | Something bought for the home goes back to the shop, for money back or in exchange for something else | — |
| Household | Non-food things bought for the home (bulbs, wire, cleaning supplies); a bill category, not groceries | — |
| Cook | An example bill | Khala |

Prepaid and postpaid utilities keep their names for now.

## 2. Users and their needs

Each home is its own account; everyone is a member, and the owner can add the Manager and Fund keeper roles on top, any number of each (FR-62 to FR-67, FR-104).

| Role | Who | Main need | Pain point today | Device |
| --- | --- | --- | --- | --- |
| Owner | One person per home, usually whoever set it up | Full control: settings, roles, rules, and fixing anything | Everything depends on one spreadsheet only they can edit | Laptop + phone |
| Manager | Chosen by the owner (optional; a home can have several) | Record bills and payments, add members, close the month | Chasing members for money and receipts | Phone + laptop |
| Fund keeper | Members chosen to hold cash for the grocery fund or the home fund (optional; several per fund) | Know how much of each fund they hold and who has money from it | Arguments over whose money paid for groceries | Phone |
| Member | Everyone, including the three roles above | Log meals, record what they paid with proof, see what they owe and why | No visibility into cost per meal, shares or balance until month end | Phone |

### What every user needs from the system

- **Trust:** every number traces back to the entries that made it, and the totals always reconcile.
- **Speed:** daily actions (meals, groceries) take a few taps on a phone.
- **Fairness:** rent by room, meals by actual consumption, utilities split equally, and when someone has a fixed deal the rest is redistributed so the home never under-recovers.
- **Continuity:** last month's dues and surpluses carry forward automatically, or can be imported for the first month. Deposit is tracked from the day someone joins until it is used for their last months.

## 3. End-user stories

Each story is written as "As a … I want … so that …" with its acceptance check. New or changed since the 2 Nov version: A2, A4, A8, A11, A12, B3, B4, M1.

### Owner / Manager

| ID | Story | Accepted when |
| --- | --- | --- |
| US-A1 | As manager, I want to set up rooms with total rent and occupant count, so that rent per person is calculated for me | Room at 13,340 with 2 occupants shows 6,670 per person |
| US-A2 | As the owner, I want my home created when I sign up and to add members by phone or email, so that each home's data is kept separate | Members of one home never see another home's data |
| US-A3 | As manager, I want to add, deactivate and move members between rooms, so that the bill follows who actually lives here | Inactive members drop out of utility splits from the next cycle |
| US-A4 | As manager, I want to set a custom amount for a member per category (Rent, Electricity, Internet, Cook, Ad-hoc) for a billing cycle, so that fixed deals are respected | Override shows on the member's bill; the rest of that category is redistributed to the other members |
| US-A5 | As manager, I want to log rent and utility bills and say who paid them (central fund or a member), so that payments to the landlord and providers are tracked | A bill paid by a member is credited to that member |
| US-A6 | As manager, I want to record member payments by category (Rent, Prepaid Utility, Postpaid Utility, General) and method (Cash, Bank, bKash, Nagad), so that collections are complete | Payment appears in the member's ledger and in central cash |
| US-A7 | As manager, I want to pay out a refund to a member with surplus, so that the fund and their balance both go down | Refund lowers member balance and central cash by the same amount |
| US-A8 | As manager, I want a dashboard of meals, cost per meal, utilities, rent, total spend and home fund balance, so that I see the month at a glance | KPI cards update on every entry |
| US-A9 | As manager, I want to see home fund balance against unpaid landlord and provider dues, so that I know if the fund can pay the next bill | Fund card shows cash, each bill to pay and the gap |
| US-A10 | As manager, I want to close the month in one action, so that dues and surpluses roll into the next month | Next cycle opens with prior due/credit per member and empty logs |
| US-A11 | As manager, I want to import or enter prior-month balances (month, year, member, Due/Credit, amount), so that I can start from my October sheet | Imported balances feed the Prev Month Due / Credit columns |
| US-A12 | As manager, I want to define expense categories and their class (Rent, Prepaid, Postpaid, Ad-hoc), so that new bills fit without code changes | A new category appears in bill and override forms |
| US-A13 | As manager, I want to edit or correct any entry with a reason, so that mistakes are fixed without losing history | Every change keeps who, when and old/new values |
| US-A14 | As manager, I want to confirm each meal session after it is cooked (lunch, dinner, or both at once), so that only meals that were really eaten count | Confirmed sessions count in the cost per meal; members can no longer change them |
| US-A15 | As manager, I want to add guests of the whole home to a session, so that the cook cooks enough and their food cost is shared fairly | Home guests show in Cook for; the cost per meal rises to cover them; nobody is charged directly |
| US-A16 | As manager, I want to keep the landlord's, cook's and providers' details (several phones and emails, photo, documents, account ID), so that anyone running the home can reach them | Each contact shows all its numbers; documents are visible only to the owner and managers |
| US-A17 | As manager, I want to mark the cook as left and add the new one, so that the old cook's details and payments stay on record | The old cook moves to Past contacts; the Cook bill is paid to the new cook from then on |

### Grocery Shopper

| ID | Story | Accepted when |
| --- | --- | --- |
| US-B1 | As grocery shopper, I want to log date, amount and items from my phone, so that the spend is recorded the same day | Entry saved in under 30 seconds on mobile |
| US-B2 | As grocery shopper, I want to mark a purchase as paid from my own pocket, so that I get credited | Amount appears in my grocery credit and in the cost per meal |
| US-B3 | As grocery shopper, I want to mark a purchase as paid from the grocery fund or central fund, so that the right cash pot goes down | Grocery fund or central cash drops; nobody is credited |
| US-B4 | As a member, I want to record cash I put into the grocery fund, so that I'm credited without it counting as food cost | Grocery fund balance rises; cost per meal unchanged |

### Resident / Member

| ID | Story | Accepted when |
| --- | --- | --- |
| US-M1 | As a member, I want to set my own meals for each session of a day in half-meal steps, and my guests' meals separately, so that my meal count is accurate | Meal saved and Cook for updates immediately; I can change it until the session is confirmed or the day ends |
| US-M2 | As a member, I want to see the live cost per meal and my meal cost so far, so that I'm not surprised at month end | Rate = grocery purchases ÷ billable meals in confirmed sessions (BR-2) |
| US-M3 | As a member, I want a bill breakdown (meals, utility share, rent, prior due), so that I understand what I owe | Breakdown adds up to my total due; overrides are labelled |
| US-M4 | As a member, I want to see all my credits (groceries, bills I paid, payments, prior credit), so that I can check nothing is missing | History lists every credit by source |
| US-M5 | As a member, I want to see my net balance, so that I know whether to pay more or expect a refund | Shows "You owe X", "You have X credit" or "Settled" |
| US-M6 | As a member, I want to view past months, so that I can check old bills | Closed months are read-only and viewable |
| US-M7 | As a member, I want to see the cook's and providers' phone numbers, so that I can tell the cook "no lunch today" or report the internet down | Home contacts shows their names and phones; landlord details and documents are hidden |

### Joining, deposit and leaving

| ID | Story | Accepted when |
| --- | --- | --- |
| US-R1 | As manager, I want to set this home's rules — deposit months (0, 1, 2, 3…) and notice period months (0, 1, 2…) — so that the app works for any home | Rules saved with an effective date; a new member gets the rules in force on their join date |
| US-R2 | As manager, I want the app to show how much deposit a new member must pay, so that I collect the right amount | A ৳6,670 seat under a 2-month rule shows ৳13,340 required |
| US-R3 | As manager, I want to record deposit payments, including instalments, so that I see who still owes deposit | Deposit status shows Pending, Partially paid or Held |
| US-R4 | As a member, I want to give leave notice in the app with my planned leave date, so that everyone knows in time | Notice is timestamped, all members are notified, and the earliest allowed leave date is shown |
| US-R5 | As a member, I want the app to stop me choosing a leave date shorter than the home's notice period, so that everyone follows the same rule | Request shows each member's Agree / Disagree, or a linked replacement |
| US-R6 | (Later phase) As a member, I want to agree or disagree with someone's short-notice request in the app, so that the decision is recorded | Waiver is granted only when every active member agrees, or a replacement is confirmed |
| US-R7 | (Later phase) As a leaving member with a granted waiver, I want my unused deposit and any rent I paid for months after I leave refunded, so that I'm not charged for a seat I don't use | Final settlement shows Deposit Refund plus prepaid rent refund |
| US-R8 | As a leaving member, I want my deposit used for my last month(s) of rent when I give full notice, so that I don't pay rent twice | With 2 months' deposit, the final 2 months' rent shows "Covered by deposit" |
| US-R9 | As manager, I want a final settlement for a leaving member, so that meals, utilities, dues and leftover deposit are cleared in one statement | Final statement shows deposit applied and the refund or amount owed; member becomes Left |
| US-R10 | As a member, I want to see my deposit held and which months it will cover | Bill card shows the deposit amount and the covered months |
| US-R11 | As manager, I want to record the deposit the home paid to the landlord, so that I know how much the landlord holds and when it will be adjusted or returned | Landlord deposit card shows amount paid, adjusted against rent, deducted for repairs (itemised), returned and still held |

### Rent changes

| ID | Story | Accepted when |
| --- | --- | --- |
| US-C1 | As manager, when the landlord raises home rent (usually yearly), I want to enter the new home rent and an effective month, so that bills change from that month on | Closed months keep old rent; bills from the effective month use the new rent |
| US-C2 | As manager, I want to choose how a home-wide change is shared — same amount for every member, or same percent of each member's current rent — so that it fits our home's rule | Preview shows each member's old rent, new rent and difference before I confirm |
| US-C3 | As manager, I want to raise or lower one room's rent or one member's rent at any time of year, so that room swaps, renovations or special deals are handled | Only that room's occupants or that member change; others stay the same |
| US-C4 | As a member, I want to see my rent history and why it changed, so that I trust the new amount | Bill card lists each change with date, reason and method |
| US-C5 | As manager, I want to see if members' rents no longer add up to the landlord's rent, so that the home doesn't silently lose money | Dashboard shows the rent gap (surplus or shortfall) per month |

### Everyday flows

| ID | Story | Accepted when |
| --- | --- | --- |
| US-E1 | As a new member, I want to log in with the phone or email the manager added me with, so that I don't need to sign up | An SMS or email arrives; a one-time code logs me in |
| US-E2 | As a member, I want to record anything I paid (rent, utilities, grocery fund, groceries, a bill) with a receipt, so that it counts toward my balance | Entry saved as Waiting until confirmed |
| US-E3 | As a manager, I want an inbox of payments to confirm with their receipts, so that nothing counts without proof | Confirm or Reject in one tap |
| US-E4 | As anyone holding fund cash, I want to give cash from the grocery fund or home fund to a shopper or bill payer, so that they spend only what they were given | Given amount shows on their home; I can't give more than I hold; overspending is blocked |
| US-E5 | As anyone, I want to fix a wrong entry with a reason, so that mistakes are corrected without hiding them | History shows who changed what and when |
| US-E6 | As a manager, I want a checklist before closing the month, so that I don't carry forward surprises | Dues, unpaid bills and money with shoppers are listed |
| US-E7 | As the owner or a manager, I want to deactivate members and see past members with their documents and settlements | Leaving members are deactivated at settlement and listed as past members |
| US-E8 | As a member, I want to message the home or one person in the app, so that money talk stays next to the records | Group chat and one-to-one chats with photos |
| US-E9 | As a manager, I want to optionally set an estimated amount for bills like cook, electricity or internet as a default for every month, and change it for one month when needed, so that members know their share from the 1st | Each member's bill shows their estimated share; categories without an estimate are unchanged |
| US-E10 | As a manager, I want unpaid bills, home fund cash and grocery fund cash to move into the next month when I close, so that nothing is lost or charged twice | Next month opens with the same cash and a "From \<month>" bill to pay; paying it isn't split again |
| US-E11 | As a member or shopper, I want to record one payment that was partly from the grocery fund or given money and partly from my pocket, so that I don't make two entries | One entry, one receipt; I'm credited only the pocket part |
| US-E12 | As a member, I want to record that something I bought went back to the shop, for money back or in exchange for something else, so that the home is charged only for what it kept | The original entry shows "Returned ৳X"; after confirmation my credit and the totals use the amount kept |
| US-E13 | As a member, I want to send a correction for my own confirmed entry, so that a mistake I made is fixed without asking the manager to retype it | The correction waits for confirmation; the old amount counts until then; history shows both |
| US-E14 | As a member, I want to confirm that I received a refund the manager paid me, so that "I gave it back" is never argued about | The refund counts only after I confirm it |
| US-E15 | As a member, I want to say who I gave my cash to (Rabbi, Karim or Hijam), so that the app knows who holds it | The person I name confirms they received it; it then counts in their cash |
| US-E16 | As anyone holding fund cash, I want to hand it over to another holder in the app, so that the app always matches who really has the money | The receiver confirms; my cash goes down and theirs goes up; the fund total stays the same |
| US-E17 | As a member, I want to see how much of each fund every holder has, so that I know the money is safe and accounted for | The Funds view lists every holder's cash and money with shoppers, adding up to the fund total |

## 4. Features

The MVP (P1) covers everything the October and November spreadsheets do, organised into the five screens from the SRS; P2 and P3 add comfort and automation.

| Screen / module | Feature | Priority | Users |
| --- | --- | --- | --- |
| Account | Home account; every record scoped to its home | P1 | Manager |
| Account | Owner sign-up creates the home; members added by phone or email log in with a one-time code; roles per home | P1 | All |
| 1. Dashboard & config | KPI cards: total meals, cost per meal, prepaid vs postpaid utilities, total rent, total spend, home fund balance | P1 | All |
| 1. Dashboard & config | Room table: name, total rent, occupants, auto rent per person | P1 | Manager |
| 1. Dashboard & config | Member profiles: name, room, Active / Inactive | P1 | Manager |
| 1. Dashboard & config | Expense categories with class: Rent, Prepaid Utility, Postpaid Utility, Ad-hoc | P1 | Manager |
| 1. Dashboard & config | Custom override form: member, category, amount, billing cycle, note; live recalculation of redistributed shares | P1 | Manager |
| 2. Meal grid | Calendar grid: dates 1–31 × members, one sub-column per meal session the home has on (FR-106) | P1 | All |
| 2. Meal grid | Own meals in half-meal steps and guest meals as a separate count, by stepper or typed decimal (FR-08) | P1 | All |
| 2. Meal grid | Home guests row per session (FR-107) | P1 | Owner, Manager |
| 2. Meal grid | Confirm a session after it is cooked, or several at once; confirmed sessions are locked for members (FR-108, FR-09) | P1 | Owner, Manager |
| 2. Meal grid | Footer row: per-member monthly meals and grand total; Cook for per session; live cost per meal from confirmed sessions | P1 | All |
| 2. Meal grid | Members edit their own column until the session is confirmed or the day ends; owner and managers edit any | P1 | All |
| 2. Meal grid | Default meal pattern and meal-edit cut-off time | P2 | Member, Manager |
| 3. Expenses & groceries | Bill entry: date, category, amount, description, paid by (member or central fund), paid to vendor yes/no | P1 | Manager |
| 3. Expenses & groceries | Groceries tab: grocery purchases separated from money added to the grocery fund | P1 | Grocery shopper, Manager |
| 3. Expenses & groceries | Filter by category, month and payer | P1 | All |
| 3. Expenses & groceries | Moved to P1 (FR-74): receipt, screenshot or photo required on every payment | P2 | Grocery shopper, Manager |
| 3. Expenses & groceries | Grocery shopping roster | P3 | Manager |
| Payments | Member payment: category, method (Cash, Bank, bKash, Nagad), note | P1 | Manager |
| Payments | General lump-sum payment not tied to a category | P1 | Manager |
| Payments | Refund disbursement with balance and cash checks; the member confirms receipt (FR-16) | P1 | Manager, Member |
| Payments | Moved to P1 (FR-75): member reports "I paid" with proof; manager confirms | P2 | Member, Manager |
| 4. Prior balance rollover | Manual entry and file import of prior balances (month, year, member, Due / Credit, amount, date-time), plus opening home fund and grocery fund cash, money with shoppers and unpaid bills | P1 | Manager |
| 4. Prior balance rollover | Automatic rollover on month close | P1 | Manager |
| 4. Prior balance rollover | Correct an entry in a closed month (owner or manager, reason required; the difference goes into the open month) | P2 | Manager |
| 5. Monthly statement | Per member: room, meals, meal cost, utility share (overrides shown), rent, total cost, itemised credits, prior due/credit, net balance, refund action | P1 | All |
| 5. Monthly statement | Personal bill card with history | P1 | Member |
| 5. Monthly statement | Central fund card: collected, spent from fund, refunds, home fund balance, grocery fund, bills to pay | P1 | Manager (visible to all) |
| 5. Monthly statement | Export to PDF / Excel; share summary to WhatsApp | P2 | Manager |
| Audit | Immutable change log for every money and meal entry | P1 | Manager |
| Notifications | Reminders: log meals, dues outstanding, month close | P3 | All |
| Language | Bangla / English interface | P3 | All |

### Home rules, deposit and leaving

These features make one app fit any home: each home sets its own rules instead of the rules being hard-coded.

| Module | Feature | Priority | Users |
| --- | --- | --- | --- |
| Home rules | Settings: deposit months, notice period months, notice period is a minimum, effective date, rule history | P1 | Manager |
| Member lifecycle | Join date, leave date and status: Active, Notice served, Left | P1 | Manager |
| Deposit | Required deposit calculated at join; deposit payments with instalments; status Pending / Partially paid / Held / Applied / Refunded | P1 | Manager, Member |
| Deposit | Deposit ledger per member: paid, applied to rent, refunded, remaining | P1 | All |
| Leave notice | Member or manager submits notice with planned leave date; earliest allowed leave date shown; all members notified | P1 | Member, Manager |
| Short-notice waiver | Later phase: waiver vote with Agree / Disagree from every active member | P1 | All |
| Short-notice waiver | Later phase: a confirmed replacement grants the waiver | P1 | Manager |
| Short-notice waiver | MVP: a leave date earlier than the notice period can't be chosen | P1 | Manager |
| Final settlement | Full notice: deposit applied automatically to the last months' rent | P1 | Manager |
| Final settlement | Later phase: with a waiver, unused deposit and rent already paid for later months are refunded | P1 | Manager |
| Final settlement | Final statement: meals, utilities, rent, deposit applied or refunded, refund or due; member set to Left | P1 | Manager, Member |
| Landlord deposit | One-time landlord deposit at lease start: date, amount, months of home rent it covers, receipt; funded from the founding members' deposits | P1 | Manager |
| Landlord deposit | Untouched by member changes; at home move-out the landlord adjusts it against last months' rent, returns it, or deducts repair costs, in any mix; itemised repair deductions shared among members; top-up if rent rises; status Held / Settled at move-out | P1 | Manager |
| Fund view | Shows member deposits held, landlord deposit held and cash free to spend, and checks they reconcile; cash is shown per holder | P1 | Manager (visible to all) |
| Seat vacancy | Seat shows vacant from the leave date; incoming replacement's deposit can fund the leaving member's refund | P2 | Manager |
| Deposit | Top-up request when a member's rent share rises | P2 | Manager |
| Leave notice | Withdraw a notice before the leave date | P2 | Member, Manager |

### Rent revisions

| Module | Feature | Priority | Users |
| --- | --- | --- | --- |
| Rent revisions | Home-wide change: enter new home rent or a percent, plus effective month and reason | P1 | Manager |
| Rent revisions | Split method, set in home rules and changeable per revision: equal amount per member, or same percent of current rent | P1 | Manager |
| Rent revisions | Room-level change: new total rent for one room, shared by its occupants | P1 | Manager |
| Rent revisions | Member-level change: raise or lower one member's rent (stored as a dated rent override) | P1 | Manager |
| Rent revisions | Preview table of old vs new rent for every affected member before confirming | P1 | Manager |
| Rent revisions | Rent history per home, room and member; past closed months never change | P1 | All |
| Rent revisions | Rent gap card: members' total rent vs landlord rent, per month; gap handled by the rent gap policy (split equally, split by rent share, home fund or ask members), overridable per revision | P1 | Manager |
| Rent revisions | Deposit top-up prompt when rent rises (member deposit, and landlord deposit if the landlord asks) | P2 | Manager |
| Rent revisions | Reminder before the yearly rent-change anniversary of the lease | P3 | Manager |

### Roles, money flows and everyday tools

| Module | Feature | Priority | Users |
| --- | --- | --- | --- |
| Roles | Owner, Manager, Fund keeper on top of Member; any number of managers and fund keepers; fund keepers chosen per fund; defaults when a role is empty | P1 | Owner |
| Fund holders | Cash per holder for each fund; pay to a named holder who confirms; hand over cash between holders (FR-104, FR-105) | P1 | All |
| Members | Add by phone or email with SMS/email notice; photo; required ID document; activate / deactivate | P1 | Owner, Manager |
| Members | Past members list with documents, bills and settlement | P1 | Owner, Manager |
| Contacts | Landlord, cook and provider contacts: several phones and emails, photo, account ID, documents; past contacts kept (FR-109, FR-110) | P1 | Owner, Manager |
| Contacts | "Paid to" contact per bill category, shown on Bills to pay (FR-111) | P1 | Owner, Manager |
| Contacts | Read-only names and phones of the cook and providers for every member (FR-112) | P1 | All |
| Grocery fund | Give cash from the grocery fund to a shopper; nobody gives out more than they hold | P1 | Fund keeper, Manager |
| Bills | Give home-fund cash to a member to pay a bill | P1 | Manager, Owner |
| I paid | One screen for every payment, with purpose, proof and confirmation by role | P1 | All |
| Inbox | Payments to confirm, edits to review, notices, grocery fund alerts | P1 | All |
| History | Edit or delete with a reason; full change history | P1 | All |
| Returns | Return or exchange on a grocery or bill entry, with money back and an optional replacement item (FR-102) | P1 | All |
| Corrections | Member sends a correction for their own confirmed entry; owner or manager corrects any entry directly (FR-103) | P1 | All |
| Month close | Checklist before closing | P1 | Manager, Owner |
| Month close | Carry forward home fund and grocery fund cash, money with shoppers and unpaid bills (FR-99) | P1 | Manager, Owner |
| Bills | Optional estimated bills: default per category for every month, changeable for one month; adjustment after close (FR-100, FR-101, BR-22) | P1 | Manager, Owner |
| Split funding | One entry paid from a shared source plus own pocket, for groceries and bills (FR-98) | P1 | All |
| Leaving | Give notice (minimum notice enforced); final settlement | P1 | Member, Manager |
| Messages | Home group chat and one-to-one chats with photos | P1 | All |
| Login | Phone or email with a one-time code | P1 | All |

## 5. Functional requirements

The system SHALL meet these requirements for v1; each maps to a feature above.

### Account, setup and access

- **FR-01** The system shall support multiple home accounts; every room, member, entry and report belongs to exactly one home.
- **FR-02** The system shall let the manager create, edit and archive rooms with name (unique in the home), total rent and occupant count (at least 1).
- **FR-03** The system shall calculate rent per person as total rent ÷ occupants.
- **FR-04** The system shall let the manager add members (name unique in the home), assign a room, and set Active / Inactive.
- **FR-05** The system shall let the manager define expense categories, each with one class: Rent, Prepaid Utility, Postpaid Utility or Ad-hoc. A new home starts with a **Household** category (Ad-hoc) for non-food things bought for the home, such as bulbs, wire or cleaning supplies; they are shared like any other bill, never through the cost per meal.
- **FR-06** The system shall store custom overrides per member, per category, per billing cycle, with a note; at most one per member, category and cycle.
- **FR-07** Members shall sign in and see only their own home; what each person can change depends on their roles (FR-62 to FR-66).

* **FR-83** Sign-up is for the person who runs the home. They enter their name and phone or email, confirm a 6-digit code, then give the home a name (plus optional area, the first month and whether they live there too). The home is created at once and they become its owner. In the MVP one account owns one home.
* **FR-84** Members don't sign up. The owner or a manager adds them by phone or email (FR-79); they log in with that phone or email and a one-time code. No home code or invite link is needed, because the phone or email already points to exactly one home. _Changed on 21 Nov 2026: from Phase 1b a person can be in several homes and chooses one after logging in._
* **FR-85** In the MVP a person can be an active member of only one home. Adding a phone or email that is active in another home is blocked with a message. Someone who wants their own home must leave the current one first; once deactivated they can be added elsewhere. _Replaced on 21 Nov 2026 (Phase 1b): a person can be an active member of several homes; adding someone already in this home is refused._
* **FR-86** A member's first log-in shows the home, their role, room and join date to check. They can fix their name and add a photo; the room or join date can only be changed by the owner or a manager.
* **FR-87** Logging in with a phone or email that isn't linked to any home shows "not added yet", with two choices: ask the home's owner or manager to add it, or create a new home.
* **FR-88** Each home gets a short Home ID (for example OF-4827), shown in Home settings for support. Members never need to type it.

### Meals

- **FR-08** The system shall store, per member, per date and per meal session (FR-106), the member's **own** meals (0, 0.5 or 1) and their **guest** meals (0 or more, in 0.5 steps) as two separate counts. Both are that member's meals and are charged to them at the cost per meal.
- **FR-09** Editing meals:
  - A member edits only their own meals, and only until that session is confirmed (FR-108) or the day ends at midnight in the home's time zone, whichever comes first. Future days are always open.
  - The owner and managers can edit anyone's meals, and home guests, until the month is closed. An edit to a confirmed session is kept in the change log (FR-27) and counts at once without a new confirmation (FR-75).
- **FR-10** The system shall show per-member and grand-total meals, the Cook for count of each session (BR-24), and recalculate the cost per meal whenever a confirmed session or a grocery entry changes. Sessions not yet confirmed show as "Waiting" and don't count yet.
- **FR-11** The system shall support bulk save of a whole day or week in one request, and confirming several sessions in one action (for example lunch and dinner together).
- **FR-106** Meal sessions. Each home has its own list of meal sessions; a new home starts with Lunch and Dinner on and Breakfast off. The owner can turn a session on or off, set the order, and set its **weight**: how many meals one serving counts as (default 1; for example Breakfast 0.5). Turning a session off keeps its past entries. A weight change applies to the whole open month; closed months keep their weights.
- **FR-107** Home guests. The owner or a manager can record **home guests** for a date and session: guests of the whole home rather than of one member (for example the landlord, or a guest everyone invited). They count in Cook for (BR-24) but not in billable meals (BR-2), so their food cost is shared through the cost per meal; nobody is charged for them directly.
- **FR-108** Meal confirmation. After a session is cooked, the owner or a manager confirms it for that date, first fixing members' and home-guest counts to what was really eaten. A session can't be confirmed before its date. Confirmation records who and when, and is not undone; later changes are owner or manager edits (FR-09). Only confirmed sessions count towards the cost per meal.

### Expenses and groceries

- **FR-12** The system shall record bills with date, category, amount (0 or more), description, paid by (a member, or the central fund when empty) and whether it has been paid to the landlord or provider; when the category names a payee contact, also whom it was paid to (FR-111).
- **FR-13** The system shall record grocery entries of two kinds: a grocery purchase (with funding source: own pocket, grocery fund, central fund, money given to the shopper, or a split of one shared source plus own pocket, see FR-98) and a top-up of the grocery fund (shared cash members put aside for shopping).
- **FR-14** Only grocery purchases, less their returns (FR-102), shall count towards the cost per meal; grocery fund top-ups and Household items shall not.
- **FR-15** The system shall show the grocery fund balance: opening balance carried from last month (FR-99) plus top-ups in, minus purchases paid from the grocery fund. The balance is split by who holds it: each holder's cash (BR-23) plus money with shoppers.

* **FR-68** Only a holder of the grocery fund (one of its fund keepers, a manager or the owner) can take money out of it, and only from the cash they hold. They can spend it directly on groceries, or give an amount to another member who is shopping.
* **FR-69** A member given grocery money can record groceries paid from that money, up to the amount given. Anything above it is paid from their own pocket, in the same entry (FR-98). Leftover money is returned to a grocery fund holder, who confirms it (FR-105).
* **FR-70** No one can spend or give out more of a fund than they hold; no holder's cash can go below ৳0 (BR-23). The Funds view shows each holder's cash and the money currently with shoppers.

- **FR-71** A holder of the home fund (the owner, a manager or a home fund keeper) can give money from it to a member to pay a specific bill (rent, a utility, the cook's salary), or pay a bill from it themselves. Never more than they hold, and never more than the home fund's free-to-spend cash (FR-32).
- **FR-72** The member records the payment as paid from the given money, from their own pocket, or both. Given money can't be exceeded; any extra is credited to the member as paid from their pocket. Leftover given money goes back to a home fund holder, who confirms it (FR-105). The bill is then marked paid.
- **FR-73** Every person, including the owner, managers and fund keepers, is also a member and has the same member features: own meals, own groceries, paying bills, own bill and balance. The owner can do everything any role can.

- **FR-98** Split funding. Any grocery purchase or bill payment can be recorded as **one entry** paid from up to two sources: one shared source (grocery fund, home fund, or money given to the payer) plus the payer's own pocket. The payer enters the total; the shared part defaults to everything still available from that source (given amount left, grocery fund balance, or home fund free-to-spend cash) and can be lowered, and the rest is the pocket part. The shared part can never exceed what is available; the pocket part is credited to the payer (BR-6). The entry keeps one receipt, one history and one confirmation. The cost per meal or bill total uses the full amount, not each part. Applies to the grocery entry screen, "I paid", "I paid a bill" and the manager's bill entry.

### Everyday flows and safeguards

- **FR-74** Every record of money paid (a member's payment to the manager, a bill paid, groceries bought, a payment the manager records) needs proof: a receipt, screenshot or photo. It can't be saved without one.
- **FR-75** Members and fund keepers record everything they pay on one "I paid" screen, choosing the purpose: rent, prepaid or postpaid utilities, general payment, deposit, money put into the grocery fund, groceries they bought, or a bill they paid. When the money goes to a person (rent, utilities, general, deposit, grocery fund top-up), they also choose **who received it**, from that fund's holders. It counts only after confirmation:
  - Money given to a holder is confirmed by **the holder who received it**; until then it is in nobody's cash (FR-104).
  - Everything else (groceries or bills paid from the member's own pocket or from money given to them), and anything a fund keeper adds, is confirmed by a manager or the owner.
  - Entries by managers and the owner are saved without confirmation; the other managers and the owner see them as updates in their inbox.
- **FR-76** An inbox shows each person what needs them (payments to confirm, bills paid with given money, edits to review, returns and corrections to confirm, refunds to confirm receiving) and updates (notices, grocery fund low, entries the owner or a manager corrected).
- **FR-77** Any entry can be edited or deleted with a reason; the full history (who, when, old and new value) stays visible. Closed months can't be changed. Who can change a confirmed entry, and how, is in FR-103; returns are in FR-102.
- **FR-78** Before closing a month the app shows a checklist: unlogged meals, meal sessions not yet confirmed (FR-108; closing anyway confirms them as logged), unpaid dues, unpaid bills, bills still on an estimate (FR-101), money still with shoppers, returns and corrections waiting for confirmation, refunds waiting for the member, handovers and payments waiting for their receiver, and a cash count of each fund **per holder** (each holder checks the cash they have against the app). The manager can fix items first or close anyway.
- **FR-79** The owner or a manager adds a member by phone or email; the app sends an SMS or email so they can log in with a one-time code. Only the owner signs up (FR-83); members never sign up, and there is no invite link or home code.
- **FR-80** The owner and managers can deactivate or reactivate a member. Final settlement deactivates the leaving member automatically; deactivated members can't log in. A member who still holds fund cash or given money can't be deactivated until they hand it over (FR-105).
- **FR-81** A Past members list (owner and managers only) keeps each former member's contact details, ID documents, monthly bills and final settlement.
- **FR-82** Members can message each other: one group chat for the home plus one-to-one chats, with photo attachments. Only people in the home can join.

* **FR-89** Closing a month can't be undone and needs a final confirmation that shows what moves into the next month: member dues and credits, home fund and grocery fund opening cash per holder, money still with shoppers, and unpaid bills (FR-99). A closed month is never reopened.
* **FR-90** The owner or a manager can still correct an entry in a closed month. A reason is required; the closed month's statement shows the corrected figures, and each member's difference is added to the open month as an "\<month> correction" line. Everyone affected is told, and the change is kept in the entry's history.
* **FR-91** Rejecting a payment or entry needs a reason (amount doesn't match, receipt not clear, money not received, wrong purpose, or other) and an optional note. The sender sees the reason in their inbox and can fix it and send again with a new receipt, or withdraw it. A rejected entry never changes any balance.
* **FR-92** Deactivating a member needs a confirmation with the date it starts; it can be undone at any time with Reactivate, which asks for the date charges start again. Any amount the member still owes stays on their record. Changing rent (owner or manager only) also asks for confirmation and shows each member's new share before it's saved.
* **FR-93** Every inbox is role-aware: members see payments, returns and corrections confirmed or rejected, money given to them, refunds to confirm receiving, entries of theirs the owner or a manager corrected, notices and rent changes; fund holders also see cash paid to them, handovers to them and returned money to confirm; managers and the owner see other managers' entries as updates.
* **FR-94** Log-in codes last 5 minutes. After 5 wrong codes the phone or email is locked for 15 minutes. A new code can be sent once a minute, up to 5 times an hour.
* **FR-95** A new home shows a setup checklist (rooms and rent, members, home rules, bills) and empty screens that explain what will appear there, instead of blank lists.

- **FR-96** Deleting is always a soft delete: the entry leaves every total but stays in the history ("Deleted by Rabbi · Entered twice"), and affected members are told. Who can delete what:
  - Anyone can withdraw their own entry while it is still waiting for confirmation.
  - The owner or a manager can delete a grocery, bill, payment or money-given entry in the open month, with a reason.
  - Nothing in a closed month can be deleted; it can only be corrected (FR-90).
  - A member's confirmed payment can't be deleted by the member; the owner or a manager can only correct it.
  - Members are deactivated, never deleted. Rooms and bill types that have entries are archived. Meals are set to 0. Deposit-applied and final settlement records are never deleted.
- **FR-97** On the web the same confirmations open as a centred dialog instead of a bottom sheet; rejecting a payment happens inside the inbox's detail panel; empty states and log-in errors use the same wording as mobile.

### Returns and corrections

Confirmed money is never overwritten. A return or a correction is a new entry linked to the original; the original keeps its values, every total uses the original plus its confirmed corrections, and the entry's history shows each step.

- **FR-102** Return or exchange. When something bought for the home (a grocery entry or a bill, Household items included) goes back to the shop, the person who paid records a **Return** on the original entry:
  - **Returned:** the value of what went back; it can't be more than the original amount less earlier returns.
  - **Taken instead (optional):** what was taken in exchange, with its own receipt. Money back = returned − taken instead.
  - **Reason** and **proof:** the shop's return slip, or a photo of the item with a note when the shop gives none (FR-74).
  - **Confirmation:** the same as the original entry's (FR-75). A pending return changes no balance; a rejected one follows FR-91.
  - **Split-funded entries (FR-98):** the money back lowers the pocket part first, then the shared part. Any shared part that comes back is money the payer holds for that source, shown as money with shoppers, and is returned to a holder of that fund like leftover given money (FR-69, FR-72, FR-105).
  - **Totals:** the cost per meal or bill total uses the original amount − returned + taken instead. The original entry shows "Returned ৳X" and links to the return.
  - **Closed months:** a return on an entry from a closed month is a closed-month correction (FR-90). The member can record it; the owner or a manager confirms it.
  - **Shop credit:** not tracked in v1. If the shop keeps the money as credit, nothing is recorded until all of it is used; then the return is recorded with what was taken instead, and money back is ৳0. Anything taken beyond the credit is a new entry.

  Example: Rahim pays ৳800 from his own pocket for wire; it is confirmed and he is credited ৳800. He returns the wire, takes a plug for ৳350 and gets ৳450 back. After the manager confirms the return, the entry counts ৳350 and Rahim's credit is ৳350; no cash moves inside the home.

- **FR-103** Correcting a confirmed entry. While an entry waits for confirmation, its sender can edit or withdraw it (FR-91, FR-96). Once it is confirmed:
  - A **member** (or a fund keeper) can't change it directly. They send a **correction** of their own entry: the new values, a reason, and a new receipt when the amount changes. It goes to whoever confirms that kind of entry (FR-75). Until it is confirmed the old values count; a rejected correction follows FR-91. A correction can also ask to remove an entry entered twice, which the owner or a manager confirms as a delete (FR-96).
  - The **owner or a manager** can correct any entry directly, with a reason. The member it belongs to is told in their inbox, with the old and new values. In v1 there is no dispute step; the member can reply in messages.
  - Corrections by the owner or a manager to their own entries are saved without confirmation, like their other entries (FR-75), and stay in the history.
  - A member can never correct someone else's entry.
  - An entry from a closed month is corrected under FR-90.

### Fund holders and handover

A fund is money kept for a purpose (the grocery fund and the home fund in v1). Its cash can be with several people at once, and the app tracks how much each one has, so the cash shown always matches the cash in people's hands (G4). Custom funds come later (Release plan).

- **FR-104** Fund holders.
  - **Who can hold a fund:** the owner and every manager can hold either fund. The owner or a manager can also choose any number of members as **fund keepers** of the grocery fund, the home fund or both. A fund with no fund keeper is held by the owner and managers.
  - **Cash per holder:** for each fund the app keeps every holder's cash (BR-23). The fund's balance is the sum of its holders' cash plus money given to members and not yet spent (money with shoppers).
  - **Paying a holder:** money paid into a fund names the holder who received it (FR-75) and counts in their cash once they confirm it.
  - **Spending:** a holder can spend, give out or refund only what they hold of that fund. From the home fund, the home's free-to-spend cash (FR-32) can't go below ৳0 either, because deposit cash stays reserved (BR-17).
  - **Removing a holder:** taking the fund keeper role away, or deactivating the member (FR-80), is blocked while they hold cash or given money; they hand it over first (FR-105).
  - **Month close:** each holder's cash is counted (FR-78) and carried into the next month with the same holder (FR-99).
- **FR-105** Handover. A holder passes cash to another holder of the same fund (for example, Karim hands ৳4,000 of rent cash to Rabbi):
  - The giver records the handover with an amount and optional proof; it can't be more than they hold.
  - The **receiver confirms** it. Until then the amount stays in the giver's cash but they can't spend it; if the receiver answers "Not received", it is released back to the giver (like FR-91).
  - The fund's total never changes; only who holds it.
  - Leftover given money handed back by a shopper (FR-69, FR-72) and money from returns (FR-102) are handovers to a holder of that fund.
  - Moving cash between the grocery fund and the home fund is a handover between funds that only the owner or a manager can start; both fund totals change by the same amount.

### Payments

- **FR-16** The system shall record member payments with date, amount (more than 0), category (Rent, Prepaid Utility, Postpaid Utility, General, Refund, Deposit, Deposit Refund), method (Cash, Bank, bKash, Nagad) and note.
- **FR-17** A Refund shall reduce both the member's balance and home fund balance. The owner or a manager records it with proof (FR-74), paid from the home fund cash they hold (FR-104); it counts only after the member confirms they received it in their inbox. The member can instead answer "Not received" with a reason, which sends it back to whoever recorded it, like a rejection (FR-91). Until then it shows as "Waiting for member", and the month-close checklist (FR-78) lists it.
- **FR-18** The system shall block a refund larger than the home fund balance and warn when it exceeds the member's positive balance.

### Dashboard and statements

- **FR-19** The dashboard shall show total meals, cost per meal, prepaid and postpaid utility totals, total rent, total operational spend and home fund balance.
- **FR-20** The monthly statement shall show, per member: room, meals, meal cost, utility share (marking overrides), rent, total cost, prior due, each credit by source, prior credit, refunds and net balance.
- **FR-21** The fund view shall show money collected, paid from the fund, refunded, home fund balance, grocery fund and bills to pay by class.
- **FR-22** Every figure shall link to the entries that produced it.
- **FR-23** The system shall check the shared cost invariant on every recalculation and flag the month if it does not hold.

### Month cycle and audit

- **FR-24** The manager shall enter or import prior-month balances for the first month on the app, at most one of each per month (and per member or bill where relevant):
  - **Member balances:** month, year, member, Due or Credit, amount, date-time.
  - **Home fund opening cash:** amount each holder (owner, managers, home fund keepers) holds for the home.
  - **Grocery fund opening cash:** amount each grocery fund holder holds.
  - **Money still with shoppers:** member and amount given but not yet spent or returned.
  - **Unpaid bills:** category, month, amount owed, and whether it is an estimate.

  Imported records are the same carry-forward records month close writes (FR-25, FR-99), so the first month works like any other: paying an imported bill lowers home fund cash and is not split among members again. The import shows a check that imported cash and bills match what the manager and fund keeper actually hold.
- **FR-25** Closing a month shall lock its entries and write one prior-month record per member with a non-zero balance: Due for negative, Credit for positive.
- **FR-26** The next cycle shall start with empty meal, expense and payment logs, the rolled-over balances and carry-forward records (FR-99), the same rooms, members and categories, and each bill category's default estimate (FR-100).
- **FR-99** Closing a month shall also write carry-forward records for the home, so no money disappears between months:
  - **Home fund opening cash:** each holder's closing home fund cash (BR-8, BR-23), carried to the same holder.
  - **Grocery fund opening cash:** each holder's closing grocery fund cash (FR-15, BR-23), carried to the same holder.
  - **Money still with shoppers:** each open given-money amount, carried to the same member; they can still record what they spent or return it.
  - **Carried bills:** each bill not yet paid to the provider (for example October gas), with category, original month, amount owed and whether it was an estimate. These show in the next month's Bills to pay as "From October".

  Paying a carried bill lowers home fund cash and the carried bill; it is **not** a new expense of the open month and is never split among members again (members were already charged in the closed month). If an estimated bill's actual amount differs, BR-22 applies.
- **FR-100** Estimated bills are optional. For any bill category (cook, electricity, internet, gas, service charge, or a category the manager adds) the owner or a manager can set a **default estimate** that is used every month. They can change or remove the estimate for one month only, without changing the default, until that month is closed. A category with no estimate works as before (charged only when the actual bill is entered). Every estimate change keeps a history (who, when, old and new value).
- **FR-101** While a category has an estimate and no actual bill, members are charged their share of the estimate (BR-21), shown as "Estimated" on their bill, statement and Bills to pay. Entering the actual bill in the same month replaces the estimate and recalculates the shares. If the month closes on the estimate, the estimate is charged and carried as a bill to pay (FR-99); when the actual bill arrives, the difference is handled by BR-22.
- **FR-27** The system shall keep an immutable log (who, when, old value, new value, reason) of every create, edit and delete; financial entries are never hard-deleted.

### Home rules, deposit and leaving

- **FR-28** The owner shall configure home rules: deposit months (0 or more), notice period months (0 or more), (the notice period is a minimum; there is no short-notice waiver in the MVP), and the home lease: start date, monthly home rent and landlord deposit months; each change keeps an effective date and history.
- **FR-29** Each member shall have a join date, an optional leave date and a status (Active, Notice served, Left), and keep a snapshot of the deposit and notice rules in force on their join date.
- **FR-30** On join, the system shall calculate the required deposit (BR-12) and record deposit payments, including instalments, showing any amount outstanding.
- **FR-31** Deposit money shall be kept out of the member's monthly total paid and balance; it lives in a separate deposit ledger.
- **FR-32** The fund view shall show member deposits held, landlord deposit held and cash free to spend, and flag when they do not reconcile (BR-17). Free to spend = home fund cash held by all holders − member deposit cash in hand. Deposit cash is part of the cash its holder holds, marked as reserved.
- **FR-33** A member or the manager shall submit a leave notice with notice date and planned leave date; the system shall compute the earliest allowed leave date (BR-13) and notify all members and the manager.
- **FR-34** If the planned leave date is earlier than allowed, the system shall block it: in the MVP nobody can leave earlier than the home's minimum notice period (short-notice waivers come later).
- **FR-35** For a member with notice served, the system shall offset rent in their last months with an Deposit Applied credit (BR-14), labelled on the statement.
- **FR-36** On the leave date, the system shall produce a final settlement (BR-15), record the refund or amount owed, set the member to Left and exclude them from later cycles.
- **FR-37** A notice may be withdrawn before the leave date; the member returns to Active and the deposit stays held.
- **FR-38** The seat shall show as vacant from the leave date, and the manager may link an incoming member as the replacement.

* **FR-39** (Later phase) When a waiver is granted, final settlement shall refund the unused deposit and any rent the member already paid for months after the leave date.
* **FR-40** The manager shall record the one-time landlord deposit paid when the home is first rented: date, amount, months of home rent it covers and receipt. It is funded from the founding members' deposits.
* **FR-41** Member joins and leaves shall never change the landlord deposit; new members pay their deposit to the manager, and leaving members are refunded by the manager. The landlord deposit changes only by a top-up when the landlord raises rent, or by home move-out (FR-44).
* **FR-42** The system shall show landlord deposit status (Held, Partly adjusted, Returned) and the amount still held.
* **FR-43** By default, a replacement's deposit (paid to the manager) funds the leaving member's deposit refund; both entries stay in the ledger.

- **FR-44** The manager shall close the home (everyone moves out): the manager records how the landlord settles the deposit (FR-45), each remaining member's deposit is applied to their own last months of rent, and every member gets a final settlement.

* **FR-45** At home move-out, the manager shall record the landlord's settlement of the deposit as any mix of: amount adjusted against the last months' home rent, repair or damage deductions (each with item, amount, note and optional photo), and cash returned. The parts must add up to the landlord deposit held.
* **FR-46** Repair deductions shall be charged to members by a method the manager picks: equally among members living there at move-out (default), by months each member stayed during the lease, or to a named member responsible. Charges appear as a Repair Deduction line on each final settlement.
* **FR-47** Months not covered by the landlord's rent adjustment shall be billed as normal rent; cash returned by the landlord goes into central cash and is paid out through final settlements.

### Rent revisions

- **FR-48** The manager shall create a rent revision with scope (home, room or member), direction (increase or decrease), amount or percent, effective month and reason; any number of revisions may be made at any time of year.
- **FR-49** For a home-wide revision, the system shall apply the split method chosen (home default, changeable per revision): equal amount per active member, or the same percent of each member's current rent (BR-19).
- **FR-50** A room revision shall change that room's total rent and recalculate its occupants' share; a member revision shall create a dated rent override for that member only.
- **FR-51** The system shall store all rent as effective-dated history and bill each cycle with the rent in force for it; closed months are never recalculated.
- **FR-52** The system shall show a preview of every affected member's old rent, new rent and difference, and require confirmation.
- **FR-53** The system shall compute the rent gap each month (members' rent total minus landlord rent) and show it on the dashboard.
- **FR-54** When a member's rent rises, the system shall recalculate their required deposit and, per home rule, request a top-up or settle the difference at leaving.

* **FR-55** The home rules shall hold a rent gap policy (Split equally, Split by rent share, Home fund, Ask members). Each rent revision shall show the resulting gap and apply the default policy, which the manager can override for that revision; the chosen policy is saved with the revision and shown in members' rent history.
* **FR-56** Under Ask members, the revision stays pending until every active member agrees in the app; until then the previous rent stays in force.

### Photos, location and ID documents

- **FR-57** The manager shall set the home's location by picking a point on Google Maps; the address field is filled from the map and can be edited.
- **FR-58** The manager may upload home photos (optional, several) and one photo per room (optional).
- **FR-59** Each member may have a profile photo (optional).
- **FR-60** Each member shall have at least one ID document before joining: type (NID, passport, driving licence, birth certificate or student ID), number, and front and back images. The members list shows who is missing one.
- **FR-61** ID documents shall be visible only to the manager, stored encrypted, and kept after a member leaves; members can see only their own.

### Home contacts

- **FR-109** Contacts. The owner or a manager keeps the home's contacts: the people and companies the home deals with. Each contact has:
  - a kind (landlord, cook, internet, electricity, gas, caretaker or other) and a name (required);
  - an optional photo;
  - any number of phone numbers and email addresses, each with an optional label (for example "bKash" or "office"), one of each marked primary;
  - an optional account or customer ID (internet customer ID, electricity meter number, gas account);
  - a note and optional documents (lease agreement, NID, contract).

  The landlord is the home's landlord contact, edited on Home & landlord together with the lease; a home has one active landlord at a time.
- **FR-110** Contact history. When a contact stops working with the home (the cook leaves, the internet provider changes), the owner or a manager marks them as left with an end date, and they move to Past contacts with all their details and payments. Contacts are never deleted. A replacement is a new contact with its own start date.
- **FR-111** Paid to. Each bill category may name **one** contact it is paid to (Cook → the cook, Internet → the provider). Bills to pay shows that contact's name and primary phone. Each bill payment records whom it was paid to, defaulting to the category's contact; changing the category's contact never changes past payments. A home with two cooks at once has two Cook bill categories, each with its own contact.
- **FR-112** Contact visibility. Every member can see the names and phone numbers of active contacts other than the landlord. The landlord's contact details, account IDs, notes and all contact documents are visible only to the owner and managers. Contact documents are stored encrypted, like ID documents (FR-61).

### Roles and permissions

- **FR-62** Every person in a home has the Member role. The owner can add Manager and Fund keeper on top; one person may hold several roles, and a home can have any number of managers and fund keepers.
- **FR-63** Each home has exactly one owner. The owner can do everything: give and remove roles, choose managers and fund keepers, change all home settings, and hand the owner role to another member.
- **FR-64** A manager can add new members, choose fund keepers, hold either fund (FR-104), record payments and bills, change rent and close the month. A manager cannot make someone a manager. Every manager has the same powers; none needs another's approval (FR-75).
- **FR-65** A fund keeper is chosen for the grocery fund, the home fund or both, and a fund can have several. A fund keeper can receive and confirm money paid into their fund, spend from and give out the cash they hold (a home fund keeper can also pay bills and give bill money, FR-71), and hand cash over (FR-105), plus everything a member can do. Removing the role is blocked while they hold cash (FR-104).
- **FR-66** A member can log their own meals and groceries, see their own bill and payments, and give notice. Members and fund keepers cannot add members.

* **FR-67** Default fallback: while no manager is set, the owner does every manager job. A fund with no fund keeper is held by the owner and managers (FR-104).

| Action | Owner | Manager | Fund keeper | Member |
| --- | --- | --- | --- | --- |
| Make someone a manager | Yes | No | No | No |
| Change home settings and rules | Yes | No | No | No |
| Add new members | Yes | Yes (as Member) | No | No |
| Record payments, bills, rent changes, close month | Yes | Yes | No | No |
| Hold fund cash, spend or give it out, hand it over | Yes (any fund) | Yes (any fund) | Yes (their funds) | No |
| Confirm money paid to them | Yes | Yes | Yes | No |
| Choose fund keepers | Yes | Yes | No | No |
| Set meal sessions and their weights | Yes | No | No | No |
| Confirm meal sessions, add home guests, change meals after the lock | Yes | Yes | No | No |
| Add, edit and end home contacts; see landlord details and documents | Yes | Yes | No | No |
| See cook and provider names and phones | Yes | Yes | Yes | Yes |
| Log own meals (until locked) and groceries, see own bill | Yes | Yes | Yes | Yes |

## 6. Business rules and calculations

The backend must reproduce the spreadsheet exactly; these rules are the acceptance test for every bill, and the October 2026 figures below are the first regression test.

**BR-1 Shared cost invariant.** Total charged to members plus bills to pay must equal total home expenditure for the cycle. Utility charges must sum exactly to the utility total.

**BR-2 Cost per meal.** Grocery purchases less their returns (FR-102), not grocery fund top-ups or Household items, divided by billable meals; 0 when there are none. A member's billable meals are their own plus guest meals in **confirmed** sessions (FR-108), each times that session's weight (FR-106). Home guests (FR-107) are not billable, so their food cost is shared through the rate.

```latex
M_i = \sum_{s \in confirmed} w_s \,(Own_{i,s} + Guest_{i,s}) \qquad M_{total} = \sum_i M_i
```

```latex
R_{meal} = \begin{cases} C_{groceries} / M_{total} & M_{total} > 0 \\ 0 & M_{total} = 0 \end{cases} \qquad C_{meal,i} = M_i \times R_{meal}
```

Example: groceries ৳10,000, 100 billable meals and 4 home-guest meals → cost per meal ৳100.00, and members are charged ৳10,000 in all. Counting the home guests as meals would give ৳96.15 and recover only ৳9,615.38, leaving ৳384.62 unpaid (BR-1).

**BR-24 Cook for.** For a date and session: every member's own meals + guest meals + home guests, without weights (it is the number of plates, not the bill).

**BR-3 Rent.** The member's Rent override for the cycle if one exists, otherwise room total rent ÷ occupants.

**BR-4 Balanced utility redistribution.** Members with an override pay exactly their override; the rest of the bill is split equally among the active members without one. Applied per utility category, so a member with only an Internet deal still pays an equal share of Electricity and Cook.

```latex
C_{util,i} = \begin{cases} Override_i & i \in S_{override} \\ (U - \sum_{j \in S_{override}} Override_j) / N_{standard} & i \in S_{standard},\ N_{standard} > 0 \\ 0 & \text{otherwise} \end{cases}
```

The statement still shows prepaid and postpaid shares separately, as the spreadsheet does.

**BR-5 Total due.**

```latex
D_{total,i} = C_{meal,i} + C_{util,i} + C_{rent,i} + PrevDue_i
```

**BR-6 Credits (total paid).** Five sources: grocery entries by the member that used their own money (own-pocket purchases and grocery fund top-ups); prepaid and postpaid bills the member paid personally; Rent payments; General, Prepaid Utility and Postpaid Utility payments; and prior-month credit. Purchases and bills count less the pocket part of their returns (FR-102), and every entry counts at its latest confirmed values (FR-103).

**BR-7 Net balance.** Positive means the home owes the member; negative means the member owes; 0 means settled.

```latex
B_i = P_{total,i} - D_{total,i} - Refund_i
```

**BR-8 Central cash.** Opening cash carried from last month (FR-99) plus member payments (except refunds) minus carried bills paid this month, minus central-fund outlays (bills and groceries paid from the fund, less money from returns handed back to the fund, FR-102) minus refunds the member has confirmed receiving (FR-17). The grocery fund is tracked separately (FR-15). Central cash is split by holder: it equals the sum of every home fund holder's cash (BR-23) plus home fund money given to members and not yet spent.

**BR-9 Bills to pay.** Per class (prepaid, postpaid, rent): bills the home owes the landlord, cook, gas, internet and other providers, minus what has already been paid to them, plus carried bills from earlier months still unpaid (FR-99). Estimated bills count at their estimate until the actual is entered. Shown to users as "Bills to pay", with carried bills marked "From \<month>" and estimates marked "Estimated".

**BR-10 Rounding.** Money is stored as NUMERIC(12,2); intermediate values (like the cost per meal 97.4766…) keep full precision and only displayed totals round to 2 decimals. Any rounding remainder from the utility split goes to one named member so BR-1 holds to the paisa.

**BR-11 Rules snapshot.** A member's deposit months (A) and notice months (N) are fixed from the home rules in force on their join date. Later rule changes apply to new joiners only, unless the manager re-applies them to a member.

**BR-12 Required deposit.** The member's monthly rent share (override included) times A. Deposit is held money: it is not part of monthly total paid or balance, and the fund shows it as reserved.

```latex
Deposit_{required,i} = C_{rent,i} \times A_i
```

**BR-13 Notice period.** Notice served in month m means the member pays through month m + N; the earliest allowed leave date is the last day of month m + N, and the app won't accept an earlier date. Example: N = 2, notice on 12 October → earliest leave date 31 December, and a 2-month deposit pays November and December rent. (A short-notice waiver may come in a later phase.)

**BR-14 Deposit applied.** In the member's last A months up to the leave date, rent is offset by an Deposit Applied credit equal to that month's rent, until the deposit runs out. Meals and utilities are charged normally. Example: A = 2, N = 2, notice on 10 January → leaves 31 March; February and March rent are covered by deposit, January rent is paid as usual.

**BR-15 Final settlement.** Final balance = normal net balance + deposit remaining. Positive → refund (Deposit Refund plus any surplus); negative → the member owes. The member becomes Left and no prior-month record is rolled forward for them.

**BR-16 Landlord deposit.** Paid once, when the home is first rented, from the founding members' deposits (landlord deposit = monthly home rent × landlord deposit months). After that, every member deposit goes to the manager, not the landlord, and member turnover only moves money between the incoming member, the manager and the leaving member. The landlord deposit is settled only when the whole home leaves the home, in whatever way the landlord chooses: adjusted against the last months of home rent (a 2-month deposit covering the final 2 months), returned in cash with rent paid as usual, or reduced by repair and damage costs from a long stay, with the rest adjusted or returned. It is a deposit held by the landlord, never part of a member's bill.

**BR-17 Deposit reconciliation.** Money members gave as deposit is either with the landlord or in hand. The fund view flags any gap.

```latex
\sum MemberDepositHeld = LandlordDepositHeld + DepositCashInHand
```

**BR-18 Move-out settlement.** The landlord deposit must be fully accounted for:

```latex
LandlordDeposit = RentAdjusted + RepairDeductions + CashReturned
```

Repair deductions are split by the chosen method (equal among members at move-out by default). Each member's final settlement = normal balance + own deposit remaining − own repair share + share of cash returned not already used for rent.

**BR-19 Rent revision split.** For a home-wide change of ΔF on landlord rent F, with N active members whose current rent is r:

```latex
\text{Equal: } r'_i = r_i + \Delta F / N \qquad \text{Percent: } r'_i = r_i \times (1 + \Delta F / F)
```

Example: home rent ৳40,000 rises to ৳44,000 with 4 members. Equal: everyone +৳1,000. Percent: everyone +10%, so a ৳6,670 seat becomes ৳7,337 and a ৳3,887.50 seat becomes ৳4,276.25. Room and member revisions change only their scope; members with a rent override keep it unless the revision targets them.

**BR-20 Rent gap policy.** Members' total rent should equal landlord rent. When a room or member change breaks this, the gap is handled by the home's rent gap policy, which the admin sets once in home rules and can override on any single revision:

| Policy | Shortfall (members pay less than landlord rent) | Surplus (members pay more) |
| --- | --- | --- |
| Split equally | Each other member pays gap ÷ number of other members | Each other member's rent falls by the same share |
| Split by rent share | Each other member pays in proportion to their current rent | Reduced in the same proportion |
| Home fund | Monthly fund expense, shown on the fund card | Kept in central cash |
| Ask members | Revision stays pending until every active member agrees to one of the above | Same |

The members whose rent was changed by the revision are excluded from the split. Example: Room C is lowered by ৳1,200 with 4 other members; under Split equally each of them pays ৳300 more.

**BR-21 Estimated bill.** For each category, the amount used for the month is the actual bill if one is entered, otherwise the month's estimate (FR-100), otherwise 0. That amount is split by the normal rule (BR-4: overrides first, the rest equally), so estimates and actual bills share one calculation path. BR-1 holds because the estimate is counted both in member charges and in Bills to pay.

```latex
U_{c,m} = \begin{cases} Actual_{c,m} & \text{actual entered} \\ Estimate_{c,m} & \text{estimate set} \\ 0 & \text{otherwise} \end{cases} \qquad Estimate_{c,m} = MonthEstimate_{c,m} \text{ if set, else } DefaultEstimate_c
```

Example: cook estimate ৳4,000, 4 members, no deals → each member's bill shows Cook ৳1,000 (Estimated) from the 1st of the month.

**BR-22 Estimate adjustment after close.** If a month closed on an estimate and the actual bill later differs, the difference Δ = actual − estimate is split among the members charged in that closed month, by that month's split (BR-4: members with an override keep exactly their override, so Δ goes to the standard members). Each share is added to the open month as an "\<month> \<category> adjustment" line, the same way as a closed-month correction (FR-90); the closed month itself is not reopened. Δ > 0 raises their dues; Δ < 0 credits them. The carried bill is updated to the actual amount. A member who has already left gets their share on their Past members record (FR-92).

Example: November cook estimated ৳2,500, 3 members, November closed on the estimate; the actual bill ৳2,800 arrives on 4 December → each member gets "November cook adjustment" +৳100 on their December bill, and Bills to pay shows ৳2,800 for the November cook.

**BR-23 Cash per holder.** For fund f and holder h in a month: opening cash, plus confirmed money paid to them and handovers to them, minus what they spent from f, gave out from f, handed over (confirmed or waiting) and paid as refunds. It can never go below 0.

```latex
H_{f,h} = Open_{f,h} + In_{f,h} + HandIn_{f,h} - Spent_{f,h} - Given_{f,h} - HandOut_{f,h} - Refund_{f,h} \geq 0 \qquad Balance_f = \sum_h H_{f,h} + WithShoppers_f
```

Example: home fund ৳14,000 = Rabbi ৳10,000 + Karim ৳4,000 (Maruf's rent cash, confirmed by Karim). Rabbi can give at most ৳10,000 for a bill until Karim hands his ৳4,000 over; after Rabbi confirms the handover, Rabbi holds ৳14,000 and Karim ৳0, and the home fund is still ৳14,000.

### Verification: October 2026 cycle

Total meals 107.0, grocery ৳10,430.00, cost per meal ৳97.4766 (shown ৳97.48). October had lunch and dinner only, every session counts as confirmed and there were no home guests, so BR-2 gives the spreadsheet's figure unchanged.

| Member | Meals | Meal cost | Prepaid | Postpaid | Rent | Total cost | Total paid | Net balance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rabbi Hasan | 28.0 | ৳2,729.35 | ৳690.00 | ৳1,027.00 | ৳6,670.00 | ৳11,116.35 | ৳11,410.00 | +৳293.65 |
| Hijam Shusil | 33.0 | ৳3,216.73 | ৳690.00 | ৳1,027.00 | ৳3,887.50 | ৳8,821.23 | ৳12,535.00 | +৳3,713.77 |

Both positive balances roll into November as Credit records.

## 7. Non-functional requirements

Each home is small (roughly 5–15 members) but the platform holds many homes and handles money, so accuracy, isolation and auditability come before scale.

| ID | Area | Requirement |
| --- | --- | --- |
| NFR-01 | Accuracy | All money in fixed-point decimal (NUMERIC(12,2) at rest, Decimal in code); no floating-point anywhere in the calculation path |
| NFR-02 | Accuracy | Automated tests replay the October 2026 cycle and match every member balance to ৳0.01, and assert the shared cost invariant on every month |
| NFR-03 | Tenant isolation | Every table carries a home id; every query is scoped by it; unique rules (member name, room name) apply within a home, not globally |
| NFR-04 | Usability | Logging meals or a grocery entry takes 3 taps or fewer on a 360 px wide phone screen |
| NFR-05 | Performance | Dashboard and statement load in under 1 second for a 15-member month; meal-rate aggregates may be cached in Redis but are recomputed from PostgreSQL on any write |
| NFR-06 | Security | Login by phone or email with a one-time code; role checks on every write (Roles and permissions); member and fund keeper entries count only after confirmation, and money paid to a holder only after that holder confirms; ID documents encrypted and visible only to the owner and managers |
| NFR-07 | Auditability | Immutable ledger / event log for all balance-affecting changes; soft delete only, with reason |
| NFR-08 | Reliability | Idempotent writes so a retried save on slow mobile data never double-counts |
| NFR-09 | Data safety | Daily database backup; export of any month to Excel |
| NFR-10 | Localisation | BDT (৳) with Bangladeshi digit grouping; dates in Asia/Dhaka time |
| NFR-11 | Architecture | REST API under /api/v1; backend FastAPI + PostgreSQL + Redis; web front end Ember.js (TypeScript); Flutter mobile app later on the same API |

## 8. Edge cases, assumptions and release plan

### Edge cases the system must handle

- No meals logged in a month → cost per meal is 0, nobody is charged for groceries.
- Overrides in a category add up to more than that category's bill → the other members' share would go negative; block the override and warn.
- Member joins or leaves mid-month → v1 charges the full month's utility share and rent; pro-rating is an open question.
- Room occupancy changes → rent per person recalculates from the new occupant count for the whole month.
- Lump-sum General payment (e.g. 10,000 BDT) → credits the member's overall balance without splitting by category.
- Refund larger than home fund balance → blocked with a warning.
- Edit after month close → only the owner or a manager, as a correction with a reason; the closed month is never reopened (FR-90).

* Every active member has an override in a category → no standard members; any leftover becomes a visible shortfall instead of dividing by zero.
* A member's guest meals are recorded in their guest count and charged to them at the normal cost per meal (FR-08).
* A session is never confirmed → members are locked out of it at midnight anyway; it doesn't count in the cost per meal; the owner or a manager can still confirm it until month close; the month-close checklist lists it, and closing anyway confirms it as logged (FR-78).
* A member wants to change a confirmed session → blocked; they ask the owner or a manager, who edits it (FR-09).
* Only home guests ate in a month (no billable meals) → cost per meal is 0, as with no meals logged.
* A session is turned off mid-month → its entries so far stay and count; no new entries.
* The cook leaves mid-month → the old cook is marked as left; the Cook bill's contact changes to the new cook; this month's Cook bill can be paid to both, each payment naming whom it went to (FR-110, FR-111).
* Groceries from the grocery fund costs more than is in the grocery fund (or more than a shopper was given) → the fund part is capped at what is available and the rest is the shopper's own pocket, in the same entry (FR-98).
* Month closes with a bill unpaid (e.g. gas) → carried into next month's Bills to pay; the money stays in home fund cash; paying it next month is not charged to members again (FR-99).
* Month closes on an estimate and the actual bill is higher or lower → the difference is added to the open month as an adjustment line for the members of the closed month (BR-22).
* Actual bill entered in the same month as its estimate → the actual replaces the estimate; no adjustment line.
* Estimate removed for one month → that category is charged only when an actual bill is entered, like a category without an estimate.
* Estimate lower than the category's overrides added up → blocked like an override that exceeds the bill (other members' share would go negative).
* Split entry with a 0 pocket part → saved as paid fully from the shared source; with a 0 shared part → saved as own pocket.
* First month on the app → manager imports October member balances, home fund and grocery fund cash, money with shoppers and unpaid bills (FR-24); without them, everyone and every fund starts at 0 with no bills to pay.
* Item returned for full money back → the entry counts ৳0 and the payer's credit for it is ৳0; the original stays in history (FR-102).
* Return bigger than what is left of the entry (after earlier returns) → blocked.
* Return on a split-funded entry bigger than its pocket part → the pocket part goes to 0 and the rest is money the payer holds for the shared source until handed back (FR-102).
* Grocery returned after its month closed → that month's statement shows the corrected cost per meal and each member's difference goes into the open month as an "\<month> correction" line (FR-90).
* Shop keeps the money as credit → nothing is recorded until the credit is used (FR-102).
* Non-food item entered as groceries → the owner or a manager corrects its purpose to Household (FR-103), which takes it out of the cost per meal.
* Member takes back some or all of a confirmed payment → recorded as a Refund by the owner or a manager and confirmed by the member (FR-17); the original payment is never edited.
* Refund the member never confirms → shows as "Waiting for member" and on the month-close checklist; it changes no balance until confirmed.
* Two managers both collect rent cash → each confirms what they received; the home fund shows each one's cash, and either can hand it to the other (FR-104, FR-105).
* Holder tries to give out more than they hold, though the fund as a whole has enough → blocked; they ask another holder for a handover first.
* Handover the receiver says they didn't get → released back to the giver; nothing moves (FR-105).
* Payment to a holder who never confirms → in nobody's cash; it shows on the month-close checklist.
* Fund keeper role removed, or member leaving, while they still hold cash → blocked until they hand it over (FR-104, FR-80).
* Member pays the wrong person (names Rabbi but gave the cash to Karim) → Rabbi answers "Not received" and the member sends it again naming Karim (FR-91).

- Rent share rises after deposit is paid → the gap is charged in the covered months, or a top-up is requested, per home rule.
- Rent share falls, or the member leaves early with deposit left over → the remainder is refunded in final settlement.
- Member leaves tries to pick a date earlier than the notice period allows → blocked; the earliest allowed date is shown.
- Deposit paid in instalments and not finished by the leave date → the unpaid part counts as rent owed.
- Member moves to another room → deposit stays; the difference is topped up or refunded against the new share.
- Notice withdrawn → status back to Active; nothing is applied.

* Central cash is too low to refund a leaving member's deposit → refund is scheduled and shown as a payable until the replacement's deposit or landlord return arrives.
* Landlord raises rent → landlord asks for an deposit top-up; members' required deposit rises for new joiners and, per rule, as a top-up for existing ones.
* Landlord deducts repair costs at move-out (broken fittings, paint, plumbing after a long stay) → each item is recorded and split among members by the chosen method; if deductions exceed the deposit, the excess is billed to members as an expense.

- Whole home moves out → the landlord may adjust the deposit against rent, return it, or cut repairs from it; members' deposits held by the manager offset each member's own last months, and any gap between the two is settled in final settlements.
- Leaving member's refund is due but no replacement has joined yet → paid from home fund balance if available, otherwise shown as a payable until a replacement pays their deposit.

* Rent revision effective mid-month → applied from the next full cycle unless pro-rating is enabled (see open questions).
* Percent split leaves paisa remainders → remainder goes to one named member so the total matches landlord rent.
* A member's rent is lowered (worse room, special deal) → the shortfall shows in the rent gap; nothing is hidden.
* Revision entered for a month already closed → blocked; closed months can't be reopened, so the owner or manager sets the current or a later effective month.

### Assumptions

### Open questions

### Release plan

- Several people may hold a home's cash (owner, managers, fund keepers); members trust entries once the person who received the money confirms them.
- Utilities are charged at actual billed amounts. The fixed floors from the 2 Nov version (Electricity 1,000, Gas 600, Internet 1,050, Cook 4,000) are dropped (confirmed 12 Nov 2026): no minimum charge per utility. Updated 14 Nov 2026: a manager may instead set an optional **estimate** per category (FR-100); it is replaced by the actual bill, and any difference after close is adjusted (BR-22). It is never a floor.
- bKash / Nagad payments are entered manually.

### Open questions

All open questions were decided on 12 Nov 2026:

- **Joining or leaving mid-month:** charge the full month in the MVP; no pro-rating.
- **Utility custom deals:** the rest is shared per bill (BR-4).
- **Rent override shortfall:** handled by the rent gap policy (BR-20).
- **Short-notice waiver:** not in the MVP. A leave date can't be earlier than the home's minimum notice.
- **Repair deductions at move-out:** split equally among the members living there at move-out.
- **Editing past meals:** members up to 2 days back; managers and the owner anytime until the month is closed. _Replaced on 19 Nov 2026 by the meal lock (FR-09)._
- **Balance visibility:** every member sees everyone's totals; ID documents and contact details stay with the owner and managers. _Members' contact details; for home contacts see FR-112 (19 Nov 2026)._

Decided on 14 Nov 2026:

- **Estimated bills:** optional, per category; estimate-and-adjust, not a minimum floor. One default for every month, changeable for a single month (FR-100, BR-21, BR-22).
- **Month close carry-forward:** home fund cash, grocery fund cash, money with shoppers and unpaid bills move into the next month along with member balances (FR-99).
- **Split funding:** one entry can mix one shared source with the payer's own pocket (FR-98).

Decided on 17 Nov 2026:

- **Returns and exchanges:** recorded on the original entry as a linked return, never by editing it; money back lowers the pocket part first (FR-102).
- **Who corrects confirmed entries:** members send corrections of their own entries for confirmation; the owner or a manager corrects any entry directly and the member is told; no dispute step in v1 (FR-103).
- **Returns after close:** handled as closed-month corrections (FR-90), so the closed month's members get the difference.
- **Shop credit:** not tracked in v1 (FR-102).
- **Household items:** a Household bill category, shared like other bills, not through the cost per meal (FR-05).
- **Refunds:** count only after the member confirms receipt (FR-17).
- **Fund holders:** any number of managers and fund keepers; a fund keeper is chosen per fund; the owner and managers can hold either fund; the app tracks cash per holder and the receiver confirms every payment or handover (FR-62–FR-67, FR-104, FR-105, BR-23).
- **Managers' own entries:** still saved without confirmation; other managers and the owner are notified (FR-75).
- **Deposit cash:** part of the cash its holder holds, marked as reserved; free to spend excludes it (FR-32, BR-17).
- **Custom funds** (repair fund, cook fund): later, not v1.

Decided on 19 Nov 2026:

- **Meal sessions:** each home picks its sessions (breakfast, lunch, dinner) and a weight per session, so breakfast can count as half a meal (FR-106).
- **Guest meals:** a member's own meals and their guests' meals are stored separately; both are charged to the member (FR-08).
- **Home guests:** counted for cooking, not billable; their cost is shared through the cost per meal (FR-107, BR-2, BR-24).
- **Daily confirmation:** the owner or a manager confirms each session after it is cooked, one or several at a time; only confirmed sessions count (FR-108).
- **Meal lock:** members edit until the session is confirmed or the day ends; after that only the owner or a manager. Replaces the 2-day rule (FR-09).
- **Unconfirmed sessions at month close:** listed on the checklist; closing anyway confirms them as logged, so nobody's meals are silently dropped (FR-78).
- **Home contacts:** one list for the landlord, cook, providers and others, with several phones and emails, documents and history; never deleted (FR-109, FR-110).
- **Paid to:** one contact per bill category; two cooks means two Cook bills; each payment keeps whom it was paid to (FR-111).
- **Contact visibility:** every member sees cook and provider names and phones; landlord details, account IDs and documents stay with the owner and managers (FR-112).
- **Custom funds:** still after the MVP; their shape is recorded in Phase 4 below.

### Release plan

1. **Phase 1 – MVP (P1 features):** one-home account, setup, override engine, meal grid with meal sessions, guests and daily confirmation, home contacts, bills and groceries with grocery fund, payments and refunds, prior-balance import, dashboard, statement, month close, home rules, deposit ledger, roles and permissions, leave notice and final settlement, give-money-first flows for the grocery fund and bills, I paid with proof and confirmation, returns and exchanges, corrections of confirmed entries, fund holders and handover, inbox, edit history, month-close checklist, past members, messaging, owner sign-up and phone/email login.
2. **Parallel run:** replay October 2026 as a test, then run November and December 2026 side by side with the spreadsheet; go live when every balance matches.
3. **Phase 2:** PDF/Excel export, WhatsApp sharing, meal cut-off and default patterns, short-notice waiver vote, whole-home move-out with landlord deposit settlement.
4. **Phase 3:** reminders, grocery shopping roster, Bangla interface, Flutter app, multiple homes per account.

**Phase 4 – worldwide use (after the MVP).** Discussed on 12 Nov 2026 and deliberately left out of the MVP so it can launch with today's model:

- **Split method per type of cost:** groceries by meals, equally, by days at home, or off; rent by room, equally or custom; each bill equally, by days at home or a fixed amount.
- **Ready-made setups when creating a home:** Meal mess (today's model), Flatshare (rent and bills shared, groceries split equally or off) and Bills only.
- **Deposit rule per home:** use it as the final months' rent (today) or refund it on leaving, minus damage.
- **Word packs:** neutral English by default; a South Asia pack that shows Mess, Bazar, Bazar box, Meal rate and Advance.
- **Language and locale:** full translation (Bangla first), currency per home, number format (lakh or million), date format and time zone.
- **Custom funds:** a home creates its own funds (repair, festival) with their own holders, alongside the grocery fund and home fund. Shape agreed on 19 Nov 2026:
  - **Who takes part:** the owner or a manager picks which members pay into each fund.
  - **Collecting:** either a set amount shared equally among the chosen members (each sees "৳500 to pay"; rounding remainder to one named member, BR-10; more can be collected later), or no set amount, where anyone pays any amount.
  - **Paying in and spending:** the same as the home fund and grocery fund: pay to a named holder who confirms, cash per holder, give money first, handovers, receipts, returns and corrections.
  - **Kept off the monthly bill:** what members pay in **is** their share of the cost, so spending from the fund is never charged on members' bills again, and nothing that is already a bill category (like Cook) is paid from a custom fund.
  - **Month close:** cash per holder and each member's unpaid share carry forward.
- **Payment methods and ID types per country:** bKash, Nagad, UPI, M-Pesa, bank transfer; NID, passport, driving licence and others.
- **Require ID as a home setting:** on by default for Meal mess, off for Flatshare, to respect privacy laws such as GDPR.
- **Utility names:** rename prepaid and postpaid to top-up bills and monthly bills.
- **Split weights and meters:** room size or a couple counting as 2; a separate meter per room.
- **Other formats:** paying guest or hostel with food (the owner sells meals to residents) and a cooking rota.
