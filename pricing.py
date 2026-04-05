import numpy as np
import pandas as pd
from scipy import stats as st
from scipy.stats import norm,zscore
import utils
from utils import binomial_pricing,QuanLib_pricing
import datetime
import math
import sklearn
from sklearn.preprocessing import MinMaxScaler,StandardScaler, Normalizer, normalize,minmax_scale
scaler = StandardScaler()

def Gold(spot_gold,gofo,sofr,t,stdev_gold,stdev_gold_down,r):
    #print(spot_gold,gofo,sofr,t,stdev_gold,stdev_gold_down,r)
    t=1
    gold = spot_gold*(1-(gofo-sofr)**t)
    profit_loss_gold = gold - spot_gold
    profit_loss_gold_ratio = profit_loss_gold/spot_gold
    sharpe_ratio = ((1-(gofo-sofr)**t)-r)/(stdev_gold)
    sortino_ratio = ((1-(gofo-sofr)**t)-r)/(stdev_gold_down)
    with open ('pricing_gold.log', 'a') as f:
        f.write('Gold value is {}\n'.format(gold))
        f.write('Profit/loss of gold is {}.\n'.format(profit_loss_gold))
        f.write('Stdev of gold is {}, stedev_down of gold is {}.\n'.format(stdev_gold,stdev_gold_down))
        f.write('Sharpe ratio is {}\n'.format(sharpe_ratio))
        f.write('Sortino ratio is {}.\n'.format(sortino_ratio))
        f.close()

    return gold,profit_loss_gold,profit_loss_gold_ratio,sharpe_ratio,sortino_ratio,stdev_gold,stdev_gold_down

def TBCoveredCallOption(S_tb_0,T,t,r,stdev_tb,opt):
    # This is to use BS-PDE model
    #t_days = t
    #T_days = T
    t = t/360
    T = T/360
    S_tb_t = S_tb_0*np.exp(r*(T-t))  #??is this correct for pde method??
    #print(S_tb_0,S_tb_t)
    K_tb_list=[]
    for i in range(10):
        if i == 0:
            k_tb_option = S_tb_t
        else:
            k_tb_option = k_tb_option-0.5
        K_tb_list.append(k_tb_option)
    #print(K_tb_list)
    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(T-t))

    mu = (r-(stdev_tb**2/2))*(T-t)+stdev_tb*np.sqrt(T-t)*omega_t  #--??should i add dividend rate and macro index when estimating mu to predict stock price at time t?
    #print(mu)
    pde_factor = (mu*(1-r)*(T-t))/(1-mu) #--??I used Brownie Motion as a martingale, is it correct?
    k_tb_selected = []
    call_option_tb_list=[]
    profit_loss_tb_list=[]
    for k_ in K_tb_list:
        d1_tb=(np.log(S_tb_t/k_)+(r+(stdev_tb**2/2)))*(T-t)/(stdev_tb*np.sqrt(T-t))
        d2_tb=d1_tb-stdev_tb*np.sqrt(T-t)
        call_option_tb = np.exp(pde_factor)*(S_tb_0*norm.cdf(d1_tb)-np.exp(-r*(T-t))*k_*norm.cdf(d2_tb))
        #put_option_tb = np.exp(pde_factor)*(np.exp(-r*(T-t))*k_*norm.cdf(-d2_tb))-S_tb_0*norm.cdf(-d1_tb)
        profit_loss_tb = call_option_tb+S_tb_t-S_tb_0
        #print(profit_loss_tb)
        k_tb_selected.append(k_)
        call_option_tb_list.append(call_option_tb)
        profit_loss_tb_list.append(profit_loss_tb)
    df_tb=pd.DataFrame()
    df_tb['k_tb']=k_tb_selected
    df_tb['call_option_tb']=call_option_tb_list
    df_tb['profit_loss_tb']=profit_loss_tb_list
    K_tb_optimised = df_tb['k_tb'][np.argmax(df_tb['profit_loss_tb'])]
    
    tb_option_optimised = df_tb['call_option_tb'][np.argmax(df_tb['profit_loss_tb'])]

    profit_loss_tb_optimised = max(df_tb['profit_loss_tb'])
    profit_loss_tb_ratio = profit_loss_tb_optimised/(tb_option_optimised+S_tb_0)
    df_tb.to_csv('pricing_tb.csv')
    return K_tb_optimised,tb_option_optimised,profit_loss_tb_optimised,profit_loss_tb_ratio,d1_tb,d2_tb,S_tb_t

