# **Crypto Token Checker Application**

## **Description**

This application is a tool that allows users to perform various checks on ERC20 tokens on the Ethereum blockchain. It has been designed to help individuals analyze these tokens, especially in the context of identifying potential scams or low-quality projects. The application is comprised of two main parts:

- **Checker.py**: This is a Python script that contains a class named `ERC20Checker`. This class has various methods that can be used to gather information about a token such as its name, contract source code, and top holders. It also includes checks for scam patterns in the contract code, whether the contract ownership has been renounced, liquidity, and market cap.

- **GUI**: This is a graphical user interface that interacts with the ERC20Checker class in `Checker.py`. The GUI makes it easy for non-technical users to interact with the application, inputting the contract address and getting the results displayed in a user-friendly manner.

## **Prerequisites**

- [Python 3.6](https://www.python.org/downloads/) or higher
- [Infura API](https://infura.io/) key for interacting with the Ethereum blockchain
- [Etherscan API](https://etherscan.io/apis) key for fetching contract ABIs and source code
- A suitable web driver for selenium. The current implementation uses Chrome, so you would need to have the [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) installed and its location added to your system PATH

## **Installation**

1. **Clone the repository**

```bash
$ git clone https://github.com/<your-username>/ERC20-Checker-App.git
```

2. **Navigate to the cloned directory**

```bash
$ cd ERC20-Checker-App
```

3. **Set up a virtual environment** (optional but recommended)

```bash
$ python -m venv env
```

4. **Activate the virtual environment**

- On Windows:
```bash
$ .\env\Scripts\activate
```

- On Unix or MacOS:
```bash
$ source env/bin/activate
```

5. **Install the required Python libraries**

```bash
$ pip install -r requirements.txt
```

6. **Store your Infura API key and Etherscan API key as environment variables**

- On Windows:
```bash
$ set INFURA_API_KEY=your_infura_api_key
$ set ETHERSCAN_API_KEY=your_etherscan_api_key
```

- On Unix or MacOS:
```bash
$ export INFURA_API_KEY=your_infura_api_key
$ export ETHERSCAN_API_KEY=your_etherscan_api_key
```

## **Usage**

1. **Run the GUI script**

```bash
$ python gui.py
```

2. **Input the contract address** of the ERC20 token you want to check in the text box and click the "Check" button.

3. The application will now use the `ERC20Checker` class in `Checker.py` to fetch information about the token and perform various checks. The results will be displayed in the GUI.

## **Notes**

Please be aware that due to the nature of blockchain data and the specificities of each smart contract, not all checks might return a result for every contract address. The application does its best to fetch and analyze as much data as possible, but in certain cases (like when a contract has non-standard implementation) the results might not be complete.

Also, this tool should not be used as the only means of due diligence when investing in ERC20 tokens. It is just one of many tools you should use to make informed decisions. Always do your own research.

## Contributions

I appreciate all contributions. If you're interested in contributing, please follow these steps:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Video Demo



https://github.com/DeanNunis1/Crypto-Token-Checker/assets/61598839/648b51bd-2493-448b-99b8-bf207cca3c83


