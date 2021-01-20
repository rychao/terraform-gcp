from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import string
from selenium.webdriver.chrome.options import Options
import sys

global driver
chromeOptions = Options()
chromeOptions.headless = True #headless runs Chrome WITHOUT UI
driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=chromeOptions)

class Scraper(object):
    def __init__(self, url, email, firstName, lastName, address, city, zip, phone, cardNum, cardName, cardExp, ccv):
        self.url = url
        # self.size = size #ADD back in argument
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.address = address
        self.city = city
        self.zip = zip
        self.phone = phone
        self.cardNum = cardNum
        self.cardName = cardName
        self.cardExp = cardExp
        self.ccv = ccv

    def scrape_init(self):
        url = self.url
        size = sys.argv[2]
        print("Requested Size: ", size)
        driver.get(url)

        email = self.email
        firstName = self.firstName
        lastName = self.lastName
        address = self.address
        city = self.city
        zip = self.zip
        phone = self.phone
        cardNum = self.cardNum.split()
        cardName = self.cardName
        cardExp = self.cardExp.split()
        ccv = self.ccv

        if '.5' in size:         # SHOE SIZES (Mens US 3-15, EU 36-46)
            driver.find_element_by_xpath('//div[@data-value="{}" and @class="swatch-element {}"]'.format(size, size.replace(".5", "-5"))).click()
        else:
            driver.find_element_by_xpath('//div[@data-value="{}" and @class="swatch-element {}"]'.format(size, size.lower())).click()

        f = open("status.txt", "w+")
        driver.find_element_by_name('add').click()
        f.write("added to size  cart.\n".format(size))
        driver.implicitly_wait(60) # wait for cart button
        driver.find_element_by_name('checkout').click()
        f.write("made it to contact page.\n")
        driver.implicitly_wait(60) # wait 1 min in case of QUEUE

        emailInput = driver.find_element_by_id('checkout_email')
        emailInput.send_keys(email)
        driver.find_element_by_id('checkout_buyer_accepts_marketing').click()
        driver.find_element_by_id('checkout_shipping_address_first_name').send_keys(firstName)
        driver.find_element_by_id('checkout_shipping_address_last_name').send_keys(lastName)
        driver.find_element_by_id('checkout_shipping_address_address1').send_keys(address)
        driver.find_element_by_id('checkout_shipping_address_city').send_keys(city)
        driver.find_element_by_id('checkout_shipping_address_zip').send_keys(zip)
        driver.find_element_by_id('checkout_shipping_address_phone').send_keys(phone)
        driver.find_element_by_name('button').click()
        f.write("filled contact info.\n")

        #shipping button
        driver.find_element_by_name('button').click()

        driver.implicitly_wait(60)
        iframe = driver.find_element_by_class_name('card-fields-iframe') #cardNumber iframe
        driver.switch_to.frame(iframe)

        driver.find_element_by_name('number').send_keys(cardNum[0]) # w/o splitting, returns '4447'
        driver.find_element_by_name('number').send_keys(cardNum[1])
        driver.find_element_by_name('number').send_keys(cardNum[2])
        driver.find_element_by_name('number').send_keys(cardNum[3])

        driver.switch_to_default_content() #resets iframe
        iframe2 = driver.find_element_by_xpath('//iframe[contains(@id, "card-fields-name")]') #card name iframe
        driver.switch_to.frame(iframe2)
        driver.find_element_by_xpath('//input[@id="name"]').send_keys(cardName)

        driver.switch_to_default_content()
        iframe3 = driver.find_element_by_xpath('//iframe[contains(@id, "card-fields-expiry")]')
        driver.switch_to.frame(iframe3)
        driver.find_element_by_xpath('//input[@id="expiry"]').send_keys(cardExp[0])
        driver.find_element_by_xpath('//input[@id="expiry"]').send_keys(cardExp[1])

        driver.switch_to_default_content()
        iframe4 = driver.find_element_by_xpath('//iframe[contains(@id, "card-fields-verification_value")]')
        driver.switch_to.frame(iframe4)
        driver.find_element_by_xpath('//input[@id="verification_value"]').send_keys(ccv)
        f.write("filled out payment info.\n")

        driver.switch_to_default_content()
        driver.find_element_by_id('continue_button').click()
        f.write("clicked pay now button.\n")

def main():
    file = open(sys.argv[1])
    elements = json.loads(file.read())
    url = (elements['url'])
    # size = (elements['size'])
    email = (elements['email'])
    firstName = (elements['firstName'])
    lastName = (elements['lastName'])
    address = (elements['address'])
    city = (elements['city'])
    zip = (elements['zip'])
    phone = (elements['phone'])
    cardNum = (elements['card number'])
    cardName = (elements['card name'])
    cardExp = (elements['card expiry'])
    ccv = (elements['ccv'])

    #add size in scraper argument
    test = Scraper(url, email, firstName, lastName, address, city, zip, phone, cardNum, cardName, cardExp, ccv)
    test.scrape_init()

if __name__ == "__main__":
    sys.argv[:]
    main()
