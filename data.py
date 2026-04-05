import pandas as pd
import numpy as np
import os
import datetime
from datetime import datetime,timedelta
import random
from sklearn.preprocessing import MinMaxScaler,StandardScaler
#import FL_BRNN
#from FL_BRNN import preprocess_fl,utils_fl
#from FL_BRNN import imputation,predict
scaler =StandardScaler()
def dataLoad(data_dir):
    files=[]
    refs=[]
    for r,d,f in os.walk(data_dir):
        for f_ in f:
            print(f_)
            if 'macro' not in r and f_.split('.')[-1]=='csv':
                file_name = f_.split('.')[0]
                files.append(f_)
                orig = pd.read_csv(r+'/'+f_,na_filter=True)
                if 'auction' in f_.lower():
                    orig['gold_future_auction']=(orig['GOAULNAM Index']+orig['GOAULNPM Index'])/2
                    orig = orig.drop(['GOAULNAM Index','GOAULNPM Index'],axis=1)
                    
                for col in orig.columns:
                    if 'volume' in col.lower():
                        orig = orig.drop(col,axis=1)
                    elif 'date' in col.lower():
                        orig['date']=pd.to_datetime(orig[col])
                        orig = orig.drop(col,axis=1)
                    elif 'treasury 5 years' in file_name.lower():
                        orig[col+'_tb']=orig[col]
                        orig = orig.drop(col,axis=1)           
                    elif 'reit' in file_name.lower():
                        orig[col+'_reit']=orig[col]
                        orig = orig.drop(col,axis=1)     
                    else:
                        orig[col+'_'+file_name]=orig[col]
                        orig = orig.drop(col,axis=1)
                
            

                if len(files)==1:
                    df_orig = orig
                else:
                    data_1=orig
                    df_orig = df_orig.merge(data_1,how='outer',on=('date'))
            df_orig = df_orig.dropna().reset_index().drop('index',axis=1)
            if 'macro' in r and f_.split('.')[-1]=='csv':
                file_name = f_.split('.')[0]
                ref = pd.read_csv(r+'/'+f_,na_filter=True)
                refs.append(file_name)
                for col in ref.columns:
                    if 'cases' in col.lower():
                        ref = ref.drop(col,axis=1)    
                    elif 'consideration' in col.lower():
                        ref = ref.drop(col,axis=1)    
                    elif 'month' in col.lower():
                        ref[col] = pd.to_datetime(ref[col],format='%Y%m').dt.strftime('%Y%m')
                if len(refs)==1:
                    df_ref = ref
                else:
                    df_ref = df_ref.merge(ref,how='outer',on=('Month'))   
    df_ref_standardized=REITMacro(df_ref)         
    df_orig['Month']=df_orig['date'].dt.strftime('%Y%m')
    df_orig = df_orig.merge(df_ref_standardized,how='outer',on=('Month'))
    df_orig = df_orig.sort_values(by='date',ascending=True)

    df_orig = df_orig.replace(np.nan,0)
    print(len(df_orig))
    
    
    #df_orig['current_date'] = datetime.now()

    df_orig.to_csv('orig.csv')
    return df_orig,df_ref

def preprocess(df_orig):

    df_orig['sofr_orig']=None
    df_orig['GOFO']=None
    df_orig['SOFR']=None
    for col in df_orig.columns:
        if 'auction' in col.lower():
            df_orig['auction'] = df_orig[col]
        elif 'sofr_sofr' in col.lower():
            #print(col)
            df_orig['sofr_orig'] = df_orig[col]
        elif 'dgs10' in col.lower() and 'yield rate' in col.lower():
            df_orig['risk free rate'] = df_orig[col]
    #print(df_orig['auction'])
    #print(df_orig['sofr_orig'])
    df_orig = df_orig.drop('Month',axis=1)
    for i in range(1,len(df_orig)):

        df_orig.loc[i,'GOFO'] = 1+np.log10(df_orig.loc[i,'auction']/df_orig.loc[i-1,'auction'])
        df_orig.loc[i,'SOFR'] = (1+(df_orig.loc[i,'sofr_orig']/100))/(1+(df_orig.loc[i-1,'sofr_orig']/100))
        df_orig.loc[i,'Phi']=(1-(df_orig.loc[i,'GOFO']-df_orig.loc[i,'SOFR']))

        i+=1


    #print(df_orig)
    df_orig.to_csv('preprocessed.csv')
    #print(df)
    random_int = random.randint(100,1700)
    #random_int=1
    df = df_orig[-random_int-100:-random_int].reset_index().drop('index',axis=1)

    #print('-------------------------preprocessed dataframe------------------------')
    #print(df)


    #df_orig = df_orig[-365:].reset_index()
    #df = df_orig.replace(np.NaN,0)
    #df = imputation(df_orig,0)
    #df = df.drop('index',axis=1)
    transaction_date_temp =  df['date'][0]
    #print(transaction_date_temp )
    df['transaction_date'] = transaction_date_temp 
    df['transaction_date']=pd.to_datetime(df['transaction_date'])
    df['current_date'] = df['date'][len(df)-1]
    df['current_date'] = pd.to_datetime(df['current_date'])
    df['strike_date']=None
    for i in range(len(df)):
        df.loc[i,'strike_date']=df.loc[i,'current_date']+timedelta(days=30)
        i+=1    

    df['strike_date']=pd.to_datetime(df['strike_date'],format='%Y/%m/%d')
    df['maturity_date']=df['strike_date']
    df['holding days']=(df['current_date']-df['transaction_date']).dt.days
    df['strike days']=(df['strike_date']-df['transaction_date']).dt.days
    #print(df['SOFR'])
    #print(df)
    #print(len(df['SOFR']))
    return df

