# import pandas as pd
# import numpy as np
# import datetime
# import os
# import shutil
# import pickle

# # Global variables
# debug = True
# writeFiles = True


# # load files
# all_donors = pd.read_csv('data/anon_donors.csv',parse_dates=['date'],index_col=0)
# all_recipients = pd.read_csv('data/anon_recipients.csv',parse_dates=['date'],index_col=0)
# distance_mat = pickle.load( open( "data/anon_distance_matrix.p", "rb" ) )


# # reshape recipients
# all_recipients = all_recipients.set_index(['rec_id','date']).stack().to_frame().reset_index()
# all_recipients.columns=['rec_id','date','ppe','qty']
# all_recipients = all_recipients[all_recipients['qty']>0]
# ppes = all_recipients['ppe'].unique()

# # returns the distance between a donor and a recipient 
# def get_distance(don_id,rec_id):
#     return distance_mat.loc[(distance_mat.don_id == don_id)&(distance_mat.rec_id == rec_id),'distance'].values[0]


    
# #### dummy strategy: first come-first-matched
# # date is the current date
# # curdon is the dataframe of current donors with the given ppe (don_req_id,don_id,date,ppe,qty)
# # currec is the dataframe of current recipients with the given ppe (rec_req_id,rec_id,date,ppe,qty)
# # ppe is the current ppe

# # assumptions: curdon currec must have one row per (don_id/rec_id,ppe)
# # return dataframe of decisions (don_id,rec_id,ppe,qty)
# def dummy_strategy(date,curdon,currec,curdistance_mat):
#     result = pd.DataFrame(columns=['don_id','rec_id','ppe','qty'])
#     ppes_to_consider = set(curdon.ppe.unique())
#     ppes_to_consider = ppes_to_consider.intersection(set(currec.ppe.unique()))

#     for ppe in ppes_to_consider:
#         donors_ppe = curdon[curdon.ppe == ppe]
#         recipients_ppe = currec[currec.ppe == ppe]

#         n = min(len(donors_ppe),len(recipients_ppe))
#         for i in range(n):
#             don = donors_ppe.iloc[i] # (don_req_id,don_id,date,ppe,qty)
#             rec = recipients_ppe.iloc[i]
#             qty = min(don.qty,rec.qty)
#             result.loc[len(result)] = [don.don_id,rec.rec_id,ppe,qty]
#     return result

# # proximity match strategy
# def proximity_match_strategy(date,curdon,currec,curdistance_mat):
#     result = pd.DataFrame(columns=['don_id','rec_id','ppe','qty'])
#     ppes_to_consider = set(curdon.ppe.unique())
#     ppes_to_consider = ppes_to_consider.intersection(set(currec.ppe.unique()))

#     for ppe in ppes_to_consider:
#         donors_ppe = curdon[curdon.ppe == ppe]
#         recipients_ppe = currec[currec.ppe == ppe]

#         for _, drow in donors_ppe.iterrows():
#             # find the closest recipient to drow.don_id
#             dr = curdistance_mat[(curdistance_mat.don_id == drow.don_id)].merge(recipients_ppe,on='rec_id').sort_values('distance').iloc[0]
#             dqty = drow.qty # donor's qty
#             rqty = recipients_ppe.loc[recipients_ppe.rec_id == dr.rec_id,'qty'].values[0] #recipient's qty
#             qty = min(dqty,rqty) #qty to ship
#             if qty == 0:
#                 print('qty is zero')
#             if qty == rqty:
#                 recipients_ppe = recipients_ppe[recipients_ppe.rec_id !=  dr.rec_id] # remove recipient
#             else:
#                 recipients_ppe.loc[recipients_ppe.rec_id == dr.rec_id,'qty'] -= qty #update recipient's qty
#             result.loc[len(result),:] = [dr.don_id, dr.rec_id,ppe,qty]

#     return result

# # run analysis 
# # # set parameters here
# interval = 7
# strategy = proximity_match_strategy
# max_donation_qty = 1000
# # end set parameters

# all_donors = all_donors[all_donors.qty <= max_donation_qty]
# cur_donors = all_donors.drop(index=all_donors.index)
# cur_recipients = all_recipients.drop(index=all_recipients.index)

# cur_date = min(all_recipients.date.min(),all_donors.date.min())- datetime.timedelta(minutes=1)
# max_date = max(all_recipients.date.max(),all_donors.date.max())+ datetime.timedelta(minutes=1)

# d1 = cur_date
# d2 = cur_date + datetime.timedelta(days=interval)

