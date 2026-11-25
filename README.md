# Time-zone Meeting Planner

An offline scheduling workbench for recurring meetings across time zones, with daylight saving checks and conflict explanations.

Implementation is planned. The scope, architecture and acceptance criteria are in [the project plan](docs/PROJECT-PLAN.md). The plan includes a reproducible verification strategy for the future build.

- [Product requirements](docs/PROJECT-PLAN.md#product-requirements)
- [Technical design](docs/PROJECT-PLAN.md#technical-design)
- [Implementation backlog and epic](https://github.com/jortega0033/time-zone-meeting-planner/issues)

The first plan of phase 1 said 17–29 engineering hours. Its open tickets, with tests and review, add up to 60 to 93 hours; the whole program is larger and is described below. All figures are estimates.

## Program goal

Turn the planner into an exact scheduling engine for whole organisations: own time-zone and calendar mathematics, an optimiser that proves the best or shows why none exists, live rescheduling for tens of thousands of people, and a standards-complete calendar server.

The program is planned ([#36](https://github.com/jortega0033/time-zone-meeting-planner/issues/36)). Phase 1 is the current epic [#1](https://github.com/jortega0033/time-zone-meeting-planner/issues/1) and the only phase with tickets.

**Score.** Share of public timetabling benchmark instances solved to a proven optimum or within a stated gap, and the share of RFC 5545 recurrence cases equal to two reference implementations.

| Phase | Content | Hours (rough) | Issue |
|---|---|---|---|
| 1 | The current epic and its tickets | 60 to 93 | [#1](https://github.com/jortega0033/time-zone-meeting-planner/issues/1) |
| 2 | Time mathematics | 80 to 140 | [#37](https://github.com/jortega0033/time-zone-meeting-planner/issues/37) |
| 3 | Exact optimiser | 160 to 280 | [#38](https://github.com/jortega0033/time-zone-meeting-planner/issues/38) |
| 4 | Organisation scale | 120 to 200 | [#39](https://github.com/jortega0033/time-zone-meeting-planner/issues/39) |
| 5 | Calendar server | 120 to 210 | [#40](https://github.com/jortega0033/time-zone-meeting-planner/issues/40) |
| 6 | Simulation | 90 to 150 | [#41](https://github.com/jortega0033/time-zone-meeting-planner/issues/41) |

About 630 to 1070 engineer hours in total: rough estimates, not measurements. The numbers in the score and the finish lines are targets until a run shows them. Only phase 1 has tickets to work; the sub-issues of a later phase are written when it starts. No single session is expected to reach the end.

## License

[MIT](LICENSE) © 2026 Jake Ortega.
