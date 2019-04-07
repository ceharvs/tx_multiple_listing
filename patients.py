# Modeling Advantages in the Transplant Waiting List.

'''Model to simulate the waiting list and multiple registrations in the organ transplant system.  '''

import numpy.random as npr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner 

class Patient(Agent):
    '''
    A patient in the simulation.
    
    Attributes:
        condition: Waiting or Selected or Transplanted or Deceased
        regions: regions where the patient is waiting
        my_id: Integer identifier, represents order the agent is added to the model
        primary: Primary listing region of the agent
        lifespan: Lifespan of the agent before selection
        waiting: amount of time spent waiting on the list
        advantaged: whether or not the patient is advantaged
        
    '''
    def __init__(self, unique_id, model, regions, lifespan, waiting=0):
        '''
        Create a new agent
        Args: 
        '''
        super().__init__(unique_id, model)
        self.my_id = str(unique_id)
        self.regions = regions
        self.primary = self.regions[0]
        self.condition = "Waiting"
        self.lifespan = lifespan
        self.waiting = waiting
        if len(regions) > 1:
            self.advantaged = True
        else:
            self.advantaged = False
        
    def selected(self):
        '''
        Set the patient's condition to "Selected"
        '''
        self.condition = "Selected"
        
    def get_advantaged(self):
        '''
        Check if patient is advantaged
        '''
        return self.advantaged
    
    def get_waiting(self):
        '''
        Get the patient's waiting years
        '''
        return self.waiting
        
    def get_primary(self):
        '''
        Return the patient's primary listing
        '''
        return self.primary
            
    def get_condition(self):
        '''
        Return the patient's condition
        '''
        return self.condition
        
    def step(self):
        '''
        If a patient is at the top of the list, they will receive a transplant
        Age the patient by one time step.
        If the patient has been selected, change their condition to transplanted
        Else: if the patient is waiting and waiting >= lifespan, change condition to Deceased
        '''
        # Increment the patient's waiting
        if self.condition == "Waiting":
            self.waiting += 1
        # Convert person to transplant
        if self.condition == "Selected":
            self.condition = "Transplanted"
        # Convert person to deceased
        elif self.condition == "Waiting" and self.waiting >= self.lifespan:
            self.condition = "Deceased"
        
    def __str__(self):
        return str(self.my_id)