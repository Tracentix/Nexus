# Nexus: Smart Health & Fitness Tracker

Nexus is a browser-based health and fitness tracker built for CSAI 203, Introduction to Software Engineering (Fall 2026), at Zewail City of Science, Technology and Innovation.

Members log their workouts and meals, set a daily calorie target and fitness goals, and follow their progress over time. They can also write workout routines and share them with other members. Administrators look after the food catalogue, member accounts and reported routines.

## Team

| Name | University ID |
|---|---|
| Ahmed Ebrahim | 202402322 |
| Mostafa Harhash | 202401133 |
| Yehia Aly | 202400641 |
| Abdelrhman Tarek | 202402412 |

Team representative: Mostafa Harhash (202401133)

Team number: not assigned yet

## Documents

- [Phase 2 SRS](docs/Nexus_SRS_Phase2_202401133.pdf): version 0.1 draft, submitted 29 October 2026

## Users

| User | What they can do |
|---|---|
| Guest | Register, sign in, or request account recovery |
| Member | Log workouts and meals, manage goals, measurements and routines, choose which routines to share |
| Administrator | Maintain food entries, enable or disable accounts, review reports and hide or restore shared routines |

## Features

The SRS defines 24 functional requirements (FR-01 to FR-24) and 14 use cases (UC-01 to UC-14). In short:

- **Accounts:** registration, sign in and sign out, password change and reset, profile editing (FR-01 to FR-04)
- **Workouts:** record, edit and delete workouts, history filtered by date or workout type (FR-05 to FR-07)
- **Meals:** search the food catalogue and log meals by serving quantity, with calories calculated from the catalogue (FR-08 to FR-10)
- **Goals:** daily calorie target and fitness goals that can be active, completed or inactive (FR-11 to FR-12)
- **Progress:** daily summary, progress charts and body measurements (FR-13 to FR-15)
- **Routines:** create, edit, publish or unpublish, browse and save shared routines (FR-16 to FR-20)
- **Moderation:** members report routines and administrators review them (FR-21, FR-24)
- **Administration:** food catalogue and member account management (FR-22 to FR-23)

## Quality Targets

The SRS also lists seven non-functional requirements. The main ones:

- 95th percentile response time of 3 seconds or less with 20 concurrent users (NFR-01)
- Passwords stored only as salted hashes, and ownership and role checks done on the server (NFR-02)
- Works with the keyboard and at 320px, 768px and 1366px widths in current Chrome, Firefox and Edge (NFR-04, NFR-05)
- Personal records are private by default; a routine is visible only when published and not hidden (NFR-06)

## Architecture

The course requires the Model-View-Controller (MVC) pattern. We haven't picked the framework or database yet. We'll choose them from the instructor's approved technology list before Phase 3.

The domain model covers User, Profile, WorkoutEntry, MealEntry, FoodItem, FitnessGoal, BodyMeasurement, WorkoutRoutine, SavedRoutine and RoutineReport.

## Out of Scope

- Wearable devices and automatic data collection (all data is entered manually)
- External nutrition APIs (we supply the food catalogue ourselves)
- Medical diagnosis or treatment advice

Calorie and workout energy values are estimates only, not medical advice.

## Repository Structure

```
docs/        SRS and other project documents
src/         Application source code
tests/       Test cases and test plans
deployment/  Deployment configuration and setup notes
```

## Status

We're in Phase 2 (Software Requirements Specification). There's no application code yet.

Before Phase 3, we still need to:

- confirm the team number with the course staff
- choose the frontend, backend and database
- check whether we can send password-reset emails
- decide on deployment, starter food data and the scope of account deletion
