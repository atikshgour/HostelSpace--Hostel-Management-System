# HostelSpace

## Hostel Management System

HostelSpace is a browser-based Hostel Management System developed as part of the **UE24CS341A – Software Engineering** course at **PES University, Bangalore**.

The system is designed to provide a centralized platform for managing student hostel services, staff workflows, attendance, leave, maintenance, mess services, laundry, fee payments, and hostel rule deviations.

---

## Project Information

| Item | Details |
|---|---|
| Project Name | HostelSpace |
| Project | Hostel Management System |
| Course | UE24CS341A – Software Engineering |
| University | PES University, Bangalore |
| Department | Computer Science and Engineering |
| Team | Team 11 |
| Methodology | Agile |
| Version | 1.0 |
| Development | Git & GitHub |
| Project Planning | Jira |

---

## Team Members

| Name | USN | Primary Responsibilities |
|---|---|---|
| Anvi Srinivas | PES1UG24CS076 | Student profile, notices, information, contacts, hostel rules |
| Arin Singh | PES1UG24CS079 | Leave, location-verified attendance, deviation records |
| Aryan Singh | PES1UG24CS086 | Study-room status, laundry allocation, handover and collection |
| Atiksh Gour | PES1UG24CS096 | Maintenance complaints, mess/coupons, hostel fee payment |

---

## Project Scope

HostelSpace covers the following first-version functionality:

- Role-based sign-in and student profile access
- Hostel notices, contacts, information, and rules
- Study-room Open/Closed status
- Assigned laundry-day tracking
- Leave management
- Location-verified attendance
- Maintenance complaints
- Mess allocation and coupons
- Hostel fee payment records
- Deviation-weightage records
- Authorized staff updates and Hostel Director reports

### Out of Scope

The first version does **not** include:

- Study-room booking
- Student selection of laundry days
- Continuous location tracking
- Full hostel accounting
- Biometric devices
- Inventory management
- Native mobile application

---

## User Roles

The system supports the following user classes:

- **Student** — Uses student services and views personal records
- **Warden** — Reviews leave, views attendance, and records deviations
- **Chief Warden** — Supervises wardens and handles escalated matters
- **Hostel Director** — Controls authorized users, information, settings, and reports
- **Maintenance Staff** — Updates assigned maintenance complaints
- **Mess Staff** — Maintains mess allocation and coupons
- **Laundry Staff** — Maintains assigned laundry days and handover/collection records

---

## Technology Stack

- **Frontend:** Next.js
- **Languages:** JavaScript, HTML, CSS
- **Database:** SQL
- **Authentication:** Role-based authentication
- **Version Control:** Git & GitHub
- **Project Management:** Jira

---

## System Architecture

At a high level, HostelSpace follows this structure:

```text
                    ┌──────────────────┐
                    │      Users       │
                    │ Student / Staff  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Browser      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Next.js      │
                    │  Web Application │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌──────────────────┐        ┌──────────────────┐
      │ Authentication & │        │    Application   │
      │ Role Management  │        │     Services     │
      └──────────────────┘        └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │    SQL Database  │
                                  └──────────────────┘
