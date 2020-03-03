# -*- coding: utf-8 -*-

import thriftpy2
import math
import random
from pynput.keyboard import Key, Listener
from thriftpy2.rpc import client_context
from thriftpy2.protocol import TCyBinaryProtocolFactory
from thriftpy2.transport import TCyBufferedTransportFactory
from datetime import datetime
from datetime import timedelta
from croniter import croniter

from event import Event


sc_thrift = thriftpy2.load("simple_clash.thrift", module_name="sc_thrift")

class App:

    def __init__(self,context):
        self.running = True
        self.context = context
        self.user_id = self.create_account()
        time_now = datetime.now()
        self.install_time = time_now.replace(minute=math.floor(time_now.minute/5)*5, second=0, microsecond=0)
        self.cur_time = self.install_time
        self.session_count = 0
        self.session_limit = 1000
        self.session_iteration_limit = 1000
        self.rolling_retention = 0.9 # chance to retain to another session TODO should be days

    # Asks the server to create an account
    def create_account(self):
        user_id = self.context.create_account()
        print("Server created account for me with id "+str(user_id))
        return user_id

    # Get account state from the server
    def get_account(self):
        account = self.context.get_account(self.user_id, str(self.cur_time))
        return account

    def play(self):
        print("Starting gameplay iteration")

        i=0
        i_lim=self.session_limit
        while i<i_lim and self.rolling_retention > random.uniform(0,1):
            self.play_session()
            self.session_count+=1
            self.cur_time = self.cur_time + timedelta(days=1)
            i+=1

    def play_session(self): 
        
        print(f"Starting session {self.session_count}. Current time: {self.cur_time}")

        i=0 # iterations - each iteration, the user chooses a thing to do, then time adanvces by tick length
        i_lim=self.session_iteration_limit # don't do more than this many iterations
        boredom=0 # the user gains boredom equal to tick length when they do nothing
        boredom_resilience=30 # user is immune to boredom less than this
        tick_length_secs=5 # default tick length - some choices increase tick length for the current iteration
        while i<i_lim:
            # Start iteration
            account = self.get_account()
            time_delta_from_choice = 0
            str_iter = ''
            str_iter += f"Iteration {str(i)} - Current time: {str(self.cur_time)}"

            # Decide what to do
            choices = {}

            # Collect the gold mine?
            mine_pct_full = account.gold_mine_amnt/account.gold_mine_amnt_max
            vault_pct_empty = 1 - (account.gold/account.gold_vault_amnt_max)
            wght_collect_gold_mine = 100 * min(vault_pct_empty,mine_pct_full)
            choices['collect_gold_mine'] = wght_collect_gold_mine

            # Have a chance to do nothing and wait tick length, becoming bored
            choices['do_nothing'] = 20

            # Log off, with a chance proportional to boredom
            wght_log_off = 0
            if boredom > boredom_resilience:
                wght_log_off = boredom
            choices['log_off'] = wght_log_off
            
            # print(f'Choices: {choices}')
            choice = random.choices(list(choices.keys()),list(choices.values()))[0]
            str_iter += f'. Choosing to: {choice}'
            # print(str_iter)

            if choice == 'collect_gold_mine':
                self.collect_gold_mine()
            elif choice == 'do_nothing':
                boredom+=tick_length_secs
                # print("Getting bored. Boredom: "+str(boredom))
            elif choice == 'log_off':
                # print(f'Logging off due to boredom. Current time: {self.cur_time}')
                return

            # Close iteration, advance time
            self.cur_time = self.cur_time + timedelta(seconds=tick_length_secs+time_delta_from_choice)
            i+=1

        print(f"Exiting due to hitting iteration limit. Current: {str(i)} Max: {str(i_lim)}")

    def collect_gold_mine(self):
        self.context.collect_gold_mine(self.user_id, str(self.cur_time))
        
        self.send_event({'cat':'base_ui','src':'gold_mine','act':'collect','tgt':'gold_mine'})

    def dump_acct(self):
        print(self.get_account())

    def send_event(self,payload):
        payload['evt_src']='client'
        payload['cts']=self.cur_time
        payload['uid']=self.user_id
        Event(payload)

def main():
    with client_context(sc_thrift.SCService, '127.0.0.1', 6000,
        proto_factory=TCyBinaryProtocolFactory(),
        trans_factory=TCyBufferedTransportFactory()) as context:
        client = App(context)
        client.play()
        # client.dump_acct()

if __name__ == '__main__':
    main()