from simulator import AirlineRmSimulation
from parameters import Parameter as Param


def main():
    # routes = [('NYC', 'LAX'), ('LAX', 'NYC'), ('NYC', 'MIA'), ('MIA', 'NYC')]
    routes = [('NYC', 'LAX')]  # for a single flight
    simulation = AirlineRmSimulation(routes)
    simulation.run(num_days=Param.num_days)


if __name__ == "__main__":
    main()
