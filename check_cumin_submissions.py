#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# check_cumin_submissions.py

# Tomas Meszaros <exo@tty.sk>

# This program logs in into the cumin web app, then navigates to
# the Submissions and checks if the jobs sharing the same description
# name are sorted correctly.

# Usage: python check_cumin_submissions.py cumin_username cumin_password

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from BeautifulSoup import BeautifulSoup
import sys

def main():
    cumin_url = 'http://localhost:45672/login.html'

    driver = webdriver.Firefox()
    driver.get(cumin_url)

    cumin_login(driver)
    cumin_navigate_to_jobs_table(driver, "python_test_submit")

    for i in range(2):
        # double check, just in case...
        if not cumin_sort_check_table(driver):
            driver.quit()
            sys.exit(1)

    driver.quit()
    sys.exit(0)

def cumin_navigate_to_jobs_table(driver, job_description):
    # wait for grid to load
    wait = WebDriverWait(driver, 3)
    grid = wait.until(EC.presence_of_element_located((By.ID, 'main.grid.view')))
    print "%s: navigating to the jobs table" % sys.argv[0]

    submissions = grid.find_element_by_link_text('Submissions')
    submissions.send_keys(Keys.RETURN)

    # wait for submissions to load
    jobs = wait.until(EC.presence_of_element_located((By.LINK_TEXT, job_description)))
    jobs.send_keys(Keys.RETURN)

def cumin_login(driver):
    user_name = sys.argv[1]
    user_passowrd = sys.argv[2]

    username = driver.find_element_by_id('form.user_name')
    username.send_keys(user_name)

    password = driver.find_element_by_name('form.password.param')
    password.send_keys(user_passowrd)
    password.send_keys(Keys.RETURN)

def cumin_sort_check_table(driver):
    cumin_wait_for_jobs(driver)
    job_id_sort = driver.find_element_by_link_text('Job id')
    job_id_sort.send_keys(Keys.RETURN)
    print "%s: sorting table" % sys.argv[0]
    return cumin_check_table(driver)

def cumin_wait_for_jobs(driver):
    # wait for jobs to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "localhost.localdomain#")))

def cumin_check_table(driver):
    # parse the page source so we end up only with job IDs
    cumin_wait_for_jobs(driver)
    print "%s: checking table" % sys.argv[0]
    parsed_html = BeautifulSoup(driver.page_source)
    raw_table = parsed_html.find('table').text
    table_items = raw_table.split('#')[1:]
    table_IDs = map(lambda x: x.split('.')[0], table_items)

    if table_IDs == sorted(table_IDs, key=lambda id: float(id), reverse=False) or \
       table_IDs == sorted(table_IDs, key=lambda id: float(id), reverse=True):
        return True
    else:
        return False

if __name__ == "__main__":
    main()
