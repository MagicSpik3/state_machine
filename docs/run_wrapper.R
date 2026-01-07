
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)

        source("payroll.R")
        
        # Create dummy DF
        df <- data.frame(GROSS = 0, TAX_RATE = 0, TAX = 0, NET_PAY = 0)
        
        # Run safely
        tryCatch({
            result <- logic_pipeline(df)
            write.csv(result, "/home/jonny/git/state_machine/docs/r_output.csv", row.names = FALSE)
        }, error = function(e) {
            # Print to stderr so Python catches it
            message("CRITICAL R ERROR: ", e$message)
            quit(status = 1)
        })
        