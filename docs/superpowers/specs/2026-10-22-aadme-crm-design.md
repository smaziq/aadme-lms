# AADME CRM and Learning Platform: Design

- Date: 2026-10-22
- Status: Approved by AADME, 2026-10-22
- Source: brainstorming with AADME's admissions/sales lead, based on their written interview

How to read this: **[Owner]** marks decisions AADME made. **[Proposed]** marks the designer's calls; they stand unless AADME changes them. Unmarked text is required behaviour that follows from those decisions. §20 lists what is left to the builder.

## 1. Intent

AADME sells cohort-based programs (for example the Agentic AI Agency Accelerator) to working professionals and business owners in India. Admissions today runs across phone calls, WhatsApp, TeleCRM, ChatGPT and internal documents. Counsellors spend about an hour a day on clerical work:

- updating lead status after every call or chat
- scrolling back through WhatsApp for context before a follow-up
- re-sending the same program, fee and payment details
- handling duplicates when one person arrives through two sources

AADME wants one product it controls end to end (data model, workflows, hosting, users) that covers the whole student journey: lead capture, SDR qualification, counselling, payment, onboarding, the learning platform, marketing campaigns and owner reporting. [Owner]

The most important job, in the counsellor's words: show "which leads need follow-up, when to contact them, what should be sent for nurturing, their latest status, and previous conversation history", all in one place.

Domain facts from the interview that shape the design:

- Counsellors prioritise: about-to-pay first, then organic/inbound, then referrals, repeat leads and anyone who asked for a call at a set time, then Meta leads.
- Most lost leads are not forgotten. They drop out over budget, not having a laptop, or a cheaper competitor, and many come back later. "Not now, because…" is a real, recurring state.
- Leads expect fast replies, including outside working hours, mostly on WhatsApp.

## 2. Users and roles

One person can hold several roles. Permissions combine, and scorecards attribute work to the role it was done under. [Owner: owners, admins, SDRs, marketing, counsellors. Mentors were added once AADME confirmed its own staff teach.]

| Role | Does | Sees |
|---|---|---|
| Owner | Everything an admin does, plus revenue. Only role that can add or remove admins. | Everything |
| Admin | Configures users, pipelines, routing, outcomes, templates, sequences, programs, payment plans, batches, checklists. Verifies manual UPI payments. | All leads, conversations, team views |
| SDR | First contact, qualification, handover to a counsellor | Leads assigned to them, with full history. Read-only view of leads they handed over. |
| Counsellor | Counselling, trial/orientation, fees, payment, onboarding | Leads and students assigned to them, with full history |
| Marketing | Campaigns, sequences, source reporting | Reports by source, campaign and tier. A lead list showing source and stage. No conversations or contact details unless an admin grants it. [Proposed] |
| Mentor | Teaches batches, reviews assignments, posts batch announcements | Students in their batches: progress, attendance, submissions. Not sales history, pre-enrollment conversations or payment amounts; only an "access paused" flag. [Proposed] |
| Student | Learns, pays instalments, completes their own onboarding items | Their own courses, schedule, payment plan and checklist, on the learning side only |

Staff and students sign in to the same product, and each person has one login. [Owner: learning platform built with the CRM]

Visibility rules:

- SDRs and counsellors see only leads currently assigned to them, including all history from before the lead reached them. Access moves with reassignment. Admins and owners see all leads and their status. [Owner]
- If a user adds or receives a lead already owned by a colleague, the CRM shows "already with [name]" without revealing details. [Proposed]
- Permissions are enforced server-side on every API call, per object, not only in the UI.
- Every role, permission and group change is logged. [Proposed]

Team size at launch is "small"; the design assumes fewer than 20 staff. [Proposed assumption] It must grow to hundreds of staff and thousands of students without a rebuild.

## 3. Goals, non-goals, anti-goals

### Goals

AADME's three goals [Owner], turned into measures [Proposed]:

1. **Work is easier.** Clerical time falls from about 1 hour a day to under 15 minutes (staff survey at launch and at 90 days). No unlogged calls at the end of the day. At least 90% of follow-ups done within their scheduled slot. Nobody goes back to phone WhatsApp or TeleCRM for context.
2. **Conversion goes up.** Lead-to-enrollment rate by source and tier, comparing leads from month 1 after launch with month 3. Hot leads first contacted within 15 minutes. Not now leads that return and enroll are counted separately.
3. **Better pipeline.** Every open lead has an owner, a stage and a next follow-up date. Owners see the pipeline by stage, value and expected enrollments without asking anyone. Stage-to-stage conversion shows where leads drop off.

Baseline: AADME does not know its current conversion rate. The TeleCRM import computes a historical rate if stages and dates are reliable, and says plainly if they aren't. Otherwise, leads arriving in month 1 after launch are the baseline. Because enrollment lags arrival, the 90-day review also uses leading indicators: qualification rate and the share of leads reaching Payment pending. [Proposed]

### Non-goals

- Cloud telephony and call recording. Calls stay on staff phones and are logged in the CRM. Leave room for a telephony connector later.
- Instagram and Facebook DM intake (later).
- Ongoing TeleCRM sync. Import is one-time, but original TeleCRM IDs are kept so sync can be added. [Owner]
- The full AI assistant: summaries, next-step suggestions, lead scoring, mentor feedback drafts (later). [Owner]
- In-platform student chat. Batch chat stays in WhatsApp groups. [Proposed]
- Native mobile apps. Responsive web first; the API must be usable by a future app.
- Issuing refunds. The CRM records refunds; the money moves through Razorpay or the bank.

### Anti-goals

The product fails if any of these happen, even if it technically works. [Proposed, accepted by AADME]

