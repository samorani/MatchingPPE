import pandas as pd
import numpy as np
import datetime
import os
import pickle


def simulate(ppe_strategy,delta,donors_file = 'data/anon_donors.csv', recipients_file = 'data/anon_recipients.csv',
    distance_file = "data/anon_distance_matrix.p", debug = False,writeFiles = False):

    # load files
    all_donors = pd.read_csv(donors_file,parse_dates=['date'],index_col=0)
    all_recipients = pd.read_csv(recipients_file,parse_dates=['date'],index_col=0)
    try:
        distance_mat = pd.read_csv(distance_file,index_col=0)
    except:
        try:
            distance_mat = pickle.load( open(distance_file, "rb" ) )
        except:
            raise(f'Cannot load distance matrix {distance_file}')

    ppes = all_recipients['ppe'].unique()

    # returns the distance between a donor and a recipient
    def get_distance(don_id,rec_id):
        return distance_mat.loc[(distance_mat.don_id == don_id)&(distance_mat.rec_id == rec_id),'distance'].values[0]

    # run analysis
    # # set parameters here
    interval = delta
    strategy = ppe_strategy
    max_donation_qty = 1000
    # end set parameters

    #TODO instead of removing the mistakes here, remove them from the data set during the preparation
    all_donors = all_donors[all_donors.qty <= max_donation_qty]

    cur_donors = all_donors.drop(index=all_donors.index)
    cur_recipients = all_recipients.drop(index=all_recipients.index)

    cur_date = min(all_recipients.date.min(),all_donors.date.min()) - datetime.timedelta(minutes=1)
    max_date = max(all_recipients.date.max(),all_donors.date.max()) + datetime.timedelta(minutes=1)

    d1 = cur_date
    d2 = cur_date + datetime.timedelta(days=interval)


    all_granular_decisions = pd.DataFrame(columns=['don_id','rec_id','ppe', 'date','qty','distance','holding_time'])
    last_iteration = False
    while not last_iteration:
        if d2 > max_date:
            d2=max_date + datetime.timedelta(minutes=2)
            last_iteration = True
        if debug:
            print(f'===== From {d1} to {d2} ======')
        cur_recipients = pd.concat([cur_recipients, all_recipients.loc[(all_recipients.date > d1)&(all_recipients.date < d2)].copy()])
        cur_donors = pd.concat([cur_donors, all_donors.loc[(all_donors.date > d1)&(all_donors.date < d2)].copy()])

        # aggregate cur_donors and cur_recipients:
        # these tables could have multiple rows for each donor (or recipient) for the same ppe. We need to create new dataframes with one row for each donor_id (or recipient_id) and ppe. We will pass these tables to the method strategy below
        agg_cur_donors = cur_donors.groupby(['don_id','ppe']).agg({'date':'min','qty':'sum'}).reset_index()
        agg_cur_recipients = cur_recipients.groupby(['rec_id','ppe']).agg({'date':'min','qty':'sum'}).reset_index()

        # for each date, write the current pending requests
        don_rec = pd.DataFrame(agg_cur_donors.merge(agg_cur_recipients,on=['ppe']).groupby(['don_id','rec_id']).groups.keys())
        if len(agg_cur_recipients) == 0 or len(agg_cur_donors) == 0 or len(don_rec) == 0:
            d1 = d2 # if there are no recipients, no donors, or no compatible pairs of donor-recipient, continue
            d2 = d1 + datetime.timedelta(days=interval)
            continue

        don_rec.columns=['don_id','rec_id']
        cur_distance_mat = don_rec.merge(distance_mat,on=['don_id','rec_id'])

        dir = f'output/{d2.date()}'
        if writeFiles:
            if not os.path.exists(dir):
                os.mkdir(dir)
            agg_cur_recipients.to_csv(dir+f'/recipients.csv')
            agg_cur_donors.to_csv(dir+f'/donors.csv')
            cur_distance_mat.to_csv(dir+f'/distance_matrix.csv')

        agg_decisions = strategy(d2,agg_cur_donors,agg_cur_recipients,cur_distance_mat)

        agg_decisions['date'] = d2
        agg_decisions = agg_decisions.merge(cur_distance_mat,on=['don_id','rec_id'])

        # The dataframe of agg_decisions contains the aggregated shipping decisions
        # example
        #    don_id rec_id          ppe   qty                      date     distance
        # 0   don0   rec0  faceShields  10.0 2020-04-09 16:26:00+00:00  2548.016134
        # 1   don1   rec1  faceShields   1.0 2020-04-09 16:26:00+00:00  2527.163615
        # 2   don3   rec2  faceShields   5.0 2020-04-09 16:26:00+00:00  2359.760082

        # turn it into granular decisions
        granular_decisions = pd.DataFrame(columns=['don_id','rec_id','ppe', 'date','qty','holding_time'])
        for _,cur_dec in agg_decisions.iterrows():
            don = cur_dec.don_id
            rec = cur_dec.rec_id
            ppe = cur_dec.ppe
            dd = cur_dec.date
            totremqty = cur_dec.qty
            don_df = cur_donors[(cur_donors.don_id == don)&(cur_donors.ppe == ppe)].sort_values('date') # just this ppe and don rec
            rec_df = cur_recipients[(cur_recipients.rec_id == rec)&(cur_recipients.ppe == ppe)].sort_values('date')

            dilocx = 0
            rilocx = 0
            # if debug:
            #     print ('========================================================')
            #     print(f'decision: ship {totremqty} from {don} to {rec}')
            #     print(f'cur_donors = \n{cur_donors}\n cur_recipients = \n{cur_recipients}\n')
            while totremqty > 0:
                drow = don_df.iloc[dilocx]
                rrow = rec_df.iloc[rilocx]
                dix = drow.name
                rix = rrow.name
                # print(f'remaining qty = {totremqty}. Donor row = [{drow.name,drow.don_id,drow.qty}]. Recipient row = [{rrow.name,rrow.rec_id,rrow.qty}].')
                shipped_qty = min(drow.qty,rrow.qty,totremqty)
                # make the granular decision of shipping
                granular_decisions.loc[len(granular_decisions)] = [drow.don_id,rrow.rec_id,ppe,dd,shipped_qty,np.round((dd-drow.date).total_seconds() / 24 / 3600)]
                # print (f'Granular decisions: ship {shipped_qty} from {drow.don_id} to {rrow.rec_id}')
                # update quantities
                totremqty-=shipped_qty

                #update donors table
                cur_donors.loc[dix,'qty'] -= shipped_qty
                don_df.loc[dix,'qty'] -= shipped_qty

                #update recipient qty
                cur_recipients.loc[rix,'qty'] -= shipped_qty
                rec_df.loc[rix,'qty'] -= shipped_qty

                # this shipping action has one of the following outcomes: (1) brings rrow.qty to 0, (2) brings drow.qty to 0, (3) brings neither to 0

                if rec_df.loc[rix,'qty'] == 0:
                    rilocx+=1
                    if rilocx == len(rec_df) and totremqty > 0:
                        # The decisions is infeasible because I am trying to ship more than requested
                        raise('The decisions is infeasible because I am trying to ship more than requested')
                elif don_df.loc[dix,'qty'] == 0:
                    dilocx+=1
                    if dilocx == len(don_df) and totremqty > 0:
                        # The decisions is infeasible because I am trying to ship more than supplied
                        raise('The decisions is infeasible because I am trying to ship more than supplied')
                else:
                    # should be totremqty == 0
                    if totremqty != 0:
                        raise('Weird error. If I am here, I should have totremqty == 0')
            # if debug:
            #     print ('========================================================')
            #     print(f'cur_donors = \n{cur_donors}\n cur_recipients = \n{cur_recipients}\n')
            #     print(f'remaining qty = {totremqty}. Donor row = [{drow.name,drow.don_id,drow.qty}]. Recipient row = [{rrow.name,rrow.rec_id,rrow.qty}].')

            # remove from tables those with qty == 0
            cur_donors = cur_donors.loc[cur_donors.qty > 0]
            cur_recipients = cur_recipients.loc[cur_recipients.qty > 0]


        granular_decisions = granular_decisions.merge(cur_distance_mat,on=['don_id','rec_id'])





        all_granular_decisions = pd.concat([all_granular_decisions,granular_decisions],ignore_index=True)
        # update decisions and print current decisions
        if writeFiles:
            granular_decisions.to_csv(dir+f'/decisions.csv')
        d1 = d2
        d2 = d1 + datetime.timedelta(days=interval)

    # print all decisions made
    all_granular_decisions.to_csv('output/decisions.csv')
    return all_recipients, all_donors, all_granular_decisions
