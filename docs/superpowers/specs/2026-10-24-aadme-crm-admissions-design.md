# AADME Admissions CRM: Design

- Date: 2026-10-24
- Status: Reconciled 2026-10-25. AADME kept the Django stack and folded this draft's
  admissions ideas into `2026-10-22-aadme-crm-design.md` §22. That document is the source of
  truth. This draft is kept for its reasoning, and its stack sections (§4, §11) are superseded.
- Source: brainstorming (2026-10-24) with AADME, grounded in admissions/sales interview answers
- Relation to prior work: An earlier, broader design exists at `2026-10-22-aadme-crm-design.md` (CRM + learning platform, Django/React). **This document is the admissions CRM spine decided in the 2026-10-24 session.** Where the two conflict, treat this document as the admissions product intent until AADME explicitly reconciles them. Stack conflict with the in-progress Django codebase is called out in §4 and §11.

How to read this: **[Owner]** = decided with AADME in this session (or carried from interview as their words). **[Proposed]** / **[Builder call]** = designer or builder judgment; stands unless AADME changes it.

## 1. Intent and why

AADME sells cohort programs (for example Agentic AI Agency Accelerator) to working professionals and business owners. Admissions today runs across phone, WhatsApp, TeleCRM, ChatGPT, and internal program docs. Counselors spend roughly an hour a day on clerical work: updating status, hunting WhatsApp history before a follow-up, re-pasting program/fee/payment copy, and dealing with duplicates across sources.

AADME wants a **fully custom CRM it controls end to end**: data model, workflows, hosting, and user population — not another SaaS CRM, not Strapi, not ERPNext. [Owner]

The single most important job in the next 90 days, in the counselor’s words: **lead follow-up tracking** — automatically show which leads need follow-up, when to contact them, what to send for nurturing, latest status, and previous conversation history, in one place. [Owner]

Domain facts that shape the product:

- Priority order in practice: about-to-pay → new inbound/organic → timed callbacks and referrals/repeats → Meta leads.
- Many “lost” leads are budget, no laptop, or competitor — not forgotten follow-ups — and often return as repeats if the reason was noted.
- WhatsApp + memory are the real system of record today; TeleCRM status lags.
- Handover fails when **intent and context** are missing.

## 2. Goals, non-goals, anti-goals

### Goals

1. **Follow-up command center.** Every open lead has one owner, one stage, and a next touch. Counselors and SDRs open the day to a prioritized queue, not a scavenger hunt across WhatsApp and TeleCRM. [Owner]
2. **Clean handoffs.** Marketing → SDR → admissions never drops intent/context; stage changes require a packet. [Owner]
3. **Owned infrastructure.** App and data run in AADME’s accounts (keys and DB held by AADME); TeleCRM can be retired after import. [Owner]
4. **Conversion visibility.** Manager and owner see pipeline by stage, source quality, and enrollment/revenue progress without asking counselors. [Owner]

Success signals at ~90 days [Proposed]:

- Clerical time on status/history hunting falls sharply (target: under ~15 minutes/day vs ~1 hour).
- ≥90% of due follow-ups completed in their scheduled window.
- Nobody needs TeleCRM or personal WhatsApp archaeology for active-lead context.
- Hot/inbound leads get first contact quickly (target: within 15 minutes during working coverage).

### Non-goals (v1 admissions CRM)

- Full learning platform, mentor teaching UI, recorded courses. [Proposed scope cut for this doc; may live in the Oct 22 design separately.]
- Strapi, ERPNext, HubSpot, Salesforce, or other vendor CRM as system of record. [Owner]
- Cloud telephony / call recording (calls stay on staff phones; outcomes logged in CRM). [Proposed]
- Native mobile apps (responsive web is enough unless AADME later insists). [Proposed; mobile not locked in session.]
- Intent scoring as a parallel pipeline (intent is a **field added after the stage ladder is stable**). [Owner]
- Ongoing TeleCRM sync (one-time import only). [Proposed]
- Automatic outbound messages into active counselling/negotiation stages without a human approving send. [Proposed anti-pattern; align with prior anti-goal.]

### Anti-goals

The product fails even if it “works” when:

1. **Double entry** — staff still update TeleCRM or keep truth only in WhatsApp.
2. **Orphan leads** — no owner, no next touch, or two people contacting the same lead.
3. **Empty handoffs** — stage flips without intent/context/objection/next touch.
4. **Data outside AADME control** — lead PII pasted into personal AI tools as the only draft path; vendor owns the canonical model.
5. **Slower than phone WhatsApp** for the daily follow-up loop.

## 3. Users and roles

Day-one roles [Owner]: **Marketing, SDR, Admissions (counselor), Manager, Owner.**