1. **Slower than WhatsApp on a phone.** The follow-up list, call outcome form and chat view are designed for phone screens first. New messages appear without refreshing. Logging a call takes one hand and about 10 seconds.
2. **Double work.** If anything people need lives somewhere else, they will run both systems and the CRM goes stale. TeleCRM is switched off after the import is verified. The official WhatsApp number is used only through the CRM. Program, fee and payment details live in the CRM. No field is required unless something downstream uses it.
3. **Untrustworthy.** Duplicates, reminders for the wrong lead, missing messages, leads routed to absent people, or alert noise teach people to ignore it. Duplicates merge on arrival, every message shows delivered or failed, routing skips absent users, and alerts are reserved for things that need action now.
4. **Data leaving AADME's control**, for example lead details pasted into personal AI accounts.
5. **A message reaching a lead in an active stage (Counselling to Payment pending) without a person approving it.**

## 4. Constraints

### Hosting [Owner]

- Start on hosted platforms: Railway for the application services, Supabase for Postgres and file storage. Move to rented servers later.
- Database and stored files in Supabase's Mumbai region. Railway's nearest region is likely Singapore; the builder confirms this before setup.
- Portability is a hard rule [Proposed]: plain Postgres and standard components only. No Supabase Auth, no Supabase-only features, no Railway-only features. Moving to rented servers must be a redeploy, not a rewrite. File storage goes through an S3-compatible interface.

### Stack

