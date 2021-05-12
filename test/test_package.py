import os
import pytest
import pandas as pd
import ppematch as pp
from pandas._testing import assert_frame_equal

# main data
data_directory = 'data'
home_dir = os.getcwd()
data_directory = os.path.join(home_dir,'data/test_1')

test_rec = f'{data_directory}/test_recipients.csv'
test_don = f'{data_directory}/test_donors.csv'
test_distance = f'{data_directory}/test_distance.csv'
dec_df = pd.read_csv(f'{data_directory}/test_decisions.csv',parse_dates=['date'])
def test_strategy(date,curdon,currec,curdistance_mat):
	decisions_to_make = dec_df[(dec_df.date - date).astype('timedelta64[m]').abs() < 10]
	return decisions_to_make[['don_id','rec_id','ppe','qty']].copy()

delta = 1

# else:
# 	test_rec = f'{data_directory}/anon_recipients.csv'
# 	test_don = f'{data_directory}/anon_donors.csv'
# 	test_distance = f'{data_directory}/anon_distance_matrix.p'
# 	test_strategy = pp.proximity_match_strategy
# 	delta = 30


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
R.to_csv('output/R.csv')
D.to_csv('output/D.csv')
X.to_csv('output/X.csv')
result.to_csv('output/results.csv')