def TBCoveredCallOption_hedge(S_tb_0,T,t,r,stdev_tb,S_reit_t,S_reit_0,stdev_reit,collar_option_reit,opt):
    # This is to use BS-PDE model
    #t_days = t
    #T_days = T

    t = t/360
    T = T/360
    S_tb_t = S_tb_0*np.exp(r*(T-t)) #??is this correct for pde method??
    #print(S_tb_0,S_tb_t)
    ir_reit = (S_reit_t-S_reit_0)*norm.cdf((r*(T-t))/(stdev_reit*np.sqrt(T-t)))
    K_tb_list=[]
    for i in range(10):
        if i == 0:
            k_tb_option = S_tb_t
        else:
            k_tb_option = k_tb_option-0.5
        K_tb_list.append(k_tb_option)
    #print(K_tb_list)
    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(T-t))

    mu = (r-(stdev_tb**2/2))*(T-t)+stdev_tb*np.sqrt(T-t)*omega_t #--??should i add dividend rate and macro index when estimating mu to predict stock price at time t?
    #print(mu)
    pde_factor = (mu*(1-r)*(T-t))/(1-mu) #--??I used Brownie Motion as a martingale, is it correct?
    #print('martingale of TB Option is: ',pde_factor,np.exp(pde_factor))
    hedged_ratio = opt.fraction_of_hedged
    k_tb_selected = []
    call_option_tb_list=[]
    profit_loss_tb_list=[]
    #-----chang to long call option--------
    for k_ in K_tb_list:
        d1_tb=(np.log(S_tb_t/k_)+(r+(stdev_tb**2/2)))*(T-t)/(stdev_tb*np.sqrt(T-t))
        d2_tb=d1_tb-stdev_tb*np.sqrt(T-t)
        call_option_tb = np.exp(pde_factor)*(S_tb_0*norm.cdf(d1_tb)-np.exp(-r*(T-t))*k_*norm.cdf(d2_tb))
        #put_option_tb = np.exp(pde_factor)*(np.exp(-r*(T-t))*k_*norm.cdf(-d2_tb)-S_tb_0*norm.cdf(-d1_tb))
        profit_loss_tb = S_tb_t-S_tb_0+call_option_tb
        #print('value of tb price at t {}, value of tb price at 0 {} and put option value {}'.format(S_tb_t,S_tb_0,put_option_tb))
        #print(profit_loss_tb)
        if collar_option_reit<0:
            print('-------------------------------Hedge REIT Interest Risk--------------------------------')
            #hedged_ir_portfolio = profit_loss_tb + collar_option_reit*hedged_ratio
            hedged_ir_portfolio = profit_loss_tb + ir_reit*hedged_ratio
            #print(hedged_ir_portfolio)
            if hedged_ir_portfolio>0:
                k_tb_selected.append(k_)
                call_option_tb_list.append(call_option_tb)
                profit_loss_tb_list.append(profit_loss_tb)
        else:
            k_tb_selected.append(k_)
            call_option_tb_list.append(call_option_tb)
            profit_loss_tb_list.append(profit_loss_tb)
    df_tb=pd.DataFrame()
    df_tb['k_tb']=k_tb_selected
    df_tb['call_option_tb']=call_option_tb_list
    df_tb['profit_loss_tb']=profit_loss_tb_list
    K_tb_optimised = df_tb['k_tb'][np.argmax(df_tb['profit_loss_tb'])]
    tb_option_optimised = df_tb['call_option_tb'][np.argmax(df_tb['profit_loss_tb'])]
    profit_loss_tb_optimised = max(df_tb['profit_loss_tb'])
    profit_loss_tb_ratio = profit_loss_tb_optimised/(tb_option_optimised+S_tb_0)
    df_tb.to_csv('pricing_tb.csv')
    return K_tb_optimised,tb_option_optimised,profit_loss_tb_optimised,profit_loss_tb_ratio,d1_tb,d2_tb,S_tb_t