| Role | Job | Primary view |
|---|---|---|
| Marketing | Campaigns, lead volume/quality, source performance | Source/campaign reports; lead list by source and stage — not counselling transcripts by default [Proposed] |
| SDR | First organized touch, triage by source/urgency, qualify, hand off | SDR queue; owns early stages |
| Admissions | Counselling through payment and into onboarding handoff | Follow-up command center; full history on assigned leads |
| Manager | Coverage, assignment, pipeline health, no orphans | Team overdue list, stuck leads, stage funnel by rep |
| Owner | Enrollments, revenue, confidence the machine works | High-level funnel, revenue/enrollment targets, ability to see anything |

Rules [Owner + Proposed]:

- Exactly **one owner** and **one stage** per open opportunity at a time. [Owner]
- SDRs and admissions see leads assigned to them (with full history). Manager and owner see the team. [Proposed]
- Before contacting a lead, staff check assignee, previous conversation, and latest follow-up (product must make that the default screen, not a policy poster). [Owner interview]
- One person may hold multiple roles; permissions combine. [Proposed]
- Admin-style configuration (pipelines, templates, users) sits with **Owner** and optionally **Manager** [Builder call: whether Manager can edit config or only operate the pipeline].

## 4. Constraints

### Hosting and ownership [Owner]

- Custom application in **AADME’s cloud project**; AADME holds keys and database.
- Existing services available: **Supabase, Resend, Railway**.
- Retire TeleCRM without another CRM vendor owning the pipeline.
- **Do not** build the CRM on Strapi or ERPNext. [Owner]

### Stack [Owner choice in this session]

Recommended and locked in conversation:

- **Next.js** (App Router) on **Railway**
- **Supabase** Postgres + Auth + RLS (+ Realtime for queues; storage for program PDFs)
- **Resend** for email
- WhatsApp Cloud API and Meta lead ingest when wired
- Small Railway cron/worker only when webhooks/reminders need it — don’t start with a heavy worker fleet

**Conflict note:** The Oct 22 approved design and current `aadme-crm` codebase use **Django/DRF + React/Vite + Celery**, with a portability rule against Supabase-only auth. AADME must reconcile **continue Django** vs **repoint to Next.js+Supabase Auth** before major new build work. Until reconciled, implementers must not silently fork the product. [Owner decision required — see §11]

### Integrations (v1 priority) [Proposed unless noted]

| Integration | Purpose | When |
|---|---|---|
| Meta WhatsApp Cloud API | Official WhatsApp as channel in CRM | As soon as follow-up center ships |
| Meta Lead Ads | Inbound leads | Day-one intake |
| Website forms | Inbound leads | Day-one intake |
| Resend | Transactional / nurture email | Day one |
| TeleCRM | One-time import | Launch migration |
| Payment confirmation | Mark Payment pending → Enrolled | [Builder call: Razorpay webhooks vs manual verify first] |
| ChatGPT/Claude in personal accounts | Not a system dependency | Drafting may later be an in-app assist on a business API; v1 can ship template library instead |

### Data protection [Proposed]

- India’s DPDP Act mindset: consent/opt-out, export/delete, access audit, backups, signed webhooks.
- Normalize phone to E.164; match duplicates on phone/email.

## 5. Pipeline (stage ladder)

Spine [Owner]:

`New → SDR working → Qualified → Counselling → Orientation/Trial → Negotiation → Payment pending → Enrolled → Onboarding → Active student`

Side doors [Owner]:

- **Paused** — budget / laptop / timing (and similar); still has an owner and a next-touch / re-engage date so it is not a black hole. [Owner + Proposed]
- **Lost** — competitor / not interested / bad data / do-not-contact

**Intent** is a field to add later (High/Medium/Low), not a second stage system. [Owner]

Stage ownership [Proposed]:

| Stages | Default owner role |
|---|---|
| New, SDR working, Qualified | SDR |
| Counselling → Payment pending | Admissions |
| Enrolled → Onboarding → Active student | Admissions (then ops/onboarding as configured) |
| Paused | Last owner (usually admissions); due on re-engage date |
| Lost | Closed; no queue unless reopened as repeat |

Repeats reopen onto the ladder with history kept (typically SDR working or Counselling depending on prior depth). [Owner]

Admins/owners may rename labels later; kinds (open / paused / lost / won) should remain stable for reporting. [Proposed]

## 6. Handoff model

**Gate by stage + owner**, with **packet fields required on stage change**. [Owner]

Required packet on any stage change that transfers work (especially into Qualified → Counselling, and into Paused/Lost) [Owner]:

1. Contact details (already on person; confirm still valid)
2. Source
3. Program
4. Intent summary
5. Last conversation snippet
6. Objection tag (budget / laptop / competitor / timing / other)
7. Next touch (datetime or explicit none for Lost)

Rules [Proposed]:

- Incomplete packet → stage/owner change blocked.
- Admissions should not “pull” raw Meta dumps; Qualified (or routing rules that skip SDR for hot tiers) is the gate.
- Assignment change without stage change still requires a short note (why reassigned). [Builder call: require full packet vs short note]

