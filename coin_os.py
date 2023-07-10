from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class Coinos(webdriver.Firefox):

    def parse_invoice(self, amount):
        try:
            int(abs(amount))
        except TypeError:
            print('amount must be a number')
            return None
        
        amount = str(amount)

        self.get('https://coinos.io/paulo.minozzo')
        time.sleep(5)

        b = self.find_elements(By.TAG_NAME, 'button')[1]
        b.click()
        time.sleep(3)

        # TODO: change to EC expected conditions
        change_to_sats = self.find_element(By.XPATH, 
                                           '/html/body/div/main/form/div/div/div/div[1]/div[2]/button')
        change_to_sats.click()
        time.sleep(.5)

        numbers_div = self.find_element(By.XPATH, '/html/body/div/main/form/div/div/div/div[2]')
        buttons = numbers_div.find_elements(By.TAG_NAME, 'button')
        for n in amount:
            if n != '0':
                buttons[int(n) - 1].click()
            else:
                buttons[10].click()
            time.sleep(.5)

        next_btn = self.find_element(By.XPATH, '/html/body/div/main/form/div/button')
        next_btn.click()
        time.sleep(3)

        invoice_link = self.find_element(By.PARTIAL_LINK_TEXT, 'lnbc')
        invoice = invoice_link.get_attribute('href').split(':')[1]

        return invoice