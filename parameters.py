class Parameter:
    num_days = 365  # Number of days to simulate
    pax_inter_time = 1
    decision_inter_time = 0.25
    freq_set_price = 0.5
    ticket_time_limit = 7

    confirm_prob = 0.5
    cancel_prob = 0.3    

    num_total_seats = 100
    preference_of_seat_classes = [0.8, 0.15, 0.05]


    # resale_prob = 0.9