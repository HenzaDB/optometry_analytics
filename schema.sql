--==================================================================
--LOOKUP TABLES
--==================================================================


CREATE TABLE gender_types (
	gender_id SERIAL PRIMARY KEY,
	gender_label VARCHAR(50) NOT NULL UNIQUE
	--'Male', 'Female', 'Non-Binary', 'Other', 'Prefer not to say'
);

CREATE TABLE visit_types (
	visit_id SERIAL PRIMARY KEY,
	visit_label VARCHAR(100) NOT NULL UNIQUE
	--e.g. 'Routine', 'Recall', 'Referral', 'Emergency', 'Follow up'
);

CREATE TABLE referral_destinations (
	referral_id SERIAL PRIMARY KEY,
	referral_label VARCHAR(100) NOT NULL UNIQUE
	--e.g. 'Ophthalmology', 'GP', 'Low Vision'
);

--==================================================================
--CORE TABLES
--==================================================================


CREATE TABLE optometrists (
	optom_id SERIAL PRIMARY KEY,
	first_name VARCHAR(100) NOT NULL,
	last_name VARCHAR (100) NOT NULL,
	ahpra_num VARCHAR (20) UNIQUE,
	practice_location VARCHAR (150)
);

CREATE TABLE patients (
	patient_id SERIAL PRIMARY KEY,
	first_name VARCHAR (100) NOT NULL,
	last_name VARCHAR (100) NOT NULL,
	date_of_birth DATE NOT NULL,
	gender_id INT REFERENCES gender_types(gender_id),
	email VARCHAR (150),
	phone VARCHAR (20),
	suburb VARCHAR (100),
	postcode CHAR (4),
	medicare_no VARCHAR (20),
	created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE diagnoses (
	diagnosis_id SERIAL PRIMARY KEY,
	icd10_code VARCHAR (10) NOT NULL UNIQUE,
	description VARCHAR (200) NOT NULL
	--e.g. 'H52.1', 'Myopia'
);

--==================================================================
--APPOINTMENTS
--==================================================================


CREATE TABLE appointments (
	appointment_id SERIAL PRIMARY KEY,
	patient_id INT NOT NULL REFERENCES patients(patient_id),
	optom_id INT NOT NULL REFERENCES optometrists(optom_id),
	appointment_date DATE NOT NULL,
	visit_id INT REFERENCES visit_types(visit_id),
	chief_complaint TEXT,

	--Visual Acuity (Denoted as Snellen denominator as integer e.g. 6 = 6/6)
	--Convert to standard 6m numerator if results in non-standard distance
	va_r_unaided INT,
	va_l_unaided INT,
	va_r_aided INT,
	va_l_aided INT,

	--Intraocular pressures (mmHg)
	iop_r NUMERIC(4, 1),
	iop_l NUMERIC(4, 1),

	--Recall period in months e.g. 6, 12, 18, 24
	next_recall_months INT,

	--Metadata
	clinical_notes TEXT,
	created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE appointment_diagnoses (
	id SERIAL PRIMARY KEY,
	appointment_id INT NOT NULL REFERENCES appointments(appointment_id),
	diagnosis_id INT NOT NULL REFERENCES diagnoses(diagnosis_id),
	is_primary BOOLEAN DEFAULT TRUE
);

CREATE TABLE referrals (
	referral_id SERIAL PRIMARY KEY,
	appointment_id INT NOT NULL REFERENCES appointments(appointment_id),
	patient_id INT NOT NULL REFERENCES patients(patient_id),
	destination_id INT REFERENCES referral_destinations(referral_id),
	referral_reason TEXT,
	referral_date DATE,
	referral_attended BOOLEAN,
	outcome_notes TEXT, --Correspondence from specifialist, if known
	created_at TIMESTAMP DEFAULT NOW()
);

--==================================================================
--COMMON VIEWS
--==================================================================


CREATE VIEW patient_last_visit AS
	SELECT
		patient_id,
		MAX(appointment_date) AS last_visit_date
	FROM
		appointments
	GROUP BY
		patient_id;

CREATE VIEW overdue_recalls AS
	SELECT
		p.patient_id,
		p.first_name,
		p.last_name,
		lv.last_visit_date,
		a.next_recall_months,
		(lv.last_visit_date + (a.next_recall_months || ' months')::INTERVAL) AS due_date
	FROM patients p
	JOIN patient_last_visit lv USING (patient_id)
	JOIN appointments a
	ON p.patient_id = a.patient_id
	AND a.appointment_date = lv.last_visit_date
	WHERE (lv.last_visit_date + (a.next_recall_months || ' months')::INTERVAL) < CURRENT_DATE;