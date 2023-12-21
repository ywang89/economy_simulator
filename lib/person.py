import pdb

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Define `person`
class Person:
    def __init__(
        self,
        name = None,
        occupation = None,
        prices = {},
        amt_cons_food_per_day = None,
        amt_cons_cloth_per_day =None,
        amt_cons_fert_per_day = None,
        amt_cons_leaf_per_day = None,
        amt_prod_food_per_day = None, 
        amt_prod_cloth_per_day = None,
    ):  
        '''
        Parameters
        ----------
        prices: dict
            Prices of each good
        '''
        # Natural resources
        self.amt_fert = 99999
        self.amt_leaf = 99999
        # Goods and services
        self.amt_food = 10
        self.amt_cloth = 10
        # gold
        self.gold = 100

        # Basic info
        self.name = name
        self.occupation = occupation
        
        # Consumption config
        self.amt_cons_food_per_day = amt_cons_food_per_day
        self.amt_cons_cloth_per_day = amt_cons_cloth_per_day
        
        # Production config
        self.amt_cons_fert_per_day = amt_cons_fert_per_day
        self.amt_cons_leaf_per_day = amt_cons_leaf_per_day

        self.amt_prod_food_per_day = amt_prod_food_per_day
        self.amt_prod_cloth_per_day = amt_prod_cloth_per_day
        
        # Price
        self.prices = prices

    def gen_name(self):
        if self.name != None:
            raise Exception('`name` already exists.')

        adjectives = ['Happy', 'Cheerful', 'Dilligent', 'Busy']
        names = ['Joe', 'Agnes', 'Mary', 'Charlie']

        n1 = np.random.choice(adjectives)
        n2 = np.random.choice(names)

        return ' '.join([n1, n2])
    
    
    def consume(self, log_list):
        if self.amt_food >= self.amt_cons_food_per_day:
            self.amt_food = self.amt_food - self.amt_cons_food_per_day
        else:
            raise Exception('No food to consume')
        
        if self.amt_cloth >= self.amt_cons_cloth_per_day:
            self.amt_cloth = self.amt_cloth - self.amt_cons_cloth_per_day
        else:
            raise Exception('No cloth to consume')
        
        log_list.append(f'{self.name} done.')

    # Production
    def _produce_food(self, log_list):
        if self.amt_fert >= self.amt_cons_fert_per_day:
            self.amt_fert = self.amt_fert - self.amt_cons_fert_per_day
            self.amt_food = self.amt_food + self.amt_prod_food_per_day
        else:
            log_list.append(self.name + ' doesn\'t have enough resource to produce.')

    def _produce_cloth(self, log_list):
        if self.amt_leaf >= self.amt_cons_leaf_per_day:
            self.amt_leaf = self.amt_leaf - self.amt_cons_leaf_per_day
            self.amt_cloth = self.amt_cloth + self.amt_prod_cloth_per_day
        else:
            log_list.append(self.name + ' doesn\'t have enough resource to produce.')

    def _get_prod_func(self):
        self.prod_funcs = [self._produce_food, self._produce_cloth]
        
    def produce_goods(self, log_list): 
        '''
        Produce goods, more likely to produce goods that person is good at.
        '''
        # When one prodcut is 0 then must produce it
        if self.amt_cloth == 0:
            goods = pd.Series({'food': 0, 'cloth': 1})
        elif self.amt_food == 0:
            goods = pd.Series({'food': 1, 'cloth': 0})
        # Common case, produce something you are good at
        else:
            goods = pd.Series({
                'food': self.amt_prod_food_per_day,
                'cloth': self.amt_prod_cloth_per_day
            })

        cumulative_p = np.cumsum(goods / goods.sum())

        self._get_prod_func()

        rand_num = np.random.random()
        for prod_func, cp in zip(self.prod_funcs, cumulative_p):
            if rand_num < cp:
                prod_func(log_list)
                break

        log_list.append(f'{self.name} done.')
        
    def trade(self, other, prices, log_list):
        '''
        Trades with another `person`.
        '''
        # Determine trading probabilities `p`
        p = pd.Series({
            'no_trade': np.nan,
            'b_f': np.nan,
            'b_c': np.nan,
            })
        if (self.amt_food // self.amt_cons_food_per_day <= 1):
            p['no_trade'] = 0
            p['b_f'] = 1
        elif (self.amt_cloth // self.amt_cons_cloth_per_day <= 1):
            p['no_trade'] = 0
            p['b_f'] = 0
        else:
            p['no_trade'] = 0.1 # 10% chance a person simply doesn't want to trade
            p_trade = 1 - p['no_trade']
            p['b_f'] = p_trade * (1 - self.amt_food / (self.amt_cloth + self.amt_food))
        p['b_c'] =  1 - p['no_trade'] - p['b_f']

        # Trade according to `p`
        choice = np.random.choice([0, 1, 2], size=1, p=p)
        if choice == 0:
            log_list.append(self.name + ' didn\'t trade.')
        elif choice == 1:
            self._buy_food(other, prices, log_list)
        elif choice == 2:
            self._buy_cloth(other, prices, log_list)
        else:
            raise Exception('Invalid choice.')
                
        
    def _buy_food(self, seller, prices, log_list):
        '''
        Buys 1 amount of food.
        '''
        if seller.amt_food > 1:         
            if self.gold > prices['food'] * 1:
                self.gold = self.gold - 1 * prices['food']
                seller.gold = seller.gold + 1 * prices['food']
                
                self.amt_food = self.amt_food + 1
                seller.amt_food = seller.amt_food - 1
                
                log_list.append(f'{self.name} bought 1 food from {seller.name}')
        else:
            log_list.append('Seller ' + seller.name + ' doesn\'t have enough to sell.')

    def _buy_cloth(self, seller, prices, log_list):
        '''
        Buys 1 amount of cloth.
        '''
        if seller.amt_cloth > 1:
            if self.gold > prices['cloth'] * 1:
                self.gold = self.gold - 1 * prices['cloth']
                seller.gold = seller.gold + 1 * prices['cloth']
                
                self.amt_cloth = self.amt_cloth + 1
                seller.amt_cloth = seller.amt_cloth - 1
                
                log_list.append(f'{self.name} bought 1 cloth from {seller.name}')
        else:
            log_list.append('Seller ' + seller.name + ' doesn\'t have enough to sell.')

    def calc_tot_wealth(self, prices):
        '''
        Calculates total gold value.
        '''
        wealth = self.gold + \
            prices['food'] * self.amt_food + prices['cloth'] * self.amt_cloth + \
            prices['fert'] * self.amt_fert + prices['leaf'] * self.amt_leaf
            
        self.wealth = wealth


class Farmer(Person):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.gen_name()
        self.occupation = 'Farmer'



        
class Taylor(Person):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.gen_name()
        self.occupation = 'Taylor'



        
