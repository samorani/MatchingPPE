import pandas as pd
from ppematch.metrics import compute_metrics
import ppematch as pp

# test

# test strategy: this strategy makes the decisions reported in a decisions.csv file

test_rec = 'data/test/test_recipients.csv'
test_don = 'data/test/test_donors.csv'
test_distance = 'data/test/test_distance.csv'
dec_df = pd.read_csv('data/test/test_decisions.csv',parse_dates=['date'])
def test_strategy(date,curdon,currec,curdistance_mat):
    decisions_to_make = dec_df[(dec_df.date - date).astype('timedelta64[m]').abs() < 10]
    return decisions_to_make[['don_id',	'rec_id',	'ppe'	,'qty']].copy()


# Initiate the simuation framework
delta = 1
donor_waste = True
R,D,X = pp.simulate(test_strategy,delta,donor_waste,test_don,test_rec,test_distance)

print(R.head())
print("===========")
print(D.head())
print("===========")
print(X.head())
print("===========")

print('Computing metrics...')
result = compute_metrics(R,D,X)
result.to_csv('output/results.csv')