def REITCollarOption(S_reit_0,t,T,r,dividend_rate_reit,mrf,stdev_reit,opt):
    # This is to use BS-PDE model
    #print(S_reit_0,t,T,r,stdev_reit)
    #t_days = t
    #T_days = T
    z_score = opt.confidence_score
    t = t/261
    T = T/261
    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(T-t))
    print('omega_t is ',omega_t)

    mu = (r+dividend_rate_reit+mrf-(stdev_reit**2/2))*(T-t)+stdev_reit*np.sqrt(T-t)*omega_t #--??should i add dividend rate and macro index when estimating mu to predict stock price at time t?
    #print(mu)
    pde_factor = (mu*(1-r)*(T-t))/(1-mu) #--??I used Brownie Motion as a martingale, is it correct?
    #print('martingale of REIT Option is: ',pde_factor,np.exp(pde_factor))
    S_reit_t = S_reit_0*np.exp(mu)
    S_reit_t_optimised = S_reit_t
    if stdev_reit==omega_t/(T-t):
        S_reit_t_optimised = S_reit_0*np.exp(r+omega_t**2/(2*(T-t)))
    #-----Calculate optimised strike price ----------
    #print(z_score*stdev_reit,r-(stdev_reit**2/2),stdev_reit**2/2)
    K_reit = S_reit_0*np.exp(z_score*stdev_reit+r-stdev_reit**2/2)
    #print(K_reit)

    if stdev_reit==z_score:
        K_reit_optimised =  S_reit_0*np.exp(r+(stdev_reit**2/2))
    else:
        K_reit_list=[]
        for i in range(10):
            if i == 0:
                k_reit_option = K_reit
            else:
                k_reit_option = k_reit_option-1
            K_reit_list.append(k_reit_option)
        #print(K_reit_list)
        k_reit_selected = []
        call_option_reit_list=[]
        put_option_reit_list=[]
        collar_option_reit_list=[]
        profit_loss_reit_list=[]
        for k_ in K_reit_list:
            d1_reit=(np.log(S_reit_t/k_)+(r-dividend_rate_reit-mrf+(stdev_reit**2/2)))*(T-t)/(stdev_reit*np.sqrt(T-t))
            d2_reit=d1_reit-stdev_reit*np.sqrt(T-t)
            call_option_reit = np.exp(pde_factor)*(S_reit_t*np.exp(-1*(dividend_rate_reit+mrf)*(T-t))*norm.cdf(d1_reit)-np.exp(-r*(T-t))*k_*norm.cdf(d2_reit))
            put_option_reit = np.exp(pde_factor)*(np.exp(-r*(T-t))*k_*norm.cdf(-d2_reit)-S_reit_t*np.exp(-1*(dividend_rate_reit+mrf)*(T-t))*norm.cdf(-d1_reit))
            collar_option_reit = -put_option_reit+call_option_reit
            profit_loss_reit = collar_option_reit +S_reit_t-S_reit_0

            #print(profit_loss_reit)
            k_reit_selected.append(k_)
            call_option_reit_list.append(call_option_reit)
            put_option_reit_list.append(put_option_reit)
            collar_option_reit_list.append(collar_option_reit)
            profit_loss_reit_list.append(profit_loss_reit)
        df_reit=pd.DataFrame()
        df_reit['k_reit']=k_reit_selected
        df_reit['call_option_reit']=call_option_reit_list
        df_reit['put_option_reit']=put_option_reit_list
        df_reit['collar_option_reit']=collar_option_reit_list
        df_reit['profit_loss_reit']=profit_loss_reit_list
        K_reit_optimised = df_reit['k_reit'][np.argmax(df_reit['profit_loss_reit'])]
        call_option_reit = df_reit['call_option_reit'][np.argmax(df_reit['profit_loss_reit'])]
        put_option_reit = df_reit['put_option_reit'][np.argmax(df_reit['profit_loss_reit'])]
        collar_option_reit = df_reit['collar_option_reit'][np.argmax(df_reit['profit_loss_reit'])]
        profit_loss_reit = max(df_reit['profit_loss_reit'])
        profit_loss_reit_ratio = profit_loss_reit/(collar_option_reit+S_reit_0)
    with open ('pricing_reit.log', 'a') as f:
        f.write('S of reit is {}.Optimised S of reit is {}\n'.format(S_reit_0,S_reit_t_optimised))
        f.write('K of reit is {}.Optimised K of reit is {}\n'.format(K_reit,K_reit_optimised))
        f.write('put option of reit is {}, call option of reit is {}, and caller option of reit is {}\n'.format(put_option_reit,call_option_reit,collar_option_reit))
        f.write('profit/loss of reit option is {}\n'.format(profit_loss_reit))
        f.close()
    return collar_option_reit,profit_loss_reit,profit_loss_reit_ratio,d1_reit,d2_reit,K_reit,S_reit_t,K_reit_optimised,S_reit_t_optimised

