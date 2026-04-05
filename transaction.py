
import numpy as np
import pandas as pd
import evaluation
from evaluation import metrics
import pricing
from utils import mimicGTBCPSPrice,mimicGTBCPSAmount



def InitialPlacement(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt):
    global total_value_issued
    value_ratio_gold_to_total,value_ratio_tb_to_total,value_ratio_reit_to_total,risk_ratio_tb_to_gold,risk_ratio_reit_to_gold,risk_ratio_gold_to_total,average_risk_gold,average_risk_reit,average_risk_tb,profit_loss_gold,profit_loss_reit,profit_loss_tb_optimised,profit_loss_gold_ratio,profit_loss_reit_ratio,profit_loss_tb_ratio,gold,collar_option_reit,tb_option_optimised,total_value,S_tb_t,S_reit_t = metrics(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt)

    S_gtbcps_0 = opt.pegged_price_in_usd
    total_value_issued = opt.total_issuance * S_gtbcps_0
    collateral_ratio_tranche_gold_preset = opt.collateral_ratio_gold
    print('--------------------------------------Initial Placement---------------------------------------')
    print('current price of gold is: {}, predicted price of gold is: {},profit is: {}'.format(spot_gold,gold,profit_loss_gold))
    print('current price of tb is: {}, current price of tb option is: {},predicted price of tb is: {},profit is: {}'.format(S_tb_0,tb_option_optimised,S_tb_t,profit_loss_tb_optimised))
    print('current price of reit is: {}, current price of reit option is: {},predicted price of reit is: {},profit is: {}'.format(S_reit_0,collar_option_reit,S_reit_t,profit_loss_reit))
    print('value_ratio_tb_to_total is: {}, risk_ratio_tb_to_gold is: {}'.format(value_ratio_tb_to_total,risk_ratio_tb_to_gold))
    print('value_ratio_gold_to_total is: {}, risk_ratio_gold_to_total is: {}'.format(value_ratio_gold_to_total,risk_ratio_gold_to_total))
    print('value_ratio_reit_to_total is: {}, risk_ratio_reit_to_gold is: {}'.format(value_ratio_reit_to_total,risk_ratio_reit_to_gold))
    print('average_risk_gold is: {}, average_risk_tb is: {}, average_risk_reit is: {}'.format(average_risk_gold,average_risk_tb,average_risk_reit))
    if value_ratio_reit_to_total>0 and value_ratio_tb_to_total>0 and value_ratio_gold_to_total>0:
        collateral_ratio_tranche_gold = collateral_ratio_tranche_gold_preset

        #print('collateral_ratio_tranche_gold_preset is: {},collateral_ratio_tranche_gold is: {}'.format(collateral_ratio_tranche_gold_preset,collateral_ratio_tranche_gold))
        collateral_ratio_tranche_reit = max(0.35,(value_ratio_reit_to_total/value_ratio_gold_to_total)*risk_ratio_reit_to_gold*collateral_ratio_tranche_gold)
        collateral_ratio_tranche_tb = max(0.35,(value_ratio_tb_to_total/value_ratio_gold_to_total)*risk_ratio_tb_to_gold*collateral_ratio_tranche_gold)
        plotValue_gold = total_value_issued  * collateral_ratio_tranche_gold
        plotValue_tb = total_value_issued  * collateral_ratio_tranche_tb
        plotValue_reit = total_value_issued  * collateral_ratio_tranche_reit

    else:
        collateral_ratio_tranche_gold = collateral_ratio_tranche_gold_preset
        collateral_ratio_tranche_tb = 0.4
        collateral_ratio_tranche_reit = 0.3
        
        plotValue_gold = total_value_issued  * collateral_ratio_tranche_gold_preset
        plotValue_tb = total_value_issued  * collateral_ratio_tranche_tb
        plotValue_reit = total_value_issued  * collateral_ratio_tranche_reit
        
        value_ratio_reit_to_gold = (collateral_ratio_tranche_reit/collateral_ratio_tranche_gold)*risk_ratio_reit_to_gold
        value_ratio_tb_to_gold = (collateral_ratio_tranche_tb/collateral_ratio_tranche_gold)*risk_ratio_tb_to_gold
    
    total_value = plotValue_gold+plotValue_tb+plotValue_reit
    collateral_ratio = total_value/total_value_issued


    print('value_ratio_tb_to_total is: {}, risk_ratio_tb_to_gold is: {}'.format(value_ratio_tb_to_total,risk_ratio_tb_to_gold))
    print('value_ratio_gold_to_total is: {}, risk_ratio_gold_to_total is: {}'.format(value_ratio_gold_to_total,risk_ratio_gold_to_total))
    print('value_ratio_reit_to_total is: {}, risk_ratio_reit_to_gold is: {}'.format(value_ratio_reit_to_total,risk_ratio_reit_to_gold))
    print('collateral_ratio_tranche_tb is: {}'.format(collateral_ratio_tranche_tb))

    print('collateral_ratio_tranche_gold is: {}'.format(collateral_ratio_tranche_gold))
    print('collateral_ratio_tranche_reit is: {}'.format(collateral_ratio_tranche_reit))
    print('Total plot size is: {}, plot size of gold is: {}, plot size of TB is: {}, plot size of REIT is: {}'.format(total_value,plotValue_gold,plotValue_tb,plotValue_reit))
    print('collateral ratio is: {}'.format(collateral_ratio))
    return plotValue_gold,plotValue_reit,plotValue_tb,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,collateral_ratio,total_value,risk_ratio_gold_to_total,risk_ratio_reit_to_gold,risk_ratio_tb_to_gold,average_risk_gold,average_risk_reit,average_risk_tb,S_tb_0,collar_option_reit,tb_option_optimised 
