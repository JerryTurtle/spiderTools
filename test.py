from selenium import webdriver
import time


def test_click_next(start_url, rules_next_page, extension, time_delay=3):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(start_url)
    time.sleep(int(time_delay))
    if extension is not None and extension != '':
        eval(extension)
    try:
        while True:
            driver.find_element_by_partial_link_text(rules_next_page).click()
            time.sleep(time_delay)
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        driver.close()


if test_click_next('http://treaty.mfa.gov.cn/Treaty/web/index.jsp', "下一页", 'driver.switch_to.frame(0)'):
    print('OK')
