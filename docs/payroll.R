library(dplyr)
library(readr)
library(lubridate)
library(haven)

#' Logic Pipeline
#' @param df Main dataframe
#' @export
logic_pipeline <- function(df) {
  df <- df %>%
    mutate(gross = 50000,
           tax_rate = 0.20,
           tax = gross * tax_rate,
           net_pay = gross - tax)
  return(df)
}