def updateCOLLARatio(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,plotValue_gold,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,plotValue_reit,S_tb_0,stdev_tb,plotValue_tb,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,risk_ratio_tb_to_gold_before,risk_ratio_reit_to_gold_before,risk_ratio_gold_to_total_before,spot_gold_before,S_tb_0_before,S_reit_0_before,collar_option_reit_before,tb_option_optimised_before,S_gtbcps,total_amount_gtbcps_new,i,opt):
    # baseline of price of gtbcps is decided by collaterals value in usd and collateral ratio 
    # if price of gtbcps is beyond the baseline, profit distribution; if price of gtbcps is less than baseline loss distribution
    # if collaterals value increase or keep stable, no handling; if decrease, check whether trgger liquidation.
    z_score=opt.confidence_score
    value_ratio_gold_to_total,value_ratio_tb_to_total,value_ratio_reit_to_total,risk_ratio_tb_to_gold,risk_ratio_reit_to_gold,risk_ratio_gold_to_total,average_risk_gold,average_risk_reit,average_risk_tb,profit_loss_gold,profit_loss_reit,profit_loss_tb_optimised,profit_loss_gold_ratio,profit_loss_reit_ratio,profit_loss_tb_ratio,gold,collar_option_reit,tb_option_optimised,total_value,S_tb_t,S_reit_t = metrics(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt)
    total_value_before = plotValue_reit+plotValue_gold+plotValue_tb
    total_profit_loss = profit_loss_gold*(plotValue_gold/total_value_before)+profit_loss_tb_optimised*(plotValue_tb/total_value_before)+profit_loss_reit*(plotValue_reit/total_value_before)
    #total_value_issued = opt.total_issuance
    #evaluate_benchmark = opt.collateral_evaluation_benchmark
    #if total_value_before<total_value_issued*evaluate_benchmark:
    print('--------------------------------------Daily Update Collateral Ratio- Day {}.-------------------------------------------'.format(i))
    print('current price of gold is: {}, predicted price of gold is: {}'.format(spot_gold,gold))
    print('current price of tb is: {}, current price of tb option is: {}, predicted price of tb is: {}'.format(S_tb_0,tb_option_optimised,S_tb_t))
    print('current price of reit is: {}, current price of reit option is: {}, predicted price of reit is: {}'.format(S_reit_0,collar_option_reit,S_reit_t))
    print('value_ratio_gold_to_total is: {}, risk_ratio_to_gold is: {}, risk_ratio_to_gold_before is: {}'.format(value_ratio_gold_to_total,risk_ratio_gold_to_total,risk_ratio_gold_to_total_before))
    print('value_ratio_tb_to_total is: {}, risk_ratio_tb_to_gold is: {}, risk_ratio_tb_to_gold_before is: {}'.format(value_ratio_tb_to_total,risk_ratio_tb_to_gold,risk_ratio_tb_to_gold_before))
    print('value_ratio_reit_to_total is: {}, risk_ratio_reit_to_gold is: {}, risk_ratio_reit_to_gold_before is: {}'.format(value_ratio_reit_to_total,risk_ratio_reit_to_gold,risk_ratio_reit_to_gold_before))

    delta_gold = spot_gold/spot_gold_before
    delta_reit = (S_reit_0+collar_option_reit)/(S_reit_0_before+collar_option_reit_before)
    delta_tb = (S_tb_0+tb_option_optimised)/(S_tb_0_before+tb_option_optimised_before)
    delta_gold_risk = (1+risk_ratio_gold_to_total)/(1+risk_ratio_gold_to_total_before)
    delta_reit_risk = (1+risk_ratio_reit_to_gold)/(1+risk_ratio_reit_to_gold_before)
    delta_tb_risk = (1+risk_ratio_tb_to_gold)/(1+risk_ratio_tb_to_gold_before)
    print('delta_gold is: {}, delta_tb is: {}, delta_reit is: {}'.format(delta_gold,delta_tb,delta_reit))
    print('delta_gold_risk is: {}, delta_tb_risk is: {}, delta_reit_risk is: {}'.format(delta_gold_risk,delta_tb_risk,delta_reit_risk))

    
    collateral_ratio_tranche_gold_new = collateral_ratio_tranche_gold* (delta_gold/delta_gold_risk)  
    collateral_ratio_tranche_reit_new = collateral_ratio_tranche_reit*((delta_reit/delta_gold)/delta_reit_risk)
    collateral_ratio_tranche_tb_new = collateral_ratio_tranche_tb*((delta_tb/delta_gold)/delta_tb_risk)


    #collateral_ratio_tranche_reit_new = collateral_ratio_tranche_gold_new*(delta_reit/delta_gold)/risk_ratio_reit_to_gold
    #collateral_ratio_tranche_tb_new = collateral_ratio_tranche_gold_new*(delta_tb/delta_gold)/risk_ratio_tb_to_gold  
    #collateral_ratio_tranche_reit_new = collateral_ratio_tranche_gold_new*((delta_reit/delta_gold)/delta_reit_risk)
    #collateral_ratio_tranche_tb_new = collateral_ratio_tranche_gold_new*((delta_tb/delta_gold)/delta_tb_risk)
    #plotValue_gold_new = plotValue_gold*(collateral_ratio_tranche_gold_new/collateral_ratio_tranche_gold)
    #plotValue_tb_new = plotValue_tb*(collateral_ratio_tranche_tb_new/collateral_ratio_tranche_tb)
    #plotValue_reit_new = plotValue_reit*(collateral_ratio_tranche_reit_new/collateral_ratio_tranche_reit)
    plotValue_gold_new = plotValue_gold*delta_gold
    plotValue_tb_new = plotValue_tb*delta_tb
    plotValue_reit_new = plotValue_reit*delta_reit
    gold = [spot_gold_before,spot_gold]
    tb = [S_tb_0_before+tb_option_optimised_before,S_tb_0+tb_option_optimised]
    reit = [S_reit_0_before+collar_option_reit_before,S_reit_0+collar_option_reit]
    plotValue_gold_net = plotValue_gold-z_score*np.std(gold)
    plotValue_tb_net = plotValue_tb-z_score*np.std(tb)
    plotValue_reit_net = plotValue_reit-z_score*np.std(reit)
    
    
    total_value_after = plotValue_reit_new+plotValue_gold_new+plotValue_tb_new



    pegged_price =  S_gtbcps
    total_value_gtbcps = total_amount_gtbcps_new*pegged_price
    collateral_ratio_new = total_value_after/total_value_gtbcps
    print('collateral_ratio_tranche_gold is: {}'.format(collateral_ratio_tranche_gold_new))
    print('collateral_ratio_tranche_tb is: {}'.format(collateral_ratio_tranche_tb_new))
    print('collateral_ratio_tranche_reit is: {}'.format(collateral_ratio_tranche_reit_new))
    print('Total plot size is: {}, plot size of gold is: {}, plot size of TB is: {}, plot size of REIT is: {}'.format(total_value_after,plotValue_gold_new,plotValue_tb_new,plotValue_reit_new))
    print('collateral ratio is: {}'.format(collateral_ratio_new))
    return  collateral_ratio_tranche_gold_new,collateral_ratio_tranche_tb_new,collateral_ratio_tranche_reit_new,plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,total_value_before,total_value_after,total_profit_loss, collateral_ratio_new,risk_ratio_gold_to_total,risk_ratio_reit_to_gold,risk_ratio_tb_to_gold,average_risk_gold,average_risk_tb,average_risk_reit,plotValue_gold_net,plotValue_reit_net,plotValue_tb_net,S_tb_0,collar_option_reit,tb_option_optimised


