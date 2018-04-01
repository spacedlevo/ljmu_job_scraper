import datetime
import sqlite3

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

db = sqlite3.connect('ljmu_jobs.db')
c = db.cursor()

WEBPAGE = 'https://jobs.ljmu.ac.uk/vacancies.html'
job_details_required = ['Contract Type', 'Hours', 'Job Type',
                        'Salary', 'Vacancy Type', 'Closing Date', 'Ref No']


def open_chrome():
    path = r'/home/levo/Documents/projects/ChromeDriver/chromedriver'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(path, chrome_options=chrome_options)
    browser.set_page_load_timeout(60)
    browser.implicitly_wait(20)
    return browser


def jobpost_body(soup):
    return soup.find_all('div', class_='jobpost')


def title(jobpost_body):
    return jobpost_body.h2.text.strip()


def job_details(jobpost_body, detail):
    details = jobpost_body.p.find_all('span')
    for info in details:
        if info.text.strip().startswith(detail):
            return info.text.replace(f'{detail}:', '').strip()


def does_record_exist(ref_no):
    c.execute(''' SELECT ref FROM jobs WHERE ref=? ''', (int(ref_no),))
    if c.fetchone() is None:
        return False
    else:
        return True


def add_job(job):
    job_title = title(job)
    job_fields = {i: job_details(job, i) for i in job_details_required}
    c.execute(''' INSERT INTO jobs(ref, "date added", title, "contract type", hours, "job type", salary, "vacancy type", "closing date")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
              (
                  int(job_fields['Ref No']),
                  datetime.date.today().strftime("%B %d %Y"),
                  job_title,
                  job_fields['Contract Type'],
                  job_fields['Hours'],
                  job_fields['Job Type'],
                  job_fields['Salary'],
                  job_fields['Vacancy Type'],
                  job_fields['Closing Date']
              ))
    db.commit()


browser = open_chrome()
browser.get(WEBPAGE)
jobs = jobpost_body(bs(browser.page_source, 'html.parser'))

for i in jobs:
    if not does_record_exist((job_details(i, 'Ref No'))):
        add_job(i)

db.close()
