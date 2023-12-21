import pdb

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .person import Farmer, Taylor, Collector


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

        # Generate economy participants
        self.gen_people()

    def gen_people(self):
        # Define persons in economy
        self.farmer = Farmer(
            amt_cons_food_per_day = 1,
            amt_cons_cloth_per_day = 1,
            amt_cons_fert_per_day=10,
            amt_cons_leaf_per_day=10,
            amt_prod_food_per_day = 4, 
            amt_prod_cloth_per_day = 2,
        )

        self.taylor = Taylor(
            amt_cons_food_per_day = 1,
            amt_cons_cloth_per_day = 1,
            amt_cons_fert_per_day=10,
            amt_cons_leaf_per_day=10,
            amt_prod_food_per_day = 2, 
            amt_prod_cloth_per_day = 4,
        )

        self.collector = Collector(
            amt_cons_food_per_day = 1,
            amt_cons_cloth_per_day = 1,
            amt_cons_fert_per_day=10,
            amt_cons_leaf_per_day=10,
            amt_prod_food_per_day = 0, 
            amt_prod_cloth_per_day = 0,
        )

    
    def log_amounts(self, log_list):
        log_list.append(
            "Farmer: Fert: {0}, Leaf: {1}, Food: {2}, Cloth: {3}, Gold: {4}".format(
                self.farmer.amt_fert, self.farmer.amt_leaf, 
                self.farmer.amt_food, self.farmer.amt_cloth, self.farmer.gold
        ))
        log_list.append(
            "Taylor: Fert: {0}, Leaf: {1}, Food: {2}, Cloth: {3}, Gold: {4}".format(
                self.taylor.amt_fert, self.taylor.amt_leaf, 
                self.taylor.amt_food, self.taylor.amt_cloth, self.taylor.gold
        ))
        log_list.append(f'++++++')
    
    
    def run_economy(self, log_file='log_file'):
        tot_amt_farmer = {}
        tot_amt_taylor = {}
        log_list = []
        for i in self.run_days:
            log_list.append('Day ' + str(i) + ' starts')
            
            self.log_amounts(log_list)

            # Collect natural resources
            log_list.append(f'*********\nCollecting natural resources...')
            self.collector.get_resource(log_list)

            # Trade natural resources
            
            # Produce goods and services
            log_list.append(f'*********\nProducing goods and services...')
            
            self.farmer.produce_goods(log_list)
            self.log_amounts(log_list)
            
            self.taylor.produce_goods(log_list)
            self.log_amounts(log_list)
            
            log_list.append(f'Produce done')
            
            # Trade goods & services
            if self.policy == 'No trading':
                pass
            else:
                log_list.append(f'*********\nTrading...')
                
                self.farmer.trade(self.taylor, self.prices, log_list)
                self.log_amounts(log_list)
                
                self.taylor.trade(self.farmer, self.prices, log_list)
                self.log_amounts(log_list)
                
                log_list.append(f'Trade done')
            
            # Consume
            log_list.append(f'*********\nConsuming...')

            self.farmer.consume(log_list)
            self.log_amounts(log_list)
            
            self.taylor.consume(log_list)
            self.log_amounts(log_list)
            
            log_list.append(f'Consume done')            

            # Bookkeeping
            self.farmer.calc_tot_wealth(self.prices)
            self.taylor.calc_tot_wealth(self.prices)
            
            tot_amt_farmer[i] = {
                'fert': self.farmer.amt_fert, 
                'leaf': self.farmer.amt_leaf, 
                'food': self.farmer.amt_food, 
                'cloth': self.farmer.amt_cloth,
                'gold': self.farmer.gold,
                'wealth': self.farmer.wealth
            }
            tot_amt_taylor[i] = {
                'fert': self.taylor.amt_fert, 
                'leaf': self.taylor.amt_leaf, 
                'food': self.taylor.amt_food, 
                'cloth': self.taylor.amt_cloth,
                'gold': self.taylor.gold,
                'wealth': self.taylor.wealth
            }

            log_list.append('Day ' + str(i) + ' ends')
            log_list.append('-------------------------')
                    
        # total amount per person
        df_tot_amt_farmer = pd.DataFrame.from_dict(tot_amt_farmer, orient='index')
        df_tot_amt_taylor = pd.DataFrame.from_dict(tot_amt_taylor, orient='index')
        
        # total wealth of economy
        tot_wealth = (
            df_tot_amt_farmer['wealth'] + df_tot_amt_taylor['wealth']
        )
        
        self.farmer.df_tot_amt = df_tot_amt_farmer
        self.taylor.df_tot_amt = df_tot_amt_taylor
        self.tot_wealth = tot_wealth
        
        # Logging
        self.log = '\n'.join(log_list)
        with open(f'logs/{log_file}.txt', "w") as file:
            file.write(self.log)
        print(f"Log saved to {log_file}.txt!")