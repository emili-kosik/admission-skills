# Credential evaluation — translating a non-US transcript into US terms

A **course-by-course credential evaluation** converts a non-US secondary-school
record into US equivalents: a course list with US-style grades, a GPA on the 4.0
scale, and a statement of diploma equivalency. The two agencies colleges name
most often are **WES** ([wes.org](https://www.wes.org)) and **ECE**; colleges
typically require the agency to be a NACES member, and some name exactly which
agency they accept.

## Rule 1 — check each college first

Do not order an evaluation until each college's own requirement is known. Three
patterns exist:

| Pattern | What it means | Typically seen at |
|---|---|---|
| **In-house evaluation** | Admissions reads the original transcript itself; some explicitly say *do not* send third-party evaluations | Many selective private colleges |
| **Third-party evaluation required** | A course-by-course report from WES/ECE (or a named NACES member) must arrive with the application | More common at public universities |
| **Required later, not now** | Original documents suffice to apply; an evaluation is requested only at admission or enrollment | Varies |

The college's international admissions page states which pattern applies. Record
the answer in that college's `notes` in `colleges.json` and track ordering with a
`credential_eval_ordered` checklist key.

Standardized international curricula (IB, A-levels and similar) typically do
**not** need third-party evaluation at application time — colleges read them
natively, usually via school-submitted predicted grades. National curricula are
what typically trigger the requirement. Again: check per college.

## Rule 2 — respect the 4–8 week + fee reality

End-to-end turnaround is typically **4–8 weeks**, because the slow parts are not
the agency's processing time:

1. the school must send documents to the agency in the exact required format, and
2. the agency verifies authenticity, sometimes directly with the issuing school
   or examination board.

Fees for a course-by-course report are typically in the low-to-mid hundreds of US
dollars plus delivery fees — verify current pricing at
[wes.org](https://www.wes.org). The practical consequence: confirm every
college's requirement in **early September** and order the same week if any
college requires one. An evaluation ordered in December for a January 1 deadline
is a coin flip.

## The typical process (WES-style; verify specifics at wes.org)

1. Create an account and select the **course-by-course** report type (the summary
   "document-by-document" report is usually not enough for admissions).
2. The agency lists **required documents by country of study** — follow that list
   exactly. Most records must be sent by the school directly (sealed envelope or
   the agency's digital channel); some countries have official electronic
   exchanges.
3. Documents not in English typically need certified translations; each agency
   has rules about who may translate — read them before paying a translator.
4. The school sends; the agency verifies and issues the report, then delivers it
   electronically to the colleges selected.
5. As the college list grows, additional recipients can typically be added to an
   existing evaluation for a smaller per-report fee — one more reason to order
   once, early, rather than per college.

## Gotchas

- **Student-submitted documents are often rejected** — records usually must come
  from the school or examining board. Warn the school registrar early that a
  verification request is coming; that reply is frequently the slowest link.
- **Studies still in progress**: the evaluation covers completed years; final
  documents go in after graduation. Colleges know this rhythm — the enrolling
  college will want final results later anyway.
- **Keep originals** — agencies typically do not return submitted documents.
- **Name consistency**: use the same name spelling as the passport everywhere;
  the same records later support the I-20 file (see
  `references/visa-sequence.md`).

Cross-references: school report and predicted grades → the school-report section
of the international SKILL; financial documents → `financial-aid`
(`international-aid.md`); per-college deadlines → `tracker`.
