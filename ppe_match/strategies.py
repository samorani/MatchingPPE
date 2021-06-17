import pandas as pd

import logging
logger = logging.getLogger(__name__)
stream_hdlr = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
stream_hdlr.setFormatter(formatter)
logger.addHandler(stream_hdlr)
logger.setLevel(logging.WARN)


#################### DEFAULT STRATEGIES ################
#### dummy strategy: first come-first-matched
# date is the current date
# curdon is the dataframe of current donors with the given ppe (don_req_id,don_id,date,ppe,qty)
# currec is the dataframe of current recipients with the given ppe (rec_req_id,rec_id,date,ppe,qty)
# ppe is the current ppe

# assumptions: curdon currec must have one row per (don_id/rec_id,ppe)
# return dataframe of decisions (don_id,rec_id,ppe,qty)
def dummy_strategy(date,curdon,currec,curdistance_mat):
    result = pd.DataFrame(columns=['don_id','rec_id','ppe','qty'])
    ppes_to_consider = set(curdon.ppe.unique())
    ppes_to_consider = ppes_to_consider.intersection(set(currec.ppe.unique()))

    for ppe in ppes_to_consider:
        donors_ppe = curdon[curdon.ppe == ppe]
        recipients_ppe = currec[currec.ppe == ppe]

        n = min(len(donors_ppe),len(recipients_ppe))
        for i in range(n):
            don = donors_ppe.iloc[i] # (don_req_id,don_id,date,ppe,qty)
            rec = recipients_ppe.iloc[i]
            qty = min(don.qty,rec.qty)
            result.loc[len(result)] = [don.don_id,rec.rec_id,ppe,qty]
    return result

# proximity match strategy
def proximity_match_strategy(date,curdon,currec,curdistance_mat):
    result = pd.DataFrame(columns=['don_id','rec_id','ppe','qty'])
    ppes_to_consider = set(curdon.ppe.unique())
    ppes_to_consider = ppes_to_consider.intersection(set(currec.ppe.unique()))

    for ppe in ppes_to_consider:
        donors_ppe = curdon[curdon.ppe == ppe].copy()
        recipients_ppe = currec[currec.ppe == ppe].copy()

        for _, drow in donors_ppe.iterrows():
            if len(recipients_ppe) == 0:
                break # if we don't have any more recipient with this ppe, consider the next ppe

            # find the closest recipient to drow.don_id
            dr = curdistance_mat[(curdistance_mat.don_id == drow.don_id)].merge(recipients_ppe,on='rec_id').sort_values('distance').iloc[0]
            dqty = drow.qty # donor's qty
            rqty = recipients_ppe.loc[recipients_ppe.rec_id == dr.rec_id,'qty'].values[0] #recipient's qty
            qty = min(dqty,rqty) #qty to ship
            if qty == 0:
                logger.info('qty is zero')
            if qty == rqty:
                recipients_ppe = recipients_ppe[recipients_ppe.rec_id !=  dr.rec_id] # remove recipient
            else:
                recipients_ppe.loc[recipients_ppe.rec_id == dr.rec_id,'qty'] -= qty #update recipient's qty
            result.loc[len(result),:] = [dr.don_id, dr.rec_id,ppe,qty]

    return result
