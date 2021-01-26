import json
import logging
# from celery import Celery
# from google.cloud import firestore
# from google.auth.credentials import Credentials
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException


# app = Celery('wishlist', broker='redis://localhost')
# credentials = Credentials(token="/Users/seanhart/Documents/Slate/backend/Slate-e468090d1c78.json")
# chromedriver_path = "/usr/lib/chromium-browser/chromedriver"
chromedriver_path = "../local/chromedriver"
base_url = "https://www.reddit.com/r/wallstreetbets/"


def post(url) -> dict:
    logging.info(f"post: {url}")
    data = {'url': url}
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(
            executable_path=chromedriver_path,
            options=chrome_options
        )
        driver.get(url)

        # Get the main post text
        text_elements = driver.find_elements_by_xpath("//div[contains(@data-click-id,'text')]")
        texts = []
        for t in text_elements:
            texts.append(t.text)
        data['text'] = texts

        # Open the discussion to get the comments
        buttons = driver.find_elements_by_tag_name('button')
        for b in buttons:
            if b.text.rfind("View Entire Discussion") > -1:
                # Click the button to open the discussion
                b.click()

        # Get the main post text
        comment_elements = driver.find_elements_by_xpath("//div[contains(@data-test-id,'comment')]")
        print(f"COMMENT ELEMENTS COUNT: {len(comment_elements)}")
        comment_texts = []
        for c in comment_elements:
            comment_texts = c.find_elements_by_tag_name('p')
            for ct in comment_texts:
                try:
                    comment_texts.append(ct.text)
                except Exception as error:
                    comment_texts.append(ct)
        data['comments'] = comment_texts

    except NoSuchElementException as error:
        logging.error(f"NoSuchElementException: {error}")
    except TimeoutException as error:
        logging.error(f"TimeoutException: {error}")
    except WebDriverException as error:
        logging.error(f"WebDriverException: {error}")
    except Exception as error:
        logging.error(f"Exception: {error}")

    finally:
        return data


def wsb():
    logging.info(f"wsb: {base_url}")
    data = []
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(
            executable_path=chromedriver_path,
            options=chrome_options
        )
        driver.get(base_url)

        # Get the main page posts - remove duplicate references
        elements = driver.find_elements_by_xpath("//div[contains(@data-click-id,'background')]")
        href_elements = set()
        for e in elements:
            hrefs = e.find_elements_by_xpath(".//a[contains(@href,'')]")
            for h in hrefs:
                href_elements.add(h)

        # Parse the posts
        for h in href_elements:
            # Limit the posts to recent hours
            timestamp = e.find_elements_by_xpath(".//a[contains(@data-click-id,'timestamp')]")
            if len(timestamp) > 0:
                hours_index = timestamp[0].text.rfind('hours')
                hours = timestamp[0].text[:hours_index - 1]

                if hours_index > -1 and int(hours) < 8:
                    post_link = h.get_attribute('href')
                    data_post = {
                        'link': post_link,
                        'age_hours': hours
                    }
                    # Ensure the link is reddit
                    if post_link.rfind("reddit.com") > -1:
                        data_post.update(post(post_link))
                        print(data_post)
                        data.append(data_post)

    except NoSuchElementException as error:
        logging.error(f"NoSuchElementException: {error}")
    except TimeoutException as error:
        logging.error(f"TimeoutException: {error}")
    except WebDriverException as error:
        logging.error(f"WebDriverException: {error}")
    except Exception as error:
        logging.error(f"Exception: {error}")

    finally:
        logging.info("FINISH")
        print(data)


debug = False
if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] {%(filename)s:%(lineno)d} - %(name)s - %(levelname)s - %(message)s')
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    wsb()
