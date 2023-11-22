## Description

This project is a stock trading finance website built with Flask. It allows users to buy and sell stocks, view their transaction history, and track their portfolio. The website utilizes the IEX Cloud API for real-time stock quotes.

## Installation & Setup

To run the project locally, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your IEX Cloud API key as an environment variable named `API_KEY`.
4. Run the Flask application with `python app.py`.

## Usage

- Visit the homepage to view your portfolio, current balance, and performance.
- Use the "Buy" page to purchase stocks by entering the symbol and number of shares.
- The "Sell" page allows you to sell stocks from your portfolio.
- The "Transactions" page displays a history of all your stock transactions.
- The "Quote" page lets you look up the latest stock price by entering the symbol.

## Main Files

1. **app.py**: The main Flask application file containing routes and database interactions.
2. **helpers.py**: Helper functions for rendering apology messages, login requirements, stock quote lookups, and USD formatting.

## Database

The project uses an SQLite database with tables for users, transactions, and portfolio information.

## Features

- User authentication and registration.
- Real-time stock quotes using the IEX Cloud API.
- Portfolio tracking with buy and sell transactions.
- Transaction history with details on bought/sold stocks.

## Contribution Guidelines

If you would like to contribute to the project, please follow these guidelines:

1. Fork the repository and clone it to your local machine.
2. Create a new branch for your feature or bug fix.
3. Implement your changes and ensure they are properly tested.
4. Commit and push your changes to your forked repository.
5. Submit a pull request to the main repository, clearly explaining the changes you have made.

Your contributions are appreciated!

## Contact

If you have any questions, feedback, or suggestions regarding the stock trading finance website, feel free to reach out:

Name: Yashas Donthi  
Email: 2yashas2@gmail.com

## Release Notes: Version 1.0

- Initial release