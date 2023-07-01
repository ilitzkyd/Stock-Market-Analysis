import random
import matplotlib.pyplot as plt
from bidder_lastname import Bidder

class User:
    """
    Class for user to have a secret probability as a boolean to indicate if a user clicks on an ad
    """

    def __init__(self):
        self.__probability = random.uniform(0, 1)

    def show_ad(self):
        return random.random() < self.__probability


class Auction:
    def __init__(self, users, bidders):
        self.users = users
        self.bidders = bidders
        self.balances = {bidder: [] for bidder in bidders}

    def execute_round(self):
        for bidder in self.bidders:
            user_id = 0  # Only one user, so the ID is always 0
            bid_amount = bidder.bid(user_id)
            adv = self.users[user_id].show_ad()
            not_current_bidder = [bid for bid in self.bidders if bid != bidder]
            other_bidder = random.choice(not_current_bidder) if not_current_bidder else None

            if adv:
                additional_bidder = other_bidder

                if additional_bidder:
                    additional_amount = additional_bidder.bid(user_id)

                    if additional_amount < bid_amount:
                        bidder.notify(auction_winner=True, price=additional_amount, clicked=True)
                        additional_bidder.notify(auction_winner=False, price=additional_amount, clicked=None)
                        if len(self.balances[bidder]) > 0:
                            self.balances[bidder].append(self.balances[bidder][-1] - additional_amount)
                        else:
                            self.balances[bidder].append(-additional_amount)
                    else:
                        bidder.notify(auction_winner=False, price=additional_amount, clicked=None)
                        additional_bidder.notify(auction_winner=True, price=bid_amount, clicked=True)
                        if len(self.balances[additional_bidder]) > 0:
                            self.balances[additional_bidder].append(self.balances[additional_bidder][-1] - bid_amount)
                        else:
                            self.balances[additional_bidder].append(-bid_amount)

                else:
                    bidder.notify(auction_winner=True, price=0, clicked=True)
                    if len(self.balances[bidder]) > 0:
                        self.balances[bidder].append(self.balances[bidder][-1])
                    else:
                        self.balances[bidder].append(0)
            else:
                bidder.notify(auction_winner=False, price=0, clicked=None)
                self.balances.setdefault(bidder, []).append(0)

    def plot_history(self):
        for bidder in self.bidders:
            balances = self.balances[bidder]
            plt.plot(range(len(balances)), balances, label=f'Bidder {self.bidders.index(bidder) + 1}')

        plt.xlabel('Round')
        plt.ylabel('Balance')
        plt.legend()
        plt.show()

b0, b1, b2 = Bidder(1, 10), Bidder(1, 10), Bidder(1, 10)
auction = Auction([User()], [b0, b1, b2])
auction.execute_round()
auction.plot_history()
balances = auction.balances

