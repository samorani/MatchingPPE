import ppematch as pp

# Initiate the simuation framework
delta = 7
donor_waste = True
R,D,X = pp.simulate(pp.dummy_strategy,delta,donor_waste,True,True)

print(R.head())
print("===========")
print(D.head())
print("===========")
print(X.head())
print("===========")
