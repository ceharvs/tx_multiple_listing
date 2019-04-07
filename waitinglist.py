# Modeling Advantages in the Transplant Waiting List.

"""Model to simulate the waiting list and multiple registrations in the organ transplant system.  """

from data_import import *
from patients import Patient
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from collections import deque


class WaitingList(Model):
    """
    Waiting List model describing multiple queues and registration listing in the organ
    transplant system.
    """
    def __init__(self, DSAs, advantage_prob=0.05, output=False, average_lifespan=98, years=20,
                 smart_listing=True, seed=42):
        """
        Method to initialize the model

        arguments:
            DSAs: DSAs to be portrayed in the model.  This can be a selection of the DSA code,
                split by commas without spaces("CAOP,ILIP,INOP,MNOP") or the word "ALL" to indicate all DSAs
                should be used.
            advantage_prob: Probability that a patient in the model will be "advantaged" and
                therefore able to register on more than one list.
            output: flag for the output of the model, set to true by default, can be turned off in batch mode
            average_lifespan: average lifespan for a patient
            years: number of years to run the model for
            smart_listing: flag for whether agents will pick alternate waiting lists based on shorter queues
            seed: Random seed for model
        """
        print("Running model for: ", advantage_prob)

        # Initialize model parameters
        # Check if DSAs Specified a certain group or ALL
        if DSAs == 'ALL':
            self.DSAs = get_all_dsas()
        else:
            self.DSAs = DSAs.split(',')
        self.regions = len(self.DSAs)
        self.advantage_probability = advantage_prob
        self.output = output
        self.average_lifespan = average_lifespan
        self.smart_listing = smart_listing
        self.months = years*12

        # Pull information for the selected DSAs
        self.rates = get_transplant_rates(self.DSAs)
        self.initial_queue_probabilities = get_initial_queue_probabilities(self.DSAs)
        self.additional_queue_probabilities = get_additional_queue_probabilities(self.DSAs)
        self.initial_patients = get_wl_size(self.DSAs)
        self.additional_patients = get_additional_patients(self.DSAs)

        npr.seed(int(seed))

        # Set up initial values for tracking model state
        self.ticks = 0
        self.candidates = 0

        # Set up the list of queues for the waiting lists
        self.queues = []

        # Set up small lists to track the outcomes of each of the waiting lists
        self.primary_listing_transplant = []  # TX of a patient that was a primary listing
        self.alternate_listing_transplant = []  # TX of a patient that was an alternate listing
        self.primary_waiting = []  # Number of Primary Patients added to the Waiting List
        self.alternate_waiting = []  # Number of Alternate Patients added to the Waiting List
        self.waiting_list_start = [] # Tracks where the method should pick up for the queue

        # Set up model objects, to track the number of patients in each state.
        self.schedule = RandomActivation(self)
        self.dc = DataCollector({"Waiting": lambda m: self.count_type(m, "Waiting"),
                                 "Selected": lambda m: self.count_type(m, "Selected"),
                                 "Deceased": lambda m: self.count_type(m, "Deceased"),
                                 "Transplanted": lambda m: self.count_type(m, "Transplanted")})

        # Initialize all the regions
        for i in range(self.regions):
            self.queues.append([])
            self.primary_listing_transplant.append(0)
            self.alternate_listing_transplant.append(0)
            self.primary_waiting.append(0)
            self.alternate_waiting.append(0)
            self.waiting_list_start.append(0)

        self.add_candidates(self.initial_patients, initial=True)

        self.running = True

    def add_candidates(self, num_to_add, initial=False):
        """
        Add people to the regions

        args:
        num_to_add: number of agent to add
        initial: Whether or not this is the initial round of patients
        """

        # Use the initial or additional probabilities listing - depending on the mode
        if initial:
            queue_probabilities = self.initial_queue_probabilities

            # Create probability tables on the waiting list time from the OTPN data on the website.
            options = [[0, 1], [1, 3], [3, 6], [6, 12], [12, 24], [24, 36], [36, 60], [60, 80]]
            initial_prob = [0.0411, 0.0665, 0.0825, 0.1368, 0.2004, 0.1409, 0.1830, 0.1488]
            # Choose the waiting range for the patient
            patient_waiting_range = list(npr.choice(len(options), num_to_add, replace=True, p=initial_prob))

        else:
            queue_probabilities = self.additional_queue_probabilities

        # Generate the list of regions to add patients to
        all_patient_regions = npr.choice(self.regions, num_to_add, replace=True, p=queue_probabilities)

        # Place a person in each region
        for i in range(num_to_add):

            # Set the regions for this patient
            primary_region = all_patient_regions[i]
            patient_region = [primary_region]

            # Select the region from the generated list
            self.primary_waiting[primary_region] += 1


            # Determine if the patient is advantaged
            if npr.rand() <= self.advantage_probability:
                # Remove the primary region from the list of possibilities
                possible_regions = list(range(self.regions))
                possible_regions.remove(primary_region)

                # if using self.smart-listing, remove the chosen primary region from the rankings
                if self.smart_listing:
                    queue_sizes = []

                    # Calculations of transplant rates/waiting list size calculations - for smart listing
                    for region in range(self.regions):
                        queue_sizes.append(len(self.queues[region]))

                    # Compute the best regions to add to by computing the number
                    # of TX per queue size
                    best_choice_score =  list(np.array(self.rates).astype('float')/(np.array(queue_sizes)+1))
                    best_choice_score.pop(primary_region)
                    probs = np.array(best_choice_score)/sum(best_choice_score)

                    # Select 1 to 4 more regions to join the waiting list
                    secondary_listings = list(npr.choice(possible_regions, npr.randint(1, 4),
                                                         replace=False, p=probs))
                else:
                    secondary_listings = list(npr.choice(possible_regions, npr.randint(1, 4),
                                                         replace=False))

                patient_region.extend(secondary_listings)

                # Add patient counts to alternate_waiting structure
                for listing in secondary_listings:
                    self.alternate_waiting[listing] += 1

            patient_id = self.candidates
            self.candidates += 1

            # If this is the initial patient addition, provide the patient with waiting time.
            if initial:
                # Use the time range to select the waiting time - uniformly distributed within the range.
                patient_waiting = npr.randint(options[patient_waiting_range[i]][0],
                                              options[patient_waiting_range[i]][1])
                patient_lifespan = 5*npr.randn(1)[0] + self.average_lifespan

                # Ensure Patients don't have a shorter lifespan than
                # the time they've already spend waiting.
                # RE-compute the lifespan until it's longer than their
                # time waiting.  We assume that any patient with
                # a shorted lifespan than their time waiting has
                # passed away before the start of the simulation.
                while patient_waiting > patient_lifespan:
                    patient_lifespan = 5*npr.randn(1)[0] + self.average_lifespan
                    print(patient_waiting, patient_lifespan)

            else:
                patient_waiting = 0
                # Set the patient's lifespan using a normal random
                # number distribution N(average_lifespan, 25)
                patient_lifespan = 5*npr.randn(1)[0] + self.average_lifespan

            # Create the patient
            new_patient = Patient(patient_id, self, patient_region,
                                  patient_lifespan, patient_waiting)

            # Add to the queue
            for q in patient_region:
                self.queues[q].append(new_patient)

            # Add the the schedule
            self.schedule.add(new_patient)

    def step(self):
        """
        Advance the model by one step.
        1. Print out the year
        2. Shuffle the order of the lists so the allocation to lists is random.
        3. For each of the regions in the model:
            a. Select the number of transplants to perform using a poisson distribution, n
            b. Mark the first n patients to be transplanted
        4. Add new candidates to the list.
        5. Increase the time stamp by one.
        """

        self.schedule.step()
        self.dc.collect(self)

        # Print out the year
        if (self.ticks % 12) == 0:
            print("... Model Year:\t %d" % (self.ticks / 12))

        # Shuffle the order of the lists
        region_list = list(range(self.regions))
        npr.shuffle(region_list)

        # Loop through the regions to allocate organs.
        for i in region_list:
            # transplants to be performed
            num_to_select = npr.poisson(self.rates[i])
            starting_point = self.waiting_list_start[i]
            queue = deque(self.queues[i][starting_point:])

            # Mark the first num_to_select patients as selected
            j = 0
            while j < num_to_select and len(queue) > 0:

                # Increment the starting point by one for the next iteration
                starting_point += 1

                # Select the top patient on the list
                top_of_list = queue.popleft()
                # Get the status of the patient
                top_status = top_of_list.get_condition()
                # Get whether the patient was on this list as their primary
                top_primary = top_of_list.get_primary()

                # If this is the primary listing location, add to the
                # number of primary transplants given
                if top_status == "Waiting":
                    top_of_list.selected()
                    if top_primary == i:
                        self.primary_listing_transplant[i] += 1
                    else:
                        self.alternate_listing_transplant[i] += 1
                    j += 1

            self.waiting_list_start[i] = starting_point

        # Add new patients
        self.add_candidates(npr.poisson(self.additional_patients))

        # Add a time stamp
        self.ticks += 1

        # Halt if no more waiting or TS >= Max Time
        if self.count_type(self, "Waiting") == 0 or self.ticks > self.months:
            if self.output:
                self.finalize()
            self.running = False



    def print_queue(self):
        # Print out the initial Queues
        for queue in self.queues:
            q = []
            for candidate in queue:
                q.append(str(candidate))
            print(q)

    @staticmethod
    def count_type(model, patient_condition):
        """
        Helper method to count patients in a given condition in a given model.
        """
        count = 0
        for patient in model.schedule.agents:
            if patient.condition == patient_condition:
                count += 1
        return count

    def get_primary_center_transplants(model):
        return sum(model.primary_listing_transplant)

    def get_alternate_center_transplants(model):
        return sum(model.alternate_listing_transplant)

    def get_primary_listings(model):
        return sum(model.primary_waiting)

    def get_alternate_listings(model):
        return sum(model.alternate_waiting)

    def get_waiting(model):
        """
        Return the total number of patients waiting for a transplant.
        """
        count = 0
        for patient in model.schedule.agents:
            if patient.get_condition() == "Waiting":
                count += 1
        return count

    def get_transplants(model):
        """
        Get the total number of transplants.
        """
        count = 0
        for patient in model.schedule.agents:
            condition = patient.get_condition()
            if condition == "Transplanted" or condition == "Selected":
                count += 1
        return count

    def get_advantaged_transplants(model):
        """
        Return the total number of advantaged patients that received a transplant.
        """
        count = 0
        for patient in model.schedule.agents:
            condition = patient.get_condition()
            if condition == "Transplanted" or condition == "Selected":
                if patient.get_advantaged():
                    count += 1
        return count

    def get_advantaged_deceased(model):
        """
        Return the total number of advantaged patients that received a transplant.
        """
        count = 0
        for patient in model.schedule.agents:
            if patient.get_condition() == "Deceased":
                if patient.get_advantaged():
                    count += 1
        return count

    def get_deceased(model):
        """
        Return the total number of patients that died.
        """
        count = 0
        for patient in model.schedule.agents:
            if patient.get_condition() == "Deceased":
                count += 1
        return count

    def get_average_waiting(model):
        """
        Return average time spent waiting for patients that received a
        transplant.
        """
        count = 0
        waiting_time = 0
        for patient in model.schedule.agents:
            condition = patient.get_condition()
            if condition == "Transplanted" or condition == "Selected":
                count += 1
                waiting_time += patient.get_waiting()
        return waiting_time / float(count)

    def get_average_waiting_advantaged(model):
        """
        Return average time spent waiting for ADVANTAGED patients
        that received a transplant.
        """
        count = 0
        waiting_time = 0
        for patient in model.schedule.agents:
            condition = patient.get_condition()
            if condition == "Transplanted" or condition == "Selected":
                if patient.get_advantaged():
                    count += 1
                    waiting_time += patient.get_waiting()
        if count == 0:
            return 0
        else:
            return waiting_time / float(count)

    def get_primary_waiting_rates(model):
        """
        Return average time spent waiting for patients that received
        a transplant on each list.
        """
        count = [0] * model.regions
        wrates = [0] * model.regions
        for patient in model.schedule.agents:
            condition = patient.get_condition()
            if condition == "Transplanted" or condition == "Selected":
                p = patient.get_primary()
                count[p] += 1
                wrates[p] += patient.get_waiting()
        return np.array(wrates).astype('float') / np.array(count).astype('float')

    def get_primary_deaths_regional(model):
        """
        Return deaths before transplant for each list.
        """
        deaths = [0] * model.regions
        for patient in model.schedule.agents:
            p = patient.get_primary()
            if patient.get_condition() == "Deceased":
                deaths[p] += 1
        return deaths

    def get_primary_wl_regional(model):
        """
        Return primary WL size per region.
        """
        count = [0] * model.regions
        for patient in model.schedule.agents:
            condition = patient.get_condition()
            if condition == "Waiting":
                p = patient.get_primary()
                count[p] += 1
        return count

    def get_primary_tx_regional(model):
        """
        Return txs for each list.
        """
        tx = [0] * model.regions
        for patient in model.schedule.agents:
            p = patient.get_primary()
            condition = patient.get_condition()
            if condition == "Transplanted" or condition == "Selected":
                tx[p] += 1
        return tx

    def finalize(model):
        print("Number of primary Center Transplants: \t", str(model.primary_listing_transplant))
        print("Number of alternate Center Transplants: \t", str(model.alternate_listing_transplant))
        print("Number of deceased before transplant - advantaged: \t" + str(model.get_advantaged_deceased()))
        print("Number Primary Listings: \t" + str(model.primary_waiting))
        print("Number Alternate Listings: \t" + str(model.alternate_waiting))
        print("Percent of transplants that were advantaged: " + str(model.get_advantaged_transplants()))
        print("Average Wait Time: " + str(model.get_average_waiting())+"\n")
        print("Average Primary Waiting Time" + str(model.get_primary_waiting_rates()))
        print("Average Deaths" + str(model.get_primary_deaths_regional()))
        print("\n")
