import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    dbname = os.getenv("DB_NAME"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")
)

# Load tables into DFs
df_patients = pd.read_sql("SELECT * FROM patients", conn)
df_optometrists = pd.read_sql("SELECT * FROM optometrists", conn)
df_appointments = pd.read_sql("SELECT * FROM appointments", conn)
df_gender_types = pd.read_sql("SELECT * FROM gender_types", conn)
df_patients = df_patients.merge(df_gender_types, on="gender_id", how="left")
df_patients['date_of_birth'] = pd.to_datetime(df_patients['date_of_birth'])
df_appointments['appointment_date'] = pd.to_datetime(df_appointments['appointment_date'])

print(df_appointments['appointment_date'].describe())
conn.close()