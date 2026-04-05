
import pandas as pd
import numpy as np
import math
import QuantLib as ql
import datetime

def binomial_pricing(S,S_t,K,r,d,stdev,T,t,mu,option_type,days):

    r = r/days
    d = d/days
    #t = t*days
    #T = T*days
    steps = np.arange(t,T,1)
    N = len(steps)
    #print(N)
    up = np.exp(mu)
    #print(up)
    #up = np.exp(stdev*np.sqrt(T/t))
    down = 1/up
    


    p = (np.exp((r-d)*(T/t))-down)/(up-down)
    S_t_list = np.zeros((N+1,N+1))
    option_values = np.zeros((N+1,N+1))
    for i in range(N+1):
        for j in range(i+1):
            #print(S,up,j,down,i-j)
            
            S_t_list[i,j] = S*(up**j)*(down**(i-j))
            #print(S_t_list[i,j])
    for j in range(N+1):
        price = S_t_list[N,j]
        if option_type.lower()=='call':
            option_values[N,j] = max(price-K,0)
        else:
            option_values[N,j]  = max(K-price,0)

    for i in range(N-1,-1,-1):
        for j in range(i+1):
            hold_value = np.exp(-(r-d)*(T/t))*(p*option_values[i+1,j+1]+(1-p)*option_values[i+1,j])
            S_t = S_t_list[i,j]
            if option_type.lower()=='call':
                exercise_price = max(S_t-K,0)
            else:
                exercise_price = max(K-S_t,0)
            option_values[i,j]=max(hold_value,exercise_price)
    option_value = option_values[0,0]
    #print('stock price is: {}'.format(S_t_list[N,N]))
    return option_value

def QuanLib_pricing(S,K,r,d,stdev,maturity_date,current_date,option_type):
    #print(maturity_date.day,maturity_date.month,maturity_date.year)
    maturity_date = ql.Date(maturity_date.day,maturity_date.month,maturity_date.year)   #??how to get maturity date for infinite perpetute american option?
    if option_type.lower()=='call':
        otype=ql.Option.Call
    else:
        otype=ql.Option.Put
    dc = ql.Actual365Fixed()
    calendar=ql.NullCalendar()
    evaluation_date = ql.Date(current_date.day,current_date.month,current_date.year)
    ql.Settings.instance().evaluationDate = evaluation_date
    payoff = ql.PlainVanillaPayoff(otype,K)
    exercise_price = ql.AmericanExercise(evaluation_date,maturity_date)
    option = ql.VanillaOption(payoff,exercise_price)
    d_ts = ql.YieldTermStructureHandle(ql.FlatForward(evaluation_date,d,dc))
    r_ts = ql.YieldTermStructureHandle(ql.FlatForward(evaluation_date,r,dc))
    sigma_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evaluation_date,calendar,stdev,dc))
    bsm_process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(S)),d_ts,r_ts,sigma_ts)
    bsm_engine = ql.BaroneAdesiWhaleyApproximationEngine(bsm_process)
    option.setPricingEngine(bsm_engine)
    #print(option.NPV())
    binomial_engine = ql.BinomialVanillaEngine(bsm_process,"crr",100)
    option.setPricingEngine(binomial_engine)
    option_value = option.NPV()
    return option_value


def TBPrice(face_value_tb,yield_rate,coupon_rate,coupon_payment_frequency,tenures):
    coupon_rate = coupon_rate/100
    yield_rate = yield_rate/100
    NV_facevalue = face_value_tb/((1+yield_rate)**tenures)
    coupon_rate_per_payment = coupon_rate/coupon_payment_frequency
    coupon_payment_counts = tenures*coupon_payment_frequency
    coupon = face_value_tb*coupon_rate_per_payment
    nv_coupon_total = 0
    for i in range(1,int(coupon_payment_counts)):
        coupon_payment_tenures = (1/coupon_payment_frequency)*i

        nv_coupon = coupon/((1+yield_rate)**coupon_payment_tenures)
        nv_coupon_total = nv_coupon_total+nv_coupon
        i+=1
    print(NV_facevalue,nv_coupon_total)
    tb_price = NV_facevalue+nv_coupon_total
    return tb_price
