import random
class Bidder:
    def __init__(self, num_users, num_rounds):
        self.num_users = num_users
        self.num_rounds = num_rounds
        self.balances = {}

    def bid(self, user_id):
        return random.uniform(0, 1)

    def notify(self, auction_winner, price, clicked):
        if auction_winner and clicked is not None:
            if self.balances:
                user_id = next(iter(self.balances))
                if len(self.balances[user_id]) > 0:
                    self.balances[user_id][-1] -= float(price)