from dotenv import load_dotenv
load_dotenv()

import psycopg2
import random
from faker import Faker
from datetime import date, timedelta

fake = Faker()
random.seed(42)

conn = psycopg2.connect(
    host = "localhost",
    port = 5432,
    dbname = "optometry_analytics",
    user = "postgres",
    password = os.environ.get("PG_PASSWORD")
)
cur = conn.cursor()

genders = ['Male', 'Female', 'Non-binary', 'Other', 'Prefer not to say']
cur.executemany("INSERT INTO gender_types (gender_label) VALUES (%s) ON CONFLICT DO NOTHING", [(g,) for g in genders]
)

visit_labels = ['Routine', 'Reminder recall', 'Inbound referral', 'Outbound referral follow-up', 'New presentation', 'Emergency', 'Post-op review']
cur.executemany("INSERT INTO visit_types (visit_label) VALUES (%s) ON CONFLICT DO NOTHING", [(v,) for v in visit_labels]
)

destinations = ['Ophthalmology','GP', 'Low vision services', 'Other']
cur.executemany("INSERT INTO referral_destinations (referral_label) VALUES (%s) ON CONFLICT DO NOTHING", [(d,) for d in destinations]
)

icd10_codes = [
    ('H52.1', 'Myopia'),
    ('H52.0', 'Hypermetropia'),
    ('H52.2', 'Astigmatism'),
    ('H40.1', 'Open-angle glaucoma'),
    ('H25.9', 'Age-related cataract'),
    ('H35.3', 'Macular degeneration'),
    ('H04.1', 'Dry eye syndrome'),
    ('H11.3', 'Conjunctival haemorrhage'),
    ('H53.2', 'Diplopia'),
    ('H57.1', 'Ocular pain')
]
cur.executemany("INSERT INTO diagnoses (icd10_code, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", icd10_codes
)

optometrist_id = []
for _ in range(3):
    cur.execute(
        """INSERT INTO optometrists(first_name, last_name, ahpra_num, practice_location)
           VALUES (%s, %s, %s, %s) RETURNING optom_id""",
        (
            fake.first_name(),
            fake.last_name(),
            'OPT' + fake.numerify('#######'),
            random.choice(['Melbourne CBD',
                           'Doncaster',
                           'Box Hill',
                           'Camberwell',
                           'Balwyn'
                           ])
        )
    )
    optometrist_id.append(cur.fetchone()[0])

cur.execute("SELECT gender_id FROM gender_types")
gender_id = [r[0] for r in cur.fetchall()]

patient_id = []
for _ in range(200):
    dob = fake.date_of_birth(minimum_age=5, maximum_age=90)
    cur.execute("""INSERT INTO patients
                (first_name, last_name, date_of_birth, gender_id,
                email, phone, suburb, postcode,
                medicare_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING patient_id""",
                (
                    fake.first_name(),
                    fake.last_name(),
                    dob,
                    random.choice(gender_id),
                    fake.email(),
                    fake.phone_number(),
                    fake.city(),
                    fake.postcode(),
                    fake.numerify('##########')
                ))
    patient_id.append(cur.fetchone()[0])

cur.execute("SELECT visit_id FROM visit_types")
visit_id = [r[0] for r in cur.fetchall()]

cur.execute("SELECT diagnosis_id FROM diagnoses")
diagnosis_id = [r[0] for r in cur.fetchall()]

cur.execute("SELECT referral_id FROM referral_destinations")
referral_id = [r[0] for r in cur.fetchall()]

complaints =['Routine check',
             'Blurry vision',
             'Ocular pain',
             'Red eye',
             'Flashes/Floaters',
             'Headache',
             'Double vision',
             'Dry eyes',
             'Itchy eyes',
             'Foreign body sensation'
             ]

appointment_id = []
for patient_id in patient_id:
    num_appts = random.randint(1, 4)
    appt_dates = sorted([
        fake.date_between(start_date = '-3y', end_date = 'today')
        for _ in range(num_appts)
    ])
    for appt_date in appt_dates:
        cur.execute(
            """INSERT INTO appointments
            (patient_id, optom_id, appointment_date,
            visit_id, chief_complaint, va_r_unaided, va_l_unaided,
            va_r_aided, va_l_aided, iop_r, iop_l, next_recall_months,
            clinical_notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING appointment_id""",
            (
                patient_id,
                random.choice(optometrist_id),
                appt_date,
                random.choice(visit_id),
                random.choice(complaints),
                random.choice([6, 12, 18, 24, 36, 42, 60]),
                random.choice([6, 12, 18, 24, 36, 42, 60]),
                random.choice([6, 6, 6, 9, 12]),
                random.choice([6, 6, 6, 9, 12]),
                round(random.uniform(10, 21), 1,),
                round(random.uniform(10, 21), 1,),
                random.choice([6, 12, 12, 18, 24]),
                fake.sentence(nb_words = 12)
            )
        )
        appointment_ids = cur.fetchone()[0]
        appointment_id.append(appointment_ids)

        sampled_diagnoses = random.sample(diagnosis_id, k = random.randint(1, 2))
        for i, diag_id in enumerate(sampled_diagnoses):
            cur.execute(
                """INSERT INTO appointment_diagnoses
                (appointment_id, diagnosis_id, is_primary)
                VALUES (%s, %s, %s)""",
                (
                    appointment_id,
                    diag_id,
                    i == 0
                )
            )
        
        if random.random() < 0.2:
            cur.execute(
                """INSERT INTO referrals
                (appointment_id, patient_id, destination_id, referral_reason, referral_date, referral_attended)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    appointment_id,
                    patient_id,
                    random.choice(referral_id),
                    fake.sentence(nb_words = 8),
                    appt_date,
                    random.choice([True, True, False, None]) # None represents unknown attendance
                )
            )

conn.commit()
cur.close()
conn.close()
print("Synthetic data generation complete!")