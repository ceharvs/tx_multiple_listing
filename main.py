# Modeling Advantages in the Transplant Waiting List.

'''Model to simulate the waiting list and multiple registrations in the organ
transplant system.
Run as:
python3 main.py seed multiply_listed_percent output_file'''

from waitinglist import WaitingList

from mesa.batchrunner import BatchRunner 

import sys

# At the end of each model run, calculate the fraction of trees which are Burned Out
model_reporter = {"Primary_Transplants": WaitingList.get_primary_center_transplants,
                  "Alternate_Transplants": WaitingList.get_alternate_center_transplants,
                  "Transplants": WaitingList.get_transplants,
                  "Primary_Listings": WaitingList.get_primary_listings,
                  "Alternate_Listings": WaitingList.get_alternate_listings,
                  "Count_Waiting": WaitingList.get_waiting,
                  "Count_Deceased": WaitingList.get_deceased,
                  "Count_Advantaged_Deceased": WaitingList.get_advantaged_deceased,
                  "Advantaged_Transplants": WaitingList.get_advantaged_transplants,
                  "Average_Wait": WaitingList.get_average_waiting,
                  "Death_Region": WaitingList.get_primary_deaths_regional,
                  "Primary_WL": WaitingList.get_primary_wl_regional,
                  "Primary_TX": WaitingList.get_primary_tx_regional,
                  "Wait_Rates": WaitingList.get_primary_waiting_rates,
                  "Advantaged_Wait": WaitingList.get_average_waiting_advantaged}

# Set the seed
s = sys.argv[1]

# Define the fixed parameters
fixed_params = {"DSAs": "ALL",  # ""CAOP,ILIP,INOP,MNOP",
                "output": False,
                "average_lifespan": 91,
                #"seed": s,
                "years": 20,
                "smart_listing": True,
                "advantage_prob": float(sys.argv[2])/100}

# Define the varied parameters
variable_params = {"seed": [s * 100 for s in range(5)]}


# Create the batch runner
param_run = BatchRunner(WaitingList, fixed_parameters=fixed_params,
                        variable_parameters=variable_params, 
                        model_reporters=model_reporter)
param_run.run_all()

# Sort the columns
c = ["DSAs","advantage_prob", "seed", "Primary_Transplants",
     "Alternate_Transplants", "Transplants", "Primary_Listings",
     "Alternate_Listings", "Count_Waiting", "Count_Deceased",
     "Count_Advantaged_Deceased", "Advantaged_Transplants",
     "Average_Wait", "Death_Region", "Primary_WL",
     "Primary_TX", "Wait_Rates", "Advantaged_Wait"]

df = param_run.get_model_vars_dataframe()
df[c].to_csv(sys.argv[3])
