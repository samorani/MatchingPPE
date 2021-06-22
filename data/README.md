# Data Files

Our  data  set  was  built  by  collecting  and  anonymizing  the  requests  (from  both  donors and  recipients)  received  on  the  GetUsPPE.org  platform  during  the  first  few  months  ofthe Covid-19 pandemic (Apr-July 2020). It includes requests by prospective donors andrecipients interested in respectively donating and receiving certain types of ppes. The data is anonymized to ensure that donors and recipients cannot be identified. The data set and the anonymization procedure are described in the research article.

## anon_donors.csv:
This is the anonymized donors' file. Each row represents a request received by GetUsPPE.org made by a donor intereted in donating PPE. The columns are:
- don_id - Unique ID for Donor *(type:str)*
- date - Datetime of Request *(type:datetime)*
- ppe - Type of PPE *(type:str)*
- qty - Number of PPEs Supplied *(type:int/float)*


#### First few rows of anon_donors.csv:
don_id|date|ppe|qty
|--|--|--|--
don0|2020-04-09 13:08:00+00:00|printedFaceShields|10
don1|2020-04-09 13:36:00+00:00|printedFaceShields|1
don2|2020-04-09 13:53:00+00:00|printedFaceShields|3000
don3|2020-04-09 14:24:00+00:00|printedFaceShields|5.0
don71|2020-04-09 17:52:00+00:00|printedFaceShields|10.0

## anon_recipients.csv:
This is the anonymized recipients' file. Each row represents a request received by GetUsPPE.org made by a recipient intereted in receiving PPE. The columns are:
- rec_id - Unique ID for Donor *(type:str)*
- date - Datetime of Request *(type:datetime)*
- ppe - Type of PPE *(type:str)*
- qty - Number of PPEs Needed *(type:int/float)*


#### First few rows of anon_recipients.csv:
rec_id|date|ppe|qty
|--|--|--|--
rec0|2020-04-02 16:27:00+00:00|gowns|1000.0
rec0|2020-04-02 16:27:00+00:00|faceShields|5000.0
rec0|2020-04-02 16:27:00+00:00|respirators|10000.0
rec0|2020-04-02 16:27:00+00:00|nitrileGloves|10000.0
rec1|2020-04-02 16:35:00+00:00|handSanitizer|4.0

## anon_distance_matrix.csv
Distance, in miles, between pairs of donor and recipients. (donor, recipient) pairs with no PPE type in common are excluded.

#### First few rows of anon_distance_matrix.csv:
don_id|rec_id|distance
|--|--|--
don585|rec5633|502.3535
don924|rec1498|2230.6760
don924|rec2260|1851.4290
don924|rec4705|2563.2325
don924|rec5045|348.2025
