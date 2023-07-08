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
    def __init__(self):
        self.__probability = random.uniform(0, 1)

    def show_ad(self):
        #return random.random() < self.__probability
        return np.random.choice([True,False],p=[self.__probability,1-self.__probability])

    def get_probability(self):
        return self.__probability


class Auction:
    def __init__(self, users, bidders):
        self._users = users
        self.bidders = bidders
        self.balances = [0]*len(bidders)
        #self.balances = {bidder: [0] for bidder in self.bidders}
        #bidder_id

        # Initialize balances for each bidder to zero
        #for bidder in self.bidders:
        #self.balances[bidder] = [0]*len(users)

    def execute_round(self):
        #user = random.choice(self.users) #Random user
        #user_id = self.users.index(user) #Index of the user 
        user_id = np.random.randint(len(self._users))
        print(user_id)
        bid_price = [bidder.bid(user_id) for bidder in self.bidders]
        potential_winner = []
        highest_bid = 0
        second_highest = 0
        #bids = [(bidder, 1000) for bidder in self.bidders] #Gets the bids for each bidder
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
        #bids.sort(key=lambda x: x[1], reverse=True) #Sorts the bids based on value 
        #winning_bidder = bids[0][0] #Highest Bid
        #winning_price = bids[1][1] if len(bids) > 1 else 0 #Gets second highest bid for the win 
        #print(bids)
        #print(winning_bidder.bid(user_id))
        #np.random.choice(winning_bidder)
        user_clicked = self._users[user_id].show_ad() #Ad click determination 
        for bidder_id in range(len(self.bidders)): 
            if bidder_id == winner: 
                self.bidders[bidder_id].notify(auction_winner=True, price=second_highest, clicked=user_clicked)
                #self.balances[bidder_id].append(self.balances[bidder_id][-1] - second_highest) #Updates the balance by removing the winning price 
                if user_clicked == True: 
                    self.balances[bidder_id] = 1- second_highest 
                else: 
                    self.balances[bidder_id]= -second_highest
            else: 
                self.bidders[bidder_id].notify(auction_winner=False, price=second_highest, clicked=None)
                #self.balance[bidder_id] = 1-second_highest 

        #for bidder in self.bidders:
        #    if bidder == winning_bidder:
        #        bidder.notify(auction_winner=True, price=winning_price, clicked=user_clicked) #Lets bidder know if they won and the price 
        #        self.balances[bidder].append(self.balances[bidder][-1] - winning_price) #Updates the balance by removing the winning price 
        #    else:
        #        bidder.notify(auction_winner=False, price=winning_price, clicked=None) #Notify the other bidders that they didn't even and the price of who won 
        #        self.balances[bidder].append(self.balances[bidder][-1]) #Appens the balance for those that did not win 

    def run_auction(self, num_rounds):
        for _ in range(num_rounds):
            self.execute_round()

    def get_balances(self):
        return self.balances

    def plot_balances(self):
        plt.plot(self.balances)
        #for balance in self.balances:
        #    plt.plot(range(len(balance)), balance, label=f"Bidder")

        plt.xlabel("User")
        plt.ylabel("Balance")
        plt.legend()
        plt.show()


'''
b0, b1, b2 = Bidder(1, 10), Bidder(1, 10), Bidder(1, 10)
auction = Auction([User()], [b0, b1, b2])
auction.run_auction(10)  # Run the auction for 10 rounds
auction.plot_balances()  # Plot the balances of the bidders
'''