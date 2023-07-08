from selenium import webdriver
from selenium.webdriver.common.by import By

import time


class UmbrelClass(webdriver.Firefox):
    '''geckodriver must be in path'''
    def __init__(
        self, umbrel_2fa, umbrel_password,
        base_url
    ):
        '''starts in umbrel page'''
        super().__init__(
            # options=None,
            # service=None,
            # keep_alive=True,
        )
        self.base_url = base_url
        # self.__umbrel_password = umbrel_password
        # self.__umbrel_2fa = umbrel_2fa
        
        self.get(self.base_url)
        self.login_umbrel(umbrel_password, umbrel_2fa)
        
    def login_umbrel(self, umbrel_password, umbrel_2fa):
        
        time.sleep(3)
        i = self.find_element(By.TAG_NAME, 'input')
        i.send_keys(umbrel_password)
        time.sleep(.5)

        xpath = '/html/body/div/div[2]/div/form/div[2]/button'
        b = self.find_element(By.XPATH, xpath)    
        b.click()
        time.sleep(3)

        two_fa_id = '__BVID__19'
        two_fa = self.find_element(By.ID, two_fa_id)
        two_fa.send_keys(umbrel_2fa)
        time.sleep(5)