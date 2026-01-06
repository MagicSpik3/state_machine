# Business Logic Specification

### ✅ Verified Execution
This logic was cross-referenced against a live PSPP execution.

## Chapter 1: Income & Tax Breakdown
* **TAX_RATE_0**: The logic step sets the Tax Rate (TAX_RATE_0) to a fixed value of 0.20, indicating a tax rate of 20%. <br> *Example Value: `0.2`*
* **GROSS_0**: The logic step sets the value of Gross (GROSS_0) to a fixed amount of 50,000. <br> *Example Value: `50000`*
* **TAX_0**: The calculation of tax (TAX_0) is derived by multiplying the gross amount (GROSS_0) by the tax rate (TAX_RATE_0). <br> *Example Value: `10000`*
* **NET_PAY_0**: The calculation of Net Pay (NET_PAY_0) is derived by subtracting the Tax (TAX_0) from the Gross Income (GROSS_0). <br> *Example Value: `40000`*
