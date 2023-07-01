"""
This program is designed to simulate a 
second-price auction with random probabilites for a set of users
"""
import random
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_IMPORTED = True
except ImportError:
    MATPLOTLIB_IMPORTED = False

from bidder_Ilitzky import Bidder

class User:
    """
    Class for user to have a secret probability as a boolean to indicate if a user clicks on an ad
    """
    def __init__(self):
        """
        User probability of a value between 0 and 1 
        """
        self.__probability = random.uniform(0, 1)

    def show_ad(self):
        """
        Indicates if a user has clicked on an ad and returns a boolean 
        """
        return random.random() < self.__probability
    def get_probability(self):
        """
        Returns the probability value of the user
        """
        return self.__probability


class Auction:
    """
    Users the are participating in the auction and bidder objects in the auction 
    """

    def __init__(self, users, bidders):
        """
        Initializes the Auction class for the users and bidders
        """
        self.users = users
        self.bidders = bidders
        self.balances = {bidder: [0] * len(users) for bidder in self.bidders}


    def execute_round(self):
        """
        Round to determine the outcome once a bidder places a bid
         """
        for bidder in self.bidders:
            user_id = 0  # Only one user, so the ID is always 0
            bid_amount = bidder.bid(user_id)
            adv = self.users[user_id].show_ad()
            not_current_bidder = [bid for bid in self.bidders if bid != bidder]
            other_bidder = random.choice(not_current_bidder) if not_current_bidder else None

        if adv and other_bidder:
            additional_bidder = other_bidder

            if additional_bidder:
                additional_amount = additional_bidder.bid(user_id)

                if additional_amount < bid_amount:
                    bidder.notify(auction_winner=True, price=additional_amount, clicked=None)
                    additional_bidder.notify(auction_winner=False, price=additional_amount, clicked=None)  # Change clicked status to None for additional bidder
                    if len(self.balances[bidder]) > 0:
                        self.balances[bidder].append(self.balances[bidder][-1] - additional_amount)
                    else:
                        self.balances[bidder].append(-additional_amount)
                else:
                    bidder.notify(auction_winner=True, price=bid_amount, clicked=None)  # Notify bidder with their own bid amount
                    additional_bidder.notify(auction_winner=False, price=additional_amount, clicked=None)  # Change clicked status to None for additional bidder
                    extra_bidder_balance = self.balances[additional_bidder]
                    if len(extra_bidder_balance) > 0:
                        extra_bidder_balance.append(self.balances[additional_bidder][-1] - additional_amount)
                    else:
                        extra_bidder_balance.append(-additional_amount)
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
        """
        Displays the plot of the bid balances for each bidder 
        """
        for bidder in self.bidders:
            balances = self.balances[bidder]
            plt.plot(range(len(balances)), balances, label=f'Bidder {self.bidders.index(bidder) + 1}')

        plt.xlabel('Round')
        plt.ylabel('Balance')
        plt.legend()
        plt.show()


b0, b1, b2 = Bidder(1, 10), Bidder(1, 10), Bidder(1, 10)
auction = Auction([User()], [b0, b1, b2])

#Executes the round calling the auction function
auction.execute_round()
auction.plot_history()

#Gets the auction balances
bal = auction.balances

#Prints the probability of the user
user = User()
probability = user.get_probability()
print(probability)
