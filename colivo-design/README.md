# Colivo: Mess, Hostel & Flat Manager

> Meal rate, rent, bills, members, bazar — manage any mess, hostel, PG or shared flat

Colivo design reference: the design source for the Colivo MVP (shared-home meal, grocery, rent and bill manager).
Use these files as the visual and behavioural reference when building the app.

- `requirements.md` — project requirements, user stories, functional rules (FR-xx) and business rules (BR-xx). **Source of truth for behaviour.**
- `mobile/` — 52 phone screens (390 px wide).
- `web/` — 43 responsive web pages (sidebar + content, collapse to one column on narrow screens).

## How to read the screen files

Each `.html` file is one screen exported from Claude Design (`.dc.html` format):

- Markup is plain HTML with **inline styles** — read them for exact layout, colours, spacing and copy.
- `{{name}}` placeholders, `<sc-for>` (loop) and `<sc-if>` (condition) are template syntax; the values come from
  `renderVals()` in the `<script type="text/x-dc">` block at the bottom. That script also shows the screen's behaviour
  (tabs, toggles, validation such as "can't spend more than you were given").
- `support.js` (the Claude Design runtime) is not included, so files won't render fully in a browser. Treat them as specs, not as code to ship.
- Sample data is one home ("Our Flat") in October 2026: Rabbi Hasan (owner/manager, Room A), Hijam Shusil (fund keeper, Room B), Maruf (member, Room B, leaving 31 Dec). Cost per meal ৳97.48 (107 meals, ৳10,430 groceries).

## Design tokens

| Token | Value |
|---|---|
| Font, body | Inter 400/500/600 |
| Font, headings and big numbers | Space Grotesk 500/600/700 |
| Background | `#F6F5F0` |
| Surface / card | `#FFFFFF`, border `#E3E1D9`, radius 16 px |
| Text / muted text | `#17201D` / `#5B6461` |
| Primary (teal) | `#0E6656`, tint `#E3F0EC`, hover `#0A4E42` |
| Owes / warning (brown) | `#9A4A10`, tint `#FBEFE3`, text `#7A3A0C` |
| Tag · Rent | bg `#ECEAE2`, text `#3E4744` |
| Tag · Prepaid | bg `#E7F1FB`, text `#1D4F86` |
| Tag · Postpaid | bg `#EFEDFF`, text `#4B3FA3` |
| Tag · Grocery fund | bg `#F9EEDA`, text `#6B4A0B` |
| Touch targets | at least 44 px |
| Money | Bangladeshi taka `৳`, tabular numbers, 2 decimals in statements |

## Words used in the app

Home (not mess/flat) · Owner (not super admin) · Manager · Fund keeper · Groceries · Grocery fund · Home fund ·
Cost per meal · Deposit (rent paid in advance) · Landlord deposit · Credit (balance carried forward) · Prepaid / Postpaid utilities.

## Roles

Owner (can do everything) · Manager · Fund keeper · Member. Everyone is also a member.
Confirmation rules, give-money-first flows and deletion rules are in `requirements.md` (FR-62–FR-97).

## Mobile screens

