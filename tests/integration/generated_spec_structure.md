# Business Logic Specification

## Chapter 1: Control Variable: Minimum Age
* **MIN_AGE_N_0**: Calculates the minimum age threshold.
  > `COMPUTE min_age_n = NUMBER(value, F3.0).`

## Chapter 2: Calculate Payment
* **###SYS_JOIN_1###_0**: The logic calculates the target variable based on inputs.
  > `MATCH FILES /FILE=* /TABLE='control_values.sav' /BY join_key.`
* **###SYS_JOIN_2###_0**: The logic calculates the target variable based on inputs.
  > `MATCH FILES /FILE=* /TABLE='benefit_rates.sav' /BY benefit_type.`
* **PAYMENT_AMOUNT_0**: The logic calculates the target variable based on inputs.
  > `COMPUTE payment_amount = eligible_days * daily_rate.`
