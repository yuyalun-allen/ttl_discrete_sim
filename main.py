from simulator import AirlineRmSimulation
from parameters import Parameter as Param
from plot import AirlineRmPlotting


def main():
    # routes = [('NYC', 'LAX'), ('LAX', 'NYC'), ('NYC', 'MIA'), ('MIA', 'NYC')]
    routes = [('NYC', 'LAX')]  # for a single flight
    AirlineRmPlotting.plot_day_to_booking_revenue(routes)

if __name__ == "__main__":
    main()
