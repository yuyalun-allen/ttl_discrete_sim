import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from parameters import Parameter as Param
from simulator import  AirlineRmSimulation as Sim
from scipy.interpolate import make_interp_spline

class AirlineRmPlotting:
    def plot_ttl_revenue(routes):
        matplotlib.rcParams['font.family'] = 'Arial'
        confirm_prob_range = [0.2, 0.4, 0.6, 0.8]
        confirm_prob_color = ["grey", "green", "red", "blue"]
        confirm_prob_line = ["-", "--", ":", "-."]
        # Simulate with different confirm prob
        plt.figure(dpi=400)
        plt.ylim(0, 25000)
        for index in range(len(confirm_prob_color)):
            Param.confirm_prob = confirm_prob_range[index]
            revenues = list()
            # Simulate with different ttl
            for i in np.arange(0, 14.5, 0.5):
                Param.ticket_time_limit = i
                simulation = Sim(routes, "INFO")
                simulation.run(num_days=Param.num_days)
                revenue = 0
                for f in simulation.flights.values():
                    revenue += f.revenue_confirmed
                revenues.append(revenue)
            # Make the curve more smooth
            spl = make_interp_spline(np.arange(0, 14.5, 0.5), revenues, k=2)
            x_smooth = np.linspace(0, 14, 300)
            y_smooth = spl(x_smooth)
            
            plt.plot(x_smooth, y_smooth, linestyle=confirm_prob_line[index], color=confirm_prob_color[index], label=Param.confirm_prob)
            plt.xlabel("ticket_time_limit")
            plt.ylabel("revenue")
        plt.legend()
        plt.savefig("assets/pictures/result.png")

    def plot_exponential_distribution(lmbda):
        matplotlib.rcParams['font.family'] = 'Arial'
        x = np.linspace(0, 10, 100)
        pdf = lmbda * np.exp(-lmbda * x)

        plt.figure(dpi=400)
        plt.plot(x, pdf, label=f'λ = {lmbda}', color='blue')

        plt.xlabel('Days')
        plt.ylabel('Probability Density')
        plt.legend()

        plt.savefig("assets/pictures/exponential_dist.png")

    def plot_price_change():
        matplotlib.rcParams['font.family'] = 'Arial'
        y_initial = 100
        x_interval = 7
        y_increment = 5
        x = np.arange(0, 50, x_interval)
        y = [y_initial + i * y_increment for i in range(len(x))]

        plt.figure(dpi=400)
        plt.step(x, y, where='post', color='b')

        plt.xlabel('Days')
        plt.ylabel('Ticket Price')

        plt.savefig("assets/pictures/ticket_price.png")
