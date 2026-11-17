# Unit, API and component test report

Generated 2026-11-17T06:56:42.800603+00:00 from recorded artifacts.
Backend execution: 2026-11-17T06:49:25.602301+00:00; frontend: 2026-11-17T06:50:01.985933+00:00.
Source HEAD: `7b7d4c436c88b03f12ac5d07039f031000ca99ae` plus uncommitted test/config/script changes.
Local synthetic PostgreSQL only. No production data changes, live payments, commit or push.
Each command's own timestamp/exit is preserved in [commands](raw/commands.md).
Independent human review remains pending. Coverage success does not override failing tests.

## Recorded totals

Backend: **175 executions; 172 passed, 3 failed, 0 not run**.
Original regressions: 116, 116 passed.
Supporting priority units: 16. Priority API workflows: 14.
Added branch-focused Python executions: 29; 29 passed.
Jest/RTL: **105 executions; 105 passed, 0 failed** in 21 suites.
Backend subtests are assertions within parent executions; do not count them again.

## What the expanded tests cover

Python: unsafe account transitions and assignments, active/legacy scope adapters,
staff directories, content edits, mess capacity and coupon reassignment, final complaint
states, attendance boundaries, malformed provider orders/captured payloads, reference
mismatches, local seed safety/idempotence, error envelopes and settings validation.
Real PostgreSQL fixtures exercise database behavior; external provider I/O is mocked.
Configuration tests use temporary files and isolated environment/module boundaries.
These are unit/API/integration tests, not all pure units.

Frontend: secure transport and pagination; shared form coercion/errors; role navigation
and keyboard focus; account/content/settings edits; leave review and filtering;
attendance location errors; deviation recording/deactivation; laundry policy/receipt/
collection; mess options, assignment and coupons; simulated/provider-adapter UI errors.
Transport/navigation are mocked in component tests. The retained unregistered legacy
LeaveWorkspace is tested with its unavailable old UI adapter mocked; this does not
claim it is an active integrated route. No implemented source was excluded for coverage.

## Observed failures

- `test_P13_duplicate_payment_callbacks_and_submissions`: AssertionError: 2 != 1 : Repeated pending initiation created separate PaymentAttempt rows
- `test_P14_deviation_total_and_duplicate_prevention`: AssertionError: 2 != 1 : Identical repeated deviation submission created a second record
- `test_direct_socket_timeout_is_validation_error`: TimeoutError: Synthetic direct socket timeout

The replay assertions distinguish requested retry invariants from legitimate separate
events. Payment initiation/deviation event identity needs owner policy review.
Duplicate successful callbacks and initial deviation calculations still pass.
No application behavior was changed or existing assertion skipped/weakened.

## Executed backend cases