def TBCoveredCallOption_Binomial(S_tb_0,T,t,r,current_date,maturity_date,stdev_tb,opt):

    # This is to use BS-PDE model
    t = t/360
    T = T/360

    S_tb_t = S_tb_0*np.exp(r*(T-t)) #??is this correct for binomial method??
    #print(S_tb_0,S_tb_t)
    mu = r*(T-t)

    K_tb_list=[]
    for i in range(10):
        if i == 0:
            k_tb_option = S_tb_t
        else:
            k_tb_option = k_tb_option-0.5
        K_tb_list.append(k_tb_option)
    #print(K_tb_list)

    k_tb_selected = []
    call_option_tb_list=[]
    profit_loss_tb_list=[]
    for k_ in K_tb_list:
        call_option_tb = binomial_pricing(S_tb_0,S_tb_t,k_,r,0,stdev_tb,T,t,mu,'call',360)
        #put_option_tb = QuanLib_pricing(S_tb_0,k_,r,0,stdev_tb,maturity_date,current_date,'call')
        #print('call option value is: ',call_option_tb)
        
        d1_tb=(np.log(S_tb_t/k_)+(r+(stdev_tb**2/2)))*(T-t)/(stdev_tb*np.sqrt(T-t))
        d2_tb=d1_tb-stdev_tb*np.sqrt(T-t)
        profit_loss_tb = call_option_tb+S_tb_t-S_tb_0
        #print(profit_loss_tb)
        k_tb_selected.append(k_)
        call_option_tb_list.append(call_option_tb)
        profit_loss_tb_list.append(profit_loss_tb)
    df_tb=pd.DataFrame()
    df_tb['k_tb']=k_tb_selected
    df_tb['call_option_tb']=call_option_tb_list
    df_tb['profit_loss_tb']=profit_loss_tb_list
    K_tb_optimised = df_tb['k_tb'][np.argmax(df_tb['profit_loss_tb'])]
    
    tb_option_optimised = df_tb['call_option_tb'][np.argmax(df_tb['profit_loss_tb'])]

    profit_loss_tb_optimised = max(df_tb['profit_loss_tb'])
    profit_loss_tb_ratio = profit_loss_tb_optimised/(tb_option_optimised+S_tb_0)
    df_tb.to_csv('pricing_tb.csv')
    return K_tb_optimised,tb_option_optimised,profit_loss_tb_optimised,profit_loss_tb_ratio,d1_tb,d2_tb,S_tb_t

