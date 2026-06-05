# Optometry Analytics — Synthetic Patient Database

## Overview
A synthetic optometry patient database generator that produces realistic,
relational clinical and administrative data modelled on what a real
optometric practice would collect. Designed for SQL querying, data pipeline
development, and health data analysis practice within a clinical context.

## Motivation
Publicly available healthcare datasets are rare, heavily anonymised, and
rarely reflect the complexity of real clinical data. This project generates
a controlled but realistic alternative — suitable for practising data
analysis without privacy concerns, while preserving the domain-specific
structure a health analyst would encounter in practice.

## Database Schema

### Lookup Tables
| Table | Description |
|---|---|
| `gender_types` | Gender identity options |
| `visit_types` | Appointment types (e.g. Routine, Emergency, Referral) |
| `referral_destinations` | Referral locations (e.g. Ophthalmology, GP, Low Vision) |
| `diagnoses` | ICD-10 coded ocular diagnoses |

### Core Tables

**`optometrists`**
| Field | Description |
|---|---|
| `optom_id` | Primary key |
| `first_name`, `last_name` | Practitioner name |
| `ahpra_num` | Simulated AHPRA registration number |
| `practice_location` | Clinic location |

**`patients`**
| Field | Description |
|---|---|
| `patient_id` | Primary key |
| `first_name`, `last_name` | Patient name |
| `date_of_birth` | DOB |
| `gender_id` | Foreign key → gender_types |
| `email`, `phone` | Contact details |
| `suburb`, `postcode` | Address |
| `medicare_no` | Simulated Medicare numbers |
| `created_at` | Record creation timestamp |

**`appointments`**
| Field | Description |
|---|---|
| `appointment_id` | Primary key |
| `patient_id`, `optom_id` | Foreign key → patients, optometrists |
| `visit_id` | Foreign key → visit_types |
| `appointment_date` | Date of consultation |
| `chief_complaint` | Reason for visit |
| `va_r_unaided`, `va_l_unaided` | Uncorrected visual acuities (Snellen denominator) |
| `va_r_aided`, `va_l_aided` | Best corrected visual acuities (Snellen denominator) |
| `iop_r`, `iop_l` | Intraocular pressures (mmHg) |
| `next_recall_months` | Recommended follow-up interval (months) |
| `clinical_notes` | Free-text examination findings |
| `created_at` | Record creation timestamp |

**`appointment_diagnoses`**
Junction table linking appointments to one or more ICD-10 diagnoses,
with a flag identifying the primary diagnosis.

**`referrals`**
| Field | Description |
|---|---|
| `referral_id` | Primary key |
| `appointment_id`, `patient_id` | Foreign key references |
| `destination_id` | Foreign key → referral_destinations |
| `referral_reason` | Free-text referral details |
| `referral_date` | Referral issue date |
| `referral_attended` | Boolean (NULL = unknown) |
| `outcome_notes` | Specialist correspondence, if available |

### Views
| View | Description |
|---|---|
| `patient_last_visit` | Most recent appointment date per patient |
| `overdue_recalls` | Patients whose recall due date has passed |

## Tech Stack
- Python 3.x
- psycopg2 (PostgreSQL adapter)
- Faker (synthetic data generation)
- python-dotenv (credential management)
- PostgreSQL

## Prerequisites
- PostgreSQL installed and running locally
- An `optometry_analytics` database created in PostgreSQL
- A `.env` file in the project root containing:
```
PG_PASSWORD=your_postgres_password
```

## How to Run
1. Clone the repository
```
git clone https://github.com/HenzaDB/optometry_analytics.git
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Create the database schema
```
psql -U postgres -d optometry_analytics -f schema.sql
```
4. Generate and populate the database
```
python generate_data.py
```

Output: a fully populated PostgreSQL database with ~200 patients,
400–800 appointments, associated diagnoses, and a 20% referral rate.

## Project Roadmap
- [x] Database schema design
- [x] Synthetic data generation
- [ ] Data cleaning and preprocessing pipeline
- [ ] Exploratory data analysis
- [ ] SQL query library — clinical and business use cases
- [ ] Dashboard (potential)

## About
Built as part of a data analytics portfolio by a practitioner transitioning
from clinical optometry — combining domain expertise with technical
analytical skills.