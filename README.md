# HostelSpace

## Hostel Management System

HostelSpace is a browser-based hostel management system developed for the **UE24CS341A - Software Engineering** course at **PES University, Bangalore**.

HostelSpace is a simple web-based hostel management system for students and hostel staff. At present, many hostel activities are handled through notice boards, paper forms, registers, messages, and repeated visits to the hostel office.
Information is spread across different places, so students may need to ask several people before they receive an update. Staff also have to check different records to answer common questions.

HostelSpace brings these activities into one portal. A student can sign in, view hostel notices and rules, check whether the study room is open, see the assigned laundry day, track clothes given and collected, apply for leave, submit attendance, raise a maintenance complaint, view mess details, pay hostel fees, and check deviation-weightage records. Students will see only their own records and the services available to them.

Hostel staff will use the same system according to their roles. Wardens will process leave, attendance, and discipline records. The Chief Warden will supervise the wardens and handle important cases. The Hostel Director will have overall control of hostel information and authorized users. Laundry, mess, and maintenance staff will update only the records related to their work. The project keeps every feature direct and limited so that the team can build, test, and explain the complete system within the course schedule.

## Project Information

| Item | Details |
|---|---|
| Project Name | HostelSpace |
| Project | Hostel Management System |
| Course | UE24CS341A - Software Engineering |
| University | PES University, Bangalore |
| Department | Computer Science and Engineering |
| Team | Team 11 |
| Methodology | Agile |
| Version | 1.0 |
| Development | Git and GitHub |
| Project Planning | Jira |

## Project Board

| Sprint | ID | User story | Owner | Req | Test | Est | Acceptance |
|---|---|---|---|---|---|---:|---|
| 1 | US-20 | As a developer, I want the monorepo, Docker Compose (PostgreSQL 16), and a GitHub Actions CI (lint, security scan, tests, build) so every PR is verified | ATIKSH | NFR-05 | TC-CICD-01 | 6 | Compose starts frontend, API and DB; PRs run all checks with no secrets; failing test blocks merge; main is protected |
| 1 | US-01 | As a user, I want to sign in and out with my role and see the correct dashboard so I access only permitted pages | ANVI | FR-01, SEC-01, SEC-02 | TC-FR01-01, TC-FR01-02 | 9 | Invalid/inactive login denied without revealing which field failed; logout invalidates session; CSRF enforced; role/ownership checks on every protected request |
| 1 | US-02 | As a student, I want to view my profile and update my phone number only | ANVI | FR-01, SEC-03 | TC-FR01-01 | 3 | One profile per student; unique SRN; other fields return 403 |
| 1 | US-04 | As the Hostel Director, I want to create users, activate/deactivate them and assign roles (reports come in Sprint 5) | ANVI | FR-11, BR-01 | TC-FR11-01 | 4 | Director-only; second active Chief Warden rejected (409) |
| 1 | US-21 | As any user, I want clear labelled forms, field errors and status/empty states | ANVI | NFR-02 | TC-NFR02-01 | 2 | Every field labelled; errors actionable; empty states say "No records" or "Not assigned" |
| 2 | US-03 | As staff, I want to manage notices, contacts and rules, and as a student, I want to see only active ones | ANVI | FR-02 | TC-FR02-01 | 5 | Invalid dates rejected; student cannot write; referenced rules deactivated, not deleted |
| 2 | US-09 | As authorized staff, I want to set the study room Open/Closed with an optional message so students see its status (no booking) | ARYAN | FR-03, BR-02 | TC-FR03-01 | 3 | Latest status shown; unauthorized write 403; no booking action in UI/API |
| 2 | US-10 | As Laundry Staff, I want to assign a laundry day so the student sees it (students cannot choose or change it) | ARYAN | FR-04, BR-03 | TC-FR04-01 | 4 | One current allocation per student; student write 403; "Not assigned" empty state |
| 3 | US-11 | As Laundry Staff, I want to record clothes received and collected so the handover is tracked | ARYAN | FR-04, BR-04 | TC-FR04-01 | 4 | Positive item count; collection blocked without earlier Received record; repeat collect idempotent |
| 3 | US-12 | As a student, I want to see my laundry status and history (read-only) | ARYAN | FR-04, SEC-03 | TC-FR04-01 | 2 | Own records only; cross-student read denied |
| 3 | US-05 | As a student, I want to submit leave dates and a reason and track the status | ARIN | FR-05 | TC-FR05-01 | 6 | Valid request gets ID and Pending; end < start rejected; each student has an assigned warden |
| 3 | US-06 | As a warden, I want to approve, reject or escalate my assigned students' leave, and as Chief Warden, to decide escalations | ARIN | FR-05, BR-01 | TC-FR05-01 | 8 | Only the assigned warden decides; Chief decides escalated only; final decision immutable (409); actor/time stored |

