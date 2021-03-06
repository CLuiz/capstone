import requests
from bs4 import BeautifulSoup
import pandas as pd
import numbeo_scraper as ns
import os


def get_grad_data(url, cols, skip_rows=5):
    '''
    INPUT: Target url to scrape, column names, and rows to skip (default=5)
    OUTPUT: Dataframe of scraped info
    '''
    file_name = url.split('/')[-1].replace('-', '_')
    path = os.getcwd()+'/data/biggestuscities'
    file_path = '{}/{}.csv'.format(path, file_name)

    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isfile(file_path):
        soup = ns.get_pages(url)
        table = soup[0].findAll('table')
        tabs = [tag.text for tag in table]
        clean_table = clean_top_100(tabs, skip_rows)
        return process_df(clean_table, file_path, cols)
    else:
        return pd.read_csv(file_path)


def clean_top_100(tabs, skip_rows):
    d = [t.replace("\n",",").strip() for t in tabs][-1]
    d = d.split(' ')
    t = [item for item in d if item != '']
    t_done = [item.replace(',',' ').strip()  for item in t]
    just_table = t_done[skip_rows:-9]

    bad_item_list = ['(adsbygoogle','=', 'window.adsbygoogle', '||',
                     '[]).push({', '});', 'San','District', 'Of',
                     'North', 'St.', 'City', 'New', 'Springs',
                     'Urban', 'Beach','Rouge', 'Los', 'El','Vista',
                     'County', 'Fort', 'Las', 'Christi', 'Ana']

    replace_dict = {'Francisco': 'san_francisco',
                    'Angeles': 'los_angeles',
                    'Carolina', 'north_carolina',
                    'Baton', 'baton_rouge',
                    'Chula', 'chula_vista',
                    'Worth', 'fort_worth',
                    'Christi', 'corpus_christi',
                    'Santa', 'santa_ana',
                    'Vegas', 'las_vegas',
                    'Bernadino', 'san_bernadino',
                    'Columbia', 'dc',
                    'Diego', 'san_diego',
                    'Jersey', 'new_jersey',
                    'Orleans', 'new_orleans',
                    'York', 'new_york'
                    }

    just_table = [item for item in just_table if item not in bad_item_list if item]
    just_table = [item.replace('Francisco', 'san_francisco') for item in just_table]
    just_table = [item.replace('Angeles', 'los_angeles') for item in just_table]
    just_table = [item.replace('Carolina', 'north_carolina') for item in just_table]
    just_table = [item.replace('Baton', 'baton_rouge') for item in just_table]
    just_table = [item.replace('Chula', 'chula_vista') for item in just_table]
    just_table = [item.replace('Worth', 'fort_worth') for item in just_table]
    just_table = [item.replace('Christi', 'corpus_christi') for item in just_table]
    just_table = [item.replace('Santa', 'santa_ana') for item in just_table]
    just_table = [item.replace('Vegas', 'las_vegas') for item in just_table]
    just_table = [item.replace('Bernadino', 'san_bernadino') for item in just_table]
    just_table = [item.replace('Columbia', 'dc') for item in just_table]
    just_table = [item.replace('Diego', 'san_diego') for item in just_table]
    just_table = [item.replace('Jersey', 'new_jersey') for item in just_table]
    just_table = [item.replace('Orleans', 'new_orleans') for item in just_table]
    just_table = [item.replace('York', 'new_york') for item in just_table]
    just_table = [item.lower() for item in just_table]

    return just_table


def process_df(clean_table, file_path, cols):
    chunks = [clean_table[x:x+4] for x in range(0, len(clean_table), 4)]
    df = pd.DataFrame(chunks)
    df.columns = cols
    df = df.drop('rank', axis=1)
    df['city']= df['city'].str.lower()
    df.set_index('city', inplace=True)
    df_csv = df.copy()
    df_csv.to_csv(file_path)
    return df


def get_city_2011_2015(url_suffix):
    url_prefix = 'https://www.biggestuscities.com/city/'
    url = url_prefix + url_suffix
    path = os.getcwd() + '/data/biggestuscities/cities'
    file_name = url.split('/')[-1].replace('-', '_')
    file_path = '{}/{}.csv'.format(path, file_name)

    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isfile(file_path):
        doc=requests.get(url).text
        done = 'I brokeded it'
        if doc != 'Not Found!':
            soup = BeautifulSoup(doc, 'lxml')
            table = soup.findAll('table')
            tabs = [tag.text for tag in table]
            data = [t.replace("\n",",").strip() for t in tabs][-1].split(',,')[1:-1]
            data = [item[1:].split(',') for item in data if item]
            dd = pd.DataFrame(data)[1:6]
            dd['pop'] = dd[1] + dd[2]
            da = pd.DataFrame(zip(dd[0], dd['pop']))
            done = da.T
            done.to_csv(file_path)
    else:
         done = pd.read_csv(file_path)
    return done


if __name__ == '__main__':
    url = 'https://www.biggestuscities.com/demographics/us/people-foreign-born-by-top-100-city'
    cols = ['rank', 'city','state_fb','pct_foreign_born']
    df = get_grad_data(url, cols)

    df1 = pd.read_csv('data/biggestuscities/business_retail_sales_per_capita_by_top_100_city.csv')
    df1['city'] = df1['city'].apply(lambda x: x.replace('_', '-'))
    df1['state_rs'] = df1['state_rs'].apply(lambda x: x.replace('_', '-'))
    df1['combo'] = df1['city'] + '-' + df1['state_rs']
    city_list = list(df1['combo'])

    for city in city_list:
        get_city_2011_2015(city)
