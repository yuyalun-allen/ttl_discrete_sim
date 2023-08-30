import numpy as np
from parameters import Parameter as Param
import simpy


class Flight:
    def __init__(self, env, flight_id, log):
        self.env = env
        self.id = flight_id
        self.bookings = 0
        self.revenue = 0
        self.num_seats = 100  # TODO: the detailed info of each flight could be loaded from an input file
        self.norm_price = 100
        self.ticket_price = self.norm_price
        self.log = log
        
        self.revenue_confirmed = 0
        self.revenue_hold_on = 0
        self.day_to_booking_revenue = [0 for _ in range(20)]
    

    # Define the revenue management function for each flight
    def revenue_management(self):
        new_price = self.norm_price
        price_increase_rate = 0
        # resale_rate = Param.resale_prob
        while True:
            yield self.env.timeout(Param.freq_set_price)       # the time frequency for updating ticket price
            # if resale_rate > 0.05:
            #     resale_rate -= 0.01
            if self.bookings < self.num_seats:
                # increase the price when days are going on
                if self.env.now % 7 == 0:
                    price_increase_rate += 0.05
                new_price = self.norm_price * (1 + price_increase_rate)

                # revenue_expectation = self.revenue_confirmed + self.revenue_hold_on * Param.confirm_prob + self.revenue_hold_on * Param.cancel_prob * resale_rate + self.revenue_hold_on * (1 - Param.confirm_prob - Param.cancel_prob) * (resale_rate - 0.01)
                # if revenue_expectation > self.revenue:
                #     self.revenue = revenue_expectation 
            else:
                new_price = 0  # no more bookings allowed
            # update the ticket price
            self.ticket_price = new_price
            if self.log == "DEBUG":
                print(f"Day {self.env.now} {self.id} ticket price: {self.ticket_price:.2f}, "
                    f"remaining {self.num_seats - self.bookings} seats.")

    # Define the function to simulate passenger bookings
    def passenger_arrivals(self):
        while True:
            yield self.env.timeout(int(np.random.exponential(scale=Param.pax_inter_time)))
            booking_price = self.ticket_price
            if self.log == "DEBUG":
                print(f"Passenger of flight {self.id} arrived at day {self.env.now} ")
            if self.bookings < self.num_seats:
                self.bookings += 1
                self.revenue_hold_on += booking_price
                if self.log == "DEBUG":
                    print(f"Passenger of flight {self.id} "
                        f"arrived at day {self.env.now} "
                        f"purchased a ticket at price {self.ticket_price:.2f}, "
                        f"remaining {self.num_seats - self.bookings} seats.")
                start = self.env.now
                # Start TTL timing
                ttl = self.env.process(self.ticket_time_limit(booking_price, start))
                # Allow decision
                self.env.process(self.decide_booking(ttl))
            else:
                if self.log == "DEBUG":
                    print(f"Passenger of flight {self.id} arrived at day {self.env.now} finds no available seats.")

    # Handle ttl
    def ticket_time_limit(self, booking_price, start):
        try:
            yield self.env.timeout(Param.ticket_time_limit)
            self.bookings -= 1
            self.revenue_hold_on -= booking_price
            if self.log == "DEBUG":
                print(f"Passenger of flight {self.id} "
                    f"automatically cancelled at day {self.env.now} "
                    f"return a ticket at price {self.ticket_price:.2f}, "
                    f"remaining {self.num_seats - self.bookings} seats.")
        except simpy.Interrupt as interrupt:
            cause = interrupt.cause
            if cause == "cancel":
                self.bookings -= 1
                self.revenue_hold_on -= booking_price
                if self.log == "DEBUG":
                    print(f"Passenger of flight {self.id} "
                        f"cancelled at day {self.env.now} "
                        f"return a ticket at price {self.ticket_price:.2f}, "
                        f"remaining {self.num_seats - self.bookings} seats.")
            elif cause == "confirm":
                self.revenue_hold_on -= booking_price
                self.revenue_confirmed += booking_price
                self.day_to_booking_revenue[self.env.now - start] += booking_price
                if self.log == "DEBUG":
                    print(f"Passenger of flight {self.id} "
                        f"confirmed at day {self.env.now} ")
    
    # Make decision
    def decide_booking(self, ttl):
        interrupted = False
        timeout = False
        while not timeout and not interrupted:
            yield self.env.timeout(Param.decision_inter_time)
            decision = np.random.random() 
            if decision <= Param.confirm_prob:
                try:
                    ttl.interrupt(cause="confirm")
                    interrupted = True
                except RuntimeError:
                    timeout = True
            elif decision > Param.confirm_prob and decision <= Param.confirm_prob + Param.cancel_prob:
                try:
                    ttl.interrupt(cause="cancel")
                    interrupted = True
                except RuntimeError:
                    timeout = True