def TBCoveredCallOption_hedge_Binomial(S_tb_0,T,t,current_date,maturity_date,r,stdev_tb,S_reit_t,S_reit_0,stdev_reit,collar_option_reit,opt):
    #t_days = t
    #T_days = T
    # This is to use BS-PDE model

    ir_reit = (S_reit_t-S_reit_0)*norm.cdf((r*(T-t))/(stdev_reit*np.sqrt(T-t)))
    t = t/360    
    T = T/360
    S_tb_t = S_tb_0*np.exp(r*(T-t)) #??is this correct for binomial method??
    mu = r*(T-t)
    print(S_tb_0,S_tb_t)
    K_tb_list=[]
    for i in range(10):
        if i == 0:
            k_tb_option = S_tb_t
        else:
            k_tb_option = k_tb_option-0.5
        K_tb_list.append(k_tb_option)
    #print(K_tb_list)
    hedged_ratio = opt.fraction_of_hedged
    k_tb_selected = []
    call_option_tb_list=[]
    profit_loss_tb_list=[]
    #-----chang to long call option--------
    for k_ in K_tb_list:
        call_option_tb = binomial_pricing(S_tb_0,S_tb_t,k_,r,0,stdev_tb,T,t,mu,'call',360)
        #call_option_tb = QuanLib_pricing(S_tb_0,k_,r,0,stdev_tb,maturity_date,current_date,'call')
        print('call option value is ',call_option_tb)
        d1_tb=(np.log(S_tb_t/k_)+(r+(stdev_tb**2/2)))*(T-t)/(stdev_tb*np.sqrt(T-t))
        d2_tb=d1_tb-stdev_tb*np.sqrt(T-t)
        profit_loss_tb = call_option_tb+S_tb_t-S_tb_0
        print('P/L is ',profit_loss_tb)

        if collar_option_reit<0:
            print('-------------------------------Hedge REIT Interest Risk--------------------------------')
            #hedged_ir_portfolio = profit_loss_tb + collar_option_reit*hedged_ratio
            hedged_ir_portfolio = profit_loss_tb + ir_reit*hedged_ratio
            #print(hedged_ir_portfolio)
            if hedged_ir_portfolio>0:
                k_tb_selected.append(k_)
                call_option_tb_list.append(call_option_tb)
                profit_loss_tb_list.append(profit_loss_tb)
        else:
            k_tb_selected.append(k_)
            call_option_tb_list.append(call_option_tb)
            profit_loss_tb_list.append(profit_loss_tb)
    df_tb=pd.DataFrame()
    df_tb['k_tb']=k_tb_selected
    df_tb['call_option_tb']=call_option_tb_list
    df_tb['profit_loss_tb']=profit_loss_tb_list
    K_tb_optimised = df_tb['k_tb'][np.argmax(df_tb['profit_loss_tb'])]
    tb_option_optimised = df_tb['call_option_tb'][np.argmax(df_tb['profit_loss_tb'])]
    profit_loss_tb_optimised = max(df_tb['profit_loss_tb'])
    profit_loss_tb_ratio = profit_loss_tb_optimised/(tb_option_optimised+S_tb_0)
    df_tb.to_csv('pricing_tb.csv')
    return K_tb_optimised,tb_option_optimised,profit_loss_tb_optimised,profit_loss_tb_ratio,d1_tb,d2_tb,S_tb_t

