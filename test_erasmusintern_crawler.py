# coding=utf-8
import random
import json
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def custom_chrome_options():
    global user_agent
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument('--disable-extensions')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'user-agent={user_agent}')


def make_http_request():
    global total_requests, requests
    requests += 1
    total_requests += 1
    return requests, total_requests


def click_next():
    try:
        more_btn = driver.find_element_by_xpath("//li[@class='next']/a")
        more_btn.click()
    except NoSuchElementException:
        logging.error("No Such Element Exception: no more next button")
        pass
    timeout_time = [ms for ms in range(15, 20)]
    driver.implicitly_wait(random.choice(timeout_time))


def set_up_url():
    global url
    url_unique_code = input('do you want test url? Type "test": ')
    if url_unique_code == "test":
        url = "https://erasmusintern.org/traineeships?search_api_views_fulltext=&field_traineeship_full_location_field_traineeship_location_count=242"
    else:
        url = input('input your own url')
    return url


def set_initial_prefs():
    driver.find_element_by_xpath(
        "//ul[@id='facetapi-facet-search-apitraineeship-index-block-field-traineeship-field-studiesparents-all']/li[@class='leaf'][2]").click()  # [2] stays for


def main():
    global requests, total_requests, chrome_options, driver
    logging.basicConfig(level=logging.INFO)
    data: Dict[str, List[Any]] = {'results': []}
    chrome_options = webdriver.ChromeOptions()
    custom_chrome_options()
    requests = 0
    total_requests = 0
    set_up_url()
    # here include your own path for the chrome driver
    driver = webdriver.Chrome("..\\chromedriver.exe",
                              options=chrome_options)
    logging.info("Starting the driver..")
    results_url = url
    driver.get(results_url)
    make_http_request()

    logging.info("%s opened", url)
    make_http_request()
    set_initial_prefs()
    logging.info("preferences for query set")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    # set up manually to avoid over complication
    soup_get_page_number = 7
    review_number = 1
    i = 0
    page = 1
    logging.info('Driver closed. Fetching Reviews:')
    while i < soup_get_page_number:
        logging.info("fetch reviews on page %s", page)
        soup_scrap_results = soup.find_all("div", class_="col-md-12")
        for review in soup_scrap_results:
            try:
                title = review.find("h3", class_='dot-title').get_text()
            except AttributeError:
                logging.info('fail to fetch review_title')
                title = "None"

            try:
                duration = review.find("div",
                                       class_="field field-name-field-traineeship-duration field-type-taxonomy-term-reference field-label-inline clearfix").find_next(
                    "div", class_="field-items").find_next("div", class_="field-item even").get_text()
            except AttributeError:
                logging.info('fail to fetch duration')
                duration = "None"

            try:
                city = review.find("div",
                                   class_="field field-name-field-traineeship-location-city field-type-text field-label-hidden pull-left").find_next(
                    "div", class_="field-items").find_next("div", class_="field-item even").get_text()
            except AttributeError:
                logging.info('fail to fetch city name')
                city = "None"

            try:
                postdate = review.find("div",
                                       class_="field field-name-post-date field-type-ds field-label-inline clearfix").find_next(
                    "div", class_="field-items").find_next("div", class_="field-item even").get_text()
            except AttributeError:
                logging.info('fail to fetch postdate')
                postdate = "None"

            try:
                deadline = review.find("div",
                                       class_="field field-name-field-traineeship-apply-deadline field-type-datestamp field-label-inline clearfix").find_next(
                    "div", class_="field-items").find_next("div", class_="field-item even").find_next("span",
                                                                                                      class_="date-display-single").get_text()
            except AttributeError():
                logging.info('fail to fetch deadline')
                deadline = "None"

            try:
                link = review.find("div",
                                   class_="field field-name-node-link field-type-ds field-label-hidden pull-right").find_next(
                    "div", class_="field-items").find_next("div", class_="field-item even").find_next("a")[
                    'href']
            except AttributeError:
                logging.info('fail to fetch link')
                link = "None"

            try:
                company = review.find("div",
                                      class_="field field-name-recruiter-name field-type-ds field-label-hidden").find_next(
                    "div", class_="field-items").find_next("div", class_="field-item even").find_next("a").get_text()
            except AttributeError:
                logging.info('fail to fetch company name')
                company = "None"

            data['results'].append({
                'id': review_number,
                'title': title,
                'city': city,
                'deadline': deadline,
                'duration': duration,
                'post_date': postdate,
                'company': company,
                'link': link,
            })
            logging.info("review appended successfully")
            review_number += 1

        page += 1
        i += 1

        if requests > 40:
            requests = 0
            continue_input = input('40 requests reached. Type "1" if you want to continue?')
            if not continue_input == '1':
                break
        logging.info("switched to the new page")

        click_next()
        make_http_request()

    review_number -= 1  # just to have  a correct logging.info fetching reviews number
    logging.info("you fetched %s reviews", review_number)
    logging.info("made %s http requests", total_requests)
    with open("erasmus_intern_results.json", "a+") as write_reviews_json:
        write_reviews_json.write('\n')
        json.dump(data, write_reviews_json, sort_keys=True, indent=4, ensure_ascii=True)
        logging.info("json file written successfully")
    driver.close()


if __name__ == "__main__":
    main()
    logging.info("End of Program")
