Process Graph
![](./assets/pictures/process%20graph.png)

TODO:

~~1. add more points to graph to make more dense~~
~~2. in the same graph, have other trend lines of different lambda~~
~~3. change the increment in price from seatwise to weekwise (increment 5% per week) equal increment~~
~~4. median/meanline in each trend line~~

In a simulation of the TTL optimization problem using SimPy, the resale time and resale rate would be parameters to configure for the simulation, rather than outputs to be studied. 

Specifically:

- Resale time: This represents how long after a cancellation a seat could be resold. It affects how soon re-revenue is realized.

- Resale rate: The probability of successfully reselling a canceled seat over time. This affects the expected revenue from resales.

These parameters would be used when simulating booking cancellations to determine:

- If a canceled seat is resold 
- How long after cancellation the resale occurs
- The associated revenue

Some ways to incorporate them in a SimPy model:

- Sample a resale time for each cancellation from a distribution (expo, normal, etc) 

- Use the resale rate function to determine if a resale occurs before departure

- Calculate the resale revenue based on price at the sampled resale time

So in summary, resale time and rate are fixed model parameters in a TTL simulation, not output metrics. You configure them upfront based on data assumptions to drive the cancellation and resale logic.

Let me know if this helps explain how to simulate with resale time and rate!