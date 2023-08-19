import numpy as np
from parameters import Parameter as Param
import simpy


class Flight:
    def __init__(self, env, flight_id):
        self.env = env
        self.id = flight_id
        self.bookings = 0
        self.revenue = 0
        self.num_seats = 100  # TODO: the detailed info of each flight could be loaded from an input file
        self.norm_price = 100
        self.ticket_price = self.norm_price
        self.total_revenue = 0
    

    # Define the revenue management function for each flight
    def revenue_management(self):
        new_price = self.norm_price
        while True:
            yield self.env.timeout(Param.freq_set_price)       # the time frequency for updating ticket price
            if self.bookings < self.num_seats:
                # increase the price if fewer seats are available
                if self.num_seats - self.bookings <= 20:
                    price = self.norm_price * 1.2
                elif self.num_seats - self.bookings <= 50:
                    price = self.norm_price * 1.1
                else:
                    price = self.norm_price

                # calculate the expected revenue for the remaining capacity
                expected_revenue = (self.num_seats - self.bookings) * price

                # if the expected revenue is higher than the current revenue,
                # update the price and revenue
                if expected_revenue + self.total_revenue > self.revenue:
                    # TODO: check this!
                    self.revenue = expected_revenue + self.total_revenue
                    new_price = price
            else:
                new_price = 0  # no more bookings allowed
            self.ticket_price = new_price
            # update the ticket price
            print(f"Day {self.env.now} {self.id} ticket price: {self.ticket_price:.2f}, "
                  f"remaining {self.num_seats - self.bookings} seats.")

    # Define the function to simulate passenger bookings
    def passenger_arrivals(self):
        while True:
            yield self.env.timeout(int(np.random.exponential(scale=Param.pax_inter_time)))
            print(f"Passenger of flight {self.id} arrived at day {self.env.now} ")
            if self.bookings < self.num_seats:
                self.bookings += 1
                self.total_revenue += self.ticket_price
                print(f"Passenger of flight {self.id} "
                      f"arrived at day {self.env.now} "
                      f"purchased a ticket at price {self.ticket_price:.2f}, "
                      f"remaining {self.num_seats - self.bookings} seats.")
                # Start TTL timing
                start = self.env.now
                ttl = self.env.process(self.ticket_time_limit())
                # Allow decision
                self.env.process(self.decide_booking(ttl))
            else:
                print(f"Passenger of flight {self.id} arrived at day {self.env.now} finds no available seats.")

    # Handle ttl
    def ticket_time_limit(self):
        try:
            yield self.env.timeout(Param.ticket_time_limit)
            self.bookings -= 1
            self.total_revenue -= self.ticket_price
            print(f"Passenger of flight {self.id} "
                f"automatically cancelled at day {self.env.now} "
                f"return a ticket at price {self.ticket_price:.2f}, "
                f"remaining {self.num_seats - self.bookings} seats.")
        except simpy.Interrupt as interrupt:
            cause = interrupt.cause
            if cause == "cancel":
                self.bookings -= 1
                self.total_revenue -= self.ticket_price
                print(f"Passenger of flight {self.id} "
                    f"cancelled at day {self.env.now} "
                    f"return a ticket at price {self.ticket_price:.2f}, "
                    f"remaining {self.num_seats - self.bookings} seats.")
            elif cause == "confirm":
                print(f"Passenger of flight {self.id} "
                    f"confirmed at day {self.env.now} ")
    
    # Make decision
    def decide_booking(self, ttl):
        interrupted = False
        while ttl.is_alive and not interrupted:
            yield self.env.timeout(Param.decision_inter_time)
            decision = np.random.random() 
            if decision <= Param.confirm_prob:
                ttl.interrupt(cause="cancel")
                interrupted = True
            elif decision > Param.confirm_prob and decision <= Param.confirm_prob + Param.cancel_prob:
                ttl.interrupt(cause="confirm")
                interrupted = True