- Backend: Python, Django with Django REST Framework. [Owner: chosen from three options once AADME confirmed its team knows Python and React]
- Frontend: React with TypeScript, built with Vite, deployed as its own Railway service. [Proposed: not Next.js, because it's an internal tool behind a login with no SEO need]
- Background work: Celery with Redis. Used for reminders, scheduled sends, sequences, webhooks, imports and Zoom report pulls. [Proposed]
- Authentication: Django's own, with role-based permissions. Two-step login required for owners and admins. [Proposed]
- AADME's in-house team will build and run it. [Owner]

### Integrations [Owner unless marked]

| Integration | Purpose | Method |
|---|---|---|
| Meta WhatsApp Cloud API | All WhatsApp messaging, connected directly. AADME has an official number with a provider today and can use either route; direct was chosen. | Direct, behind a channel connector |
| Gmail API | Workspace mailboxes | Per-user Google OAuth |
| IMAP/SMTP | Other mail providers | Encrypted stored credentials |
| Microsoft Graph | Only if any mailboxes are on Microsoft 365 [Proposed] | Microsoft OAuth |
| Bulk email service (for example Amazon SES) | Campaigns and sequences, from a subdomain such as `mail.aadme.com` [Proposed] | API |
| Meta Lead Ads | Lead intake | Webhook |
| Google Ads lead forms | Lead intake | Webhook |
| Website forms | Lead intake | CRM endpoint |
| Zoom | Webinar and orientation registrations, attendance, class meetings, cloud recordings | AADME-owned Zoom app, webhooks plus API |
| Razorpay | Payment links, instalments, confirmation | API plus signed webhooks |
| TeleCRM | One-time import of about 500 leads | TeleCRM API, with CSV/Excel as fallback |
| AI provider (Claude, OpenAI or other) | Message drafting [Proposed: provider-agnostic] | Connector, on a business plan that doesn't train on customer data |
| Video hosting (for example Bunny Stream or Mux) | Recorded lessons [Proposed] | API |

Every external system sits behind a connector module, so adding, swapping or removing a provider is a new connector, not a rebuild. [Proposed]

### WhatsApp platform rules

These are Meta's rules, not choices:

- Free-form messages are only allowed within 24 hours of the lead's last message. Outside that window, every message must use a template Meta has approved.
- A number connects to one platform at a time, so moving it off the current provider has a short window where messages can't be sent.
- Templates may need resubmitting after the move.
- Adding people to WhatsApp groups through the API is limited, so group joins happen through invite links.
- Meta charges per conversation or message by category; marketing templates cost the most.

### Data protection

India's DPDP Act applies. [Proposed]

- Record consent and its source for each lead, and honour opt-outs on every channel.
- Support exporting or deleting a person's data on request.
- Keep an audit log of data access by staff and of exports.
- Daily backups, with a tested restore.
- Mailbox, WhatsApp, Razorpay, Zoom and AI credentials encrypted at rest.
- Every incoming webhook verified by the sender's signature; website forms protected by captcha, rate limits and a key per form.

## 5. Leads: intake, identity and sources

### Sources [Owner: Meta ads, Google Ads, website forms, WhatsApp, webinars, referrals, organic inbound]

Automatic from day one [Proposed methods]:

- **Meta ads.** Lead Ads webhook, so the lead arrives within seconds. Campaign, ad set and ad recorded. Click-to-WhatsApp ads arrive through WhatsApp with the ad referral attached.
- **Google Ads.** Lead form webhook. Google traffic that lands on the website is captured by the website form with UTM tags.
- **Website forms.** POST to a CRM endpoint, which records UTMs and the landing page.
- **WhatsApp.** The first message from an unknown number to the official number creates a lead with the conversation attached.
- **Webinars (Zoom).** Registrations arrive by webhook. Attendance is pulled after the session (see §11).
- **Organic inbound.** Website visits with no ad tag are tagged organic. Emails to a shared inbox (for example admissions@) from unknown senders create leads. Calls to the company number are added with a one-tap "new inbound call" form.

Semi-automatic:

- **Referrals.** Staff add them with a quick form that records the referrer. Each enrolled student also gets a personal referral link. Referrals start as Hot.
- **CSV/Excel upload.** For event and partner lists, and as the TeleCRM fallback. Same matching and dry-run rules as the import.

### Identity and duplicates [Proposed]

- A person is matched on phone number (normalised to E.164) and email.
- A match is recorded as a new touch on the existing lead, not as a second lead.
- First source, latest source and every touch in between are kept, for attribution reporting.
- Anyone who returns after Not now or Lost is flagged as a repeat lead and routed back to their previous owner if that person is still active.
- Lead and student are the same person record. Enrollment adds student data; it doesn't copy the person.

### Person, opportunity and enrollment [Proposed]

- **Person:** one record per human, holding contact details, consent, touches and the full conversation timeline across every channel.
- **Opportunity:** a person's interest in one program. It sits in one pipeline and has its own stage, owner, tier, follow-ups and stage history. In the rest of this document, "lead" means the person plus their open opportunity.
- **Enrollment:** created when an opportunity's first payment is confirmed, and linked to a batch, a payment plan, a payment schedule, an onboarding checklist and course access.
- **Rules:**
  - A person can have at most one open opportunity per program at a time, but may have open opportunities in different programs at once.
  - A new touch that names a program the person has no open opportunity for creates a new opportunity in that program's pipeline. This covers enrolled students enquiring about a second program. The new opportunity is routed to the person's most recent owner if that owner is active.
  - A touch with no program, or for a program they already have open, is added to the existing opportunity.
  - The program comes from the source (form, ad or session). If the source doesn't say, the opportunity goes in the default pipeline and the SDR sets the program.
  - A repeat lead reopens as a new opportunity in the same program, linked to the earlier one, so conversion reports count both attempts.
  - Each program maps to one pipeline. Programs with no pipeline of their own use the default pipeline.

### Quality tiers [Owner: route better leads to better SDRs. Proposed tier rules]

- **Hot:** referrals, repeat leads, organic/inbound.
- **Warm:** website forms, webinars.
- **Standard:** Meta leads.
- A "call me now" request or a high-intent form answer raises a lead one tier.
- Admins edit the rules. Marketing sees tiers by source.

## 6. Pipelines

Ship one standard admissions pipeline. Admins can edit it, add pipelines (for example one per program) and delete them. [Owner]

Default stages [Proposed]:

| # | Stage | Kind | Meaning |
|---|---|---|---|
| 1 | New | open | Arrived, not yet contacted |
| 2 | Contacted | open | SDR has reached them |
| 3 | Qualified | open | Interest and fit confirmed; handed to a counsellor |
| 4 | Counselling | open | Counsellor discussing goals and concerns |
| 5 | Trial / Orientation | open | Session booked or attended |
| 6 | Payment pending | open | Agreed in principle; fees and payment modes shared |
| 7 | Enrolled | won | First payment confirmed |
| 8 | Onboarded | won | Required onboarding items complete |
| — | Not now | not now | Has a reason and a re-engage date |
| — | Lost | lost | Closed for good: wrong number, fake, asked not to be contacted |

Rules [Proposed]:

- Admins and owners can rename, reorder, add and delete stages.
- Every stage has a kind (open, won, not now, lost). Reports, targets and automations key off the kind, so renaming a stage never breaks them.
- A stage that still holds leads can't be deleted until those leads are moved.
- Each lead keeps its full stage history with timestamps.
- Stages 1–3 belong to the SDR. Stages 4 onward belong to the counsellor.

### Not now

- Requires a reason (budget, no laptop, chose a competitor, not ready, unreachable, other) and a re-engage date.
- Default re-engage dates: budget or no laptop 30 days; competitor 90 days; not ready 30 days unless the lead names a date; unreachable 30 days. [Proposed]
- On the re-engage date the lead returns to its owner's follow-up list and may enter a nurturing sequence (§10).

## 7. Routing

### SDR routing [Owner: round robin, plus routing better leads to better SDRs]

- Admins put SDRs into groups (for example Senior and Standard) and map each tier to a group. Within a group, leads are assigned round robin.
- Groups are set by hand. The CRM never regroups anyone automatically. [Owner: conversion numbers plus manager judgment]
- An SDR scorecard supports that judgment: contact rate, qualification rate and lead-to-enrollment conversion, broken down by tier and source, over a chosen period. It flags patterns such as "this Standard SDR has out-converted the Senior group for 4 weeks". [Proposed]

### Counsellor routing [Owner: rule-based round robin]

- Counsellor groups can be mapped to a tier, a program, or both. Leads are assigned round robin within the matching group.
- Day one has one general group covering every program, because any counsellor sells any program today. Program groups are added later in settings. Programs with no group of their own fall back to the general group. [Owner]

### Skipping the SDR step [Proposed]

- By default, every new opportunity goes to an SDR first.
- Admins can set a routing rule so chosen tiers or sources go straight to a counsellor group at Counselling, with no handover note. For example, referrals and repeat leads can skip the SDR, as counsellors call them directly today.
- If no SDRs are active, new opportunities go straight to counsellors. A small team can launch without SDRs and add them later.
- When one person holds both roles, scorecards credit each stage to the role whose stage it is: stages 1–3 to SDR, stages 4 onward to counsellor.

### Shared safeguards [Proposed]

- Users marked away or on leave are skipped. Their open leads can be reassigned in bulk.
- Optional daily cap per user. When a group is full, overflow goes to the next group.
- If no one in the matching group is available, the lead goes to a general pool and the admin is alerted. Leads are never left unassigned.
- Repeat leads return to their previous owner if that person is active.
- Hot leads not contacted within 15 minutes (configurable) alert the admin and can be reassigned.
- Admins can always reassign by hand. Every assignment records who made it and why.

### Handover from SDR to counsellor [Proposed]

- On Qualified, the SDR fills in a short, required handover note: intent, background, concerns, budget signal, laptop (yes/no), promised next step.
- The counsellor is alerted and a first-contact timer starts for them.
- The full conversation and email history moves with the lead. The counsellor's first email can introduce them as the new contact.

## 8. Daily work: the follow-up list and call logging

### Home screens [Owner: today's follow-up list for counsellors, chosen from three mockups]

**Counsellor home** is today's follow-up list. Default order [Proposed, admin-configurable]:

1. Unlogged calls
2. About to pay, including unpaid payment links and overdue instalments
3. Timed call-backs ("call me at 10:15")
4. New handovers
5. Overnight replies
6. Hot leads not yet contacted
7. Everything else due today, with Not now leads returning on their re-engage date at the end

Each row shows why the lead is there (for example "said he'd confirm today" or "attempt 3 of 6") and has one-tap Call, WhatsApp and History. Bottom tabs: Today, Inbox, Pipeline, Search.

- **Inbox:** every WhatsApp and email conversation for the user's leads, newest first.
- **Pipeline:** the user's leads by stage, with drag to move.

**SDR home** is the same screen in SDR order: Hot leads not yet contacted, timed call-backs, no-answer retries, then new leads by tier.

**Admin and owner home** is a team view: overdue follow-ups by person, unassigned or stuck leads, today's pipeline numbers. They can open any user's list as that user sees it.

**Mentor home** is a review queue (§13).

### Call logging [Owner: one-tap outcome plus next step]

- A Call button on the lead opens the phone dialer (`tel:` link). When the user returns, the outcome form is waiting.
- Counsellor outcomes: no answer, call back later, interested, has doubts, wants a trial, discussing fees, will confirm, ready to pay, not now (with reason), not interested.
- SDR outcomes: no answer, wrong number, interested, qualified, not a fit.
- After the outcome, the user sets the next follow-up time with quick picks ("in 15 min", "tomorrow", "after orientation"). A one-line note is optional.
- Each outcome can change the stage, book the next follow-up, start or stop a sequence, and suggest a template. Examples:
  - "Discussing fees" moves the lead to Payment pending and offers the fee template.
  - "Will confirm" books tomorrow.
  - "Not now: budget" sets Not now with that reason and a re-engage date.
- Admins edit the outcome lists and what each outcome does. [Proposed]
- Templates are suggested, never sent automatically. [Proposed]
- A call with no outcome stays "unlogged" at the top of the list until it's filled in. [Proposed]
- "After orientation" needs real session dates, so sessions come from Zoom or an admin-kept list (§11).

### No-answer cadence [Owner: use standard parameters. Proposed values, all admin-configurable]

- Six attempts over 7 days:
  1. Right away (within 15 minutes for Hot leads, same day otherwise)
  2. Same day, a few hours later
  3. Day 2, at the opposite time of day
  4. Day 3
  5. Day 5
  6. Day 7
- Each no-answer brings up a one-tap WhatsApp nudge. Email nudges are offered on days 3 and 7.
- After the sixth no-answer, the lead moves to Not now (unreachable) and returns in 30 days for one more round.
- Any reply or call-back cancels the remaining attempts and moves the lead to the top of the owner's list.

## 9. Messaging: WhatsApp and email

### WhatsApp [Owner: direct Cloud API]

- One official number for the whole team. Each conversation belongs to the lead's owner. Replies alert the owner, and other users can't reply in that chat. Admins can see all chats.
- Free-form replies are allowed inside the 24-hour window. Outside it, only approved templates. The composer enforces this and shows the window's remaining time.
- Admins manage approved templates (first contact, no-answer nudge, fee and payment details, orientation follow-up, reminders, welcome) and submit new ones to Meta.
- Every message shows sent, delivered, read or failed. Failures appear in the owner's list.
- Messages arriving after hours attach to the lead and alert the owner. AADME's practice is to reply promptly to high-intent leads. [Owner] Sending outside quiet hours is only blocked for automatic messages (§10).

### Moving the number from the current provider [Proposed]

1. Build and test against a separate test number.
2. Export chat history from the current provider and import it onto matching leads as read-only history.
3. Bring the existing template list across; resubmit any that don't carry over.
4. Move the number outside working hours, as part of the launch (§18).

Past chats on staff personal phones or the WhatsApp Business app can't be imported. TeleCRM's logged WhatsApp messages are imported if its API exposes them.

### Email [Owner: Google Workspace and other providers; personal and shared addresses]

- Each user connects their own mailbox: Gmail API for Workspace, IMAP/SMTP for others, Microsoft Graph if needed.
- Only messages to or from a lead's address are synced, so personal and internal mail stays out. [Proposed]
- One-to-one email defaults to the user's own address. Admins connect shared addresses (for example admissions@) and choose which roles can send from each. The composer has a "send as" picker.
- Replies to a shared address attach to the lead and alert the owner. Unknown senders become organic inbound leads.
- Each address has its own signature. Replies stay in the same thread.
- A revoked or broken mailbox connection is flagged as disconnected, never fails silently.
- Bulk email (campaigns and sequences) goes through the bulk sending service on a subdomain, never through staff mailboxes, and always includes unsubscribe.

### Program details as the single source [Proposed]

Programs, curriculum summaries, fees, payment plans and batch dates are stored once (§11, §12). Templates insert them as variables, so a fee or date change updates every future message.

### AI drafting [Owner: Draft button now; full assistant possibly later]

- A Draft button in the WhatsApp and email composers writes a message from:
  - the lead's stage and last call outcome
  - recent conversation and handover notes
  - current program, fee and batch details
- Quick prompts refine it ("follow up after orientation", "answer fee concern", "shorter").
- The user always edits and sends. Drafts can't be sent automatically.
- WhatsApp drafts are only available inside the 24-hour window.
- Admins can switch AI off. The provider sits behind a connector, on a plan that doesn't train on AADME data. [Proposed]
- Each lead's context sent to the AI is limited to what's needed for the draft, and every draft request is logged. [Proposed]

## 10. Nurturing sequences and campaigns

### Sequences [Owner: both automatic and manual]

- A sequence is a series of steps. Each step is a WhatsApp template or email, with a delay and an optional condition (for example "only if the next batch starts within 30 days").
- Example, "Budget: not now":
  - Day 7: a success story
  - Day 21: the next batch start date and the EMI option
  - Day 30: back to the follow-up list for a call
- Leads join automatically from stage, outcome or Not now reason, or are added by hand.
- Each sequence is set to manual or automatic [Proposed]:
  - **Manual:** each step appears in the owner's follow-up list, ready to send, edit or skip.
  - **Automatic:** the step sends on schedule.
- Sequences for leads in Counselling through Payment pending are always manual. Not now and cold-lead sequences can be automatic. [Proposed; required by anti-goal 5]
- Marketing and admins build sequences. Automatic sequences need admin approval before going live.

### Campaigns [Proposed]

- One-off WhatsApp or email broadcasts to a filtered list (by stage, tier, source, program, Not now reason, tags).
- Built by marketing, approved by an admin.
- Leads in active stages are excluded unless explicitly included.

### Guardrails for anything sent automatically [Proposed]

- **Stops on engagement.** Any reply, call or stage change removes the lead from the sequence and alerts the owner.
- **Quiet hours.** Nothing sends between 9 pm and 9 am in the lead's time zone.
- **Frequency cap.** At most 2 marketing messages per lead per week, across all sequences and campaigns.
- **Opt-out.** "STOP" on WhatsApp, or an email unsubscribe, ends all automatic and marketing sending on every channel. One-to-one replies from the owner are still allowed if the lead writes in.
- **Meta rules.** Only approved templates. The expected Meta cost is shown before a sequence or campaign goes live.
- **Performance.** Each step shows delivered, read, replied and opted out.

## 11. Programs, batches, sessions and Zoom

### Programs and batches [Proposed]

- A program has a curriculum summary, duration, format, a fee list and payment plans (§12), an onboarding checklist template (§12) and course content (§13).
- A batch belongs to a program and has a start date, seat limit, mentors, a Zoom class meeting or series, and a WhatsApp group invite link.
- At enrollment the counsellor picks a batch and sees the seats left. A full batch needs admin override.
- The batch start date drives instalment due dates, checklist deadlines and lesson release.

### Sessions

Orientation and trial sessions are listed with date, program and Zoom link, so outcomes like "after orientation" can resolve to a real date. They're pulled from Zoom where possible, otherwise kept by admins. [Proposed]

### Zoom [Owner: Zoom is the webinar platform]

- AADME creates an app in its own Zoom account. Credentials stay with AADME.
- Registration must be on for tracked sessions.
- Registrations arrive by webhook and are matched to leads (new touch) or create leads with source "Webinar" and the session name.
- After each session the CRM pulls the attendance report: attended or no-show, plus time attended.
- **Orientation attended:** the lead moves to Trial / Orientation and the owner gets a same-day follow-up task.
- **No-show:** the owner gets a task with a "sorry we missed you, here's the next date" template ready.
- **Classes:** attendance is pulled into the learning platform (§13). Cloud recordings attach to the week's lesson; this needs a Zoom plan with cloud recording.

## 12. Payments and onboarding

### Payment methods [Owner: Razorpay mostly, plus direct UPI]

**Razorpay.**

- At Payment pending the counsellor picks the agreed payment plan. The CRM creates a Razorpay payment link for the first instalment and sends it with the fee template.
- Razorpay's signed webhook confirms payment. The CRM records it and moves the lead to Enrolled, alerts the owner, and starts onboarding.
- Unpaid links after 24 hours, and expired or failed links, create follow-up tasks with a reminder ready. [Proposed]

**Direct UPI** (to AADME's UPI ID or QR, outside Razorpay) [Proposed]:

- The counsellor records the amount, the UTR reference and a screenshot.
- The payment stays "awaiting verification" until an admin confirms it against the bank. Only then does it count.
- A UTR can't be recorded twice.

Recommendation to AADME: Razorpay links accept UPI too, which removes manual verification. Check Razorpay's UPI fees first. The manual route stays for exceptions.

Every payment records amount, method, Razorpay or UTR reference, date, instalment, and who recorded or verified it.

### GST invoices [Owner: the CRM issues GST invoices]

- **Fees and tax.** Each fee and payment plan instalment stores a taxable amount, a GST rate, the SAC code, and whether the quoted price includes GST. Admins set these per program.
- **Invoice details.** Each invoice carries AADME's legal name, GSTIN and registered address, and the student's name and billing address. It also carries their GSTIN if they want a business (B2B) invoice. Students can add a GSTIN at payment or in the portal.
- **Tax split.**
  - CGST plus SGST when the student is in AADME's registered state.
  - IGST when they're in a different state.
  - The student's state is captured at payment for this; it's the "place of supply".
- **Invoice on payment.** Every confirmed payment, Razorpay or verified UPI, generates a tax invoice. Each instalment gets its own invoice. The invoice is a PDF, emailed to the student and available in the portal.
- **Numbering.** Invoice numbers run in sequence per financial year (April–March), with no gaps or duplicates. They're allocated inside the same database transaction that confirms the payment. The format is admin-configurable before the first invoice of a year, for example `AADME/2026-27/00001`.
- **Locked once issued.** A wrong invoice is corrected by a credit note and a reissue, never by editing it.
- **Refunds and cancellations** generate a credit note that references the original invoice.
- **Reports and exports.**
  - Revenue reports show taxable value, tax and total separately.
  - A monthly invoice and credit note register exports to CSV for the accountant.
  - The export is shaped for GST returns, but the CRM does not file them.
- **Accountant sign-off first.** AADME's accountant confirms the GST rate, SAC code, invoice format and numbering before the payments phase starts (§21).

### Payment plans [Owner: predefined by the team]

- Admins define plans per program, for example: full payment; booking amount plus balance before batch start; three instalments.
- Each instalment is a fixed amount or a percentage, due a set number of days after the first payment or relative to batch start.
- Editing or retiring a plan only affects students who choose it afterwards.
- Counsellors pick from defined plans and can't change amounts. Exceptions need logged admin approval.
- After the first payment, the remaining schedule is created:
  - each instalment's link is sent 3 days before it's due, with a reminder on the due date
  - overdue instalments go to the top of the owner's list
- Each student's record shows paid, next due and overdue.

### Enrollment and payment status [Owner: use standard practice]

- A student is Enrolled when their first payment is confirmed, whether booking amount or full fee.
- Payment status sits alongside the stage: Paid in full, Partly paid, Overdue.
- An instalment unpaid 14 days past due (configurable) alerts the admin. The admin chooses to pause access, extend the deadline or cancel. The CRM never cancels on its own. [Proposed]
- Refunds and cancellations are recorded against the payment with a reason. A cancelled enrollment is subtracted from conversion reports, not deleted.

### Onboarding [Owner: checklist per program]

- On Enrolled, the CRM creates a checklist from the program's template. Admins build the template.
- Each item is required or optional, automatic or manual, and due a number of days after enrollment or before batch start.
- Template edits only affect students who enroll afterwards.
- Default items:
  - welcome message sent (auto)
  - assigned to a batch
  - batch WhatsApp group invite sent (auto) and joined (ticked by owner)
  - course access granted (auto)
  - Zoom class invites sent (auto)
  - laptop and setup confirmed
  - onboarding call done
- Students can complete some items themselves in the portal, such as confirming their details and laptop. [Proposed]
- The enrolling counsellor owns the checklist by default. Admins can assign items or whole checklists to someone else.
- When all required items are done, the student moves to Onboarded.
- Three days before batch start (configurable), open items go to the top of the owner's list and the admin is alerted.
- The laptop question is also asked at qualification (in the handover note), so a laptop gap comes up before payment.

## 13. Learning platform

AADME is building its own learning platform as part of this product. [Owner] The default format is a live cohort with recordings and weekly assignments, taught and reviewed by AADME's own staff. [Owner]

### Building blocks [Proposed]

- A program's content is organised into modules and lessons.
- A lesson contains any mix of:
  - recorded video, streamed from the video hosting service with signed, expiring URLs so links can't simply be shared
  - documents and files
  - links
  - a live class (Zoom)
  - an assignment
  - a quiz
- Programs combine these freely, so self-paced or milestone-based programs can be built later from the same blocks.
- Lessons release per batch on a schedule relative to the batch start date. Mentors and admins can release early or hold back.

### A week for a student (default format)

- Watch short recorded lessons before class.
- Attend 1–2 live Zoom classes and a weekly Q&A, joined from the student's schedule. Recordings appear on the lesson afterwards.
- Submit one practical assignment as a file, link or text.
- Read batch announcements from mentors. Day-to-day chat stays in the batch WhatsApp group.

### Assignments and review

- Each assignment has a due date. Late submissions are flagged.
- The mentor marks a submission Approved or Needs revision, with comments and an optional score. Students can resubmit.
- The mentor review queue is ordered: overdue reviews, new submissions, then students flagged as falling behind.

### Progress and risk [Proposed]

- Lessons completed, classes attended (from Zoom) and assignments submitted appear on the student's CRM record.
- A student who misses 2 classes or 2 assignments in a row (configurable) is flagged. Their mentor gets a task and their counsellor sees the flag.

### Completion [Proposed]

- Completing the required lessons and assignments generates a completion certificate as a PDF.
- Completed students are tagged in the CRM for testimonials and referral asks, and can enter nurturing sequences.

### Student portal [Proposed]

- Students see their courses, schedule, payment plan and instalments. They pay through Razorpay links and complete their own onboarding items.
- Access follows payment: the first confirmed payment unlocks the program and batch, and an admin pausing a student pauses access.
- Students can only ever see their own data.

## 14. Reporting [Proposed unless noted]

Owners and admins:

- Pipeline by stage, value and expected enrollments.
- Enrollments and revenue: collected versus still due. Revenue is visible to owners only. [Owner: admins and owners see all leads; revenue restriction is Proposed]
- Targets versus actuals: admins set weekly and monthly enrollment and revenue targets by team or person.
- Stage-to-stage conversion and time in stage, by source, tier, program and person.
- Follow-up health: overdue by person, unlogged calls, leads with no next step (target zero), Hot leads not contacted within 15 minutes.
- SDR and counsellor scorecards (§7).
- Not now: count by reason, and how many return and enroll.

Marketing:

- Lead volume, tier mix, qualification rate, stage reached and enrollments by source, campaign, ad set and ad. First-touch and last-touch views.
- Sequence and campaign performance, including WhatsApp messaging cost (worked out from data the CRM already holds).
- Ad spend [Proposed]: daily spend per campaign, ad set and ad is pulled from the Meta Marketing API and the Google Ads API. That gives cost per lead, per qualified lead and per enrollment, matching the "campaign performance" marketing reports to sales today. These two read-only connectors belong in phase 13.

Learning:

- Attendance, assignment completion and at-risk students by batch and mentor.
- Completion rate by program.

All reports filter by date range and export to CSV for roles allowed to see the underlying data. Exports are logged.

## 15. Admin configuration

Everything below is editable by admins (and owners) without code changes. Each change is logged.

- users, roles, groups, leave and away status, daily caps
- pipelines and stages
- tier rules
- routing groups and mappings
- call outcomes and their actions
- no-answer cadence
- Not now reasons and re-engage defaults
- follow-up list ordering
- WhatsApp templates and email templates
- sequences and campaigns (with approval)
- programs, fees, payment plans and batches
- sessions
- onboarding checklist templates
- at-risk thresholds
- quiet hours and frequency caps
- connected mailboxes and shared addresses
- AI on or off
- integration credentials (owners only) [Proposed]

## 16. TeleCRM migration [Owner: one-time, via API, about 500 leads]

- A connector pulls leads, statuses, notes, call history, owner assignments and any logged WhatsApp messages through TeleCRM's API.
- CSV/Excel export fills any gaps.
- The builder verifies TeleCRM's API coverage first.
- TeleCRM statuses are mapped to the new pipeline stages and owners are mapped to users. Admins review the mapping before import.
- Duplicates are matched by the same rules as live intake (§5) and merged.
- A dry run reports how many leads would be created, merged or skipped, with reasons, before anything is written.
- Original TeleCRM IDs are kept on each record, so ongoing sync can be added later. [Owner]
- The import is rehearsed on staging and rerun on fresh data on launch day (§18).
- After import, every lead has an owner, a stage and a next follow-up date. Imported leads with no next step land in their owner's list for triage.

## 16a. Existing students, batches and course content [Owner: everything moves, including content]

On launch day, everything current moves into the new system, so no one runs two systems afterwards.

**Records** (through import templates the CRM provides, CSV/Excel, with the same matching, dry-run and staging rehearsal as the TeleCRM import) [Proposed]:

- programs and their fees, GST settings and payment plans
- batches: start date, mentors, Zoom meetings, WhatsApp group link, seat limit
- active and past students, each linked to their program, batch and enrolling counsellor
- payment history: amount, date, method and reference for each payment already made
- remaining instalments, with due dates, so reminders and overdue tracking continue
- onboarding status for each active student
- course progress where it's known: lessons completed, assignments submitted

**Past invoices** [Proposed]:

- Payments made before launch are imported as historical records, not re-invoiced.
- Their existing invoice numbers and PDFs are attached where AADME has them.
- New invoice numbering continues from the last number AADME issued in the current financial year, so the sequence has no gaps or duplicates.

**Course content** [Proposed]:

- All existing recordings and materials are uploaded into the platform's video hosting and file storage, then organised into programs, modules and lessons.
- A bulk upload tool takes a folder of files plus a spreadsheet that maps each file to a program, module, lesson and order. Videos are transcoded in the background, and the tool reports any file that fails.
- Running batches get their lessons released up to the week they're in at launch, so students lose nothing.
- AADME's team sorts the content and fills the mapping spreadsheet. This is a content task, not a build task, and it should start early in the build so it isn't on the launch's critical path.

**Students' first login:**

- Imported students get an invitation email or WhatsApp message to set up their login on launch day.
- Their progress, schedule and remaining instalments are already in place.

## 17. Security and audit [Proposed]

- Two-step login (TOTP) for owners and admins. Optional for other staff. Students log in by email and password, or email one-time code.
- Sessions expire. Users can be deactivated instantly, which ends their sessions and returns their leads for reassignment.
- Object-level permission checks on every API endpoint. Tests cover each role's visibility rules.
- Append-only audit log for:
  - logins
  - assignments and reassignments
  - permission and role changes
  - stage changes
  - payment records and verifications
  - invoices and credit notes issued
  - exports
  - data deletion requests
  - admin configuration changes
  - AI draft requests
- Secrets in environment variables or a secrets manager, never in the repository. Stored third-party tokens are encrypted.
- Rate limiting on public endpoints (forms, webhooks, student login).
- Daily database backups, kept 30 days, with a restore tested before launch.

## 18. Launch [Owner: launch the fully complete solution at once]

Nothing replaces TeleCRM or the current WhatsApp provider until the whole product is built and tested. Both keep running until switch-over.

Risk noted to AADME: counsellors keep today's clerical load until launch. The rough estimate for a small team is 6–9 months, depending on team size. AADME accepted this. The phased build order (§19) keeps the option of launching earlier open.

To reduce the risk of one big launch [Proposed]:

- **Staff testing each phase.** At the end of every build phase, a counsellor, an SDR and (from phase 3) a mentor use it on a staging environment. Staging has a copy of TeleCRM data and a test WhatsApp number. No real leads are contacted from staging.
- **Rehearsed migration.** The TeleCRM import and the student, batch, payment and content imports (§16a) run on staging first, then rerun on fresh data at switch-over. Content uploads are done ahead of time and only topped up at switch-over.
- **Launch checklist.** Before switch-over, every lead source, connector, payment flow, invoice, onboarding step and student login is tested end to end. Counts for imported students, outstanding instalments and lessons are checked against the source spreadsheets.
- **Timing between batches.** Switch-over avoids the week before a batch starts and, where possible, falls between instalment due dates for active students.
- **Timing.** The WhatsApp number moves outside working hours and not in the week before a batch starts.

## 19. Build order

Built and tested in this order. Each phase ends with staff testing on staging (§18). Phases are planned one at a time. [Proposed order, adjusted by AADME's decisions]

1. **Foundation.** Repository, environments (local, staging, production), Django/DRF and React apps, users, roles and permissions, two-step login, audit log, person and lead model, pipelines and stages, admin configuration framework, connector pattern, background jobs, CI.
2. **Lead intake and routing.** All sources (§5), matching and duplicates, tiers, SDR and counsellor routing, handover.
3. **Follow-up core.** Home screens and follow-up list, call logging and outcomes, no-answer cadence, Not now and re-engage.
4. **Messaging.** WhatsApp Cloud API connector on the test number, templates and the 24-hour rule, email connectors (Gmail, IMAP/SMTP), shared addresses, unified timeline and inbox.
5. **TeleCRM migration.** Connector, mapping, dry run and staging rehearsal. Import of the current provider's WhatsApp history.
6. **AI drafting.** Draft button.
7. **Programs, batches, sessions and Zoom.**
8. **Payments and invoicing.** Razorpay links and webhooks, plans and instalments, UPI verification, payment status, GST invoices, credit notes, invoice register.
9. **Onboarding.** Checklists, batch assignment, automatic items.
10. **Learning platform, content.** Modules, lessons, video hosting, release schedule, student login and portal, access tied to payment.
11. **Learning platform, teaching.** Live classes, attendance, recordings, assignments and review, mentor queue, at-risk flags, certificates.
12. **Nurturing and campaigns.** Sequences, campaigns, bulk email service, guardrails.
13. **Reporting and launch readiness.** All reports (§14), Meta and Google Ads spend connectors, DPDP export and delete, backup restore test, student/batch/payment/content imports (§16a), launch checklist, switch-over.

The content bulk-upload tool ships with phase 10, so AADME's team can start uploading and organising content on staging while phases 11–13 are built.

## 20. Left to the builder

- Data model details, API design, URL structure and code organisation, within the constraints above.
- Exact libraries. Use well-maintained ones with pinned versions.
- UI visual design, beyond the mobile-first requirement and the agreed counsellor home screen layout (today's list, with Today, Inbox, Pipeline and Search tabs).
- Real-time updates mechanism (for example WebSockets or server-sent events) for new messages and list changes.
- Choice of bulk email service and video hosting service, within the portability rule.
- Choice of AI provider and model, within the no-training rule.
- Testing approach: test-driven, with permission and visibility rules covered in every phase.
- Staging data handling: personal data copied from production into staging must be access-controlled like production.

## 21. To confirm during the build

These are facts to check, not decisions for AADME:

- Railway's nearest region to Mumbai, and latency to Supabase Mumbai.
- TeleCRM API coverage: leads, notes, call logs, statuses, owners, WhatsApp messages.
- Current WhatsApp provider's name, its chat export format, and whether templates carry over.
- Whether any mailboxes are on Microsoft 365.
- AADME's Zoom plan: webinar add-on, cloud recording, and API access.
- Razorpay plan fees for UPI.
- With AADME's accountant, before phase 8: GST rate and SAC code for each program, whether quoted fees include GST, AADME's GSTIN and registered state, invoice number format, and the last invoice number issued this financial year.
- Where current student, payment and course content records live today (spreadsheets, Drive, YouTube or elsewhere), so the import templates match them.

## 22. Amendments from the admissions design (2026-10-25) [Owner]

On 2026-10-25 AADME reconciled this design with the admissions draft
(`2026-10-24-aadme-crm-admissions-design.md`). The product stays on this document's stack
(Django/DRF, React/Vite, Celery), and phases 1 and 2 stand as built. The draft's admissions
ideas below are folded into this design and take effect from the phase that next touches each
area. Where this section conflicts with an earlier section, this section wins.

1. **Handover packet on every work transfer.** Any stage change that transfers work needs a
   packet. That means a move into Qualified or a counsellor stage, into Not now, or into Lost.
   The packet has these fields:
   - intent summary
   - source and program (confirmed, prefilled)
   - last conversation snippet
   - objection tag (budget, laptop, competitor, timing, other)
   - next touch (a datetime, or an explicit "none" for Lost)

   Phase 2's handover note keeps its fields (background, concerns, budget signal, laptop,
   next step). The packet adds the fields above and extends where the note is required. An
   incomplete packet blocks the move.
2. **Reassignment note.** Changing a lead's owner without a stage change needs a short
   note saying why. Bulk reassign takes one note for the whole batch.
3. **Not now keeps its owner.** It is the draft's "Paused". It already has a reason and a
   re-engage date (§6). It keeps the stage kind `not now`, so repeat detection and reports
   are unchanged. The default label stays "Not now", and admins can rename it to "Paused".
4. **"Admissions" as the counsellor role's label.** The role code stays `counsellor`
   internally, so permissions, routing and data are unchanged. The UI shows "Admissions".
5. **Intent field.** Opportunities gain an intent level (High, Medium or Low). It is a
   field, not a second stage system.
6. **Scope and launch.** §18's full-launch decision and §19's build order stand unless
   AADME changes them. The draft's other open questions follow this document until AADME
   says otherwise:
   - a narrower v1 (§18, §19)
   - WhatsApp in the CRM at launch (§9)
   - Razorpay at launch (§12)
   - manager permissions (§2)

Items 1, 2 and 5 land in phase 3 (follow-up core). Item 3 lands in phase 3 with the Not now
work. Item 4 lands in the next frontend task.

