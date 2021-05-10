import pandas as pd
import ppematch as pp
import numpy as np

# 
data_directory = 'test data/section3_example'

# recipients' table (Table 1 in the paper)
test_rec = f'{data_directory}/Table1.csv'
# donors' table (Table 2 in the paper)
test_don = f'{data_directory}/Table2.csv'
# distance matrix (Table 3 in the paper)
test_distance = f'{data_directory}/Table3.csv'
# decisions to be made (Table 4 in the paper)
dec_df = pd.read_csv(f'{data_directory}/Table4.csv',parse_dates=['date'])
def test_strategy(date,curdon,currec,curdistance_mat):
    decisions_to_make = dec_df[(dec_df.date - date).astype('timedelta64[m]').abs() < 10]
    return decisions_to_make[['don_id',	'rec_id',	'ppe'	,'qty']].copy()
  
delta = 1
R,D,X = pp.simulate(test_strategy,delta,test_don,test_rec,test_distance,True,True)

print(R.head())
print("===========")
print(D.head())
print("===========")
print(X.head())
print("===========")

print('Computing metrics...')
result = pp.compute_metrics(R,D,X)
print(result.tail(10))
result.to_csv('output/results.csv')
