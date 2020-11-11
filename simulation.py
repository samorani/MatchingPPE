# import pandas as pd
# import numpy as np
# import datetime
# import os
# import shutil

# # Global variables
# debug = True
# writeFiles = True

# # these variables contain the current set of donors and recipients
# cur_recipients = pd.DataFrame()
# cur_donors = pd.DataFrame()


# # load files
# all_donors = pd.read_csv('data/anon_donors.csv',parse_dates=['date'],index_col=0)
# all_recipients = pd.read_csv('data/anon_recipients.csv',parse_dates=['date'],index_col=0)
# distance_mat = pd.read_csv('data/anon_distance_matrix.csv',index_col=0)

# # reshape recipients
# all_recipients = all_recipients.set_index(['rec_id','date']).stack().to_frame().reset_index()
# all_recipients.columns=['rec_id','date','ppe','qty']
# all_recipients = all_recipients[all_recipients['qty']>0]
# ppes = all_recipients['ppe'].unique()

# # returns the distance between a donor and a recipient 
# def get_distance(don_id,rec_id):
#     return distance_mat.loc[(distance_mat.don_id == don_id)&(distance_mat.rec_id == rec_id),'distance'].values[0]

# # match a donor with a recipient on a given date for a given qty of ppe.
# # This method does NOT update the current dataframe. It updates the results
# # date is the current date
# # donor is the index in teh donor table of the donation to match
# # recipient is the index of the recipient table of the request to match
# # donors and recipients are the data frames of current recipients/donors with the given ppe (rec_id/don_id,date,ppe,qty)
# # curdecisions are the data frame of curdecisions (date,don_id,rec_id,distance,qty)
# def match(date,donor,recipient,ppe,qty,donors,recipients,curdecisions,remove_donor_regardless=True):
#     # row of donor and recipient
#     # row_donor = donors.loc[(donors.don_id == donor) & ((donors.ppe == ppe) )].copy()
#     row_donor = donors.loc[donor,:].copy()
#     donor_id = row_donor.don_id
#     # row_recipient = recipients.loc[(recipients.rec_id == recipient) & ((recipients.ppe == ppe) )].copy()
#     row_recipient = recipients.loc[recipient,:].copy()
#     recipient_id = row_recipient.rec_id
#     donor_qty = row_donor.qty
#     recipient_qty = row_recipient.qty
#     if qty > donor_qty or qty > recipient_qty:
#         raise('Error in qty!')
#     # update curdecisions
#     curdecisions.loc[len(curdecisions)] = [date,donor_id,recipient_id,get_distance(donor_id,recipient_id),ppe,qty]
#     # exhausted donor? Yes => remove it from the shared global variable cur_donors
#     if qty == donor_qty or remove_donor_regardless:
#         cur_donors.drop(donor,inplace=True)
#     # update recipient quantity in the shared global variable
#     cur_recipients.loc[recipient,'qty'] = recipient_qty - qty
#     if qty == recipient_qty:
#         cur_recipients.drop(recipient,inplace=True)
    
# #### dummy strategy: first come-first-matched
# # date is the current date
# # curdon is the dataframe of current donors with the given ppe (don_id,date,ppe,qty)
# # currec is the dataframe of current recipients with the given ppe (rec_id,date,ppe,qty)
# # ppe is the current ppe
# # curdecisions is the current data frame of curdecisions (date,don_id,rec_id,distance,qty)
# def dummy_strategy(date,curdon,currec,curdistance_mat,ppe,curdecisions):
#     # match donor 0 with recipient 0
#     # throw away the other donors
#     n = min(len(curdon),len(currec))
#     for i in range(n):
#         don = curdon.iloc[i]
#         rec = currec.iloc[i]
#         qty = min(don.qty,rec.qty)
#         # ship qty units of ppe on date from don.name (the index, as the same donor could have multiple entries) to rec.name
#         match(date,don.name,rec.name,ppe,qty,curdon,currec,curdecisions,True)

# # run analysis 
# # # set parameters here
# interval = 7
# strategy = dummy_strategy
# max_donation_qty = 1000
# # end set parameters

# all_donors = all_donors[all_donors.qty <= max_donation_qty]
# cur_donors = all_donors.drop(index=all_donors.index)
# cur_recipients = all_recipients.drop(index=all_recipients.index)

# cur_date = min(all_recipients.date.min(),all_donors.date.min())- datetime.timedelta(minutes=1)
# max_date = max(all_recipients.date.max(),all_donors.date.max())+ datetime.timedelta(minutes=1)

# d1 = cur_date
# d2 = cur_date + datetime.timedelta(days=interval)

# alldecisions = pd.DataFrame(columns=['date','don_id','rec_id','distance','ppe','qty'])
# while d2 < max_date:
#     if debug:
#         print(f'===== From {d1} to {d2} ======')
#     cur_recipients = pd.concat([cur_recipients, all_recipients.loc[(all_recipients.date > d1)&(all_recipients.date < d2)].copy()])
#     cur_donors = pd.concat([cur_donors, all_donors.loc[(all_donors.date > d1)&(all_donors.date < d2)].copy()])

#     # for each date, write the current pending requests
#     dir = f'output/{d2.date()}' 
    
#     if writeFiles and not os.path.exists(dir):
#         os.mkdir(dir)
#         cur_recipients.to_csv(dir+'/recipients.csv')
#         cur_donors.to_csv(dir+'/donors.csv')


#     ppes_to_consider = set(cur_donors.ppe.unique())
#     ppes_to_consider = ppes_to_consider.intersection(set(cur_recipients.ppe.unique()))
#     for ppe in ppes_to_consider:
#     # for ppe in ['faceShields']:
#         if debug:
#             print(f'Ppe {ppe}')
#         cur_rec_ppe = cur_recipients[cur_recipients.ppe == ppe] # ['rec_id', 'date', 'ppe', 'qty']
#         cur_don_ppe = cur_donors[cur_donors.ppe == ppe] # ['don_id', 'date', 'ppe', 'qty']
#         if len(cur_rec_ppe) == 0 or len(cur_don_ppe) == 0:
#             continue 

#         curdecisions = pd.DataFrame(columns=['date','don_id','rec_id','distance','ppe','qty'])
#         cur_distance_mat = cur_don_ppe.merge(distance_mat).merge(cur_rec_ppe,on='rec_id')[['don_id','rec_id','distance']]

#         if writeFiles:
#             dir2 = dir + f'/{ppe}'
#             if not os.path.exists(dir2):
#                 os.mkdir(dir2)
#             cur_rec_ppe.to_csv(dir2+f'/recipients_{ppe}.csv')
#             cur_don_ppe.to_csv(dir2+f'/donors_{ppe}.csv')
#             cur_distance_mat.to_csv(dir2+f'/distance_matrix_{ppe}.csv')
            
#         strategy(d2,cur_don_ppe,cur_rec_ppe,cur_distance_mat,ppe,curdecisions)
#         alldecisions = pd.concat([alldecisions,curdecisions],ignore_index=True)
#         # update decisions and print current decisions
#         if writeFiles:
#             #cur_distance_mat.to_csv(dir2+f'/distance_matrix_{ppe}.csv')
#             curdecisions.to_csv(dir2+f'/decisions_{ppe}.csv')
#     d1 = d2
#     d2 = d1 + datetime.timedelta(days=interval)

# # print all decisions made
# alldecisions.to_csv('decisions.csv')


