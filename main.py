import pandas as pd
from time import time
from sqlalchemy import create_engine
from postgres_writer import PostgresWriter


if __name__ == "__main__":

    start = time()

    engine = create_engine('postgresql+psycopg2://user:password@host/db_name')
    conn = engine.connect()

    dates_2008 = pd.read_csv('service_files/dorset/additional.txt')
    PostgresWriter.write_to_postgres(date_df=dates_2008, log_file='service_files/dorset/written_both.txt',
                                     breed='object3', gender='0')

    end = time() - start
    print(end)
