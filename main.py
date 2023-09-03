from simulator import AirlineRmSimulation
from parameters import Parameter as Param
from plot import AirlineRmPlotting


def main():
    # routes = [('NYC', 'LAX'), ('LAX', 'NYC'), ('NYC', 'MIA'), ('MIA', 'NYC')]
    routes = [('NYC', 'LAX'), ('BOS', 'JFK')]  # for a single flight
    seats_info = [{"total_seats": 200, 
                "ratio_of_seat_classes": [0.6, 0.3, 0.1],
                "norm_prices": [100, 200, 300]}, 
                {"total_seats": 100, 
                "ratio_of_seat_classes": [0.7, 0.2, 0.1],
                "norm_prices": [120, 240, 300]}]
    AirlineRmPlotting.plot_ttl_revenue(routes, seats_info)

if __name__ == "__main__":
    main()
