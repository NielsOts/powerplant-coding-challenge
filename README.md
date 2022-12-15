##Read Me

Install the requirements in requirements.txt and execute python main.py.

##Algorithm:
Step 1) Check if the required load can be produced by either or both Windfarms (this has to be exact).
Step 2) If so, no other powerplants are necessary and the load produced matches the pmax multiplied with efficiency of the windfarm(s). The problem is solved.
Step 3) If not, you calculate the residual load or load that needs to be produced by the powerplants.
Step 4) You rank your powerplants based on their cost efficiency (i.e. cost/efficiency) to determine the order in which they will be used to meet the required loads.
Step 5) You check if the most cost (second cost efficient, etc.) efficient powerplant is able to produce the required/residual load.
Step 6) If so, this powerplant produces the power that is equal to the residual/required load. The problem is solved.
Step 7) If not, you produce pmax power in this powerplant and recalculate the residual load and go back to step 5.

I tested the API using Postman

Run the code using python3 app.py

Make POST request with json file as input.

\*The code is not dynamic in the fact that it is only able to read a json file of the structure as provided in all three payload examples.

\*\*Files that are not json cannot be read
