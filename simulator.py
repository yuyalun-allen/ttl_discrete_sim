import simpy
from flight import Flight


class AirlineRmSimulation:
    def __init__(self, routes):
        self.env = simpy.Environment()
        self.routes = routes
        self.flights = {}
        for origin, destination in routes:
            self.flights[(origin, destination)] = Flight(self.env, flight_id=(origin, destination))

    def run(self, num_days):
        for flight in self.flights.values():
            self.env.process(flight.revenue_management())
            self.env.process(flight.passenger_arrivals())
        self.env.run(until=num_days)
        self.print_results()

    def print_results(self):
        for origin, destination in self.routes:
            flight = self.flights[(origin, destination)]
            print(f"From {origin} to {destination}:")
            print(f"Total revenue: ${flight.total_revenue:.2f}")
            print(f"Total seats sold: {flight.bookings}")
            print()