## 7. Daily work: follow-up command center

### Admissions / SDR home [Owner intent]

A single prioritized list answering: who, why now, what to do, what’s the history.

Default admissions order [Proposed, from interview]:

1. Payment pending / about to pay
2. Timed callbacks (“call me in 15 minutes”)
3. New inbound / organic / referral / repeat needing contact
4. Orientation/trial follow-ups and open doubts
5. Meta / lower-urgency due today
6. Paused returning on re-engage date

Each row: reason on list, stage, source, program, next action, one-tap Call / WhatsApp / open history.

Logging after a call or chat [Proposed]:

- Outcome + optional one-line note + next follow-up (quick picks)
- Stage may advance when outcome implies it (e.g. discussing fees → Negotiation or Payment pending)
- Status update is the clerical pain today — keep this to seconds, not a second form in TeleCRM

### Outside hours [Owner interview]

High-intent replies should not wait unnecessarily; product should surface overnight replies at the top of the next session and support responsive web so staff can act from a phone browser. Auto-blast marketing templates into active deals is out of scope.

### Program / fee truth [Owner pain]

Canonical program, fee, payment modes, batch dates live in the CRM (and are what gets inserted into WhatsApp/email templates). Stop copy-paste from scattered internal docs as the source of truth. [Proposed]

## 8. Intake, duplicates, priority

Sources in play [Owner interview]: organic/inbound, referral/repeat, Meta, campaigns/webinars, WhatsApp.

On batch arrival, first physical action today is prioritize then call — the CRM should present that ordered queue automatically. [Owner]

Duplicates: same person via multiple sources merges to one person with multiple touches; preserve first and latest source for reporting. [Proposed]

Quality / priority hints without a parallel stage system [Proposed until Intent field ships]:

- Treat referral, repeat, organic/inbound as higher urgency than Meta by default (matches current practice).

### First owner and routing [Proposed — carried from prior AADME design where this session did not re-decide]

- New opportunities are auto-assigned (round robin within SDR groups). Tier/source can map to groups (stronger SDRs get hotter tiers).
- Hot tiers/sources (e.g. referral, repeat, organic) may skip SDR and go straight to an admissions group at Counselling when configured.
- If no SDRs are available, route to admissions.
- On Qualified → Counselling, ownership transfers to the admissions assignee (round robin in the matching counsellor group) as part of the same gated stage change.
- Repeat leads prefer their previous owner if that person is active.
- Away/leave users are skipped; manager/owner can bulk reassign. Leads are never left with no owner.
- Manual reassignment always allowed; record who did it and why.

## 9. Post-payment stages without a learning platform [Proposed]

Until a learning product is in scope, **Onboarding** and **Active student** are CRM stages plus light ops data — not an LMS:

- Onboarding: checklist items (e.g. payment confirmed, WhatsApp group invite sent, batch assigned, orientation-to-class handoff done), batch/start date fields, owner still admissions or an ops assignee.
- Active student: checklist complete; used for reporting that enrollment reached class start. No mentor teaching UI, no lesson player in this spine.

## 10. Role views (manager / owner / marketing)

- **Marketing:** volume, quality proxies (qualification rate, stage reached, enrollments) by campaign/source — not counselor chat logs by default. [Proposed]
- **Manager:** unassigned/stuck, overdue follow-ups by person, double-contact prevention via single owner, coverage when someone is absent (reassign). [Owner]
- **Owner:** enrollments, revenue targets, funnel conversion; drill-down allowed. [Owner]

## 11. What’s left to the builder

Builders may decide without further AADME input unless marked §12:

- Exact schema and permission enforcement implementing roles above
- UI layout/components (must pass phone-first anti-goal)
- Template storage for program/fee WhatsApp snippets
- Duplicate-match edge cases (same phone different email, etc.)
- Reminder delivery channel (in-app + email via Resend first)
- Mapping TeleCRM statuses → this stage ladder during import
- Worker/cron shape after stack reconciliation
- Onboarding checklist item list (sensible defaults; admins edit later)

## 12. Open decisions for AADME (must answer before approval)

Settled in-doc without re-asking: routing (§8), post-payment CRM-only meaning (§9).

Still required from AADME:

1. **Stack reconciliation**
2. **V1 scope** (admissions spine vs full Oct 22 CRM+learning)
3. **WhatsApp at launch** (in-CRM Cloud API vs deep-link + logged outcomes)
4. **Payments at launch** (manual confirm vs Razorpay/webhooks)
5. **Manager permissions** (pipeline-ops only vs full admin config)

## 13. Builder check

Builder review completed 2026-10-24. Minor gaps folded into §§8–9. Remaining questions are §12 (AADME only). Nothing is built from this draft until AADME answers §12 and approves the full description.
