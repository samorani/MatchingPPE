import pandas as pd
import numpy as np

# this code comes from Process results.ipynb
def compute_metrics(R,D,X):
    # fill rate
    recipients = R.copy()
    recipients = recipients[recipients['qty']>0]
    donors = D.copy()
    decisions = X.copy()


    all_ppes = set(donors.ppe.unique())
    all_ppes = all_ppes.union(set(recipients.ppe.unique()))

    # set up result DataFrame
    result = pd.DataFrame(columns=['metric_name','description','value'])

    ############### FILL RATE for rec_id, ppe ##################
    total_request = recipients.groupby(['rec_id','ppe'])['qty'].agg(['sum'])
    total_request =total_request.reset_index()
    total_request.columns=['rec_id','ppe','qty']
    fr = total_request.merge(decisions,how='left',on=['rec_id','ppe'],suffixes=['_rec','_dec']).groupby(['rec_id','ppe']).agg({'qty_rec':['mean'],'qty_dec':['sum','size']})
    fr = fr.reset_index()
    fr.columns = ['rec_id','ppe','requested','received','fill_rate']
    fr['fill_rate'] = fr['received'] / fr['requested']
    fr.loc[fr['fill_rate'] > 1,'fill_rate'] = 1
    fr['fill_rate'] = fr['fill_rate'].fillna(0)

    result['metric_name'] = "fill rate (" + fr['rec_id'] + "," + fr['ppe'] + ")"
    result['description'] = "fill rate of recipient " + fr['rec_id'] + " limited to " + fr['ppe']
    result['value'] = fr['fill_rate']

    ############ FILL RATE FOR EACH PPE ##########
    fr_p = fr.groupby('ppe')['fill_rate'].mean()

    for ppe,val in fr_p.items():
        result.loc[len(result)] = [f'fill rate ({ppe})', f'average fill rate among recipients who requested {ppe}',val]

    fr_p_zero = fr[fr.fill_rate > 0].groupby('ppe')['fill_rate'].mean()
    fr_p_zero

    for ppe,val in fr_p_zero.items():
        result.loc[len(result)] = [f'fill rate exc zeros ({ppe})', f'average fill rate among recipients who requested {ppe} and received at least one unit',val]

    ########## OVERALL FILL RATE ##############
    result.loc[len(result)] = [f'fill rate', f'overall fill rate, i.e., the average of the fill rates (ppe)',fr_p.mean()]
    result.loc[len(result)] = [f'fill rate exc zeros', f'overall fill rate among recipients who received something, i.e., the average of the fill rates (ppe) among recipients who received at least one unit',fr_p_zero.mean()]

    ############# UNIT_MILES ####################
    decisions['unit_miles'] = decisions['distance'] * decisions['qty']

    gb = decisions.groupby('ppe')
    rr = (gb['unit_miles'].sum() / gb['qty'].sum()).to_frame().reset_index()
    rr.columns=['ppe','avg_unit_miles']

    for _,row in rr.iterrows():
        ppe = row['ppe']
        result.loc[len(result)] = [f'avg unit-miles ({ppe})', f'average miles travelled by each unit of {ppe}',row['avg_unit_miles']]

    overall_unit_miles = decisions.unit_miles.sum() / decisions.qty.sum()
    result.loc[len(result)] = [f'avg unit-miles', f'average miles travelled by each unit of ppe',overall_unit_miles]

    ######### HOLDING TIME ######################
    dd = decisions.merge(donors,on=['don_id','ppe'],suffixes=['_dec','_don'])
    dd['holding_time'] = (dd['date_dec'] - dd['date_don']).dt.days
    dd['unit_holding_time'] = dd['holding_time'] * dd['qty_dec']

    gb = dd.groupby('ppe')
    rr = (gb['unit_holding_time'].sum() / gb['qty_dec'].sum()).to_frame().reset_index()
    rr.columns=['ppe','avg_unit_days']

    for _,row in rr.iterrows():
        ppe = row['ppe']
        result.loc[len(result)] = [f'avg unit-days ({ppe})', f'average days that each unit of {ppe} stayed idle',row['avg_unit_days']]

    overall_holding_time = dd.unit_holding_time.sum() / dd.qty_dec.sum()
    result.loc[len(result)] = [f'avg holding time', f'average days that each unit of ppe stayed idle',overall_holding_time]

    ########## NUMBER OF SHIPMENTS ############
    total_shipments = len(decisions.groupby(['don_id','rec_id']).size())
    donors = decisions['don_id'].nunique()
    result.loc[len(result)] = [f'avg number of shipments', f'average number of shipments among donors',total_shipments/donors]

    return result