Priority:
- **High:** FR-01, FR-05, and security-related rows
- **Medium:** All remaining rows

## Team Members

| Name | USN | Primary Responsibilities |
|---|---|---|
| Anvi Srinivas | PES1UG24CS076 | Student profile, notices, information, contacts, and hostel rules |
| Arin Singh | PES1UG24CS079 | Leave, location-verified attendance, and deviation records |
| Aryan Singh | PES1UG24CS086 | Study-room status, laundry allocation, handover, and collection |
| Atiksh Gour | PES1UG24CS096 | Maintenance complaints, mess and coupons, and hostel fee payment |

## Project Scope

HostelSpace covers the following first-version functionality:

- Role-based sign-in and student profile access
- Hostel notices, contacts, information, and rules
- Study-room open or closed status
- Assigned laundry-day tracking
- Laundry handover and collection tracking
- Leave management
- Location-verified attendance submission
- Maintenance complaints
- Mess allocation and coupons
- Hostel fee payment records
- Deviation-weightage records
- Authorized staff updates and Hostel Director reports

Students can view hostel notices and rules, check the study-room status, see their assigned laundry day, track clothes, apply for leave, submit attendance, raise maintenance complaints, view mess details, pay hostel fees, and review their deviation-weightage records. Students see only their own records and the services available to them.

### Out of Scope

The first version does not include:

- Study-room booking
- Student selection of laundry days
- Continuous location tracking
- Full hostel accounting
- Biometric devices
- Inventory management
- Native mobile application

## User Roles

The system supports the following user classes:

- **Student** - Uses student services and views personal records
- **Warden** - Reviews leave, views attendance, and records deviations
- **Chief Warden** - Supervises wardens and handles escalated matters
- **Hostel Director** - Controls authorized users, information, settings, and reports
- **Maintenance Staff** - Updates assigned maintenance complaints
- **Mess Staff** - Maintains mess allocation and coupons
- **Laundry Staff** - Maintains assigned laundry days and handover or collection records

Staff members use the system according to their roles. Each staff role updates only the records related to its work, while wardens, the Chief Warden, and the Hostel Director handle progressively broader oversight and authorization responsibilities.

## Technology Stack

- **Frontend:** Next.js
- **Languages:** JavaScript, HTML, CSS
- **Database:** SQL
- **Authentication:** Role-based authentication
- **Version Control:** Git and GitHub
- **Project Management:** Jira

## System Architecture

At a high level, HostelSpace follows this structure:

```text
		    +------------------+
		    |      Users       |
		    | Student / Staff  |
		    +--------+---------+
			     |
			     v
		    +------------------+
		    |     Browser      |
		    +--------+---------+
			     |
			     v
		    +------------------+
		    |     Next.js      |
		    |  Web Application |
		    +--------+---------+
			     |
	      +--------------+--------------+
	      |                             |
	      v                             v
      +------------------+        +------------------+
      | Authentication & |        |    Application   |
      | Role Management  |        |     Services     |
      +------------------+        +--------+---------+
					   |
					   v
				  +------------------+
				  |    SQL Database  |
				  +------------------+
```
## Maintenance Complaints

Students can submit maintenance complaints, and authorized staff can update their status.
