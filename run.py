import os
import argparse
import datetime
import pandas as pd
import data
from data import dataLoad,preprocess,split,imputation
from transaction import InitialPlacement,updateCOLLARatio,Payout,Create,Redemption,Liquidation
import evaluation
from evaluation import metrics
import gc
from Config import config

def get_parser():
    gc.collect()
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir',type=str,default='/data', help = 'directory of the original data.' )
    parser.add_argument('--output_dir',type=str,default='./output/', help = 'directory of the original data.' )
    parser.add_argument('--graph_dir',type=str,default='./graph/', help = 'directory of graphs' )
    parser.add_argument('--log_dir',type=str,default='./log/', help = 'directory of the transaction logs.' )
    parser.add_argument('--confidence_score', type=float,default=1.96,help='confidence score of predicted price.')
    parser.add_argument('--total_issuance', type=float,default=100000000,help='Total issued value of the stablecoin.')   
    parser.add_argument('--pegged_price_in_usd', type=float,default=1.00,help='Initially pegged price of GTBCPS to USD')   
    parser.add_argument('--collateral_ratio_gold', type=float,default=0.8,help='collateral value of gold to value of GTBCPS.')
    parser.add_argument('--display_payout_of_tranches',type=str,default='all',help='display pricing of specific tranches, can be 1, 2, 3, all or an array.')
    parser.add_argument('--fraction_of_hedged',type=float,default=0.80,help='set the fraction percentage of the interest risk to be hedged.Default to "100%".')
    parser.add_argument('--single_redemption_amount',type=float,default=0.00,help='amount of GTBCPS to be reddemed once.')
    #parser.add_argument('--premium_retained_rate',type=float,default=0.95,help='rate of premium to be retained with GTBCPS')
    parser.add_argument('--with_learnings',type=bool,default=False, help='Bool type. True for auto-imputating and predicting missing data in original datasets')
    parser.add_argument('--liquidation_benchmark',type=float,default=0.8, help='Bottom line of total value of collaterals to trigger liquidation.')
    parser.add_argument('--liquidation_flag',type=str,default='No', help='Indicator to trigger liquidation')

    opt = parser.parse_args()
    return opt



