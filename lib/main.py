import pdb

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define `person`
class person:
    def __init__(
        self,
        name,
        amt_cons_food_per_day,
        amt_cons_cloth_per_day,

        amt_cons_fert_per_day,
        amt_cons_leaf_per_day,

        amt_prod_food_per_day, 
        amt_prod_cloth_per_day,
        prices,
    ):  
        '''
        Parameters
        ----------
        prices: dict
            Prices of each good
        '''
        self.name = name

        # Natural resources
        self.amt_fert = 99999
        self.amt_leaf = 99999
        # Goods and services
        self.amt_food = 10
        self.amt_cloth = 10
        # gold
        self.gold = 100
        
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
            p['no_trade'] = 0.1 # 10% a person simply doesn't want to trade
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


# Define `economy`
class economy:
    
    def __init__(
        self,
        run_days=20,
        prices={},
        policy='',
        # **kwargs, include list of persons
    ):
        '''
        Parameters
        ----------
        run_days: int
            Number of days to run the economy.
        '''
        self.run_days = np.arange(0, run_days, step=1)
        self.log = ''
        self.prices = prices
        self.policy = policy
        
        # Define persons in economy
        self.farmer = person(
            name = 'farmer',
            amt_cons_food_per_day = 1,
            amt_cons_cloth_per_day = 1,

            amt_cons_fert_per_day=10,
            amt_cons_leaf_per_day=10,
            amt_prod_food_per_day = 4, 
            amt_prod_cloth_per_day = 2,
            prices = prices
        )

        self.carpenter = person(
            name = 'carpenter',
            amt_cons_food_per_day = 1,
            amt_cons_cloth_per_day = 1,
            amt_cons_fert_per_day=10,
            amt_cons_leaf_per_day=10,
            amt_prod_food_per_day = 2, 
            amt_prod_cloth_per_day = 4,
            prices = prices
        )
        
    def log_amounts(self, log_list):
        log_list.append(
            "Farmer: Fert: {0}, Leaf: {1}, Food: {2}, Cloth: {3}, gold: {4}".format(
                self.farmer.amt_fert, self.farmer.amt_leaf, 
                self.farmer.amt_food, self.farmer.amt_cloth, self.farmer.gold
        ))
        log_list.append(
            "Carpenter: Fert: {0}, Leaf: {1}, Food: {2}, Cloth: {3}, gold: {4}".format(
                self.carpenter.amt_fert, self.carpenter.amt_leaf, 
                self.carpenter.amt_food, self.carpenter.amt_cloth, self.carpenter.gold
        ))
        log_list.append(f'++++++')
    
    
    def run_economy(self, log_file='log_file'):
        tot_amt_farmer = {}
        tot_amt_carpenter = {}
        log_list = []
        for i in self.run_days:
            log_list.append('Day ' + str(i) + ' starts')
            
            self.log_amounts(log_list)
            
            # Produce
            log_list.append(f'*********\nProducing...')
            
            self.farmer.produce_goods(log_list)
            self.log_amounts(log_list)
            
            self.carpenter.produce_goods(log_list)
            self.log_amounts(log_list)
            
            log_list.append(f'Produce done')
            
            # Trade
            if self.policy == 'No trading':
                pass
            else:
                log_list.append(f'*********\nTrading...')
                
                self.farmer.trade(self.carpenter, self.prices, log_list)
                self.log_amounts(log_list)
                
                self.carpenter.trade(self.farmer, self.prices, log_list)
                self.log_amounts(log_list)
                
                log_list.append(f'Trade done')
            
            # Consume
            log_list.append(f'*********\nConsuming...')

            self.farmer.consume(log_list)
            self.log_amounts(log_list)
            
            self.carpenter.consume(log_list)
            self.log_amounts(log_list)
            
            log_list.append(f'Consume done')            

            # Bookkeeping
            self.farmer.calc_tot_wealth(self.prices)
            self.carpenter.calc_tot_wealth(self.prices)
            
            tot_amt_farmer[i] = {
                'fert': self.farmer.amt_fert, 
                'leaf': self.farmer.amt_leaf, 
                'food': self.farmer.amt_food, 
                'cloth': self.farmer.amt_cloth,
                'gold': self.farmer.gold,
                'wealth': self.farmer.wealth
            }
            tot_amt_carpenter[i] = {
                'fert': self.carpenter.amt_fert, 
                'leaf': self.carpenter.amt_leaf, 
                'food': self.carpenter.amt_food, 
                'cloth': self.carpenter.amt_cloth,
                'gold': self.carpenter.gold,
                'wealth': self.carpenter.wealth
            }

            log_list.append('Day ' + str(i) + ' ends')
            log_list.append('-------------------------')
                    
        # total amount per person
        df_tot_amt_farmer = pd.DataFrame.from_dict(tot_amt_farmer, orient='index')
        df_tot_amt_carpenter = pd.DataFrame.from_dict(tot_amt_carpenter, orient='index')
        
        # total wealth of economy
        tot_wealth = (
            df_tot_amt_farmer['wealth'] + df_tot_amt_carpenter['wealth']
        )
        
        self.farmer.df_tot_amt = df_tot_amt_farmer
        self.carpenter.df_tot_amt = df_tot_amt_carpenter
        self.tot_wealth = tot_wealth
        
        # Logging
        self.log = '\n'.join(log_list)
        with open(f'logs/{log_file}.txt', "w") as file:
            file.write(self.log)
        print(f"Log saved to {log_file}.txt!")