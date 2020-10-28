# -*- coding: utf-8 -*-

import thriftpy2
import pandas as pd

from account import Account
from datetime import datetime
from thriftpy2.rpc import make_server

from event import Event

sc_thrift = thriftpy2.load("simple_clash.thrift", module_name="sc_thrift")
# profiles = sc_thrift.Profile

class Dispatcher(object):
    
    def __init__(self):
        print("Getting config")
        self.config = {}
        df_account = pd.read_excel('config/excel/account.xlsx',sheet_name='account')
        df_account = df_account.set_index(['account_profile','attr_name'])
        self.config['account'] = df_account

    def ping(self):
        print("Got ping")
        return ('The server was pinged')

    def create_account(self,account_profile):
        print(f"Got request to create an account with profile {account_profile}")
        params = {}
        account_config = self.config['account'].loc[account_profile]
        params['starting_gold'] = account_config.loc['starting_gold']['value_int']
        account = Account(params)
        print("Created account with user ID " + str(account.user_id))
        return account.user_id

    def get_account_local(self,user_id):
        return Account._instances[user_id]

    # find and serialize a specified account for Thrift
    def get_account(self, user_id, client_time):
        # print(f"Got request for account for user {user_id}")
        account_py = self.get_account_local(user_id)
        # if any time has passed, also update the account
        if not client_time is None:
            try:
                client_time_dt = datetime.strptime(client_time,"%Y-%m-%d %H:%M:%S.%f")
            except:
                client_time_dt = datetime.strptime(client_time,"%Y-%m-%d %H:%M:%S")
            if client_time_dt > account_py.last_active_time:
                account_py.update(client_time)

        # serialize
        account_thrift = sc_thrift.Account(
            gold=account_py.gold,
            gold_vault_amnt_max=account_py.gold_vault_amnt_max,
            gold_mine_amnt=account_py.gold_mine_amnt,
            gold_mine_amnt_max=account_py.gold_mine_amnt_max,
            gold_mine_prod=account_py.gold_mine_prod,
            install_time=str(account_py.install_time),
            last_active_time=str(account_py.last_active_time)
        )
        return account_thrift

    # def install_time(self, user_id):
    #     print("Got request for install time for user "+str(user_id))
    #     user = self.get_account(user_id)
    #     return str(user.install_time)

    # def cur_time():
    #     return user.cur_time()

    def collect_gold_mine(self, user_id, client_time):
        account_py = self.get_account_local(user_id)
        transact_amnt = min(account_py.gold_vault_amnt_max-account_py.gold,account_py.gold_mine_amnt)
        account_py.gold_mine_amnt -= transact_amnt
        account_py.gold += transact_amnt
        # send data
        payload = {'cat':'base_ui','src':'gold_mine','act':'collect','tgt':'gold_mine'}
        payload['src_cur_id'] = 'gold'
        payload['src_cur_amt'] = transact_amnt
        payload['sts']=client_time
        payload['uid']=user_id
        self.send_event(payload)

    def send_event(self,payload):
        payload['evt_src']='server'
        # print("In Server.send_event()")
        # in reality, the server would send its own time
        # here, the client passes its current time for the server to print to events
        if 'sts' not in payload:
            payload['sts']=self.cur_time            
        Event(payload)

def main():
    server = make_server(sc_thrift.SCService, Dispatcher(),'127.0.0.1', 6000)
    print("serving...")

    server.serve()

if __name__ == '__main__':
    main()