if __name__=='__main__':
    GTBCPS_config = config()
    project_dir=os.getcwd()
    os.chdir(project_dir)
    opt = get_parser()
    data_dir = project_dir+opt.data_dir
    output_dir = opt.output_dir
    total_issuance_amount = opt.total_issuance
    initial_pegged_price = opt.pegged_price_in_usd 
    redemption_amount = opt.single_redemption_amount
    days_range=GTBCPS_config.days_range
    computation_days=GTBCPS_config.computation_days
    

    if os.path.exists(output_dir)==False:
        os.makedirs(output_dir)
    timeSequence = str(datetime.datetime.now())[20:26]
    df_orig,df_ref = dataLoad(data_dir)
    df = preprocess(df_orig)

    if opt.with_learnings==True:
        df = imputation(df,timeSequence,opt)



    for i in range(days_range):
        spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,maturity_date,current_date,r,mrf,dividend_rate_reit,stdev_reit,S_tb_0,stdev_tb = split(df,i,computation_days,days_range)
        
        if i ==0:
            plotValue_gold,plotValue_reit,plotValue_tb,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,collateral_ratio,total_value,risk_ratio_gold_to_total,risk_ratio_reit_to_gold,risk_ratio_tb_to_gold,average_risk_gold,average_risk_reit,average_risk_tb,S_tb_0,collar_option_reit,tb_option_optimised  = InitialPlacement(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt)
            plotValue_gold_init = plotValue_gold
            plotValue_reit_init = plotValue_reit
            plotValue_tb_init = plotValue_tb
            total_value_init = plotValue_gold_init+plotValue_reit_init+plotValue_tb_init
            payout_gold,payout_tb,payout_reit,plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,S_gtbcps_t_after,stdev_gtbcps,total_amount_gtbcps,collateral_ratio_new,collateral_ratio_tranche_gold_new,collateral_ratio_tranche_tb_new,collateral_ratio_tranche_reit_new=Payout(initial_pegged_price,total_issuance_amount,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,plotValue_gold_init,plotValue_tb_init,plotValue_reit_init,total_value_init ,stdev_gold,stdev_tb ,stdev_reit,collateral_ratio,0,0,0,T,t,r,opt)
            total_amount_gtbcps_new = total_amount_gtbcps
            S_gtbcps_new = S_gtbcps_t_after
            stdev_gtbcps_new = stdev_gtbcps
            risk_ratio_tb_to_gold_before = risk_ratio_tb_to_gold
            risk_ratio_reit_to_gold_before = risk_ratio_reit_to_gold
            risk_ratio_gold_to_total_before = risk_ratio_gold_to_total
            spot_gold_before = spot_gold
            S_tb_0_before = S_tb_0
            S_reit_0_before = S_reit_0
            collar_option_reit_before = collar_option_reit
            tb_option_optimised_before = tb_option_optimised

            collateral_ratio = collateral_ratio_new
            collateral_ratio_tranche_gold = collateral_ratio_tranche_gold_new
            collateral_ratio_tranche_tb = collateral_ratio_tranche_tb_new
            collateral_ratio_tranche_reit = collateral_ratio_tranche_reit_new
            
        else: 
            collateral_ratio_tranche_gold_new,collateral_ratio_tranche_tb_new,collateral_ratio_tranche_reit_new,plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,total_value_before,total_value_after,total_profit_loss, collateral_ratio_new,risk_ratio_gold_to_total,risk_ratio_reit_to_gold,risk_ratio_tb_to_gold,average_risk_gold,average_risk_tb,average_risk_reit,plotValue_gold_net,plotValue_reit_net,plotValue_tb_net,S_tb_0,collar_option_reit,tb_option_optimised =  updateCOLLARatio(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,plotValue_gold,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,plotValue_reit,S_tb_0,stdev_tb,plotValue_tb,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,risk_ratio_tb_to_gold_before,risk_ratio_reit_to_gold_before,risk_ratio_gold_to_total_before,spot_gold_before,S_tb_0_before,S_reit_0_before,collar_option_reit_before,tb_option_optimised_before,S_gtbcps_new,total_amount_gtbcps_new,i,opt)
            collateral_ratio_tranche_gold = collateral_ratio_tranche_gold_new
            collateral_ratio_tranche_tb = collateral_ratio_tranche_tb_new
            collateral_ratio_tranche_reit = collateral_ratio_tranche_reit_new
            collateral_ratio = collateral_ratio_new
            #total_value_before = plotValue_gold_new+plotValue_tb_new+plotValue_reit_new
            plotValue_gold = plotValue_gold_new
            plotValue_reit = plotValue_reit_new
            plotValue_tb = plotValue_tb_new
            total_value = total_value_after
            risk_ratio_tb_to_gold_before = risk_ratio_tb_to_gold
            risk_ratio_reit_to_gold_before = risk_ratio_reit_to_gold
            risk_ratio_gold_to_total_before = risk_ratio_gold_to_total
            spot_gold_before = spot_gold
            S_tb_0_before = S_tb_0
            S_reit_0_before = S_reit_0
            collar_option_reit_before = collar_option_reit
            tb_option_optimised_before = tb_option_optimised
            total_amount_gtbcps_before = total_amount_gtbcps_new
            payout_gold,payout_tb,payout_reit,plotValue_gold_new,plotValue_tb_new,plotValue_reit_new,S_gtbcps_t,stdev_gtbcps,total_amount_gtbcps,collateral_ratio_new,collateral_ratio_tranche_gold_new,collateral_ratio_tranche_tb_new,collateral_ratio_tranche_reit_new=Payout(S_gtbcps_new ,total_amount_gtbcps_before,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,plotValue_gold,plotValue_tb,plotValue_reit,total_value,stdev_gold,stdev_tb ,stdev_reit,collateral_ratio,plotValue_gold_net,plotValue_reit_net,plotValue_tb_net,T,t,r,opt)
            S_gtbcps_new = S_gtbcps_t
            total_amount_gtbcps_new = total_amount_gtbcps
            stdev_gtbcps_new = stdev_gtbcps
            total_value_before = plotValue_gold_new+plotValue_tb_new+plotValue_reit_new
            plotValue_gold = plotValue_gold_new
            plotValue_reit = plotValue_reit_new
            plotValue_tb = plotValue_tb_new       
            collateral_ratio = collateral_ratio_new
            collateral_ratio_tranche_gold = collateral_ratio_tranche_gold_new
            collateral_ratio_tranche_tb = collateral_ratio_tranche_tb_new
            collateral_ratio_tranche_reit = collateral_ratio_tranche_reit_new
            plotValue_gold_new,plotValue_reit_new,plotValue_tb_new,total_value_new,created_value = Create(S_gtbcps_new,total_amount_gtbcps_before,total_amount_gtbcps,plotValue_gold,plotValue_tb,plotValue_reit,collateral_ratio)
            plotValue_gold = plotValue_gold_new
            plotValue_reit = plotValue_reit_new
            plotValue_tb = plotValue_tb_new  
            total_amount_gtbcps_new = total_amount_gtbcps
            if redemption_amount>0:     
                plotValue_gold_new,plotValue_reit_new,plotValue_tb_new,total_value_new,total_amount_gtbcps,redemption_value=Redemption(S_gtbcps_new,total_amount_gtbcps_new,plotValue_gold,plotValue_tb,plotValue_reit,total_value_before,collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit,collateral_ratio,stdev_gold,stdev_tb ,stdev_reit,r,opt)
                plotValue_gold = plotValue_gold_new
                plotValue_reit = plotValue_reit_new
                plotValue_tb = plotValue_tb_new  
                total_amount_gtbcps_new = total_amount_gtbcps
        #value_ratio_reit_to_total,value_ratio_tb_to_total,value_ratio_gold_to_total,risk_ratio_reit_to_gold,risk_ratio_tb_to_gold,risk_ratio_total_to_gold,profit_loss_gold,average_risk_gold,profit_loss_reit,profit_loss_tb_optimised,gold,collar_option_reit,tb_option_optimised,total_value = metrics(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,face_value_tb,yield_rate_tb,stdev_tb,opt)
            
        if opt.display_payout_of_tranches.lower() == 'all':
            print('payout of tranche of gold is: {}, payout of tranche of Treausry Bill Option is: {}, payout of tranche of Collar of REIT is: {}'.format(payout_gold,payout_tb,payout_reit))
            print('Collateral size of tranche of gold is: {}, collateral size of tranche of Treausry Bill Option is: {}, collateral size of tranche of Collar of REIT is: {}'.format(plotValue_gold_new,plotValue_tb_new,plotValue_reit_new))
            print('Collateral ratio of tranche of gold is: {}, collateral ratio of tranche of Treausry Bill Option is: {}, collateral ratio of tranche of Collar of REIT is: {}'.format(collateral_ratio_tranche_gold,collateral_ratio_tranche_tb,collateral_ratio_tranche_reit))
        elif '1' in opt.pricing_of_tranches:
            print('payout of tranche of gold is: {}'.format(payout_gold))
            print('Collateral size of tranche of gold is: {}'.format(plotValue_gold_new))
            print('Collateral ratio of tranche of gold is: {}'.format(collateral_ratio_tranche_gold))    
        elif '2' in opt.pricing_of_tranches:
            print('payout of tranche of Treausry Bill Option is: {}'.format(payout_tb))
            print('Collateral size of tranche of Treausry Bill Option is: {}'.format(plotValue_tb_new))
            print('Collateral ratio of tranche of Treausry Bill Option is: {}'.format(collateral_ratio_tranche_tb))
        elif '3' in opt.pricing_of_tranches:
            print('payout of tranche of Collar of REIT is: {}'.format(payout_reit))
            print('Collateral size of tranche of Collar of REIT is: {}'.format(plotValue_reit_new))
            print('Collateral ratio of tranche of Collar of REIT is: {}'.format(collateral_ratio_tranche_reit))
        #total_value_liquidation = plotValue_gold_new+plotValue_tb_new+plotValue_reit_new
        plotValue_hl = plotValue_gold+plotValue_tb
        if redemption_amount>0:
            if collateral_ratio  <= opt.liquidation_benchmark or plotValue_hl<=redemption_value or opt.liquidation_flag.lower() == 'yes':
                liquidationValue_reit,liquidationValue_tb,liquidationValue_gold  = Liquidation(S_gtbcps_new,total_amount_gtbcps_new,plotValue_gold,plotValue_tb,plotValue_reit)
                with open ('liquidation.txt','a') as f:
                    f.write('---------------------liquidation value of gold------------------\n')
                    f.write(str(liquidationValue_gold)+'\n')
                    f.write('---------------------liquidation value of Treasury Bill option------------------\n')
                    f.write(str(liquidationValue_tb)+'\n')
                    f.write('---------------------liquidation value of Collar Option of REIT------------------\n')
                    f.write(str(liquidationValue_reit)+'\n')       
                    f.close()
                exit()
        else:
            if collateral_ratio  <= opt.liquidation_benchmark or opt.liquidation_flag.lower() == 'yes':
                liquidationValue_reit,liquidationValue_tb,liquidationValue_gold  = Liquidation(S_gtbcps_new,total_amount_gtbcps_new,plotValue_gold,plotValue_tb,plotValue_reit)
                with open ('liquidation.txt','a') as f:
                    f.write('---------------------liquidation value of gold------------------\n')
                    f.write(str(liquidationValue_gold)+'\n')
                    f.write('---------------------liquidation value of Treasury Bill option------------------\n')
                    f.write(str(liquidationValue_tb)+'\n')
                    f.write('---------------------liquidation value of Collar Option of REIT------------------\n')
                    f.write(str(liquidationValue_reit)+'\n')       
                    f.close()
                exit()