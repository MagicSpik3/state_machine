
        source("payroll.R")
        
        # Create a dummy 1-row dataframe
        df <- data.frame(id = 1)
        
        # Run the pipeline
        tryCatch({
            result <- logic_pipeline(df)
            write.csv(result, "/home/jonny/git/state_machine/docs/r_output.csv", row.names = FALSE)
        }, error = function(e) {
            cat("Error:", e$message)
            quit(status = 1)
        })
        