def mimicGTBCPSPrice(S_gtbcps_0,T,t,change_of_collaterals,stdev_gtbcps):
    #t_days = t
    #T_days = T
    t = t/365
    T = T/365
    d = change_of_collaterals
    print('------GTBCPS Price-----------')
    print('S_gtbcps_0 is: {},T is: {},t is: {},change_of_collaterals is: {},stdev_gtbcps is: {}'.format(S_gtbcps_0,T,t,change_of_collaterals,stdev_gtbcps))



    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(T-t))
    mu = (d-(stdev_gtbcps**2/2))*(T-t)+stdev_gtbcps*np.sqrt(T-t)*omega_t #--??should i add dividend rate and macro index when estimating mu to predict stock price at time t?
    print(mu)
    #pde_factor = (omega_t*(1-r)*(T-t))/(1-omega_t) #--??I used Brownie Motion as a martingale, is it correct?
    #print(pde_factor,np.exp(pde_factor))
    S_gtbcps_t = S_gtbcps_0*np.exp(mu)
    return S_gtbcps_t
def mimicGTBCPSAmount(T,t,change_of_collaterals,change_of_pegged_price,stdev_gtbcps,total_amount_gtbcps_before):
    #t_days = t
    #T_days = T
    t = t/365
    T = T/365
    d1 = change_of_collaterals
    d2 = change_of_pegged_price

    #-----generate Brownie motion ----------
    omega_t = np.random.normal(0,np.sqrt(T-t))
    mu = (d1+d2-(stdev_gtbcps**2/2))*(T-t)+stdev_gtbcps*np.sqrt(T-t)*omega_t #--??should i add dividend rate and macro index when estimating mu to predict stock price at time t?
    print(mu)
    #pde_factor = (omega_t*(1-r)*(T-t))/(1-omega_t) #--??I used Brownie Motion as a martingale, is it correct?
    #print(pde_factor,np.exp(pde_factor))
    total_amount_gtbcps = total_amount_gtbcps_before*np.exp(mu)
    print('------GTBCPS Amount-----------')
    print('total_amount_gtbcps_before is: {}, total_amount_gtbcps is: {}, T is: {},t is: {},change_of_collaterals is: {},stdev_gtbcps is: {}'.format(total_amount_gtbcps_before,total_amount_gtbcps,T,t,change_of_collaterals,stdev_gtbcps))

    return total_amount_gtbcps

def imputation(df,imputationd_value):
    if 'index' in df.columns:
        df = df.drop(('index'),axis=1)
    df = df.reset_index()
    for col in df.columns:
        for i in range(len(df)):
            try:
                if i==0:
                    estimate_matrix = [item for item in df.loc[i:,col] if item!=imputationd_value ][:7]
                    df.loc[i,col]  =np.mean(estimate_matrix)   
                else:  
                    if df.loc[i,col]==imputationd_value:
                        if df.loc[i-1,col]!=imputationd_value and df.loc[i+1,col]!=imputationd_value:
                            matrix_before =  [item for item in df.loc[:i-1,col] if item !=imputationd_value ][-3:]
                            matrix_after =  [item for item in df.loc[i+1:,col] if item !=imputationd_value ][:3]
                            df.loc[i,col] = 0.4*np.mean(matrix_before)+0.6*np.mean(matrix_after)
                        else:
                            estimate_matrix = [item for item in df.loc[max(0,i-1):,col] if item!=imputationd_value ][:7]
                            df.loc[i,col]  =np.mean(estimate_matrix)     
                    else:
                        continue
            except Exception as e:
                print(e)              
 
    df = df.drop(('index'),axis=1)
    return df