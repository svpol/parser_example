import pandas as pd
from parser import NPR
from random import randint
from time import time, sleep


class PostgresWriter:

    @staticmethod
    def write_to_postgres(date_df: pd.DataFrame, log_file: str, breed: str,
                          breed_group: str = 'object:29', gender: str = '0') -> None:
        """
        Writes a parsed data df to a Postgres database.
        :param date_df: a pandas dataframe with born_after and born_before dates to search animals for and then parse.
        :param log_file: a file where the result of writing to the databese is written in the format:
        born_before,born_after,number_of_animals_written,time
        :param breed: str, breed to search for and the parse, as specified in NPR.__init__.
        :param breed_group: str, breed_group to search for and the parse, as specified in NPR.__init__.
        :param gender: str, gender to search for and the parse, as specified in NPR.__init__.
        :return: None
        """
        born_before = date_df['born_before'].to_list()
        born_after = date_df['born_after'].to_list()

        for i in range(len(born_before)):
            iter_time = time()
            id_search = NPR(breed=breed, breed_group=breed_group, born_after=born_after[i],
                             born_before=born_before[i], gender=gender)
            ids = id_search.get_animal_list()
            animal_info = NPR.get_animal_info(ids)
            animal_info.to_sql(name='mytable', schema='myschema', con=conn, if_exists='append', index=False)
            with open(log_file, 'a') as f:
                f.write(f'{born_before[i]},{born_after[i]},{len(ids)},{time() - iter_time}\n')
            print(f'{len(ids)} animals are written to database.')
            sleep(randint(30, 50))
