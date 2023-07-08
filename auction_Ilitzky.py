"""
This program is designed to simulate a 
second-price auction with random probabilities for a set of users
"""
import random
import numpy as np
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_IMPORTED = True
except ImportError:
    MATPLOTLIB_IMPORTED = False

#from bidder_Ilitzky import Bidder

class User:

    '''
    Represents the user in the auction 
    '''
    def __init__(self):
        '''
        User instance with random probability 
        '''
        self.__probability = random.uniform(0, 1)

    def show_ad(self):
        '''
        Method to show the ad clicking choice
        '''
        return np.random.choice([True,False],p=[self.__probability,1-self.__probability])

    def get_probability(self):
        '''
        Probability of ad clicking
        '''
        return self.__probability


class Auction:
    '''
    Class to simulate the second-price auction 
    '''
    def __init__(self, users, bidders):
        '''
        Initializes the bidders, users and balances in the auction 
        '''
        self._users = users
        self.bidders = bidders
        self.balance_timeseries = np.empty((0, len(bidders)))
        self.balances = {bidder: 0 for bidder in (self.bidders)}

    def execute_round(self):
        '''
        Method to execute auction round based on specific parameters
        '''
        user_id = np.random.randint(len(self._users))
        bid_price = [bidder.bid(user_id) for bidder in self.bidders]
        potential_winner = []
        highest_bid = 0
        second_highest = 0
        for i in range(len(self.bidders)):
            if bid_price[i] == highest_bid:
                potential_winner.append(i)
                second_highest = highest_bid
            if bid_price[i]>highest_bid:
                potential_winner = [i]
                second_highest = highest_bid
                highest_bid = bid_price[i]
            else:
                if bid_price[i]>second_highest:
                    second_highest = bid_price[i]

        winner = random.choice(potential_winner)
        user_clicked = self._users[user_id].show_ad()
        self.balances[self.bidders[winner]]-=second_highest
        if user_clicked:
            self.balances[self.bidders[winner]]+=1
        self.balance_timeseries = np.vstack((self.balance_timeseries, list(self.balances.values())))

        for bidder_id in range(len(self.bidders)):
            if bidder_id == winner:
                self.bidders[bidder_id].notify(auction_winner=True, price=second_highest, clicked=user_clicked)
            else:
                self.bidders[bidder_id].notify(auction_winner=False, price=second_highest, clicked=None)

    def run_auction(self, num_rounds):
        '''
        Run the auction for the specified amount of rounds
        '''
        for _ in range(num_rounds):
            self.execute_round()

    def get_balances(self):
        '''
        Gets current balances for bidders
        '''
        return self.balances

    def plot_balances(self):
        '''
        Plot the balance as a time series 
        '''
        num_rounds = self.balance_timeseries.shape[0]
        num_bidders = self.balance_timeseries.shape[1]

        for bidder_id in range(num_bidders):
            plt.plot(range(num_rounds), self.balance_timeseries[:, bidder_id], label=f"Bidder {bidder_id}")

        plt.xlabel("Round")
        plt.ylabel("Balance")
        plt.legend()
        plt.show()


