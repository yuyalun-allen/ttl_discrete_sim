import matplotlib.pyplot as plt
import numpy as np
from parameters import Parameter as Param
from simulator import  AirlineRmSimulation as Sim
from scipy.interpolate import make_interp_spline

class AirlineRmPlotting:
    def plot_ttl_revenue(routes):
        confirm_prob_range = [0, 0.2, 0.4, 0.6, 1]
        confirm_prob_color = ["black", "green", "red", "blue", "yellow"]
        # Simulate with different confirm prob
        for index in range(len(confirm_prob_color)):
            Param.confirm_prob = confirm_prob_range[index]
            revenues = list()
            # Simulate with different ttl
            for i in np.arange(0, 60.5, 0.5):
                Param.ticket_time_limit = i
                simulation = Sim(routes, "INFO")
                simulation.run(num_days=Param.num_days)
                revenue = 0
                for f in simulation.flights.values():
                    revenue += f.revenue_expected
                revenues.append(revenue)
            # Make the curve more smooth
            spl = make_interp_spline(np.arange(0, 60.5, 0.5), revenues, k=2)
            x_smooth = np.linspace(0, 60, 300)
            y_smooth = spl(x_smooth)
            
            plt.plot(x_smooth, y_smooth, color=confirm_prob_color[index], label=Param.confirm_prob)
            plt.xlabel("ticket_time_limit")
            plt.ylabel("revenue")
        plt.legend()
        plt.savefig("assets/pictures/result.png")

        

