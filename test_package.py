from testpymatch import simulation as sm


# Initiate the simuation framework
s = sm.Simulation()

# Set debug as True to monitor logs
s.debug(True)

# Run the simulation
s.run()

# Check outputs
s.get_decision() # Pandas dataframe that can be stored