from selenium import webdriver
import undetected_chromedriver as uc

driver = uc.Chrome()
driver.get("https://www.google.com")

# search_box = driver.find_element("name", "q")
# search_box.send_keys("Selenium Python")
# search_box.submit()