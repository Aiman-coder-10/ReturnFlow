# ReturnFlow

ReturnFlow is a policy-driven returns and refund management system for an e-commerce and retail business.

## Project Overview

ReturnFlow helps an online retailer manage customer returns using a consistent set of return policies.

The system allows users to look up orders, check return eligibility, record returns, calculate refunds, and track return statuses.

## Core Features

1. Look up an order by order ID and view its items.
2. Check return eligibility based on days since delivery and product category rules.
3. Record a return using a fixed list of reason codes.
4. Calculate the refund amount after applicable shipping or restocking charges.
5. Track return status and summarize returns by reason.

## Stretch Features

- Flag customers with more than 3 returns within 30 days.
- Allow exchanges instead of refunds when replacement stock is available.

## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript
- Git
- GitHub

## Project Structure

```text
ReturnFlow/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
├── static/
└── database/
    └── schema.sql