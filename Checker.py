import json
import re
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from uniswap import Uniswap
from web3.middleware import geth_poa_middleware
from collections import defaultdict
import random
from decimal import Decimal
load_dotenv()

# This class is used for analyzing ERC-20 Tokens for potential scam patterns
class ERC20Checker():
    def __init__(self, contract_address):
        # Retrieving API keys from environment variables
        self.infura_key = os.getenv('INFURA_API_KEY')
        self.etherscan_key = os.getenv('ETHERSCAN_API_KEY')

        # Ethereum address used for Uniswap
        ETHEREUM_ADDRESS = '0x9c0Ad4EBf1605EC9229d804215c2231df13cE408'

        # Establishing connection with Ethereum node
        self.w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{self.infura_key}"))

        # Check if connection is established
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum node.")

        # Convert the address to its checksummed version
        try:
            self.contract_address = self.w3.to_checksum_address(contract_address)
        except ValueError as e:
            raise ValueError("Invalid Ethereum address.") from e
        
        # Attempt to create a contract and Uniswap instance
        try: 
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.get_contract_abi())
            self.uniswap = Uniswap(ETHEREUM_ADDRESS, None, version=2, provider=f"https://mainnet.infura.io/v3/{self.infura_key}")
        except Exception as e:
            return e

    # Retrieves the name of the Token through a contract call    
    def get_name(self):
        try:
            name = self.contract.functions.name().call()
        except:
            # Fallback to 'Unknown' if 'name' function is not found
            name = 'Unknown Name'
        return name

    # Retrieves the contract abi through etherscan API    
    def get_contract_abi(self):
        try:
            etherscan_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={self.contract_address}&apikey={self.etherscan_key}"
            response = requests.get(etherscan_url)

            if response.status_code != 200:
                raise Exception("Failed to fetch contract ABI from Etherscan")

            data = response.json()

            if data['status'] != '1':
                raise Exception("Error fetching contract ABI from Etherscan")

            return json.loads(data['result'])
        
        except:
            return False
        
    # Retrieves the contract source code through etherscan API
    def get_contract_source_code(self):
        try:
            etherscan_url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={self.contract_address}&apikey={self.etherscan_key}"
            response = requests.get(etherscan_url)

            if response.status_code != 200:
                raise Exception("Failed to fetch contract source code from Etherscan")

            data = response.json()

            if data['status'] != '1':
                raise Exception("Error fetching contract source code from Etherscan")

            return data['result'][0]['SourceCode']
        except:
            pass
    
    # Parses the contract source code for common scam patterns 
    def check_scam_patterns(self):
        source_code = self.get_contract_source_code()
        # scam indicators in contract source code
        scam_patterns = [
            r"address public _Owner = 0x",
            r"swapAndLiquifyEnabled",
            r"function burn(uint256 value) external onlyOwner",
            r"address public constant router = 0x",
            r"bytes32 accountHash = 0x",
            r"setWhitelist",
            r"_user_"
        ]
        warnings = []
        for pattern in scam_patterns:
            if re.search(pattern, source_code):
                warnings.append(f"Suspicious pattern found: {pattern}, likely a SCAM")
        if warnings:
            return warnings
        if len(source_code) < 4000:
            warning = "Contract is very short, may indicate a SCAM if ownership is not renounced"
            return warning
        else:
            warning = "Source Code is Clean\nSafe✓"
            return warning

    # Utalizes webscraping to get buy, sell, cant sell and siphoned values of the token
    def scrape_honeypot(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://honeypot.is/ethereum?address={self.contract_address}")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "lxml")
        results = {}

        try:
            buy_tax = None
            sell_tax = None

            tax_div = soup.find('div', class_='grid grid-cols-[1fr_1fr] gap-0 md:grid-cols-[1fr_1fr_1.5fr]')
            if tax_div:
                taxes_selector = tax_div.find_all('li')
            else:
                taxes_selector = soup.find_all('li')

            for tax_selector in taxes_selector:
                tax_div = tax_selector.find('h4', class_='font-bebasNeue text-xl uppercase text-lightGreen')
                if tax_div:
                    tax_div_text = tax_div.get_text().strip()
                    if tax_div_text == "Buy Tax":
                        buy_tax = tax_selector.find('p', class_='font-bebasNeue text-2xl uppercase leading-none text-white').get_text().strip()
                    if tax_div_text == "Sell Tax":
                        sell_tax = tax_selector.find('p', class_='font-bebasNeue text-2xl uppercase leading-none text-white').get_text().strip()

            holder_div = soup.find_all('div', class_='grid grid-cols-[1fr_1fr] gap-0 md:grid-cols-[1fr_1fr_1.5fr]')[1]
            if holder_div:
                holders_selector = holder_div.find_all('li')
            else:
                holders_selector = soup.find_all('li')

            for holder_selector in holders_selector:
                holder_div = holder_selector.find('h4', class_='font-bebasNeue text-xl uppercase text-lightGreen')
                if holder_div:
                    holder_div_text = holder_div.get_text().strip()
                    if holder_div_text == "Can't sell":
                        cant_sell = holder_selector.find('p', class_='font-bebasNeue text-2xl uppercase leading-none text-white').get_text().strip()
                    if holder_div_text == "Siphoned":
                        siphoned = holder_selector.find('p', class_='font-bebasNeue text-2xl uppercase leading-none text-white').get_text().strip()
      
            if buy_tax and sell_tax and cant_sell and siphoned:
                buy_tax_float = float(buy_tax.rstrip('%'))
                sell_tax_float = float(sell_tax.rstrip('%'))
                cant_sell = int(cant_sell)
                siphoned = int(siphoned)
                results = {
                'buy_tax': f"Buy Tax: {buy_tax_float}%",
                'sell_tax': f"Sell Tax: {sell_tax_float}%",
                "cant_sell": f"Unable to Sell: {cant_sell}",
                'siphoned': f"Wallets Siphoned: {siphoned}"
                }

                if buy_tax_float > 10:
                    return f"{results['buy_tax']}\nWarning! Token might a Scam"
                elif sell_tax_float > 10:
                    return f"{results['sell_tax']}\nWarning! Token might a Scam"
                elif cant_sell >= 1:
                    return f"{results['cant_sell']}\nWarning! Token might a Scam"
                elif siphoned >= 1:
                    return f"{results['siphoned']}\nWarning! Token might a Scam"
                
                else:
                    return ', '.join(results.values()) + "\nSafe✓"
            else:
                return "Warning! Could not determine taxes, Token is likely a scam"
        except:
            return "Warning! Could not determine taxes, Token is likely a scam"
        finally:
            driver.quit()

    # Performs a contract call of owner function to get the current contract owner
    def is_ownership_renounced_or_no_owner(self):                           
        try:
            owner_address = self.contract.functions.owner().call()
        except:
            # Fallback to 'getOwner' if 'owner' function is not found
            try:
                owner_address = self.contract.functions.getOwner().call()
            except:
                owner_address = "Could not determine owner"
                return owner_address

        if owner_address == '0x0000000000000000000000000000000000000000' or owner_address == '0x000000000000000000000000000000000000dEaD':
            return owner_address +"\nSafe✓"
        else:
            owner = ("Ownership NOT Renounced\n" + "Owner: " + owner_address)
            return owner
        
    # Retrieves top token holders (1-10) through webscraping of Etherscan website
    def get_top_holders(self, top=10):
        etherscan_url = f"https://etherscan.io/token/{self.contract_address}#balances"
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
        driver = webdriver.Chrome(options=chrome_options)

        try:
            time.sleep(random.uniform(5, 10))  # Added delay before making a request
            driver.get(etherscan_url)
            time.sleep(3)
            driver.switch_to.frame("tokeholdersiframe")
            top_holders = []
            percentage_counts = {}  # Dictionary to count individual holders with same percentage

            for row in range(1, top + 1):
                rank = driver.find_element(By.XPATH, f'//*[@id="maintable"]/div[2]/table/tbody/tr[{row}]/td[1]').text
                try: 
                    address = driver.find_element(By.XPATH, f'//*[@id="maintable"]/div[2]/table/tbody/tr[{row}]/td[2]/div/a').get_attribute("data-clipboard-text").strip()
                except:
                    address = driver.find_element(By.XPATH, f'//*[@id="maintable"]/div[2]/table/tbody/tr[{row}]/td[2]/div/a[2]').get_attribute("data-clipboard-text").strip()

                percentage = driver.find_element(By.XPATH, f'//*[@id="maintable"]/div[2]/table/tbody/tr[{row}]/td[4]').text.strip('%')
                if address.startswith('0x00000000000000000000000000000000000'):
                    type = "Burn Address"
                else:
                    try:
                        type = driver.find_element(By.XPATH, f'//*[@id="maintable"]/div[2]/table/tbody/tr[{row}]/td[2]/div/i').get_attribute("aria-label").strip()
                    except:
                        try:
                            type = driver.find_element(By.XPATH, f'//*[@id="maintable"]/div[2]/table/tbody/tr[{row}]/td[2]/div/span/i').get_attribute("aria-label").strip()
                        except:
                            type = "individual"
                
                # Check the count of individuals with the same percentage
                if type == "individual":
                    if percentage in percentage_counts:
                        percentage_counts[percentage] += 1
                        if percentage_counts[percentage] > 2:
                            raise Exception(f"More than 3 individuals with same percentage ({percentage}%) found")
                    else:
                        percentage_counts[percentage] = 1
                top_holders.append(f"{rank} --- {address} --- {float(percentage)}% --- {type}")

            return "\n".join(top_holders)

        except Exception as e:
            top_holders = []
            return f"failed to get top holders"

        finally:
            driver.quit()

    # Performs webscraping of Dextools.io for data such as market cap, liquidity, 24hr percent change
    def market_cap(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://www.dextools.io/app/en/ether/pair-explorer/{self.contract_address}")
        wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'value')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        percentage = soup.find('span', class_='buy-color ng-star-inserted').get_text().strip()
        if percentage == 'buy':
            percentage = soup.find('span', class_='sell-color ng-star-inserted').get_text().strip()
        labels = soup.find_all('label')
        liquidity = None
        market_cap_value = None
        for label in labels:
            if 'Liquidity:' in label.text:
                liquidity = label.find_next_sibling('span').text
            if 'TMCap:' in label.text:
                market_cap_value = label.find_next_sibling('span').text
    
        driver.quit()
        if not liquidity and not market_cap_value:
            return f"Market information is N/A\nCould indicate a SCAM"
        elif not market_cap_value:
            return f"Liquidity:{liquidity} --- 24hr Change: {percentage}"
        elif not liquidity:
            return f"Market Cap: {market_cap_value} --- 24hr Change: {percentage}"
        else:
            return f"Liquidity:{liquidity} --- Market Cap: {market_cap_value} --- 24hr Change: {percentage}"
