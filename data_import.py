# Modeling Advantages in the Transplant Waiting List.

"""Helper functions to read in data elements from OPTN data files. """

import numpy.random as npr
import numpy as np
import pandas as pd


def read_data():
    """Read in the data Files"""
    wl_additions = pd.read_csv('data/WLAdditions.csv')
    transplants = pd.read_csv('data/Transplants.csv')
    wl_removals = pd.read_csv('data/WLRemoval.csv')
    wl = pd.read_csv('data/WL.csv')

    # Remove commas from the data
    wl_additions['WL-Add-2017-Candidates'] = wl_additions['WL-Add-2017-Candidates'].str.replace(",", "").astype(int)

    # Only consider removals from 2017
    wl_removals_2017 = wl_removals[wl_removals['WL-Remove-Year'] == 2017]

    # Merge data and select important columns
    all_data = transplants.merge(wl_additions, on='DSA').merge(wl, on='DSA').merge(wl_removals_2017, on='DSA')
    all_data['WL-Ignored-Removals'] = all_data['WL-Remove-Living Donor Transplant'] + \
                                      all_data['WL-Remove-Transplanted in another country'] + \
                                      all_data['WL-Remove-Unable to contact candidate'] + \
                                      all_data['WL-Remove-Waiting for KP, will not Accept Isol. Or'] + \
                                      all_data['WL-Remove-Also Waiting for KP; recvd KP'] + \
                                      all_data['WL-Remove-Also Waiting for KP; WL-Remove-recvd Pancreas Alon'] + \
                                      all_data['WL-Remove-Refused transplant'] + all_data['WL-Remove-Other'] + \
                                      all_data['WL-Remove-Condition Improved'] + \
                                      all_data['WL-Remove-Transplanted At Another Center']
    all_data = all_data[['DSA', '2017-TX', 'WL-Add-2017-Candidates', 'WL-Candidates', 'WL-Remove-All Removal Reason',
                         'WL-Ignored-Removals',
                         'WL-Remove-Deceased Donor Transplant', 'WL-Remove-Died', 'WL-Remove-Too Sick to Transplant',
                         'WL-Remove-Transplanted At Another Center']]

    return all_data


def get_all_dsas():
    """Return a list of all DSAs in the database"""
    all_data = read_data()
    return list(all_data.DSA)


def get_wl_size(dsas):
    """Return the expected total Waiting List size (for initial model generation.)"""
    all_data = read_data()
    selected_data = all_data[all_data['DSA'].isin(dsas)]
    return sum(selected_data['WL-Candidates'])


def get_additional_patients(dsas):
    """Return the expected additional monthly patients."""
    all_data = read_data()
    selected_data = all_data[all_data['DSA'].isin(dsas)]
    # Return the number of candidates added in a year, minus those not acknowledged in the model and
    # divide by 12 to get the monthly rate
    return sum(selected_data['WL-Add-2017-Candidates'] - selected_data['WL-Ignored-Removals'])/float(12)


def get_transplant_rates(dsas):
    """Return the monthly transplants in each DSA"""
    all_data = read_data()
    selected_data = all_data[all_data['DSA'].isin(dsas)]
    transplant_rates = selected_data[['DSA', '2017-TX']]
    # Divide by 12 to get the correct number in months
    return list(transplant_rates['2017-TX'] / float(12) )


def get_additional_queue_probabilities(dsas):
    """Return the yearly queue probabilities for additions in each DSA"""
    all_data = read_data()
    selected_data = all_data[all_data['DSA'].isin(dsas)]
    queue_probabilities = selected_data['WL-Add-2017-Candidates'] / sum(selected_data['WL-Add-2017-Candidates'])
    return list(queue_probabilities)


def get_initial_queue_probabilities(dsas):
    """Return the yearly queue probabilities for the initial WL size in each DSA"""
    all_data = read_data()
    selected_data = all_data[all_data['DSA'].isin(dsas)]
    queue_probabilities = selected_data['WL-Candidates'] / sum(selected_data['WL-Candidates'])
    return list(queue_probabilities)