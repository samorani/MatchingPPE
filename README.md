# Framework for PPE Matching

## Table of Contents
  * [Overview](#overview)
    + [What is the PPE matching problem?](#what-is-the-ppe-matching-problem)
    + [Who needs to solve the PPE matching problem?](#who-needs-to-solve-the-ppe-matching-problem)
    + [What does this software package do?](#what-does-this-software-package-do)
  * [Installation](#installation)
  * [Simulation Class](#simulation-class)
    + [Parameters](#parameters)
    + [Methods](#methods)

 
## Overview
### What is the PPE matching problem?
The PPE Matching Problem consists of optimally matching a set of requests, D, made by donors interested in donating Personal Protective Equipment (or PPE, such as masks, gowns, gloves, etc) with a set of requests, R, made by recipients interested in receieving PPE. Requests are characterized by a timestamp (date), a type and quantity of PPE to donate or request, and a donor or recipient id. The input of the problem also includes a matrix M of distances between donors and recipients. The objectives are multiple, and include maximizing the recipients' fill rate, minimizing the total shipping distance, minimizing the holding time of PPE, and minimizing the number of shipments of each donor.   

### Who needs to solve the PPE matching problem?
During health crises like the Covid-19 pandemic, organizations such as GetUsPPE.org provide a platform that aims at connecting prospective donors of PPE to prospective recipients of PPE. Requests by donors and recipients are collected over time. Every _delta_ days, the organization solves the PPE Matching Problem, in order to direct each donor to ship a certain quantity of PPE to a given recipient.

### What does this software package do?
Our package provides an open-source simulation framework for researchers interested in developing and testing methodologies to solve the PPE matching problem.

The user only needs to implement a function _ppestrategy(D,R,M)_, which solves the PPE matching problem. Our simulation framework evaluates the performance of that user-defined solution method on real-world requests received by GetUsPPE.org in the early months of the Covid-19 pandemic (April-July 2020).

## Installation
In a virtual environment with Python 3.6+, ppe_match can be installed via pip

    pip install ppe_match

### Import the package using

    from ppe_match import Simulation

### Test the installation with the code snippet below

    from ppe_match import Simulation

	# Initiate the simuation framework with default parameters
    s = Simulation()

    # Run the simulation on the GetUsPPE.org data set
    s.run()

	# Check outputs
	s.get_decisions() # Pandas dataframe that can be stored

	# Display metrics
	s.get_metrics() # Pandas dataframe that can be stored

### User-defined matching solution methods

To test a new matching solution method, start by defining a function that takes as input the current date (date, a datetime object), the current donor and recipient requests (Dt and Rt), and the distance matrix between donors and recipients. Dt is a DataFrame with columns (don_id,date,ppe,qty), Rt is a DataFrame with columns (rec_id,date,ppe,qty), M is a DataFrame with columns (don_id,rec_id,distance). The function must return the DataFrame Xt of matching decisions (don_id, rec_id, ppe, qty).

For example, a first-come-first-matched strategy that matches the i-th donor's request with the i-th recipient's request is implemented as follows:

    import pandas as pd
    def my_strategy(date,Dt,Rt,M):
        # prepare the result DataFrame (X^t)
        result = pd.DataFrame(columns=['don_id','rec_id','ppe','qty'])

        # the ppe to consider are the intersection of the PPEs in the table of current donors Dt (D^t) and the table of current recipients Rt (R^t)
        ppes_to_consider = set(Dt.ppe.unique())
        ppes_to_consider = ppes_to_consider.intersection(set(Rt.ppe.unique()))

        # for each ppe to consider, match the i-th donor request with the i-th recipient request
        for ppe in ppes_to_consider:
            donors_ppe = Dt[Dt.ppe == ppe]
            recipients_ppe = Rt[Rt.ppe == ppe]

            n = min(len(donors_ppe),len(recipients_ppe))
            for i in range(n):
                don = donors_ppe.iloc[i]
                rec = recipients_ppe.iloc[i]
                qty = min(don.qty,rec.qty)

                # add
                result.loc[len(result)] = [don.don_id,rec.rec_id,ppe,qty]
        return result

To run a simulation on the GetUsPPE.org data set, modify the code above by passing the user-defined function to the Simulation constructor:

    s = Simulation(strategy=my_strategy)

The ppe_match package contains the implementation of two strategies: the first-come-first-matched strategy illustrated above (strategies.FCFM_strategy) and the "proximity matching" strategy tested by Bala et al. (2021) (strategies.proximity_match_strategy).

## Simulation Class
### Parameters
#### donor_path
Path to the data set containing the donors' requests. See expected format in the data folder.

Expected input type: csv

*Default: anon_donors.csv (which is the anonymized table of donors' requests from GetUsPPE.org)*

---
#### recipient_path
Path to the data set containing the recipients' requests. See expected format in the data folder.

Expected input type: csv

*Default: anon_recipients.csv (which is the anonymized table of recipients' requests from GetUsPPE.org)*


---
#### distance_matrix_path
Path to distance matrix between donors and recipients. See expected format in the data folder.

Expected input type: csv

*Default: anon_distance_matrix.csv (which is the anonymized distance matrix from GetUsPPE.org)*

---
#### strategy
User defined strategy to allocate PPE
The function must have the following arguments:

    ppestrategy(date, Dt,Rt,M)

where,

- `date` is a datetime with the current date
- `Dt` is a pandas.DataFrame object whose rows contain the current donor requests
- `Rt` is a pandas.DataFrame object whose rows contain the current recipient requests
- `M` is a pandas.DataFrameobject that reports the distance between each donor and each recipient.

*Default: proximity_match_strategy*

###### Returns:
pd.dataframe of decisions with columns (don_id, rec_id, ppe, qty). Each row represents the decision of shipping from donor _don_id_ to recipient _rec_id_ _qty_ units of PPE of type _ppe_.


---
#### interval
Day Interval set for framework to iterate over.
*Default: 7 (days)*

---
#### max_donation_qty
Maximum quantity limit for donor to donate (helps filter out dummy entries or test entries)
*Default: 1000 (ppe units)*

---
#### writeFiles
Boolean flag to save intermediate outputs and final decisions as csv
*Default: False*

If set to *True* intermediate data will be saved for every iteration as follows:
```
output
├── 2020-04-09
	 ├── decisions.csv
	 ├── distance_matrix.csv
	 ├── donors.csv
	 └── recipients.csv
├── 2020-04-16
	 ├── decisions.csv
	 ├── distance_matrix.csv
	 ├── donors.csv
	 └── recipients.csv
├── ...
```
---
#### output_directory
Sets the directory where the intermediate files and results will be saved
*Default: output/*

---


### Methods

#### run()
Executes the strategy function over the data in a date simulation

---
#### get_decisions()
Returns the list of all matching decisions made during the simulation.

---
#### get_metrics()
Returns the performance metrics described in Section 4 of the research article. The metrics are reported at the PPE level, the recipient level, and the "overall" level (see Section 4). The "overall" metrics are at the bottom of the DataFrame.

---
#### debug(bool_flag)
Sets the logging level to DEBUG if *True*
*Default: False (Loglevel sets to WARN)*

---
