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

        # Initialize balances for each bidder to zero
        for bidder in self.bidders:
            self.balances[bidder] = [0]*len(users)

    def execute_round(self):
        user = random.choice(self.users)
        user_id = self.users.index(user)

        bids = [(bidder, bidder.bid(user_id)) for bidder in self.bidders]
        bids.sort(key=lambda x: x[1], reverse=True)
        winning_bidder = bids[0][0]
        winning_price = bids[1][1] if len(bids) > 1 else 0

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