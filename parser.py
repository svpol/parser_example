import re
import datetime
import pandas as pd
from time import sleep
from random import randint

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NPR:

    def __init__(self, breed: str, breed_group: str = 'object2111', born_after: str = '',
                 born_before: str = '', gender: str = '0') -> None:
        """
        Creates an object of NPR class. All params should be specified as strings in the way they
        are present as values of the site HTML elements.
        :param breed: required, str, dorset='object31', texel='object599', ile-de-france='object18', others see at the site
        :param breed_group: optional, str, terminal='object:29', others see at the site.
        :param born_after: optional, str, 'MM/DD/YYYY', date after which searched animals are born, included in the search.
        :param born_before: optional, str, 'MM/DD/YYYY', date before which searched animals are born, included in the search.
        :param gender: optional, str, both='0', male='1', female='2'.
        """
        self.breed = breed
        self.born_after = born_after
        self.born_before = born_before
        self.breed_group = breed_group
        self.gender = gender

    def get_animal_list(self) -> list:
        """
        Allows to retrieve the IDs of animals found by search parameters specified in __init__ while object creation.
        :return: list, animal IDs.
        """
        # options = Options()
        # options.add_argument("--headless")
        driver = wd.Firefox()
        driver.get('http://mylink.com')

        # select breed_group, breed, gender, born_after and born_before parameters
        dropdowns = {
            'breed_group': ['//*[@id="performSearchForm"]/table[1]/tbody/tr[1]/td[2]/select', self.breed_group],
            'breed': ['//*[@id="performSearchForm"]/table[1]/tbody/tr[2]/td[2]/select', self.breed],
            'gender': ['//*[@id="performSearchForm"]/table[1]/tbody/tr[5]/td[2]/select', self.gender]
        }
        for v in dropdowns.values():
            dropdown = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, fr'{v[0]}')))
            select = Select(dropdown)
            select.select_by_value(f'{v[1]}')

        # input born before and after dates
        driver.find_element(By.ID, value='bornAfter').send_keys(self.born_after)
        driver.find_element(By.ID, value='bornBefore').send_keys(self.born_before)
        driver.find_element(By.ID, value='submit').click()

        # pagination
        # pagination_text = driver.find_element(by=By.XPATH,
        #                                       value='//*[@id="performSearchForm"]/div[2]/table/tfoot/tr/td/div/nav/div').text
        pagination_text = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="performSearchForm"]/div[2]/table/tfoot/tr/td/div/nav/div'))).text
        pages = int(re.search(r'(?<=of )(\d*)', pagination_text)[0])
        current_page = 1

        # parsing animal IDs with pagination
        animals = []
        for i in range(1, pages + 1):
            sleep(randint(3, 7))
            elements = driver.find_elements(by=By.CLASS_NAME, value='ng-binding')
            # elements = WebDriverWait(driver, 15).until(
            #     EC.presence_of_all_elements_located((By.CLASS_NAME, "ng-binding")))
            elements = [x.text for x in elements]
            for i in elements:
                id = re.search(r'^\d{4,}.*', i)
                if id is not None and i == id[0]:
                    animals.append(i)
            print(f'Page {current_page} of {pages} is done.')
            if current_page < pages:
                if pages >= 10:
                    xpath = '//*[@id="performSearchForm"]/div[2]/table/tfoot/tr/td/div/nav/ul/li[13]/a'
                else:
                    xpath = f'//*[@id="performSearchForm"]/div[2]/table/tfoot/tr/td/div/nav/ul/li[{pages + 3}]/a'
                driver.find_element(By.XPATH, value=xpath).click()
                current_page += 1
        driver.close()
        return animals

    @staticmethod
    def _reformat_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Helper function which reformats the DataFrame.
        :param df: df to reformat.
        :return: the reformatted df.
        """
        # remove accuracy from indice
        cols = ['bwt', 'pemd', 'nlb', 'wwt', 'pwwt', 'nlw']
        for i in cols:
            df[i] = df[i].apply(lambda x: x.split('\n')[0])
        # making a single address from 2 strings
        df['address'] = df["address1"] + ' ' + df["address2"]
        col = df.pop('address')
        df.insert(14, col.name, col)
        df = df.drop(['address1', 'address2'], axis=1)
        # reformatting birth_date
        df['birth_date'] = df['birth_date'].apply(lambda x:
                                                  datetime.datetime.strptime(x, "%m/%d/%Y").strftime("%Y-%m-%d") if x != '' else None)
        # Fixing breed name to avoid encoding problems
        df.loc[df['breed'] == 'Île-de-France', 'breed'] = 'Ile-de-France'
        return df

    @staticmethod
    def get_animal_info(animal_ids: list) -> pd.DataFrame:
        """
        The main parsing function. Generates links from animal IDs and parses the data for each animal
        from the website.
        :param animal_ids: the list of animal IDs.
        :return: a DataFrame with the parsed data.
        """
        output_dict = {'id': [], 'breed_group': [], 'breed': [], 'birth_date': [], 'gender': [],
                       'regnum': [], 'progeny_total': [], 'flock_count': [], 'sire': [], 'dam': [],
                       'status': [], 'genotyped': [], 'farm_name': [], 'contact_name': [], 'address1': [],
                       'address2': [], 'phone': [], 'email': [], 'bwt': [], 'bwt_accuracy': [], 'mwwt': [],
                       'pemd': [], 'pemd_accuracy': [], 'nlb': [], 'nlb_accuracy': [], 'carcass_plus_index': [],
                       'wwt': [], 'wwt_accuracy': [], 'pwwt': [], 'pwwt_accuracy': [], 'pfat': [],
                       'nlw': [], 'nlw_accuracy': [], 'src_index': []}
        elements_indice = {
            'id': 14, 'breed_group': 16, 'breed': 18, 'birth_date': 20, 'gender': 22,
            'regnum': 24, 'progeny_total': 15, 'flock_count': 17, 'sire': 19, 'dam': 21,
            'status': 23, 'genotyped': 25, 'farm_name': 32, 'contact_name': 34, 'address1': 36,
            'address2': 37, 'phone': 33, 'email': 35, 'bwt': 39, 'bwt_accuracy': 40, 'mwwt': 45, 'pemd': 50,
            'pemd_accuracy': 51, 'nlb': 55, 'nlb_accuracy': 56, 'carcass_plus_index': 61,
            'wwt': 42, 'wwt_accuracy': 43, 'pwwt': 47, 'pwwt_accuracy': 48, 'pfat': 53,
            'nlw': 58, 'nlw_accuracy': 59, 'src_index': 63
        }

        options = Options()
        options.add_argument("--headless")
        driver = wd.Firefox(options)
        for i in range(len(animal_ids)):
            driver.get(fr'http://mylink.com/{animal_ids[i]}')
            sleep(randint(5, 8))
            elements = driver.find_elements(by=By.CLASS_NAME, value='ng-binding')
            elements = [x.text for x in elements]
            for k, v in elements_indice.items():
                output_dict[k].append(elements[v])
            print(f'{i + 1} of {len(animal_ids)} animals done.')
        driver.close()
        output_df = pd.DataFrame(output_dict)
        output_df = NPR._reformat_df(output_df)
        return output_df
