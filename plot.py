import matplotlib.pyplot as plt
import numpy as np
from parameters import Parameter as Param
from simulator import  AirlineRmSimulation as Sim

class AirlineRmPlotting:
    def plot_ttl_revenue(routes):
        revenues = list()
        max_ttl = 60
        for i in range(1, max_ttl):
            Param.ticket_time_limit = i
            simulation = Sim(routes, "INFO")
            simulation.run(num_days=Param.num_days)
            revenue = 0
            for f in simulation.flights.values():
                revenue += f.total_revenue
                revenues.append(revenue)
        
        plt.plot(range(1,max_ttl), revenues, color='blue', label=Param.confirm_prob)
        plt.xlabel("ticket_time_limit")
        plt.ylabel("revenue")
        plt.savefig("assets/pictures/result.png")

        

