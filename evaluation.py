import numpy as np
import pricing
from pricing import Gold,TBCoveredCallOption,TBCoveredCallOption_hedge,REITCollarOption,REIT, BSMGreeks,TBCoveredCallOption_Binomial,TBCoveredCallOption_hedge_Binomial,REITCollarOption_Binomial

def TotalProfitLoss(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt):
    global z_score
    z_score = opt.confidence_score
    gold,profit_loss_gold,profit_loss_gold_ratio,sharpe_ratio,sortino_ratio,stdev_gold,stdev_gold_down = Gold(spot_gold,gofo,sofr,t,stdev_gold,stdev_gold_down,r)
    collar_option_reit,profit_loss_reit,profit_loss_reit_ratio,d1_reit,d2_reit,K_reit,S_reit_t,K_reit_optimised,S_reit_t_optimised = REITCollarOption_Binomial(S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,opt)
    K_tb_optimised,tb_option_optimised,profit_loss_tb_optimised,profit_loss_tb_ratio,d1_tb,d2_tb,S_tb_t = TBCoveredCallOption_hedge_Binomial(S_tb_0,T,t,current_date,maturity_date,r,stdev_tb,S_reit_t,S_reit_0,stdev_reit,collar_option_reit,opt)
    #collar_option_reit,profit_loss_reit,profit_loss_reit_ratio,d1_reit,d2_reit,K_reit,S_reit_t,K_reit_optimised,S_reit_t_optimised = REITCollarOption(S_reit_0,t,T,r,dividend_rate_reit,mrf,stdev_reit,opt)
    #K_tb_optimised,tb_option_optimised,profit_loss_tb_optimised,profit_loss_tb_ratio,d1_tb,d2_tb,S_tb_t = TBCoveredCallOption_hedge(S_tb_0,T,t,r,stdev_tb,S_reit_t,S_reit_0,stdev_reit,collar_option_reit,opt)
    
    total_profit = profit_loss_gold+profit_loss_tb_optimised+profit_loss_reit
    total_value = gold+collar_option_reit+tb_option_optimised
    #print(profit_loss_gold,profit_loss_tb_optimised,profit_loss_reit,total_profit)
    return total_profit,d1_tb,d2_tb,d1_reit,d2_reit,S_tb_t,S_reit_t,K_tb_optimised,K_reit_optimised,gold,tb_option_optimised,collar_option_reit,profit_loss_reit,profit_loss_gold,profit_loss_tb_optimised,profit_loss_gold_ratio,profit_loss_reit_ratio,profit_loss_tb_ratio,total_value

def TotalRisk(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,d1_tb,d2_tb,d1_reit,d2_reit,S_tb_t,S_reit_t,K_tb_optimised,K_reit_optimised,stdev_tb,stdev_reit,t,T,r,dividend_rate_reit):
    gold,profit_loss_gold,profit_loss_gold_ratio,sharpe_ratio,sortino_ratio,stdev_gold,stdev_gold_down = Gold(spot_gold,gofo,sofr,t,stdev_gold,stdev_gold_down,r)
    
    delta_call_reit,delta_put_reit,gamma_reit,theta_call_reit,theta_put_reit,vega_reit,rho_call_reit,rho_put_reit = BSMGreeks(d1_reit,d2_reit,T/261,t/261,dividend_rate_reit,r,stdev_reit,S_reit_t,K_reit_optimised)

    delta_call_tb,delta_put,gamma_tb,theta_call_tb,theta_put,vega_tb,rho_call_tb,rho_put_tb = BSMGreeks(d1_tb,d2_tb,T/360,t/360,0,r,stdev_tb,S_tb_t,K_tb_optimised)
    average_risk_reit = np.mean([delta_call_reit,delta_put_reit,gamma_reit,theta_call_reit,theta_put_reit,vega_reit,rho_call_reit,rho_put_reit])
    average_risk_tb = np.mean([delta_call_tb,gamma_tb,theta_call_tb,vega_tb,rho_call_tb])
    #average_risk_gold = np.mean([sharpe_ratio,sortino_ratio])
    average_risk_gold = np.mean([stdev_gold,stdev_gold_down])
    risk_stdev_gold = 0.2*stdev_gold+0.8*stdev_gold_down
    risk_stdev_tb = stdev_tb
    #total_risk = average_risk_reit+average_risk_tb+average_risk_gold
    #print(average_risk_reit,average_risk_tb,average_risk_gold,risk_stdev_gold,risk_stdev_tb)
    return risk_stdev_gold,risk_stdev_tb,average_risk_reit,average_risk_tb,average_risk_gold

