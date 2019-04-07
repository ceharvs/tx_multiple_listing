# Multiple Listings on the Organ Transplant List
This repository is the code base for agent-based model of multiple listings on the organ transplant system.  This is an agent-based model develoepd in Python using the Mesa module to implement the agent-based model component.  The goal of this code is to explore the impact of mulitple listings in the organ transplant system.  Input data included is all from the [OPTN Website](https://optn.transplant.hrsa.gov/data/view-data-reports/).

The model is designed to explore the impact when varying proporations of the kidney transplant waiting list are multiply listed, and are registered on a waiting list in more than one Donor Service Area (DSA). The model can be run with different in puts to explore different variations.

## Run the Model
To run the model first edit the inputs in `main.py` and then run the model with:
```python
python3 main.py seed multiply_listed_percent output_file
```

Where `seed` is a random input seed, used for reporducibility. The fraction of the populatino that is multiply listed is `multiply_listed_percent`, and the output file is directed with `output_file` as an input.  

A submit script, `run_python.sh` is included which demonstrates how to run this code on a scheduler such as TORQUE or MOAB. 

## Data
All data in the data folder was downloaded from the Organ Procurement and Transplantation Network (OPTN) Website and was downloaded on 16 May 2018.  The OPTN website offers a wealth of information about transplantation [Link](http://optn.transplant.hrsa.gov). Additional input data was gathered and computed from the United States Renal Data System (USRDS). 

This work was supported in part by Health Resources and Services Administration contract 234-2005-37011C. The content is the responsibility of the authors alone and does not necessarily reflect the views or policies of the Department of Health and Human Services, nor does mention of trade names, commercial products, or organizations imply endorsement by the U.S. Government.

The data reported here have been supplied by the United States Renal Data System (USRDS). The interpretation and reporting of these data are the responsibility of the author(s) and in no way should be seen as an official policy or interpretation of the U.S. government. 
