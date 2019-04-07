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