| Executed node | Outcome |
|---|---|
| `tests.test_branch_workflows.StaffBranches.test_assignment_validation_and_identity_without_warden` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_choice_directories_enforce_roles_and_assignments` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_director_creates_converts_and_rejects_conflicting_users` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_director_rejects_unsafe_account_transitions` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_mess_option_edits_capacity_and_coupon_reassignment` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_resolved_complaint_cannot_be_reassigned_or_reopened` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_staff_content_edits_and_empty_study_fallback` | Passed |
| `tests.test_branch_workflows.StaffBranches.test_staff_lists_and_overview_scopes` | Passed |
| `tests.test_branch_workflows.WorkflowScopes.test_active_and_legacy_scope_adapters_agree` | Passed |
| `tests.test_branch_workflows.WorkflowScopes.test_boundary_rejections_do_not_create_accepted_attendance` | Passed |
| `tests.test_branch_workflows.WorkflowScopes.test_service_validation_and_missing_staff_filter` | Passed |
| `tests.test_branch_workflows.ProviderBranches.test_disabled_checkout_and_missing_test_credentials` | Passed |
| `tests.test_branch_workflows.ProviderBranches.test_malformed_provider_orders_and_captured_payloads` | Passed |
| `tests.test_branch_workflows.ProviderBranches.test_provider_json_transport_and_reference_mismatch` | Passed |
| `tests.test_branch_workflows.test_seed_commands_require_local_mode_and_preserve_existing_passwords` | Passed |
| `tests.test_health.test_health_checks_postgresql` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P01_valid_login` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P02_invalid_login` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P03_student_denied_staff_and_admin_actions` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P04_valid_leave` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P05_invalid_leave` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P06_warden_approves_and_rejects` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P07_valid_attendance` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P08_outside_boundary_rejected` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P09_repeated_attendance_prevented` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P10_complaint_creation_and_ownership` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P11_unauthorized_complaint_update` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P12_payment_success_failure_timeout_retry` | Passed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P13_duplicate_payment_callbacks_and_submissions` | Failed |
| `tests.test_priority_acceptance.PriorityAcceptanceTests.test_P14_deviation_total_and_duplicate_prevention` | Failed |
| `apps.accounts.tests.test_api.AuthenticationTests.test_anonymous_apis_require_login` | Passed |
| `apps.accounts.tests.test_api.AuthenticationTests.test_deactivation_revokes_existing_session` | Passed |
| `apps.accounts.tests.test_api.AuthenticationTests.test_invalid_login_is_generic` | Passed |
| `apps.accounts.tests.test_api.AuthenticationTests.test_login_logout_real_session_and_cache` | Passed |
| `apps.accounts.tests.test_api.AuthenticationTests.test_login_requires_csrf_even_when_anonymous` | Passed |
| `apps.accounts.tests.test_api.AuthenticationTests.test_session_write_requires_csrf` | Passed |
| `apps.accounts.tests.test_api.ProfileTests.test_invalid_phone_rejected` | Passed |
| `apps.accounts.tests.test_api.ProfileTests.test_phone_update_persists` | Passed |
| `apps.accounts.tests.test_api.ProfileTests.test_protected_profile_fields_rejected` | Passed |
| `apps.accounts.tests.test_api.ProfileTests.test_staff_cannot_edit_student_profile` | Passed |
| `apps.accounts.tests.test_api.LoginRateTests.test_csrf_bootstrap_does_not_consume_login_rate_bucket` | Passed |
| `apps.accounts.tests.test_services.AccountModelTests.test_identity_omits_secrets` | Passed |
| `apps.accounts.tests.test_services.AccountModelTests.test_inactive_chief_can_coexist` | Passed |
| `apps.accounts.tests.test_services.AccountModelTests.test_single_active_chief_database_constraint` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_cannot_create_privileged_roles_or_spoof_assignments` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_cannot_deactivate_self_or_assigned_warden` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_choice_directory_scopes_students` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_director_can_create_each_service_staff_type` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_director_creates_student_with_assignment` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_invalid_assignment_rejected` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_password_validation_and_duplicate_username` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_reports_counts_use_source_rows` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_service_staff_overview_does_not_expose_fee_or_leave_counts` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_settings_allowlist_and_audit` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_student_cannot_manage_accounts_or_reports` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_warden_and_chief_overview_excludes_other_domains` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_warden_cannot_create_operational_accounts` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_warden_cannot_list_or_edit_accounts` | Passed |
| `apps.director_dashboard.tests.test_api.DirectorTests.test_warden_overview_scopes_active_students` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_authorized_director_updates_study` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_cannot_collect_before_ready` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_invalid_study_status` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_manual_allocation_disabled_for_every_role` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_number_modulo_schedule_and_stability` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_only_laundry_staff_changes_policy` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_policy_change_affects_future_only` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_positive_whole_item_count` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_ready_then_collection_idempotent` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_receive_without_manual_allocation` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_selected_turnaround_and_invalid_bounds` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_student_cannot_transition_or_read_other_batches` | Passed |
| `apps.facilities.tests.test_api.FacilitiesTests.test_student_schedule_is_owned_and_warden_is_denied` | Passed |
| `apps.facilities.tests.test_api.PdfPermissionTests.test_warden_has_no_laundry_or_study_management_permission` | Passed |
| `apps.information.tests.test_api.InformationTests.test_authorized_staff_create_and_edit` | Passed |
| `apps.information.tests.test_api.InformationTests.test_empty_title_rejected` | Passed |
| `apps.information.tests.test_api.InformationTests.test_invalid_notice_dates_rejected` | Passed |
| `apps.information.tests.test_api.InformationTests.test_rule_deactivation_retains_id` | Passed |
| `apps.information.tests.test_api.InformationTests.test_rule_negative_weight_rejected` | Passed |
| `apps.information.tests.test_api.InformationTests.test_student_cannot_publish` | Passed |
| `apps.information.tests.test_api.InformationTests.test_student_reads_only_active_current_notices` | Passed |
| `apps.information.tests.test_api.InformationTests.test_warden_cannot_publish_or_rewrite_rules` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_anonymous_and_nonworkflow_roles_are_denied` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_attendance_submission_does_not_echo_coordinates` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_chief_reads_only_escalated_or_self_finalized_requests` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_choices_are_scoped_and_staff_only` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_create_leave_and_private_cache_headers` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_deviation_permissions_and_server_owned_weight` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_deviation_snapshot_total_and_retained_deactivation` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_invalid_or_unassigned_attendance_is_rejected` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_leave_scope_and_decision_scope` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_pagination_is_bounded` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_protected_fields_and_bad_dates_are_rejected` | Passed |
| `apps.leave_attendance.tests.test_api.ApiTests.test_unknown_and_malformed_identifiers` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_database_prevents_second_acceptance` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_deviation_snapshot_and_deactivation_history` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_escalation_then_chief_finalization` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_final_decision_is_immutable` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_future_location_sample_outside_tolerance_is_rejected` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_leave_submission_records_actor_and_assignment` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_location_boundaries` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_one_accepted_attendance_and_rejected_retry` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_only_student_submits` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_raw_student_sample_is_not_persisted` | Passed |
| `apps.leave_attendance.tests.test_services.ServiceTests.test_warden_cannot_finalize_escalated_request` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_full_progress_and_history_no_revert` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_invalid_category_and_empty_description` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_only_director_assigns_active_maintenance` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_room_and_student_derived_on_server` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_spoofed_student_rejected` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_student_scope_in_list_and_detail` | Passed |
| `apps.student_services.tests.test_api.ComplaintTests.test_unassigned_staff_has_no_access` | Passed |
| `apps.student_services.tests.test_api.MessTests.test_blank_coupon_rejected` | Passed |
| `apps.student_services.tests.test_api.MessTests.test_current_coupon_filter_and_owner_scope` | Passed |
| `apps.student_services.tests.test_api.MessTests.test_invalid_coupon_range` | Passed |
| `apps.student_services.tests.test_api.MessTests.test_mess_staff_assigns_personal_allocation` | Passed |
| `apps.student_services.tests.test_api.MessTests.test_students_cannot_assign` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_caller_cannot_supply_amount` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_cannot_pay_others_fee` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_failed_attempt_cannot_silently_become_success` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_failure_and_cancellation_keep_fee_unpaid` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_payment_history_is_owner_scoped` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_provider_mismatched_amount_cannot_mark_paid` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_provider_success_requires_valid_signature_and_capture` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_simulation_disabled_without_opt_in` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_simulation_explicit_label_and_server_amount` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_simulation_not_allowed_outside_local` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_success_is_idempotent_and_marks_paid` | Passed |
| `apps.student_services.tests.test_payments.PaymentTests.test_unverified_attempt_stays_pending` | Passed |
| `apps.student_services.tests.test_stp.STPAuditTests.test_TC_FR07_01_prior_history_cannot_be_rewritten` | Passed |
| `apps.student_services.tests.test_stp.STPAuditTests.test_TC_SEC06_01_payment_credentials_are_rejected_and_not_stored` | Passed |
| `apps.student_services.tests.test_stp.STPMessPermissionTests.test_TC_FR07_01_warden_cannot_read_or_assign_complaints` | Passed |
| `apps.student_services.tests.test_stp.STPMessPermissionTests.test_TC_FR08_01_change_preserves_history_and_releases_capacity` | Passed |
| `apps.student_services.tests.test_stp.STPMessPermissionTests.test_TC_FR08_01_enrolled_name_and_capacity_are_protected` | Passed |
| `apps.student_services.tests.test_stp.STPMessPermissionTests.test_TC_FR08_01_only_mess_staff_publish_catalogue` | Passed |
| `apps.student_services.tests.test_stp.STPMessPermissionTests.test_TC_FR08_01_staff_allocation_retry_and_history` | Passed |
| `apps.student_services.tests.test_stp.STPMessPermissionTests.test_TC_FR08_01_students_and_unrelated_staff_cannot_write` | Passed |
| `apps.leave_attendance.tests.test_concurrency.ConcurrentTests.test_concurrent_attendance_accepts_once` | Passed |
| `apps.leave_attendance.tests.test_concurrency.ConcurrentTests.test_concurrent_leave_finalizes_once` | Passed |
| `apps.leave_attendance.tests.test_services.ConcurrentTests.test_concurrent_attendance_accepts_once` | Passed |
| `apps.leave_attendance.tests.test_services.ConcurrentTests.test_concurrent_leave_finalizes_once` | Passed |
| `apps.student_services.tests.test_concurrency.MessCapacityRace.test_last_place_cannot_be_double_booked` | Passed |
| `apps.student_services.tests.test_stp.STPPaymentRaceTests.test_TC_FR09_01_two_attempts_cannot_both_pay_one_fee` | Passed |
| `apps.student_services.tests.test_stp.STPPaymentRaceTests.test_TC_NFR03_01_concurrent_success_callbacks_are_idempotent` | Passed |
| `tests.test_branch_workflows.test_local_settings_create_or_reuse_only_a_local_key[True]` | Passed |
| `tests.test_branch_workflows.test_local_settings_create_or_reuse_only_a_local_key[False]` | Passed |
| `tests.test_branch_workflows.test_serializers_reject_nonobjects_and_invalid_windows` | Passed |
| `tests.test_branch_workflows.test_error_envelope_handles_unknown_and_list_errors[config.exceptions]` | Passed |
| `tests.test_branch_workflows.test_error_envelope_handles_unknown_and_list_errors[apps.leave_attendance.errors]` | Passed |
| `tests.test_branch_workflows.test_database_settings_validate_urls_without_connecting[postgresql://test@localhost/test-0-postgresql]` | Passed |
| `tests.test_branch_workflows.test_database_settings_validate_urls_without_connecting[-1-sqlite3]` | Passed |
| `tests.test_branch_workflows.test_database_settings_validate_urls_without_connecting[https://localhost/db-0-None]` | Passed |
| `tests.test_branch_workflows.test_database_settings_validate_urls_without_connecting[postgresql://localhost/db?sslmode=wrong-0-None]` | Passed |
| `tests.test_branch_workflows.test_production_settings_reject_insecure_configuration[-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-origins0-require-hostnames]` | Passed |
| `tests.test_branch_workflows.test_production_settings_reject_insecure_configuration[example.invalid-short-origins1-require-secret]` | Passed |
| `tests.test_branch_workflows.test_production_settings_reject_insecure_configuration[example.invalid-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-origins2-require-HTTPS]` | Passed |
| `tests.test_branch_workflows.test_production_settings_reject_insecure_configuration[example.invalid-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-origins3-prefer-encrypted]` | Passed |
| `tests.test_branch_workflows.test_production_settings_reject_insecure_configuration[example.invalid-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-origins4-require-None]` | Passed |
| `tests.test_health.test_database_failure_is_unavailable_without_details` | Passed |
| `tests.test_health.test_health_rejects_writes_without_querying_database` | Passed |
| `tests.test_priority_unit.test_attendance_boundary_decisions[change0-expected0]` | Passed |
| `tests.test_priority_unit.test_attendance_boundary_decisions[change1-expected1]` | Passed |
| `tests.test_priority_unit.test_attendance_boundary_decisions[change2-expected2]` | Passed |
| `tests.test_priority_unit.test_attendance_boundary_decisions[change3-expected3]` | Passed |
| `tests.test_priority_unit.test_attendance_boundary_decisions[change4-expected4]` | Passed |
| `tests.test_priority_unit.test_haversine_distance_identity_and_scale` | Passed |
| `tests.test_priority_unit.test_leave_input_validation[body0-True]` | Passed |
| `tests.test_priority_unit.test_leave_input_validation[body1-False]` | Passed |
| `tests.test_priority_unit.test_leave_input_validation[body2-False]` | Passed |
| `tests.test_priority_unit.test_leave_input_validation[body3-False]` | Passed |
| `tests.test_priority_unit.test_active_role_permission[DIRECTOR-True-True-True]` | Passed |
| `tests.test_priority_unit.test_active_role_permission[STUDENT-True-True-False]` | Passed |
| `tests.test_priority_unit.test_active_role_permission[DIRECTOR-False-True-False]` | Passed |
| `tests.test_priority_unit.test_active_role_permission[DIRECTOR-True-False-False]` | Passed |
| `tests.test_priority_unit.test_wrapped_provider_timeout_is_validation_error` | Passed |
| `tests.test_priority_unit.test_direct_socket_timeout_is_validation_error` | Failed |

## Executed component cases

- WARDEN leave detail preserves review permissions: passed
- CHIEF_WARDEN leave detail preserves review permissions: passed
- STUDENT leave detail preserves review permissions: passed
- leave list follows pagination, searches and filters: passed
- leave write/review/read failures remain visible: passed
- leave history fallbacks and final state have no review action: passed
- leave detail without optional names renders safe fallbacks: passed
- WARDEN attendance shows sessions and retained history: passed
- CHIEF_WARDEN attendance shows sessions and retained history: passed
- STUDENT attendance shows sessions and retained history: passed
- attendance form validates dates, posts numeric policy and shows server errors: passed
- one-time attendance handles absent and denied location, then retries: passed
- attendance displays identity failures: passed
- attendance displays records failures: passed
- Warden records/deactivates deviations, retaining failed write feedback: passed
- deviation panel reports identity read failures: passed
- deviation panel reports choices read failures: passed
- deviation panel reports totals read failures: passed
- mess staff create/edit menu, assign student and issue/toggle coupons: passed
- populated STUDENT mess view preserves read-only scope: passed
- populated DIRECTOR mess view preserves read-only scope: passed
- empty MESS_STAFF mess shows useful states: passed
- empty STUDENT mess shows useful states: passed
- Director creates a due and reads mixed payment modes: passed
- local fee simulation records Success: passed
- local fee simulation records Failed: passed
- local fee simulation records Cancelled: passed
- fee simulation and initiation failures stay visible: passed
- sandbox adapter verifies, reports failure and handles dismissal without live I/O: passed
- checkout script failure is recoverable and loading success opens adapter: passed
- Director assigns and progresses a complaint: passed
- DIRECTOR complaint detail in Open state: passed
- MAINTENANCE_STAFF complaint detail in In Progress state: passed
- DIRECTOR complaint detail in Resolved state: passed
- STUDENT complaint detail in Open state: passed
- student complaint form, list filters and empty search: passed
- Laundry Staff saves future policy and receives a batch: passed
- laundry transitions confirm collection, cancel safely and expose failure: passed
- STUDENT laundry record view handles all statuses: passed
- DIRECTOR laundry record view handles all statuses: passed
- laundry timetable filters populated schedules: passed
- resource form serializes numbers, checkboxes, nullable and optional fields: passed
- resource form preserves edit values and reports rejected writes: passed
- shared presentation handles histories, optional error fields and dialog cancellation: passed
- shell renders the STUDENT menu and signs out: passed
- shell renders the WARDEN menu and signs out: passed
- shell renders the CHIEF_WARDEN menu and signs out: passed
- shell renders the DIRECTOR menu and signs out: passed
- shell renders the LAUNDRY_STAFF menu and signs out: passed
- shell renders the MESS_STAFF menu and signs out: passed
- shell renders the MAINTENANCE_STAFF menu and signs out: passed
- shell renders the CONTENT_STAFF menu and signs out: passed
- shell renders the UNKNOWN menu and signs out: passed
- mobile navigation restores focus, traps Tab, closes and responds to media changes: passed
- shell handles session status 401: passed
- shell handles session status 403: passed
- shell handles session status 500: passed
- resource ignores responses after unmount and exposes loading failures: passed
- logout errors stay visible: passed
- confirmation dialog forwards the user decision: passed
- director creates student and service accounts, searches and edits: passed
- account editing supports nonstudent rows and closes dialogs: passed
- non-director account view has no creation controls: passed
- staff publishes, edits timed/untimed content and creates rules: passed
- settings and study editor save backend values: passed
- staff panel exposes failed reads 0: passed
- staff panel exposes failed reads 1: passed
- Director summary renders nonempty attendance sessions: passed
- student submits validated leave without caller-owned identity fields: passed
- client rejects reversed dates before an API write: passed
- legacy role STUDENT gates its workflow: passed
- legacy role WARDEN gates its workflow: passed
- legacy role CHIEF_WARDEN gates its workflow: passed
- legacy role DIRECTOR gates its workflow: passed
- legacy role undefined gates its workflow: passed
- legacy leave form validates reversed dates and exposes write/retry outcomes: passed
- legacy WARDEN finalizes Pending with retry feedback: passed
- legacy CHIEF_WARDEN finalizes Escalated with retry feedback: passed
- legacy detail refreshes after a decision and ignores late responses: passed
- legacy empty and loading states distinguish availability: passed
- profile protects identity and saves only the phone field: passed
- login sends session credentials through CSRF transport: passed
- invalid login displays backend error: passed
- sign-in fallback never submits credentials in a URL: passed
- TC-FR08-01: student reads assigned mess and coupons without write controls: passed
- information tabs display real API notices and rules: passed
- frontend: incomplete login stays invalid and does not send a request: passed
- frontend: pending sign-in disables repeat submission, then navigates on success: passed
- frontend: transport failure is visible and permits a later retry: passed
- study room is read-only and shows the current server status: passed
- student submits category and description, never room or identity: passed
- test checkout displays explicit simulation label and takes no payment credentials: passed
- director report displays zero counts without inventing records: passed
- student sees automatic weekday and cannot change policy or collect batches: passed
- health returns uncached JSON: passed
- domain transport enforces origin, CSRF and JSON errors 0: passed
- domain transport enforces origin, CSRF and JSON errors 1: passed
- domain transport enforces origin, CSRF and JSON errors 2: passed
- shared transport, failures and pagination keep credentials same-origin: passed
- domain endpoint helpers encode identifiers and optional filters: passed
- formatters and role menus handle defaults and all navigation categories: passed
- geolocation is requested only after the explicit submit click: passed
- shared components expose accessible labels, status and table headers: passed
- disabled button prevents duplicate actions: passed
- student receives read-only history and server-calculated active total: passed

[JUnit](raw/backend-junit.xml), [Jest JSON](raw/frontend-results.json),
[backend log](raw/backend.log), [frontend log](raw/frontend.log),
[raw failures](raw/observed-failures.json), [coverage analysis](code_branch_coverage_analysis.md).
