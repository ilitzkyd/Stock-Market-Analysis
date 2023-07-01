"""
This program is made to represent the set of bidders that will be participating in the second price auction 
"""
import random
class Bidder:
    """
    Represents the bidder participating in the auction 
    """
    def __init__(self, num_users, num_rounds):
        """
        Initializes the bidder objects with user participation and rounds
        """
        self.num_users = num_users
        self.num_rounds = num_rounds
        self.balances = {user: [0] for user in range(num_users)}

    def bid(self, user_id):
        """
        Places a bid for user
        """
        max_bid = 1000
        min_bid = 0
        total_bid = round(random.uniform(min_bid, max_bid), 3)
        return total_bid

    def notify(self, auction_winner, price, clicked):
        """
        Lets the user know of their outcome
        """
        if auction_winner and clicked is not None:
            if not self.balances:
                self.balances = {user: [0] for user in range(self.num_users)}
            user_id = next(iter(self.balances))
            if len(self.balances[user_id]) > 0:
                self.balances[user_id].append(self.balances[user_id][-1] - price)
            else:
                self.balances[user_id].append(-price)
        else:
        # Set auction_winner to False for b1 and b2
            self.balances = {user: [0] for user in range(self.num_users)}

