# Business Logic Specification

## Chapter 1: Tax Calculation Variables (TAX_RATE, NET_PAY, GROSS
* **GROSS_0**: The logic step sets the value of Gross (GROSS_0) to a fixed amount of 50,000.
* **TAX_RATE_0**: The logic step sets the Tax Rate (TAX_RATE_0) to a fixed value of 0.20, indicating a tax rate of 20%.
* **TAX_0**: The computation of the tax amount (TAX_0) is determined by multiplying the gross income (GROSS_0) with the tax rate (TAX_RATE_0).
* **NET_PAY_0**: The computation of Net Pay (NET_PAY_0) is derived by subtracting the Tax (TAX_0) from the Gross Salary (GROSS_0).