# alldecisions = pd.DataFrame(columns=['date','don_id','rec_id','ppe','qty','distance'])
# while d2 < max_date:
#     if debug:
#         print(f'===== From {d1} to {d2} ======')
#     cur_recipients = pd.concat([cur_recipients, all_recipients.loc[(all_recipients.date > d1)&(all_recipients.date < d2)].copy()])
#     cur_donors = pd.concat([cur_donors, all_donors.loc[(all_donors.date > d1)&(all_donors.date < d2)].copy()])

#     # aggregate cur_donors and cur_recipients:
#     # these tables could have multiple rows for each donor (or recipient) for the same ppe. We need to create new dataframes with one row for each donor_id (or recipient_id) and ppe. We will pass these tables to the method strategy below
#     agg_cur_donors = cur_donors.groupby(['don_id','ppe']).agg({'date':'max','qty':'sum'}).reset_index()
#     agg_cur_recipients = cur_recipients.groupby(['rec_id','ppe']).agg({'date':'max','qty':'sum'}).reset_index()

#     if (len(agg_cur_donors) != len(cur_donors) and debug):
#         print('agg_cur_donors and cur_donors have different lengths')
#     if (len(agg_cur_recipients) != len(cur_recipients) and debug):
#         print('agg_cur_recipients and cur_recipients have different lengths')


#     # for each date, write the current pending requests

#     if len(agg_cur_recipients) == 0 or len(agg_cur_donors) == 0:
#         continue 

#     cur_distance_mat = agg_cur_donors.merge(agg_cur_recipients,on='ppe').merge(distance_mat,on=['don_id','rec_id'])[['don_id','rec_id','distance']]

#     dir = f'output/{d2.date()}' 
#     if writeFiles:
#         if not os.path.exists(dir):
#             os.mkdir(dir)
#         agg_cur_recipients.to_csv(dir+f'/recipients.csv')
#         agg_cur_donors.to_csv(dir+f'/donors.csv')
#         cur_distance_mat.to_csv(dir+f'/distance_matrix.csv')
        
#     decisions = strategy(d2,agg_cur_donors,agg_cur_recipients,cur_distance_mat)
#     decisions['date'] = d2
#     decisions['distance'] = decisions.merge(cur_distance_mat)['distance']
    
#     # The dataframe of decisions contains the shipping decisions 
#     # example
#     #    don_id rec_id          ppe   qty                      date     distance
#     # 0   don0   rec0  faceShields  10.0 2020-04-09 16:26:00+00:00  2548.016134
#     # 1   don1   rec1  faceShields   1.0 2020-04-09 16:26:00+00:00  2527.163615
#     # 2   don3   rec2  faceShields   5.0 2020-04-09 16:26:00+00:00  2359.760082

#     # update cur_recipients by decreasing qty received, as follows:
#     # 1) for each recipient, sum all qty received 
#     # 2) iterate cur_recipients through the rows of that recipient, decreasing the qty column of all rows as long as there is more quantity received
#     # 3) remove the rows with zero qty
#     rec_requests_to_remove = [] # this list contains the index of the rows of cur_recipients to delete
#     for _,dec in decisions.iterrows():
#         rem_qty_to_ship = dec.qty
#         ppe = dec.ppe
#         rec = dec.rec_id
#         rec_df = cur_recipients[(cur_recipients.rec_id == rec)&(cur_recipients.ppe == ppe)]
#         for _,row in rec_df.iterrows():
#             request_idx = row.name
#             request_qty = row.qty
#             request_date = row.date
#             if rem_qty_to_ship < request_qty:
#                 #  modify the row, but keep it, then exit the loop
#                 cur_recipients.loc[request_idx,'qty'] -= rem_qty_to_ship
#                 rem_qty_to_ship = 0
#             else:
#                 if rem_qty_to_ship > request_qty:
#                     print(f'Error: shipping to a recipient more  {ppe} than requested')
#                 # remove the row and update remo_qty_to_ship
#                 rem_qty_to_ship -= request_qty
#                 rec_requests_to_remove.append(request_idx)
#     cur_recipients.drop(rec_requests_to_remove,inplace=True)

#     #  update donors table by removing all donors that shipped something 
#     for don_id,ppe in decisions.groupby(['don_id','ppe']).groups:
#         cur_donors = cur_donors[(cur_donors.don_id != don_id) | (cur_donors.ppe != ppe)]
    

#     alldecisions = pd.concat([alldecisions,decisions],ignore_index=True)
#     # update decisions and print current decisions
#     if writeFiles:
#         decisions.to_csv(dir+f'/decisions.csv')
#     d1 = d2
#     d2 = d1 + datetime.timedelta(days=interval)

# # print all decisions made
# alldecisions.to_csv('decisions.csv')


