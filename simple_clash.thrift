namespace py sc_thrift

service SCService {
    i32 create_account(
        1:string account_profile
        ),
    Account get_account(
        1:i32 user_id,
        2:string client_time
        ),
    void collect_gold_mine(
        1:i32 user_id
        2:string client_time
        ),        
}

struct Account {
    1: i32 gold,
    2: i32 gold_vault_amnt_max,
    3: double gold_mine_amnt,
    4: i32 gold_mine_amnt_max,
    5: double gold_mine_prod,
    6: string install_time,
    7: string last_active_time,
}