def Payout(S_gtbcps_0,total_amount_gtbcps_before,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,plotValue_gold,plotValue_tb,plotValue_reit,total_value_before,stdev_gold,stdev_tb ,stdev_reit,collateral_ratio,plotValue_gold_net,plotValue_reit_net,plotValue_tb_net,T,t,r,opt):
    preset_collateral_ratio = opt.collateral_ratio_gold
    #retained_rate = opt.premium_retained_rate/365
    total_value = plotValue_gold+plotValue_tb+plotValue_reit

    stdev_gtbcps = stdev_gold*(plotValue_gold/total_value)+stdev_tb*(plotValue_tb/total_value)+stdev_reit*(plotValue_reit/total_value)
    change_of_collaterals = total_value/total_value_before-1
    S_gtbcps_t = mimicGTBCPSPrice(S_gtbcps_0,1,0,change_of_collaterals,stdev_gtbcps)
    change_of_pegged_price = S_gtbcps_t/S_gtbcps_0-1
    total_amount_gtbcps = (total_value/min(collateral_ratio,1.5))/S_gtbcps_t
    print('--------------------------------------Regular payout---------------------------------------')
    print('predicted price of GTBCPS is: {}, actual price is: {}'.format(S_gtbcps_t,S_gtbcps_0))
    print('predicted amount of GTBCPS is: {}, actual amount is: {}'.format(total_amount_gtbcps,total_amount_gtbcps_before))
    print('plot sizes of gold is: {}, plot sizes of tb is: {} , plot sizes of reit is: {}, plot sizes of total is: {}.'.format(plotValue_gold,plotValue_tb,plotValue_reit,total_value))
    print('predicted stdevs of gold is: {}, predicted stdevs of tb is: {}, predicted stdevs of reit is: {}, predicted stdevs of GTBCPS is: {}.'.format(stdev_gold,stdev_tb,stdev_reit,stdev_gtbcps))
    '''
    if S_gtbcps_t-S_gtbcps_0>0:
        retained_premium = retained_rate*(S_gtbcps_t-S_gtbcps_0)
        S_gtbcps_t_net = S_gtbcps_t-retained_premium
    else:
        S_gtbcps_t_net = S_gtbcps_t
    '''
    premium = (S_gtbcps_t-S_gtbcps_0)*total_amount_gtbcps
    collaterals = ['gold','TB','REIT']
    collateral_ratios = [collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit]
    plot_values = [plotValue_gold,plotValue_tb,plotValue_reit]
    var_ratios = [plotValue_gold_net/plotValue_gold,plotValue_tb_net/plotValue_tb,plotValue_reit_net/plotValue_reit]
    df = pd.DataFrame()
    df['collateral_name']= collaterals
    df['plot_value'] = plot_values 
    df['var_ratio'] = var_ratios
    df['collateral_ratio']=collateral_ratios
    df['collateral_ratio_total']=collateral_ratio_tranche_gold+collateral_ratio_tranche_reit+collateral_ratio_tranche_tb
    df['plot_value_total']=plotValue_gold+plotValue_tb+plotValue_reit
    df['payout']=0.0000
    if premium>0:
        #df = df.sort_values(by='collateral_ratio',ascending=False).reset_index()
        
        if df['var_ratio'].any()==0:
            df = df.sort_values(by='collateral_ratio',ascending=False).reset_index()
        else:
            df = df.sort_values(by='var_ratio',ascending=False).reset_index()
        
        df = df.drop('index',axis=1)
        for i in range(len(df)):
            df.loc[i,'payout'] = premium*max(0,min(0.5,(df.loc[i,'collateral_ratio']/df.loc[i,'collateral_ratio_total'])))*(df.loc[i,'plot_value']/df.loc[i,'plot_value_total'])
            premium = max(0,premium-df.loc[i,'payout'])
    else:
        #df = df.sort_values(by='collateral_ratio',ascending=True).reset_index()
        df = df.sort_values(by='var_ratio',ascending=True).reset_index()
        df = df.drop('index',axis=1)
        for i in range(len(df)):
            df.loc[i,'payout']  = premium*min(0.5,abs(max(-0.5,df.loc[i,'collateral_ratio']/df.loc[i,'collateral_ratio_total'])))*(df.loc[i,'plot_value']/df.loc[i,'plot_value_total'])
            premium = min(0,premium-df.loc[i,'payout'])
    df['plot_value_new'] = df['plot_value']+df['payout']
    for i in range(len(df)):
        name = df.loc[i,'collateral_name']
        if 'gold' in name.lower():
            payout_gold = df.loc[i,'payout']
            plotValue_gold_new = df.loc[i,'plot_value_new']
        elif 'tb' in name.lower():
            payout_tb = df.loc[i,'payout']
            plotValue_tb_new = df.loc[i,'plot_value_new']
        elif 'reit' in name.lower():
            payout_reit = df.loc[i,'payout']
            plotValue_reit_new = df.loc[i,'plot_value_new']   

    collateral_ratio_tranche_gold_new = plotValue_gold_new/(S_gtbcps_t*total_amount_gtbcps)
    collateral_ratio_tranche_tb_new = plotValue_tb_new/(S_gtbcps_t*total_amount_gtbcps)
    collateral_ratio_tranche_reit_new = plotValue_reit_new/(S_gtbcps_t*total_amount_gtbcps)
    collateral_ratio_new = (plotValue_gold_new+plotValue_tb_new+plotValue_reit_new)/(S_gtbcps_t*total_amount_gtbcps)

    return payout_gold,payout_tb,payout_reit,plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,S_gtbcps_t,stdev_gtbcps,total_amount_gtbcps,collateral_ratio_new,collateral_ratio_tranche_gold_new,collateral_ratio_tranche_tb_new,collateral_ratio_tranche_reit_new
