# MatchingPPE

<ol>
  <li>anonymize data.ipynb anonymizes the original data (from raw_data to data)</li>
  <li>the file simulation w Rohit.py performs a rolling horizon simulation. It populates the folder output and it creates a file decisions.csv with all matching decisions</li>
  <li>the file Process results.ipynb analyzes decisions.csv and computes the fill rate</li>
</ol>  
<b>For Rohit</b>: the file "simulation w Rohit.py" makes calls to a "strategy" function, which performs the matching. See  "dummy strategy" to see an example of how to implement it. Can you wrap the method you implemented in a strategy function, so that we can test it?