def REITCollarOption_Binomial(S_reit_0,t,T,current_date,maturity_date,r,dividend_rate_reit,mrf,stdev_reit,opt):
    # This is to use BS-PDE model
    #print(S_reit_0,t,T,r,stdev_reit)
    #t_days = t
    #T_days = T
    z_score = opt.confidence_score
    t = t/261
    T = T/261
    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(T-t))
    print('omega_t is ',omega_t)
    print(S_reit_0,r,dividend_rate_reit,mrf,stdev_reit,T-t,omega_t)
    mu = (r+dividend_rate_reit+mrf-(stdev_reit**2/2))*(T-t)+stdev_reit*np.sqrt(T-t)*omega_t #--??should i add dividend rate and macro index when estimating mu to predict stock price at time t?
    #print(mu)
    #pde_factor = (omega_t*(1-r)*(T-t))/(1-omega_t) #--??I used Brownie Motion as a martingale, is it correct?
    #print(pde_factor,np.exp(pde_factor))
    S_reit_t = S_reit_0*np.exp(mu)
    print(S_reit_t)
    S_reit_t_optimised = S_reit_t
    if stdev_reit==omega_t/(T-t):
        S_reit_t_optimised = S_reit_0*np.exp(r+omega_t**2/(2*(T-t)))
    print(S_reit_t_optimised)
    #-----Calculate optimised strike price ----------
    #print(z_score*stdev_reit,r-(stdev_reit**2/2),stdev_reit**2/2)

    K_reit = S_reit_0*np.exp(z_score*stdev_reit+r-stdev_reit**2/2)
    #print(K_reit)
    if stdev_reit==z_score:
        K_reit_optimised =  S_reit_0*np.exp(r+(stdev_reit**2/2))
    else:
        K_reit_list=[]
        for i in range(10):
            if i == 0:
                k_reit_option = K_reit
            else:
                k_reit_option = k_reit_option-1
            K_reit_list.append(k_reit_option)
        #print(K_reit_list)
        k_reit_selected = []
        call_option_reit_list=[]
        put_option_reit_list=[]
        collar_option_reit_list=[]
        profit_loss_reit_list=[]
        for k_ in K_reit_list:
            call_option_reit = QuanLib_pricing(S_reit_0,k_,r,dividend_rate_reit,stdev_reit,maturity_date,current_date,'call')
            put_option_reit = QuanLib_pricing(S_reit_0,k_,r,dividend_rate_reit,stdev_reit,maturity_date,current_date,'put')
            #call_option_reit = binomial_pricing(S_reit_0,S_reit_t,k_,r,dividend_rate_reit,stdev_reit,T,t,mu,'call',261)
            #put_option_reit = binomial_pricing(S_reit_0,S_reit_t,k_,r,dividend_rate_reit,stdev_reit,T,t,mu,'put',261)
            #print('call option value is: ',call_option_reit)
            collar_option_reit = -put_option_reit+call_option_reit
            profit_loss_reit = collar_option_reit +S_reit_t-S_reit_0
            d1_reit=(np.log(S_reit_t/k_)+(r-dividend_rate_reit-mrf+(stdev_reit**2/2)))*(T-t)/(stdev_reit*np.sqrt(T-t))
            d2_reit=d1_reit-stdev_reit*np.sqrt(T-t)
            #print(profit_loss_reit)
            k_reit_selected.append(k_)
            call_option_reit_list.append(call_option_reit)
            put_option_reit_list.append(put_option_reit)
            collar_option_reit_list.append(collar_option_reit)
            profit_loss_reit_list.append(profit_loss_reit)
        df_reit=pd.DataFrame()
        df_reit['k_reit']=k_reit_selected
        df_reit['call_option_reit']=call_option_reit_list
        df_reit['put_option_reit']=put_option_reit_list
        df_reit['collar_option_reit']=collar_option_reit_list
        df_reit['profit_loss_reit']=profit_loss_reit_list
        #print(df_reit)
        K_reit_optimised = df_reit['k_reit'][np.argmax(df_reit['profit_loss_reit'])]
        call_option_reit = df_reit['call_option_reit'][np.argmax(df_reit['profit_loss_reit'])]
        put_option_reit = df_reit['put_option_reit'][np.argmax(df_reit['profit_loss_reit'])]
        collar_option_reit = df_reit['collar_option_reit'][np.argmax(df_reit['profit_loss_reit'])]

        profit_loss_reit = max(df_reit['profit_loss_reit'])
        profit_loss_reit_ratio = profit_loss_reit/(collar_option_reit+S_reit_0)
    with open ('pricing_reit.log', 'a') as f:
        f.write('S of reit is {}.Optimised S of reit is {}\n'.format(S_reit_0,S_reit_t_optimised))
        f.write('K of reit is {}.Optimised K of reit is {}\n'.format(K_reit,K_reit_optimised))
        f.write('put option of reit is {}, call option of reit is {}, and caller option of reit is {}\n'.format(put_option_reit,call_option_reit,collar_option_reit))
        f.write('profit/loss of reit option is {}\n'.format(profit_loss_reit))
        f.close()
    return collar_option_reit,profit_loss_reit,profit_loss_reit_ratio,d1_reit,d2_reit,K_reit,S_reit_t,K_reit_optimised,S_reit_t_optimised


