import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    dbname = os.getenv("DB_NAME"),
    dbuser = os.genenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")
)

# Load tables into DFs
df_patients = pd.read_sql("SELECT * FROM patients", conn)
df_optometrists = pd.read_sql("SELECT * FROM optometrists", conn)
df_appointments = pd.read_sql("SELECT * FROM appointments", conn)

print(df_patients.shape)
print(df_patients.head())
print(df_optometrists.shape)
print(df_optometrists.head())
print(df_appointments.shape)
print(df_appointments.head())

conn.close()