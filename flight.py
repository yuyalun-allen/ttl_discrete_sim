import numpy as np
from parameters import Parameter as Param
import simpy


class Flight:
    def __init__(self, env, flight_id, log, total_seats, ratio_of_seat_classes, norm_prices):
        self.env = env
        self.id = flight_id
        self.total_seats = total_seats
        self.ratio_of_seat_classes = ratio_of_seat_classes
        self.norm_prices = norm_prices

        self.revenue = 0
        self.bookings = [0 for _ in range(len(self.ratio_of_seat_classes))]
        self.num_seats = [self.total_seats * ratio for ratio in self.ratio_of_seat_classes]  # TODO: the detailed info of each flight could be loaded from an input file
        self.ticket_prices = self.norm_prices
        self.log = log
        
        self.revenue_confirmed = 0
        self.revenue_hold_on = 0
    

    # Define the revenue management function for each flight
    def revenue_management(self):
        new_price = self.norm_prices.copy()
        price_increase_rate = 0
        # resale_rate = Param.resale_prob
        while True:
            yield self.env.timeout(Param.freq_set_price)       # the time frequency for updating ticket price
            # if resale_rate > 0.05:
            #     resale_rate -= 0.01
            if self.env.now % 7 == 0:
                price_increase_rate += 0.05
            for i in range(len(self.ratio_of_seat_classes)):
                if self.bookings[i] < self.num_seats[i]:
                    # increase the price when days are going on
                    new_price[i] = self.norm_prices[i] * (1 + price_increase_rate) 

                    # revenue_expectation = self.revenue_confirmed + self.revenue_hold_on * Param.confirm_prob + self.revenue_hold_on * Param.cancel_prob * resale_rate + self.revenue_hold_on * (1 - Param.confirm_prob - Param.cancel_prob) * (resale_rate - 0.01)
                    # if revenue_expectation > self.revenue:
                    #     self.revenue = revenue_expectation 
                else:
                    new_price[i] = 0  # no more bookings allowed
            # update the ticket price
            self.ticket_prices = new_price
            if self.log == "DEBUG":
                format_ticket_prices = [f"{price:.2f}" for price in self.ticket_prices]
                remaining_seats = [self.num_seats[i] - self.bookings[i] for i in range(len(self.ratio_of_seat_classes))]
                print(f"Day {self.env.now} {self.id} ticket prices: {format_ticket_prices}, "
                    f"remaining {remaining_seats} seats.")

    # Define the function to simulate passenger bookings
    def passenger_arrivals(self):
        while True:
            yield self.env.timeout(int(np.random.exponential(scale=Param.pax_inter_time)))
            if self.log == "DEBUG":
                print(f"Passenger of flight {self.id} arrived at day {self.env.now} ")

            base_seat_choice = np.random.random()
            if base_seat_choice < Param.preference_of_seat_classes[0]:
                choice = 0
            elif (base_seat_choice >= Param.preference_of_seat_classes[0] 
                  and base_seat_choice < Param.preference_of_seat_classes[0] + Param.preference_of_seat_classes[1]):
                choice = 1
            else:
                choice = 2
            if self.log == "DEBUG":
                print(f"Passenger of flight {self.id} chose class {choice} seat.")

            while choice < len(self.ratio_of_seat_classes) and self.bookings[choice] >= self.num_seats[choice]:
                choice += 1
                if self.log == "DEBUG" and choice < len(self.ratio_of_seat_classes):
                    print(f"Passenger of flight {self.id} arrived at day {self.env.now} upgraded the seat class")
            if choice < len(self.ratio_of_seat_classes):
                self.bookings[choice] += 1
                self.revenue_hold_on += self.ticket_prices[choice]
                if self.log == "DEBUG":
                    remaining_seats = [self.num_seats[i] - self.bookings[i] for i in range(len(self.ratio_of_seat_classes))]
                    print(f"Passenger of flight {self.id} "
                        f"arrived at day {self.env.now} "
                        f"purchased a ticket at price {self.ticket_prices[choice]:.2f}, "
                        f"remaining {remaining_seats} seats.")
                # Start TTL timing
                ttl = self.env.process(self.ticket_time_limit(self.ticket_prices[choice], choice))
                # Allow decision
                self.env.process(self.decide_booking(ttl))
            else:
                if self.log == "DEBUG":
                    print(f"Passenger of flight {self.id} arrived at day {self.env.now} finds no available seats.")

    # Handle ttl
    def ticket_time_limit(self, booking_price, choice):
        try:
            yield self.env.timeout(Param.ticket_time_limit)
            self.bookings[choice] -= 1
            self.revenue_hold_on -= booking_price
            if self.log == "DEBUG":
                remaining_seats = [self.num_seats[i] - self.bookings[i] for i in range(len(self.ratio_of_seat_classes))]
                print(f"Passenger of flight {self.id} "
                    f"automatically cancelled at day {self.env.now} "
                    f"return a ticket at price {booking_price:.2f}, "
                    f"remaining {remaining_seats} seats.")
        except simpy.Interrupt as interrupt:
            cause = interrupt.cause
            if cause == "cancel":
                self.bookings[choice] -= 1
                self.revenue_hold_on -= booking_price
                if self.log == "DEBUG":
                    remaining_seats = [self.num_seats[i] - self.bookings[i] for i in range(len(self.ratio_of_seat_classes))]
                    print(f"Passenger of flight {self.id} "
                        f"cancelled at day {self.env.now} "
                        f"return a ticket at price {booking_price:.2f}, "
                        f"remaining {remaining_seats} seats.")
            elif cause == "confirm":
                self.revenue_hold_on -= booking_price
                self.revenue_confirmed += booking_price
                if self.log == "DEBUG":
                    print(f"Passenger of flight {self.id} "
                        f"confirmed at day {self.env.now} ")
    
    # Make decision
    def decide_booking(self, ttl):
        interrupted = False
        timeout = False
        while not timeout and not interrupted:
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
            yield self.env.timeout(Param.decision_inter_time)