| Screen | File | Interactive |
|---|---|---|
| 1 · Home (owner) | `Main.html` | yes |
| 2 · Meal grid | `Meals.html` | yes |
| 3 · Groceries & expenses | `Bazar.html` | yes |
| 4 · Record payment | `Payments.html` | yes |
| 5 · My bill (member) | `MyBill.html` |  |
| 6 · Monthly statement | `Statement.html` |  |
| 24 · My profile | `Profile.html` | yes |
| 7 · Deposits held | `Advance.html` |  |
| 8 · Funds (who holds the cash) | `BazarBox.html` | yes |
| 9 · Bills to pay | `BillsToPay.html` |  |
| 10 · Member detail | `MemberDetail.html` | yes |
| 11 · Previous month balances | `PrevMonth.html` | yes |
| 12 · Utilities | `Utilities.html` |  |
| 13 · Rent | `Rent.html` |  |
| 14 · Change rent | `ChangeRent.html` | yes |
| 15 · Home settings (hub) | `Settings.html` |  |
| 16 · Home & landlord | `SetFlat.html` |  |
| 17 · Rooms | `SetRooms.html` |  |
| 18 · Members & roles | `SetMembers.html` | yes |
| 19 · Home rules | `SetRules.html` | yes |
| 20 · Bills & categories | `SetBills.html` |  |
| 21 · Custom deals | `SetDeals.html` |  |
| 22 · Funds and keepers (settings) | `SetBazarBox.html` | yes |
| 23 · Starting balances | `SetStart.html` |  |
| 25 · Home (member) | `MemberHome.html` | yes |
| 26 · Add groceries (member / keeper) | `MemberBazar.html` | yes |
| 27 · Home (fund keeper) | `KeeperHome.html` | yes |
| 28 · Home (manager) | `ManagerHome.html` | yes |
| 29 · Members (manager view) | `ManagerMembers.html` | yes |
| 30 · Give money for groceries | `GiveBazar.html` | yes |
| 31 · Give money to pay a bill | `GiveBill.html` | yes |
| 32 · I paid a bill (member) | `PayBill.html` | yes |
| 33 · Log in | `Login.html` | yes |
| 34 · Give notice to leave | `GiveNotice.html` | yes |
| 35 · I paid (everyone) | `IPaid.html` | yes |
| 36 · Inbox (approvals) | `Inbox.html` |  |
| 37 · Entry detail & history | `EntryDetail.html` |  |
| 38 · Before closing the month | `CloseCheck.html` |  |
| 39 · Final settlement | `FinalSettlement.html` |  |
| 40 · Past members | `PastMembers.html` |  |
| 41 · Messages | `Chats.html` |  |
| 42 · Home group chat | `ChatThread.html` |  |
| 53 · Sign up · create a home | `SignUp.html` | yes |
| 55 · New home (empty dashboard) | `HomeEmpty.html` |  |
| 56 · Empty screens | `EmptyStates.html` | yes |
| 57 · Reject a payment (manager) | `RejectPayment.html` | yes |
| 58 · Payment not confirmed (member) | `Rejected.html` |  |
| 59 · Inbox (member / fund keeper) | `MyInbox.html` | yes |
| 60 · Log-in problems | `LoginErrors.html` | yes |
| 61 · Confirmations | `Confirm.html` | yes |
| 62 · Return or exchange | `Return.html` | yes |
| 63 · Hand over cash | `Handover.html` | yes |

## Web pages

| Screen | File | Interactive |
|---|---|---|
| 1 · Log in / create a home | `WebAuth.html` | yes |
| 2 · Log-in problems | `WebAuthErrors.html` | yes |
| 3 · New home | `WebHomeEmpty.html` |  |
| 4 · Dashboard | `WebDashboard.html` |  |
| 5 · Home (manager) | `WebManagerHome.html` |  |
| 6 · Home (fund keeper) | `WebKeeperHome.html` |  |
| 7 · Member home | `WebMemberHome.html` |  |
| 8 · Meal grid | `WebMeals.html` |  |
| 9 · Expenses | `WebExpenses.html` |  |
| 10 · I paid (everyone) | `WebIPaid.html` | yes |
| 11 · Record a payment | `WebPayments.html` |  |
| 12 · Give money | `WebGiveMoney.html` | yes |
| 13 · I paid a bill | `WebPayBill.html` |  |
| 14 · Statement | `WebStatement.html` |  |
| 15 · My bill (member) | `WebMyBill.html` |  |
| 16 · Member detail | `WebMemberDetail.html` |  |
| 17 · Bills to pay | `WebBillsToPay.html` |  |
| 18 · Funds (who holds the cash) | `WebGroceryFund.html` |  |
| 19 · Deposits | `WebDeposits.html` |  |
| 20 · Utilities | `WebUtilities.html` |  |
| 21 · Rent | `WebRent.html` |  |
| 22 · Previous month balances | `WebPrevMonth.html` | yes |
| 23 · Before closing the month | `WebCloseCheck.html` |  |
| 24 · Inbox | `WebInbox.html` |  |
| 25 · Reject a payment | `WebReject.html` | yes |
| 26 · Inbox (member / fund keeper) | `WebMyInbox.html` | yes |
| 27 · Messages | `WebMessages.html` |  |
| 28 · Entry history | `WebEntryHistory.html` |  |
| 29 · Confirmations | `WebConfirm.html` | yes |
| 30 · Members & roles | `WebMembers.html` |  |
| 31 · Past members | `WebPastMembers.html` |  |
| 32 · Give notice to leave | `WebNotice.html` |  |
| 33 · Final settlement | `WebSettlement.html` |  |
| 34 · My profile | `WebProfile.html` |  |
| 35 · Home settings | `WebSettings.html` |  |
| 36 · Settings · Home & landlord | `WebSetHome.html` |  |
| 37 · Settings · Rooms | `WebSetRooms.html` |  |
| 38 · Settings · Bills & categories | `WebSetBills.html` |  |
| 39 · Settings · Custom deals | `WebSetDeals.html` |  |
| 40 · Settings · Funds and keepers | `WebSetGroceryFund.html` |  |
| 41 · Settings · Starting balances | `WebSetStart.html` |  |
| 42 · Return or exchange | `WebReturn.html` | yes |
| 43 · Hand over cash | `WebHandover.html` | yes |
