import math
from datetime import datetime

# The player's account on the server

class Account:
    
    _instances = dict()

    def __init__(self):
        self.username = 'UserName'
        self.user_id = len(self._instances)
        
        # TODO abstract these to config
        self.gold = 100
        self.gold_vault_amnt_max = 10000 # max gold that can be held in the vault
        self.gold_mine_amnt = 0 # current amount held by the gold mine
        self.gold_mine_amnt_max = 200 # max amount held by the gold mine
        self.gold_mine_prod = 5 # amount produced by the gold mine every second
        time_now = datetime.now()
        self.install_time = time_now.replace(minute=math.floor(time_now.minute/5)*5, second=0, microsecond=0)
        self.last_active_time = self.install_time
        
        self._instances[self.user_id] = self

    def update(self,cur_time):
        # TODO validation and error handling
        try:
            cur_time = datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S.%f")
        except:
            cur_time = datetime.strptime(cur_time,"%Y-%m-%d %H:%M:%S")
        time_delta_sec = (cur_time - self.last_active_time).total_seconds()
        print(f"Updating account with user id {self.user_id} due to time delta:"+str(time_delta_sec))
        self.gold_mine_amnt += min(time_delta_sec * self.gold_mine_prod, self.gold_mine_amnt_max - self.gold_mine_amnt)
        self.last_active_time = cur_time