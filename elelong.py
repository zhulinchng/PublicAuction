from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas


def loadConfirmation(driver, confirmationtext, tableclass, timeinc):
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.findAll('table', class_=tableclass)
        if len(table) > 0:
            if confirmationtext.strip() == table[0].findAll('td')[0].text.strip():
                break
        else:
            time.sleep(timeinc)


# config
url = 'https://elelong.kehakiman.gov.my/BidderWeb/Home/Index'

# constants
tableclass = 'table table-noline auction-result-info'
confirmationtext = 'Auction date/time:'
rooturl = url.split('/')[0] + '//' + url.split('/')[2]

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)

# Create empty list
weblist = []

# Load initial page
loadConfirmation(driver, confirmationtext, tableclass, 0.01)
soup = BeautifulSoup(driver.page_source, 'html.parser')
pages = int(soup.findAll('li', class_='disabled')
            [-1].text.strip().split(' ')[-1])

# loop through all pages
for c in range(pages):
    weblist.append(driver.page_source)
    # find next buttom
    nxt = driver.find_element_by_id('liNext')
    driver.execute_script("arguments[0].click();", nxt)
    loadConfirmation(driver, confirmationtext, tableclass, 0.01)
driver.close()


# create a dataframe
df = pandas.DataFrame(columns=['Auction date/time', 'Land Used', 'State',
                      'District', 'Reserved Price (RM)', 'Tenure'])

# extract data from each page to table
for web in weblist:
    # Finding by id
    s = soup.findAll('a', class_='btn btn-primary aIamInterested')
    table = soup.findAll(
        'table', class_='table table-noline auction-result-info')
    # add the data to the dataframe
    df2 = pandas.DataFrame(columns=['Auction date/time', 'Land Used', 'State',
                                    'District', 'Reserved Price (RM)', 'Tenure', 'URL'])
    for i in range(len(table)):
        df2.loc[i] = [table[i].findAll('td')[1].text, table[i].findAll('td')[3].text, table[i].findAll('td')[
            5].text, table[i].findAll('td')[7].text, table[i].findAll('td')[9].text, table[i].findAll('td')[11].text, s[i].get('href')]
    df = pandas.concat([df, df2])


# parse the first column into date and time
df['Auction date/time'] = pandas.to_datetime(
    df['Auction date/time'], format='%d/%m/%Y, %H:%M:00 %p')

# parse Reserved Price (RM) to float
df['Reserved Price (RM)'] = df['Reserved Price (RM)'].str.replace(',', '')
df['Reserved Price (RM)'] = df['Reserved Price (RM)'].astype(float)

# append root url to url column
df['URL'] = rooturl + df['URL']

# output to csv
df.to_csv('elelong.csv', index=False)
