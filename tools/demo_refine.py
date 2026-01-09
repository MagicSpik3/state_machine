# demo_refine.py
import logging
from code_forge.refiner import CodeRefiner

# Setup logs to see what happens
logging.basicConfig(level=logging.INFO)

rough_code = """
logic_pipeline <- function(df) {
  df <- df %>%
    mutate(dob_date = DATE.MDY(
      trunc((dob_num %%10000)/100),
      (dob_num %%100), 
      trunc(dob_num/10000)
    ))
  return(df)
}
"""

print("--- ROUGH DRAFT ---")
print(rough_code)
print("\n... Sending to Qwen ...\n")

refiner = CodeRefiner(model="qwen2.5-coder:latest")
final = refiner.refine(rough_code)

print("--- REFINED OUTPUT ---")
print(final)