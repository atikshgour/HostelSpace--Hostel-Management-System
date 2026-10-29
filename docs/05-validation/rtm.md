# Requirement → story → implementation → test → evidence

Source: original SRS FR-01–11, NFR-01–05, SEC-01–06, BR-01–07; existing starter story and sprint mapping. Preserve source use cases: FR-05→UC-04, FR-06→UC-05, FR-10→UC-09. Legacy SRS TC-05/06/10 correspond to expanded TC-FR05/06/10-01. See `cases.md` for preconditions/steps/expected outcomes and `execution-log.md` for commands and observed results. **No PR, CI or approval URL exists yet.**

| Requirement | Story / implementation boundary | Cases / automated evidence | Completion |
|---|---|---|---|
| FR-01 | US-01 — teammate-owned module, not implemented here | TC-FR01-01; Not Run for shared/team module | Local login/session/CSRF flow passed; real dashboard/profile NOT RUN |
| FR-02 | US-03 — teammate-owned module, not implemented here | TC-FR02-01; Not Run for shared/team module | NOT RUN — teammate content CRUD; Arin rule-choice boundary tested |
| FR-03 | US-04 — teammate-owned module, not implemented here | TC-FR03-01; Not Run for shared/team module | NOT RUN — teammate module |
| FR-04 | US-09; US-10 — teammate-owned module, not implemented here | TC-FR04-01; Not Run for shared/team module | NOT RUN — teammate module |
| FR-05 | US-05/06 — LeaveList workspace; models/serializers/services/permissions/views | TC-FR05-01; test_api.py; test_services.py; leave.test.jsx; isolated backend harness; concurrent finalization test pending | LOCAL PASS; PostgreSQL concurrent finalization gate pending |
| FR-06 | US-07 — AttendanceHistory workspace; location.py; Attendance/Session; services | TC-FR06-01; test_api.py; test_services.py; attendance.test.jsx; isolated backend harness; concurrent acceptance test pending | LOCAL PASS; PostgreSQL race and real-policy approval pending |
| FR-07 | US-11; US-12 — teammate-owned module, not implemented here | TC-FR07-01; Not Run for shared/team module | NOT RUN — teammate module |
| FR-08 | US-13 — teammate-owned module, not implemented here | TC-FR08-01; Not Run for shared/team module | NOT RUN — teammate module |
| FR-09 | US-14; US-15 — teammate-owned module, not implemented here | TC-FR09-01; Not Run for shared/team module | NOT RUN — teammate module |
| FR-10 | US-08 — DeviationPanel workspace; rule snapshot/deactivation/total | TC-FR10-01; test_api.py; test_services.py; deviations.test.jsx; isolated backend harness | LOCAL PASS; real shared Rule integration pending |
| FR-11 | US-16 — teammate-owned module, not implemented here | TC-FR11-01; Not Run for shared/team module | NOT RUN — teammate module |
| NFR-01 | US-22 + relevant owner stories — All; see cases register | TC-NFR01-01 | See per-case local vs pending status; no global pass inferred |
| NFR-02 | US-22 + relevant owner stories — All; see cases register | TC-NFR02-01 | See per-case local vs pending status; no global pass inferred |
| NFR-03 | US-22 + relevant owner stories — Arin/Atiksh; see cases register | TC-NFR03-01 | See per-case local vs pending status; no global pass inferred |
| NFR-04 | US-22 + relevant owner stories — All; see cases register | TC-NFR04-01 | See per-case local vs pending status; no global pass inferred |
| NFR-05 | US-22 + relevant owner stories — All; see cases register | TC-NFR05-01; TC-CICD-01 | See per-case local vs pending status; no global pass inferred |
| SEC-01 | US-22 + relevant owner stories — All; see cases register | TC-SEC01-01; TC-CICD-01 | See per-case local vs pending status; no global pass inferred |
| SEC-02 | US-22 + relevant owner stories — Anvi; see cases register | TC-SEC02-01 | See per-case local vs pending status; no global pass inferred |
| SEC-03 | US-22 + relevant owner stories — All; see cases register | TC-SEC01-01 | See per-case local vs pending status; no global pass inferred |
| SEC-04 | US-22 + relevant owner stories — All; see cases register | TC-SEC04-01; TC-CICD-01 | See per-case local vs pending status; no global pass inferred |
| SEC-05 | US-22 + relevant owner stories — Arin; see cases register | TC-SEC05-01 | See per-case local vs pending status; no global pass inferred |
| SEC-06 | US-22 + relevant owner stories — Atiksh; see cases register | TC-SEC06-01 | See per-case local vs pending status; no global pass inferred |
| BR-01 | US-22 + relevant owner stories — Arin; see cases register | TC-FR05-01 | See per-case local vs pending status; no global pass inferred |
| BR-02 | US-22 + relevant owner stories — Aryan; see cases register | TC-FR03-01 | See per-case local vs pending status; no global pass inferred |
| BR-03 | US-22 + relevant owner stories — Aryan; see cases register | TC-FR04-01 | See per-case local vs pending status; no global pass inferred |
| BR-04 | US-22 + relevant owner stories — Aryan; see cases register | TC-FR04-01 | See per-case local vs pending status; no global pass inferred |
| BR-05 | US-22 + relevant owner stories — Arin / Arin/Atiksh; see cases register | TC-FR06-01; TC-NFR03-01 | See per-case local vs pending status; no global pass inferred |
| BR-06 | US-22 + relevant owner stories — Atiksh; see cases register | TC-FR09-01 | See per-case local vs pending status; no global pass inferred |
| BR-07 | US-22 + relevant owner stories — Arin; see cases register | TC-FR10-01 | See per-case local vs pending status; no global pass inferred |


## Acceptance gates not represented as passing evidence

US-18 still requires all-owner shared schema/permission approval, actual shared-model migration integration and PostgreSQL checks. US-22 still requires full-team/CI/cross-browser/load/release evidence. Arin code alone cannot close those stories. After peer review, record actual board links, commit SHA, PR, CI run and reviewer here; do not insert placeholder links that look real.