def metrics(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt):
    total_profit,d1_tb,d2_tb,d1_reit,d2_reit,S_tb_t,S_reit_t,K_tb_optimised,K_reit_optimised,gold,tb_option_optimised,collar_option_reit,profit_loss_reit,profit_loss_gold,profit_loss_tb_optimised,profit_loss_gold_ratio,profit_loss_reit_ratio,profit_loss_tb_ratio,total_value = TotalProfitLoss(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,S_tb_0,stdev_tb,opt)
    risk_stdev_gold,risk_stdev_tb,average_risk_reit,average_risk_tb,average_risk_gold=TotalRisk(spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,d1_tb,d2_tb,d1_reit,d2_reit,S_tb_t,S_reit_t,K_tb_optimised,K_reit_optimised,stdev_tb,stdev_reit,t,T,r,dividend_rate_reit)
    value_ratio_gold_to_total = profit_loss_gold/total_profit
    value_ratio_tb_to_total = profit_loss_tb_optimised/total_profit
    value_ratio_reit_to_total = profit_loss_reit/total_profit
    
    #value_ratio_gold_to_total =profit_loss_gold/total_profit
    #value_ratio_tb_to_gold = profit_loss_tb_optimised/profit_loss_gold
    #value_ratio_reit_to_gold = profit_loss_reit/profit_loss_gold
    
    risk_ratio_tb_to_reit = average_risk_tb/average_risk_reit
    risk_ratio_tb_to_gold = stdev_tb/average_risk_gold
    risk_ratio_reit_to_gold = risk_ratio_tb_to_gold/risk_ratio_tb_to_reit
    risk_ratio_gold_to_total = 1/(1+ risk_ratio_tb_to_gold +risk_ratio_reit_to_gold )
    risk_ratio_tb_to_total = risk_ratio_gold_to_total*risk_ratio_tb_to_gold
    risk_ratio_reit_to_total = risk_ratio_gold_to_total*risk_ratio_reit_to_gold
    with open ('metrics.log','a') as f:
        f.write('Total profit is {}\n'.format(total_profit))
        f.write('value_ratio_gold_to_total is {}\n'.format(value_ratio_gold_to_total))
        f.write('value_ratio_tb_to_total is {}\n'.format(value_ratio_tb_to_total))
        f.write('risk_ratio_tb_to_reit is {}\n'.format(risk_ratio_tb_to_reit))
        f.write('value_ratio_reit_to_total is {}\n'.format(value_ratio_reit_to_total ))
        f.write('risk_ratio_gold_to_total is {}\n'.format(risk_ratio_gold_to_total))
        f.write('risk_ratio_tb_to_gold is {}\n'.format(risk_ratio_tb_to_gold))  
        f.write('risk_ratio_reit_to_gold is {}\n'.format(risk_ratio_reit_to_gold))  
        f.close()
    return value_ratio_gold_to_total,value_ratio_tb_to_total,value_ratio_reit_to_total,risk_ratio_tb_to_gold,risk_ratio_reit_to_gold,risk_ratio_gold_to_total,average_risk_gold,average_risk_reit,average_risk_tb,profit_loss_gold,profit_loss_reit,profit_loss_tb_optimised,profit_loss_gold_ratio,profit_loss_reit_ratio,profit_loss_tb_ratio,gold,collar_option_reit,tb_option_optimised,total_value,S_tb_t,S_reit_t