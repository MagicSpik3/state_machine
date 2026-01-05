# Business Logic Specification

## Chapter 1: Subject Status and Age at Date of Birth
* **DOB_1**: The system sets the Date of Birth (DOB_1) to a fixed value '1980-01-01' regardless of any other factors or dependencies.
* **AGE_0**: The logic calculates the age (AGE_0) by subtracting the four-digit year of birth (extracted from DOB_1) from the current year (2026).
* **STATUS_0**: If an individual's age exceeds 65, then their status is computed as 'Retired', implying that the status of being retired depends on the individual reaching a certain age.

## Chapter 3: Income, Tax Rate, Tax Deducted, Net Paycheck
* **TAX_RATE_0**: The logic step sets the Tax Rate (TAX_RATE_0) to a fixed value of 0.20, indicating a tax rate of 20%.
* **GROSS_0**: The logic step sets the value of Gross (GROSS_0) to a fixed amount of 50,000.
* **TAX_0**: The computation of tax (TAX_0) is determined by multiplying the gross amount (GROSS_0) by the tax rate (TAX_RATE_0).
* **NET_PAY_0**: The computation of Net Pay (NET_PAY_0) is derived by subtracting the Tax (TAX_0) from the Gross salary (GROSS_0).
