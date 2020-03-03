import pandas as pd
import numpy as np

# Processes raw log data, taking the place of an aggregation pipeline

if __name__ == '__main__':
    log = pd.read_csv('log.csv')

    # create new columns
    log['date']=pd.to_datetime(log['ets']).dt.date
    log['gold_earn'] = np.where(log['src_cur_id']=='gold',log.src_cur_amt,0)    

    # users
    u = log.groupby(['uid'])
    u = u.agg({'date':min},as_index=False)
    u = u.rename(columns = {'date':'date_install'})

    # user-days
    ud = log.groupby(['uid','date'])
    ud = ud.agg({'gold_earn':sum})
    ud = ud.reset_index(level='date')
    ud = ud.join(u)
    ud['player_age'] = ud['date'] - ud['date_install']
    ud['player_age'] = ud['player_age'].dt.days

    # player-age days
    a = ud.reset_index().groupby('player_age')
    a = a.agg({'gold_earn':sum,'uid':pd.Series.nunique}) # unique count of uids
    a = a.rename(columns = {'uid':'users'})

    # write
    a.to_csv('analytics_outputs/a.csv')
    ud.to_csv('analytics_outputs/ud.csv')