def split(df,number,computation_days,days_range):
    df = df[number:number+computation_days].reset_index()
    df = df.drop('index',axis=1)
    #print(df)
    df['gold_value']=None
    end = len(df)-1
    for col in df.columns:
        if 'gofo' in col.lower():
            gofo =  df.loc[end,col]
        elif 'sofr' in col.lower():
            #print(col)
            sofr = df.loc[end,col]
            #print(sofr)
        elif 'xauusd' in col.lower():
            #print(col)
            #print(df[col])
            spot_gold = df.loc[end,col]
            df['gold_delta']=None
            for i in range(1,len(df)-1):
                df.loc[i+1,'gold_value']=df.loc[i,col]*df.loc[i,'Phi']
                df.loc[i+1,'gold_delta']=df[col][i]/df[col][i-1]-1
                i+=1

        
            stdev_gold =np.std(df['gold_delta'])
            stdev_gold_down = np.std(df[df['gold_delta']<0]['gold_delta'])
            #print('stdev of gold down is ',stdev_gold_down)
        elif 'reit' in col.lower() and 'dividend' not in col.lower():
            #print(col,df.loc[end,col])
            S_reit_0 = df.loc[end,col]
            #print(S_reit_0)
            #print(df[col])
            df['reit_delta']=None
            for i in range(1,len(df)):
                df.loc[i,'reit_delta']=df[col][i]/df[col][i-1]-1
                i+=1

            stdev_reit = np.std(df['reit_delta'])
            #stdev_reit = np.std(df[col])
        elif 'reit' in col.lower() and 'dividend' in col.lower():
            #print(col,df.loc[end,col])
            dividend_rate_reit = df.loc[end,col]/100
            #print(S_reit_0)
            #print(df[col])
        elif 'tb' in col.lower():
            S_tb_0 = df.loc[end,col]
            df['tb_delta']=None
            for i in range(1,len(df)):
                df.loc[i,'tb_delta']=df[col][i]/df[col][i-1]-1
                i+=1

            stdev_tb = np.std(df['tb_delta'])
            #stdev_tb = np.std(df[col])
        elif 'maturity_date' in col.lower():
            maturity_date =  df.loc[end,col]
        elif 'current_date' in col.lower():

            current_date =  df.loc[end,col]
        elif 'holding days' in col.lower():
            t =  int(df.loc[end,col])
        elif 'strike days' in col.lower():

            T =  int(df.loc[end,col])
        elif 'risk free' in col.lower():
            r = df.loc[end,col]/100
        elif 'mrf' in col.lower():
            mrf = df.loc[end,col]/100
    #--------extreme test--------
    '''
    if number==days_range-1:
        spot_gold=spot_gold*0.6
        S_reit_0=S_reit_0*0.2
    '''
    print('date is: {}'.format(df.loc[end,'date']))
    df.to_csv('preprocessed_nonna.csv')
    return spot_gold,gofo,sofr,stdev_gold,stdev_gold_down,S_reit_0,t,T,maturity_date,current_date,r,mrf,dividend_rate_reit,stdev_reit,S_tb_0,stdev_tb
def imputation(orig,timeSequence,opt):
    cols=[]
    for col in orig.columns:
        if 'date' in col:
            cols.append(col)
    df_drop = orig[cols]
    orig = orig.drop(cols,axis=1)
    print(orig)
    x,y,x_imputation,x_train,y_train,x_test,y_test,y_actual,start,cols_orig,df_imputation = preprocess_fl.dataSplit(orig,timeSequence,opt,0)
    #y_predict, y_actual = predict.FL_train_nn(x_train,y_train,x_test,y_test,y_actual,x_imputation,cols_orig,timeSequence,start,opt)
    #y_actual,y_predict = FL_train_gan(x_train,y_train,x_test,y_test,y_actual)
    #y_actual,y_predict = FL_train_predict_window(x,y,x_train,y_train,x_test,y_test,y_actual,start)
    #y_predict_fl = utils_fl.fl_convertion(y_predict).reshape(-1,1)
    #df_predict = pd.DataFrame(y_predict_fl)
    df_imputation = pd.concat((df_drop,df_imputation),axis=1)
    return df_imputation
def REITMacro(df_ref):
    #print(df_ref)
    df_ref_ = df_ref.drop('Month',axis=1)
    df_ref_standardized =  pd.DataFrame(scaler.fit_transform(df_ref_.values),columns=df_ref_.columns+'_standardized',index=df_ref_.index)
    
    df_ref_standardized['mrf']=df_ref_standardized.mean(axis=1)
    df_ref_standardized['Month']=df_ref['Month']
    return df_ref_standardized
