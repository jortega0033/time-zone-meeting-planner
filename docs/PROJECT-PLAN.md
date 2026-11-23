# Time-zone Meeting Planner

## Product requirements

A distributed team coordinator can plan a week of synthetic meetings and see which recurring times stay workable when clocks change. Load a scenario in Chrome, generate a schedule, inspect each person's local time and any conflicts, then save and reopen the scenario. Use a synthetic case with 40 meetings for 15 people across six zones as a stress fixture. The first release prioritizes a correct schedule on a smaller case with clear explanations for any unresolved meetings.

**Primary user.** A coordinator balancing attendance and inconvenient hours across teams. All starter scenarios use made-up participants, calendars and meeting names.

**User stories.**

- As a coordinator, I can enter weekly work hours, preferred hours and one-off busy periods in each participant's zone. I can tell which occurrence or field failed validation.
- As a coordinator, I can schedule one-off and weekly meetings together while keeping a recurring series on the same local weekday and time in its anchor zone.
- As a participant, I can see the local time and UTC offset for each occurrence and see when a time would sit outside my preferred hours.
- As a coordinator, I can distinguish a scenario with no feasible schedule from a search that stopped at its limit. I can inspect blocked meetings and adjust the inputs.
- As a coordinator, I can save a valid scenario on the local machine, restart the app, and reproduce its results with the same time-zone data version.

**First meaningful slice.** Ship a bundled two-person, one-series fixture. Both Ada in Amsterdam and Bo in New York are available on Mondays from 09:00 to 17:00 local time. Their 30-minute meeting meets at 15:00 Amsterdam time on March 8, 15 and 29, 2027, within a four-week recurrence that excludes March 22. The first slice loads the fixture, generates the schedule, and renders all three occurrences with both local times and UTC. Include a second fixture with one occurrence blocked by Bo's calendar and show the conflicting date. The numbers below are precomputed expectations for these fixtures.

**Release boundary.** Local Chrome and a loopback-only Python process. The supported input is synthetic data. Calendar sync, external solver APIs, live accounts, team sharing, arbitrary recurrence rules, overnight windows and cloud services are outside the first release. Weekly work windows must start and end on the same local date. A series can include explicit date exceptions. Participation and meeting duration are fixed by the input.

## Technical design

### Local app and reproducibility

Serve bundled HTML, CSS and JavaScript plus a small JSON API from Python 3.12 on an ephemeral or configurable loopback port. Keep the time conversion, candidate generation, allocation and rendering as separate layers. Keep the initial API shape small with scenario validation, solve, save and load operations. Render all participants' local labels from the solver result so Chrome's time-zone data cannot change the reported offsets. Use local assets and bind only to loopback. Accept writes with the local UI's origin and JSON content type. Set request limits and use atomic file replacement for saving user-selected scenarios to an app-owned data folder. User input is rendered as text. No telemetry or third-party requests.

Use Python's standard-library `zoneinfo` with a staged, versioned IANA TZif directory. The implementation ticket must record the selected IANA release, source archive checksum, staged zone IDs and staged input hash. Load the supported zones explicitly with `ZoneInfo.from_file`. The app shows a targeted setup error when the selected zone or data version is unavailable. Time-zone rules and offsets can be updated by IANA, and Python may otherwise use host data or a fallback package. [Python 3.12 zoneinfo](https://docs.python.org/3.12/library/zoneinfo.html), [IANA Time Zone Database](https://www.iana.org/time-zones)

### Contracts and rules

| Object | Required contract |
| --- | --- |
| Scenario | Schema version, supported time-zone release, stable ID, horizon start and end in UTC, participants and meetings. The horizon is a half-open interval. Up to 8 weeks. |
| Participant | Stable ID, display label, IANA zone ID, recurring local work and preferred windows by weekday, date-specific busy intervals. Preferred windows must sit within work windows. Missing preferred hours mean all work hours are preferred. |
| Meeting | Stable ID, required participant IDs, anchor zone, elapsed minutes, local allowed weekdays and start window, one-off local date or inclusive weekly date range, optional exception dates. A weekly series uses the same local weekday and time for each included occurrence. A one-off meeting has one fixed date. |
| Result | Status, time-zone data version, visits, occurrences or blocker evidence. Occurrences include UTC interval, anchor and participant local labels with offsets, and per-participant burden. Options and results use stable ordering. |