def REIT(S_reit_0,t,r,dividend_rate_reit,mrf,stdev_reit,opt):
    t = t/261

    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(t))
    mu = (r+dividend_rate_reit+mrf-(stdev_reit**2/2))*t+stdev_reit*np.sqrt(t)*omega_t
    S_reit_t = S_reit_0*np.exp(mu)
    if stdev_reit==omega_t/t:
        S_reit_t_optimised = S_reit_0*np.exp(r+(omega_t**2)/(2*t))
   
    profit_loss_reit = S_reit_t_optimised - S_reit_0

    return profit_loss_reit,S_reit_t_optimised,S_reit_t


def BSMGreeks(d1,d2,T,t,q,r,stdev,S,K):
    if q==0:
        delta_call = norm.cdf(d1)
        delta_put = -norm.cdf(-d1)
        gamma = norm.pdf(d1)/(S*np.exp(-r*(T-t))*stdev*np.sqrt(T-t))
        theta_call = -S*np.exp(-r*(T-t))*stdev*norm.pdf(d1)/(2*np.sqrt(T-t))-r*K*np.exp(-r*(T-t))*norm.cdf(d2)
        theta_put = -S*np.exp(-r*(T-t))*stdev*norm.pdf(d1)/(2*np.sqrt(T-t))+r*K*np.exp(-r*(T-t))*norm.cdf(-d2)
        vega = (S*np.sqrt(T-t)*norm.pdf(d1))
        rho_call = (K*(T-t)*np.exp(-r*(T-t))*norm.cdf(d2))
        rho_put = -(K*(T-t)*np.exp(-r*(T-t))*norm.cdf(-d2))
    else:
        delta_call = np.exp(-q*(T-t))*norm.cdf(d1)
        delta_put = -np.exp(-q*(T-t))*norm.cdf(-d1)
        gamma = norm.pdf(d1)/(S*stdev*np.sqrt(T-t))
        theta_call = -S*np.exp(-r*(T-t))*stdev*norm.pdf(d1)/(2*np.sqrt(T-t))-r*K*np.exp(-r*(T-t))*norm.cdf(d2)+q*S*np.exp(-r*(T-t))*norm.cdf(d1)
        theta_put = -S*np.exp(-r*(T-t))*stdev*norm.pdf(d1)/(2*np.sqrt(T-t))+r*K*np.exp(-r*(T-t))*norm.cdf(-d2)-q*S*np.exp(-r*(T-t))*norm.cdf(-d1)
        vega = (S*np.exp(-r*(T-t))*np.sqrt(T-t)*norm.pdf(d1))
        rho_call = (K*(T-t)*np.exp(-q*(T-t))*norm.cdf(d2))
        rho_put = -(K*(T-t)*np.exp(-q*(T-t))*norm.cdf(-d2))
    with open ('risk_metrics.log','a') as f:
        f.write('d1 is {}\n'.format(d1))
        f.write('d2 is {}\n'.format(d2))
        f.write('T is {}\n'.format(T))
        f.write('t  is {}\n'.format(t ))
        f.write('stdev is {}\n'.format(stdev ))
        f.write('Stock price is {}\n'.format(S))
        f.write('Strike price is {}\n'.format(K)) 
        f.write('delta_call is {}\n'.format(delta_call))
        f.write('delta_put is {}\n'.format(delta_put))
        f.write('gamma is {}\n'.format(gamma))
        f.write('theta_call is {}\n'.format(theta_call))
        f.write('theta_put  is {}\n'.format(theta_put ))
        f.write('vega is {}\n'.format(vega ))
        f.write('rho_call is {}\n'.format(rho_call))
        f.write('rho_put is {}\n'.format(rho_put))  
        f.close()
    return delta_call,delta_put,gamma,theta_call,theta_put,vega,rho_call,rho_put