def Create(S_gtbcps_t,total_amount_gtbcps_before,total_amount_gtbcps,plotValue_gold,plotValue_tb,plotValue_reit,collateral_ratio):
    total_value = plotValue_gold+plotValue_tb+plotValue_reit
    created_amount = total_amount_gtbcps-total_amount_gtbcps_before
    created_value = created_amount*S_gtbcps_t
    createdValue_gold = (created_value*collateral_ratio)*(plotValue_gold/total_value )
    createdValue_tb = (created_value*collateral_ratio)*(plotValue_tb/total_value)
    createdValue_reit = (created_value*collateral_ratio)*(plotValue_reit/total_value)
    plotValue_gold_new = plotValue_gold-createdValue_gold
    plotValue_tb_new = plotValue_tb-createdValue_tb
    plotValue_reit_new = plotValue_reit-createdValue_reit
    total_value_new = plotValue_gold_new+plotValue_tb_new+plotValue_reit_new
    print('--------------------------------------Create GTBCPS---------------------------------------')
    print('total_value_of_collaterals is: {}, createdtionValue_gold is: {}, createdValue_tb is: {}, createdValue_reit is: {}'.format(total_value,createdValue_gold,createdValue_tb,createdValue_reit))
    print('plotValue_gold_after_creation is: {}, plotValue_tb_after_creation  is: {}, plotValue_reit_after_creation  is: {},total_value_after_creation is: {}'.format(plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,total_value_new))
    print('total_amount_gtncps_before_creation is: {},creation_amount_gtbcps is: {},total_amount_gtbcps_new is: {}'.format(total_amount_gtbcps_before,created_amount,total_amount_gtbcps))
    return plotValue_gold_new,plotValue_reit_new,plotValue_tb_new,total_value_new,created_value

