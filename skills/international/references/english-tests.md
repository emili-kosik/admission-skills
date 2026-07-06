# English proficiency tests — TOEFL, IELTS, Duolingo

Most US colleges require international applicants to prove English proficiency
unless they qualify for a waiver. Every college sets its own accepted tests,
minimum scores, and waiver rules — **never assert a specific college's policy
from memory**; its international admissions page is the contract.

## The three main tests

| | TOEFL iBT | IELTS Academic | Duolingo English Test (DET) |
|---|---|---|---|
| Format | Reading, Listening, Speaking, Writing; computer-based | Listening, Reading, Writing, Speaking (speaking with an examiner) | Adaptive, all skills mixed; includes a recorded video interview and writing sample shared with colleges |
| Length | ~2 hours | ~2¾ hours | ~1 hour |
| Score scale | 0–120 | Bands 1–9 in 0.5 steps | 10–160 |
| Where | Test centers; a Home Edition exists | Test centers; computer or paper; an online version exists | At home, any time, webcam-proctored |
| Results | Typically ~4–8 days | Typically ~1–5 days (computer), ~13 days (paper) | Typically ~2 days |
| Cost | Varies by country — check registration | Varies by country — check registration | Typically the cheapest of the three |
| Register / verify | [ets.org/toefl](https://www.ets.org/toefl) | [ielts.org](https://ielts.org) | [englishtest.duolingo.com](https://englishtest.duolingo.com) |

Acceptance: TOEFL and IELTS are accepted nearly everywhere; DET acceptance is
broad but **not universal** — confirm per college before relying on it. Some
colleges also decline the at-home editions of TOEFL/IELTS — verify if the student
plans to test from home.

## The timing rule: delivered by the deadline, not taken by it

Colleges need scores **in hand** by the application deadline. Work backward from
result turnaround plus official-score delivery, and leave room for one retake:

| Application deadline | Last comfortable test window |
|---|---|
| Nov 1 ED/EA | September–October |
| Nov 30 (UC filing) | October–early November |
| Jan 1–15 RD | October–November (December is cutting it close) |

Score delivery is a separate step from getting results: the student must order
official score reports to each college. TOEFL typically includes a few free
recipients chosen around test day with a per-report fee after; DET sends are
typically free and unlimited; IELTS institutions vary — verify current rules on
each test's site (links above).

## Minimums and waivers — patterns only, verify everything

- Highly selective privates typically look for TOEFL 100+ / IELTS 7.0–7.5 /
  DET 120–130; large publics typically 79–90 / 6.5 / 105–120. These are
  **patterns**, not policy — check each college, including per-section minimums
  (some colleges set them).
- Waivers are typically granted for several years of English-medium schooling,
  citizenship/education in designated English-speaking countries, or sometimes a
  strong SAT Reading & Writing / ACT English score. Definitions differ college to
  college — a waiver at one is not a waiver at another. When in doubt, testing
  once is cheaper than a deferred file.
- Superscore-style options (e.g., TOEFL MyBest) are accepted by some colleges and
  ignored by others — verify before counting on them.

## Choosing a test

1. **Acceptance first**: every college on the list must take it.
2. **Logistics second**: DET runs at home on demand; TOEFL/IELTS need a test
   center seat, which in some cities books out weeks ahead.
3. **Cost third**: fees vary by country; DET is typically the cheapest.

## Recording the plan

Store the plan and results in `profile.json` under `testing.english_proficiency`
(e.g., test, date, scores, colleges sent). When a college confirms receipt, tick
its `english_scores_sent` checklist key in `colleges.json`.

Cross-references: SAT/ACT sequencing → `testing-plan`; whether SAT/ACT is even
required per college → `data/test_policy.json` (mind its 6-month staleness rule);
deadline math → `tracker`.
