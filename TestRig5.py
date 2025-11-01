
# import os, time, math, random, threading
from datetime import datetime
from sqlalchemy import create_engine, text

# # --------------------------------------------------------------------------
SERVER = '10.0.3.172'
DATABASE = "DAQ_sSPC"
USERNAME = "TCP01"
PASSWORD = "Testing27!"
TEMPLATE_TABLE = "pipe_data_template"

conn_str = (f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"
            "?driver=ODBC+Driver+17+for+SQL+Server")
engine = create_engine(conn_str)

# --- Table Check Function ---
def table_exists(engine, schema_name, table_name):
    try:
        with engine.begin() as conn:
            query = text("""
                SELECT CASE 
                    WHEN EXISTS (
                        SELECT 1 
                        FROM INFORMATION_SCHEMA.TABLES 
                        WHERE TABLE_SCHEMA = :schema 
                          AND TABLE_NAME = :table
                    )
                    THEN 'Yes'
                    ELSE 'No'
                END AS table_exists
            """)
            result = conn.execute(query, {"schema": schema_name, "table": table_name})
            return result.scalar()
    except Exception as e:
        print(f"Error checking table: {e}")
        return None

# --- Run Check ---
pWON = '20250923'
xRP = f"XRP_{pWON}"
xTT = f"XTT_{pWON}"
xST = f"XST_{pWON}"
newSqlTables1, newSqlTables2, newSqlTables3 = xRP, xTT, xST
dataTemplate1, dataTemplate2, dataTemplate3 = '[dbo].[18_EoPRP]', '[dbo].[19_EoPTT]', '[dbo].[20_EoPST]'

def create_table_from_template(uCalling, engine, newSqlTables1, newSqlTables2, newSqlTables3, dataTemplate1, dataTemplate2, dataTemplate3):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_table = f"pipe_data_run_{timestamp}"
    try:
        existsA = table_exists(engine, "dbo", newSqlTables1)
        existsB = table_exists(engine, "dbo", newSqlTables2)
        existsC = table_exists(engine, "dbo", newSqlTables3)
        print('TP01', existsA, existsB, existsC)
    except Exception:
        print('[SPC 2 SQL] Tables not exist, creating new Tables...')

    if uCalling == 1:
        if existsA == 'No' or existsB == 'No' or existsC == 'No':
            try:
                with engine.begin() as conn:
                    conn.execute(text(f"SELECT TOP 0 * INTO {newSqlTables1} FROM {dataTemplate1}"))
                    conn.execute(text(f"SELECT TOP 0 * INTO {newSqlTables2} FROM {dataTemplate2}"))
                    conn.execute(text(f"SELECT TOP 0 * INTO {newSqlTables3} FROM {dataTemplate3}"))
                print(f"[SQL] Created new table: {newSqlTables1, newSqlTables2, newSqlTables3}")
            except Exception:
                print('TP03 Error creating new Tables..')
        else:
            print('Required tables are available for SPC Live Analysis')

    elif uCalling == 2 or uCalling == 3:
        if existsA == 'Yes' or existsB == 'Yes' or existsC == 'Yes':
            print('Required tables are available for Post-Prod Analysis')
        else:
            print('Sorry, no valid data repository found, cannot proceed..')

    else:
        print('Tables already exists...')

    return newSqlTables1, newSqlTables2, newSqlTables3

uCalling = 1
table_name = create_table_from_template(uCalling, engine, newSqlTables1, newSqlTables2, newSqlTables3, dataTemplate1, dataTemplate2, dataTemplate3)
print('TP01', table_name)
print('TP02', table_name[0])
print('TP03', table_name[1])
print('TP04', table_name[2])