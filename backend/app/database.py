import psycopg
import psycopg.rows
import time
# from  .config import settings

IntegrityError = psycopg.IntegrityError

while True:
    try:
        db = psycopg.connect(f"""host={"localhost"} 
                    dbname={"majlis"}
                    user={"postgres"}
                    password={"1234"}""")
        cur = db.cursor(row_factory=psycopg.rows.dict_row)
        print('Database Connected Successfully')
        break

    except Exception as error:
        print(error)
        time.sleep(2)
