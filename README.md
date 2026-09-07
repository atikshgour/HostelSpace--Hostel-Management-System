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
