'''
Simulate a second-price auction with a set of bidders with random probabilities
'''
import random
class Bidder:
    '''
    Class for the specific bidder
    '''
    def __init__(self, num_users, num_rounds):
        '''
        Initializes the number of users and number of rounds in auction 
        '''
        self.num_users = num_users
        self.num_rounds = num_rounds
        self.balances = {}
        self.valuations = {user_id: random.uniform(0, 1) for user_id in range(num_users)}


    def bid(self, user_id):
        '''
        Creates a bid for a user based on valuation
        '''
        if user_id in self.valuations:
            valuation = self.valuations[user_id]
            return valuation
        else:
            return random.uniform(0, 1)  # Random bid if no valuation is set for the user

    def notify(self, auction_winner, price, clicked):
        '''
        Notify bidder if they are a winner in the auction 
        '''
        if auction_winner and clicked is not None:
            if self.balances:
                user_id = next(iter(self.balances))
                if len(self.balances[user_id]) > 0:
                    self.balances[user_id][-1] -= price