def Redemption(S_gtbcps_0,total_amount_gtbcps_before,plotValue_gold,plotValue_tb,plotValue_reit,total_value_before,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,collateral_ratio,stdev_gold,stdev_tb ,stdev_reit,r,opt):
    total_value = plotValue_gold+plotValue_tb+plotValue_reit
    redemption_amount = opt.single_redemption_amount
    stdev_gtbcps = stdev_gold*(plotValue_gold/total_value)+stdev_tb*(plotValue_tb/total_value)+stdev_reit*(plotValue_reit/total_value)
    change_of_collaterals = total_value/total_value_before-1
    S_gtbcps_t = mimicGTBCPSPrice(S_gtbcps_0,1,0,r,change_of_collaterals,stdev_gtbcps)
    redemption_value = redemption_amount*S_gtbcps_t
    redemptionValue_gold = (redemption_value*collateral_ratio)*(plotValue_gold/total_value )
    redemptionValue_tb = (redemption_value*collateral_ratio)*(plotValue_tb/total_value)
    redemptionValue_reit = (redemption_value*collateral_ratio)*(plotValue_reit/total_value)
    plotValue_gold_new = plotValue_gold-redemptionValue_gold
    plotValue_tb_new = plotValue_tb-redemptionValue_tb
    plotValue_reit_new = plotValue_reit-redemptionValue_reit
    total_value_new = plotValue_gold_new+plotValue_tb_new+plotValue_reit_new
    total_amount_gtbcps = total_amount_gtbcps_before-redemption_amount
    print('--------------------------------------Redemption---------------------------------------')
    print('total_value_of_collaterals is: {}, redemptionValue_gold is: {}, redemptionValue_tb is: {}, redemptionValue_reit is: {}'.format(total_value,redemptionValue_gold,redemptionValue_tb,redemptionValue_reit))
    print(' plotValue_gold_after_redemption is: {}, plotValue_tb_after_redemption  is: {}, plotValue_reit_after_redemption  is: {},total_value_after_redemption is: {}'.format(plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,total_value_new))
    print('total_amount_gtncps_before_redemption is: {},redemption_amount_gtbcps is: {},total_amount_gtbcps_new is: {}').format(total_amount_gtbcps_before,redemption_amount,total_amount_gtbcps)

    return plotValue_gold_new,plotValue_reit_new,plotValue_tb_new,total_value_new,total_amount_gtbcps,redemption_value

def Liquidation(S_gtbcps_t,total_amount_gtbcps,plotValue_gold,plotValue_tb,plotValue_reit):
    total_value_gtbcps = total_amount_gtbcps*S_gtbcps_t


    liquidationValue_reit = min(total_value_gtbcps,plotValue_reit)
    liquidationValue_tb = min(total_value_gtbcps-liquidationValue_reit,plotValue_tb)
    liquidationValue_gold = min(total_value_gtbcps-liquidationValue_reit-liquidationValue_tb,plotValue_gold)
    print('--------------------------------------Liquidation---------------------------------------')
    print('total_value is: {}, liquidationSize_gold is: {}, liquidationSize_tb is: {}, liquidationSize_reit is: {}'.format(total_value_gtbcps,liquidationValue_gold,liquidationValue_tb,liquidationValue_reit))

    return liquidationValue_reit,liquidationValue_tb,liquidationValue_gold 
