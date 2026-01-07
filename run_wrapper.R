
        library(dplyr)
        library(readr)
        library(lubridate)
        library(haven)

        source("dummy_script.R")
        
        # Create dummy DF
        df <- data.frame(o = 0, u = 0, t = 0, p = 0, u = 0, t = 0, . = 0, c = 0, s = 0, v = 0)
        
        # Run safely
        tryCatch({
            result <- logic_pipeline(df)
            write.csv(result, "/home/jonny/git/state_machine/r_output.csv", row.names = FALSE)
        }, error = function(e) {
            # Print to stderr so Python catches it
            message("CRITICAL R ERROR: ", e$message)
            quit(status = 1)
        })
        