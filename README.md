
# FraPPE Matcha
_(Framework for Automatic PPE Matching)_

An open-source Simulation Framework for researchers interested in developing and testing methodologies  to  solve  the  PPE  Matching  Problem

## Installation
In a virtual environment with Python 3.6+, pytestmatch can be installed via pip

    pip install fraPPE-Matcha

### Import the package using

    from frappe_match import simulation sm

### Test the installation with the code snippet below

    from frappe_match import Simulation

	# Initiate the simuation framework
    s = Simulation()

    # Set debug as True to monitor logs
    s.debug(True)

    # Run the simulation
    s.run()

	# Check outputs
	s.get_decision() # Pandas dataframe that can be stored

	# Display metrics
	s.get_metrics() # Pandas dataframe that can be stored


## Simulation Class
### Parameters
#### donor_path
Path to donor data.
Expected input type: csv
Expected columns:
- don_id - Unique ID for Donor *(type:str)*
- date - Datetime of Request *(type:datetime)*
- ppe - Type of PPE *(type:str)*
- qty - Number of PPEs Requested *(type:int/float)*
- don_req_id - Unique ID for Each Donor Request *(type:int)*

###### Example:
 don_id|date|ppe|qty|don_req_id
 |--|--|--|--|--|
don0|2020-04-09 13:08:00+00:00|faceShields|10|0
don1|2020-04-09 13:36:00+00:00|faceShields|1|1
don2|2020-04-09 13:53:00+00:00|faceShields|3000|2

*Default: anon_donors.csv*

---
#### recipient_path - Path to recipient data
Path to recipient data.
Expected input type: csv
Expected columns:
- rec_id - Unique ID for Recipient *(type:str)*
- date - Datetime of Request *(type:datetime)*
- (*PPE Type column) - Every PPE type is defined as its own column and the value in these column represent the quantity the recipient requested for the respective PPE type *(type: int/float)*
- rec_req_id - Unique ID for Each Recipient Request *(type:int)*


###### Example:
rec_id|date|disinfectingWipes|surgicalCaps|disposableBooties|respirators|handmadeMasks|nitrileGloves|coveralls|handSanitizer|safetyGlasses|bodyBags|gowns|faceShields|safetyGoggles|thermometers|surgicalMasks|paprShield|babyMonitors|rec_req_id
--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--
rec0|2020-04-02 16:27:00+00:00|0|0|0|10000.0|0|10000|0|0|0|0|1000|5000|0|0|0|0|0|0
rec1|2020-04-02 16:35:00+00:00|4|0|0|9.0|9|5|0|4|0|0|9|9|0|0|0|0|0|1
rec2|2020-04-02 16:44:00+00:00|300|0|100|5.0|0|0|0|25|0|0|100|10|0|20|0|0|0|2

*Default: anon_recipients.csv*

---
#### distance_matrix_path
Path to distance matrix between donors and recipients.
Expected input type: pickle(pandas dataframe)
Expected columns:
- don_id - Unique ID for Donnor *(type:str)*
- rec_id - Unique ID for Recipient *(type:str)*
- date - Datetime of Request *(type:datetime)*

###### Example:
don_id|rec_id|distance
--|--|--
don585|rec4650|540.263969
don749 |rec5876|770.589552

---
#### strategy
User defined strategy to allocate PPE
The function must have the following arguments:

    ppestrategy(D,R,M)

where,

 - `D` is a pandas.DataFrame object whose rows contain the donors requests
- `R` is a pandas.DataFrame object whose rows contain the
   recipients requests
- `M` is a pandas.DataFrameobject that reports
   the distance between each donor and each recipient.

*Default: proximity_match_strategy*

###### Returns:
pd.dataframe of decisions with columns (don_id, rec_id, ppe, qty)

Class methods:

    get_strategy()
    set_strategy()

---
#### interval
Day Interval set for framework to iterate over.
*Default: 7 (days)*

Class methods:

    get_interval()
    set_interval()

---
#### max_donation_qty
Maximum quantity limit for donor to donate (helps filter out dummy entries or test entries)
*Default: 1000 (ppe units)*

Class methods:

    get_max_donation_qty()
    set_max_donation_qty()

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

### Methods

#### run()
Executes the strategy function over the data in a date simulation

---
#### get_decisions()
Returns final decision output from the framework after run()

---
#### debug(bool_flag)
Sets the logging level to DEBUG if *True*
*Default: False (WARN)*

---
