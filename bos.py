from umbrel import UmbrelClass
from coin_os import Coinos
from selenium.webdriver.common.by import By
import math
import random
import time

from IPython.display import clear_output

class BOS(UmbrelClass):
    '''Deals with BOS app'''

    _increment_fee = 1.5
    amount_to_loopout = 0
    bos_port = ':8055'

    def __init__(self, umbrel_2fa, umbrel_password, bos_username, bos_password, max_ppm):
        super().__init__(umbrel_2fa, umbrel_password)
        self.__bos_username = bos_username
        self.__bos_password = bos_password
        self._open_bos()
        self.max_ppm = max_ppm
        
    def log_it(self, msg):
        t = time.ctime()
        msg = f'{t},{msg}\n'
        with open('./loopout_log.txt', 'a') as a_writer:
            a_writer.write(msg)

    def _open_bos(self):
        self.get(self.base_url + self.bos_port)
        time.sleep(5)
        self._restart_bos_if_needed()

    def _restart_bos_if_needed(self):
        url = self.base_url + self.bos_port + '/auth/Login'
        if self.current_url == url:
            self._first_open_bos()
        
    def _first_open_bos(self):
        i = self.find_element(By.ID, 'accountName')
        i.send_keys(self.__bos_username)

        p = self.find_element(By.ID, 'password')
        p.send_keys(self.__bos_password)
        time.sleep(1)

        b = self.find_elements(By.TAG_NAME, 'button')[1]
        b.click()
        time.sleep(3)
        
    def pay_invoice(self, invoice, max_fee='10'):
        bos_url = self.parse_bos_url(invoice, max_fee=max_fee)
        self._open_bos()
        self.get(bos_url)
    
    def parse_bos_url(self, invoice, avoid_high_fee_routes = 'true', max_fee='10'):
        if type(max_fee) != str:
            max_fee = str(max_fee)
        url = f'{self.base_url}{self.bos_port}/result/PayResult?message=&node=&avoid=&in_through=&is_strict_max_fee={avoid_high_fee_routes}&max_fee={max_fee}&max_paths=0&out=&request={invoice}'
        return url
    
    def parse_invoice_from_coinos(self, amount):
        c = Coinos()
        invoice = c.parse_invoice(amount)
        c.quit()
        return invoice
    
    def read_pre_msg(self):
        msg = self.find_element(By.TAG_NAME, 'pre').text
        return msg
    
    def calculate_max_fee(self, max_ppm=500):
        max_fee = max_ppm / 1000000 * self.amount_to_loopout
        return max(1, int(max_fee))
    
    def too_expensive(self, max_fee):
        multiplier = round(self.amount_to_loopout / 10000)
        worst_case = self.calculate_max_fee(self.max_ppm)
        worst_fee = worst_case * multiplier
        return min(max_fee, worst_fee)
    
    def deal_with_pre_msg(self, msg):

        if msg.find('success') > 0:
            log_msg = 'success'
            self.log_it(log_msg)
            return 'success'
        
        elif msg.find('is_failed: true') > 0:
            log_msg = 'failed - increasing fee'
            self.log_it(log_msg)
            return 'failed'
        
        return ''
    
    def calculate_invoice_and_max_fee(self, max_ppm):
        
        amount_rand = self.amount_to_loopout + random.randint(0, 100)
        max_fee = self.calculate_max_fee(max_ppm)
        invoice = self.parse_invoice_from_coinos(amount_rand)
        
        return (invoice, max_fee)
    
    def try_pay_invoice(self, invoice, max_fee):
        self.pay_invoice(invoice, max_fee)
        
        for i in range(60*24):
            time.sleep(5)

            try:
                pre_msg = self.read_pre_msg()
            except Exception as e:
                log_msg = repr(e)
                self.log_it(log_msg)
                break

            response = self.deal_with_pre_msg(pre_msg)
            if response == 'success':
                return
            elif response == 'failed':
                max_fee = math.ceil(max_fee * self._increment_fee)

                max_fee = self.too_expensive(max_fee)
                
                log_msg = f'no paths - trying again, max fee: {max_fee}'
                self.log_it(log_msg)

                self.pay_invoice(invoice, max_fee)

                
        log_msg = 'invoice expired - parsing new invoice'
        self.log_it(log_msg) 

    def loop_out(self, amount, n_times=3, max_ppm=500):
        self.amount_to_loopout = amount
        
        # each iteration means one invoice
        for t in range(n_times):
            invoice, max_fee = self.calculate_invoice_and_max_fee(max_ppm)
            self.log_it(f'starting new invoice - amount: {self.amount_to_loopout}, max fee: {max_fee}')
            self.try_pay_invoice(invoice, max_fee)

        print('finished iterations')