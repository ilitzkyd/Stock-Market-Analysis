"""
This program is designed to simulate a 
second-price auction with random probabilities for a set of users
"""
import random
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_IMPORTED = True
except ImportError:
    MATPLOTLIB_IMPORTED = False
#from bidder_Ilitzky import Bidder
class User:
    def __init__(self):
        self.__probability = random.uniform(0, 1)

    def show_ad(self):
        return random.random() < self.__probability

    def get_probability(self):
        return self.__probability


class Auction:
    def __init__(self, users, bidders):
        self.users = users
        self.bidders = bidders
        self.balances = {bidder: [0] for bidder in self.bidders}

    def execute_round(self):
        user = random.choice(self.users)
        user_id = self.users.index(user)

        bids = [bidder.bid(user_id) for bidder in self.bidders]
        max_bid = max(bids)
        max_bid_indices = [i for i, bid in enumerate(bids) if bid == max_bid]

        if len(max_bid_indices) > 1:
            winning_bidder_index = random.choice(max_bid_indices)
        else:
            winning_bidder_index = max_bid_indices[0]

        winning_bidder = self.bidders[winning_bidder_index]
        winning_price = max_bid if max_bid_indices else 0

        user_clicked = user.show_ad()

        for bidder in self.bidders:
            if bidder == winning_bidder:
                bidder.notify(auction_winner=True, price=winning_price, clicked=user_clicked)
                self.balances[bidder].append(self.balances[bidder][-1] - winning_price)
            else:
                bidder.notify(auction_winner=False, price=winning_price, clicked=None)
                self.balances[bidder].append(self.balances[bidder][-1])

    def run_auction(self, num_rounds):
        for _ in range(num_rounds):
            self.execute_round()

    def get_balances(self):
        return self.balances

    def plot_balances(self):
        for bidder, balance in self.balances.items():
            plt.plot(range(len(balance)), balance, label=f"Bidder {bidder}")

        plt.xlabel("Round")
        plt.ylabel("Balance")
        plt.legend()
        plt.show()

'''
b0, b1, b2 = Bidder(1, 10), Bidder(1, 10), Bidder(1, 10)
auction = Auction([User()], [b0, b1, b2])
auction.run_auction(10)  # Run the auction for 10 rounds
auction.plot_balances()  # Plot the balances of the bidders
'''