- Represent elapsed time as integer UTC minutes. Accept input times on a 15-minute grid and meeting durations from 15 to 120 minutes in 15-minute steps. Resolve each local date separately. A recurring 15:00 anchor remains 15:00 after a DST shift.
- For a local wall time, test both `fold` values by converting to UTC and back. Retain matching wall times, deduplicate UTC instants and sort. Zero matches means a gap. Two matches means a fold. Exact user-entered local busy endpoints require an explicit fold choice when ambiguous and return a field-level error for a gap. Availability boundaries reject ambiguous or missing occurrences in the planning horizon with a dated message so the scenario can be corrected. Generated meeting candidates choose the earlier instant in a fold. If a recurring candidate falls into a gap on an included date, exclude the entire option and show that date as a possible blocker. An explicit exception date removes that occurrence from consideration. Use actual elapsed minutes for all meeting endpoints. [Python 3.12 zoneinfo](https://docs.python.org/3.12/library/zoneinfo.html), [PEP 495](https://peps.python.org/pep-0495/)
- Expand work and preferred windows and normalize overlaps before scoring. A meeting must fit entirely within work time for every required attendee and within the scenario horizon. All occupied intervals use `[start,end)` exclusion. For example, an event ending at 14:30 UTC leaves 14:30 UTC available. Simultaneous meetings are allowed when their attendee sets are disjoint.
- Generate UTC occurrence vectors from meeting anchor grid candidates. An option is eligible when every occurrence passes single-meeting constraints. Keep a tally of rejection reasons and deterministic examples with meeting, participant, date, and blocker type.
- Search eligible options with a stable backtracking order following smallest remaining domain, then meeting ID. Reject overlapping events with a shared attendee. Score complete schedules by minimizing the highest individual burden across all scheduled occurrences, then the sum of all individual burdens, then the lexicographic vector of anchor slots ordered by meeting ID. Burden is the elapsed minutes a participant spends outside their preferred windows, with zero cost when fully inside. Ties on a fold follow the earlier-instant rule.
- Limit input to 15 participants, 40 meetings, 8 weeks and a total of 20,000 candidate occurrences evaluated during generation. Validate participant calendars and candidate limits before commencing search. Limit search to 50,000 candidate visits and return deterministic distinct statuses `solved`, `infeasible`, `limit_reached` or `invalid_input`. A valid complete schedule found before the limit can be returned as a feasible preview, with optimality pending and an explicit reason. If all domains fail locally, show the first dated blocking examples. If domains exist but no global assignment is possible, show a recorded shared-attendee collision and identify it as one conflict found during search. When the limit is reached without a complete schedule, show that completion is unknown. Provide a runtime target of two seconds to first result for the demo fixture on the target VM and record measured time in QA, with deterministic visit budgets as the repeatable guard. Label missing time-zone data and unsupported sizes separately.

### Fixed fixture expectations

Computed by converting 15:00 Amsterdam to UTC, then converting that instant to New York. These dates cover the period when the cities are on different DST schedules. The release must also validate them against its staged TZif data.

| Monday in 2027 | Amsterdam anchor | Expected UTC | Expected New York |
| --- | --- | --- | --- |
| March 8 | 15:00 CET (+01:00) | 14:00Z | 09:00 EST (−05:00) |
| March 15 | 15:00 CET (+01:00) | 14:00Z | 10:00 EDT (−04:00) |
| March 29 | 15:00 CEST (+02:00) | 13:00Z | 09:00 EDT (−04:00) |

- Amsterdam 2027-03-28 02:30 and New York 2027-03-14 02:30 have zero valid UTC instants. Amsterdam 2027-10-31 02:30 has UTC answers 00:30Z and 01:30Z. New York 2027-11-07 01:30 has UTC answers 05:30Z and 06:30Z. Assert exact offsets and statuses. [IANA Time Zone Database](https://www.iana.org/time-zones)
- At 14:00Z on March 15, 2027, a 30-minute duration touches but does not overlap `[14:30Z,15:00Z)`. A block at `[14:15Z,14:45Z)` rejects the option when it represents a required attendee's calendar.
- A tiny fairness fixture has one attendee preferring 09:00–10:00, two half-hour meetings, and one feasible assignment. Meeting M1 can use 09:00 or 10:00. Meeting M2 must use 09:00. The solver must place M2 at 09:00 and M1 at 10:00 for a burden of 30. Removing M1's 10:00 option must produce `infeasible`. In a separate fixture, M1 and M2 both accept 09:00 or 10:00 with equal costs. The stable tie chooses 09:00 for M1 and 10:00 for M2. A third fixture compares one meeting across two attendees, with feasible costs `(0,30)` at an earlier slot and `(15,15)` at a later slot. The later slot wins under the highest-individual-burden policy.

## Epic E49 · Build an offline scheduling workbench

**Goal.** A coordinator can generate and review an offline schedule for a saved synthetic scenario, including DST-safe dates, time-zone labels, and evidence for conflicts.

**Definition of done.** The demo and a blocked scenario work from a clean offline installation staged with the requisite assets and data. Fixed DST fixtures and the independent solver oracle pass. Relaunch preserves a schema-versioned scenario and its outputs for the same input and TZif version. The documented visit and input boundaries are exercised without misreporting a search cutoff as infeasibility. No output durations are reported as actual work time.

**Estimated engineering effort.** 17–29 hours across the six implementation tickets, including their tests. This is an estimate for future work.

### E49-01 · Resolve and validate local times

**Estimate.** 3–5 hours. **Dependencies.** None.

Deliver the versioned TZif staging instructions, supported zone registry and conversion module, and starter fixtures. Declare schemas and field error shape for downstream tickets.

**Acceptance criteria.**

- A clean supported environment with staged TZif can load Amsterdam and New York offline and report the exact data version. Missing or wrong-version data returns an actionable error.
- Automated checks assert every expected UTC and local value in the three-date table, both gaps and both folds. The fold policy and local round-trip behavior are tested independently of candidate search.
- Unknown zone IDs, duplicate IDs, invalid dates, malformed intervals and invalid fold choices surface error codes with field paths. Interval validation uses resolved instant ordering.

### E49-02 · Expand recurring calendars and generate meeting options

**Estimate.** 3–5 hours. **Dependencies.** E49-01.

Deliver weekly work and preferred window expansion, dated busy intervals, recurrence expansion, feasible occurrence vectors, burden per attendee, and dated rejection examples.

**Acceptance criteria.**

- The first fixture yields exactly three 15:00 Amsterdam occurrences with the expected UTC and New York values. An exception date disappears from the occurrence vector. A DST gap on an included date removes the option.
- Merge overlapping work, preferred and busy intervals by kind. Tests prove touching endpoints are permitted, a 15-minute overlap blocks, and an event that crosses the end of availability or horizon is rejected.
- Keep reason counts by constraint type and at least one stable dated example. Repeated runs over the same input return identical ordered options. Enforce the candidate generation cap.

### E49-03 · Allocate meetings and compare with a tiny exhaustive oracle

**Estimate.** 4–6 hours. **Dependencies.** E49-02.

Deliver a deterministic solver, score components, feasible preview on cutoff where available, bounded search and structured conflict evidence.

**Acceptance criteria.**

- Only events with at least one shared attendee block each other. Verify the three fairness fixtures, equality tie order, proven infeasibility and forced budget exhaustion. When the search finds a feasible preview under the cap but cannot prove optimality, preserve the preview and its status.
- Implement a deliberately independent exhaustive reference for tiny option sets with up to five meetings and six candidates each. Enumerate combinations and check all pairwise half-open collisions, then recompute the score from raw burden totals. Cross-check production status, score and stable winning vector with scripted and reproducibly seeded input, including cases without any solution.
- Provide dated blocker examples after local or global failure and label budget exhaustion separately from proven infeasibility. Tests cover the visit count at the hard cap and repeatability.

### E49-04 · Build the local Chrome schedule and conflict view

**Estimate.** 3–5 hours. **Dependencies.** E49-01 contracts. Fixture-backed UI work can run alongside E49-02 and E49-03. Live integration needs E49-03.

Deliver scenario selection, a basic editor for synthetic inputs, an accessible agenda grouped by date, attendee local-time details and a conflict view.

**Acceptance criteria.**

- From a new tab, select the demo, generate a result, identify all three dates and display each attendee's local time and offset without visiting a second page. Show when the time falls outside preferred hours.
- The conflict view accepts structured examples, shows the affected dates and people where available, and distinguishes the four result statuses in plain language. Field errors link to the relevant input and appear in a status region.
- Keyboard users can complete fixture load, solve and date inspection. The agenda explains offsets in text and remains usable at 320 px width and 200% browser zoom. Include a manual check for focus and retry.

### E49-05 · Save and reopen versioned scenarios locally

**Estimate.** 2–4 hours. **Dependencies.** E49-01 contracts. Can run alongside E49-02, E49-03 and E49-04.

Deliver app-owned scenario storage and JSON import/export, schema version and time-zone metadata, and a local restart test.

**Acceptance criteria.**

- A saved valid scenario reopens after process restart and reproduces equivalent results with the same TZif version. Preserve optional exception dates and fold choices through export/import.
- Malformed JSON, unsupported schema versions, oversize inputs, invalid names and missing fields show actionable errors without replacing the previously saved scenario. Save uses atomic replacement.
- A differing data version is visible and blocks silent reproduction. Export contains synthetic scenario inputs and version metadata only.

### E49-06 · Verify the offline journey and largest input boundary

**Estimate.** 2–4 hours. **Dependencies.** E49-01 through E49-05.

Deliver documented local run steps, offline proof, browser acceptance walkthrough, a smaller end-to-end fixture and a synthetic stress dataset.

**Acceptance criteria.**

- With network access disabled for the app and local assets staged, Chrome can solve the demo, display conflict details, save, restart, reopen and solve again. The app makes no non-loopback requests. Log observed timings in QA.
- Run a synthetic stress fixture of 40 meetings, 15 participants and six zones. It either produces a valid full schedule or a correctly labeled boundary outcome, within the documented input and visit limits. Test oversize rejection adjacent to the limit. Document the cap and observed outcome.
- Record QA evidence against the three-date recurrence, one fold and one gap, exact half-open boundary, fairness tie, keyboard path and saved restart. Capture exact checks run with their results.

**Sequencing.** Land E49-01 first. Run E49-02, E49-04's fixture UI and E49-05 in parallel on the shared contracts. Start E49-03 after E49-02 and integrate it into E49-04. Run E49-06 after integration. The first meaningful slice combines E49-01 and a small vertical portion of E49-02 through E49-04, then proves full restart with E49-05.
