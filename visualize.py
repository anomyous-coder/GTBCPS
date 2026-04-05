import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from sklearn.metrics import auc,f1_score,accuracy_score,mean_absolute_error,mean_squared_error
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score,roc_curve, precision_recall_curve,auc, f1_score,silhouette_score,normalized_mutual_info_score, adjusted_rand_score

project_dir = os.getcwd()
print(project_dir)
graph_dir = project_dir+'/graph/'
perforamance_dir = './log/test/template/90_days.csv'
benchmark_dir = './test/benchmark/DAI/'
#collateral_dir = './visualize_data/collaterals.csv'
#gold_dir = './visualize_data/gold_prediction.csv'
def performance(data_dir,graph_dir):
    df = pd.read_csv(data_dir)
    df['date']=pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df['days']=df['Days'].astype('str')
    df['ref price of GTBCPS']=df[' actual price is'].astype('float')
    df['total amount of GTBCPS']=df[' actual amount is'].astype('float')
    df['marketcap of GTBCPS']=df['ref price of GTBCPS']*df['total amount of GTBCPS']
    df['total value of collaterals']=df['total_value_of_collaterals is'].astype('float')
    df['collateral ratio']=df['collateral ratio is'].astype('float')
    print(df)
    start_date = df.loc[0,'date']
    end_date = df.loc[len(df)-1,'date']
    days = df['days'].values
    price_GTBCPS = df['ref price of GTBCPS'].values
    marketcap_GTBCPS = df['marketcap of GTBCPS'].values
    value_collaterals = df['total value of collaterals'].values
    collateral_ratio = df['collateral ratio'].values
    
    fig,ax1=plt.subplots()
    min_marketcap_GTBCPS = min(marketcap_GTBCPS)
    max_marketcap_GTBCPS = max(marketcap_GTBCPS)
    print(min_marketcap_GTBCPS)

    color = 'tab:orange'
    x = np.arange(0,len(df),1)
    ax1.set_ylabel('Price of GTBCPS',color=color)
    ax1.plot( x, price_GTBCPS,color=color,lw=1.2)
    ax1.tick_params(axis='y',color=color)

    ax1.set_ylim(0.995,1.005)
    
    #ax1.set_xlabel('Days')
    ax2 = ax1.twinx()

    color = 'tab:green'
    ax2.set_ylabel('Marketcap of GTBCPS',color=color)
    #ax2.plot( days, marketcap_GTBCPS,color=color,lw=1.5)
    ax2.fill_between( x,min_marketcap_GTBCPS ,marketcap_GTBCPS,color=color,alpha=0.4)
    ax2.tick_params(axis='y',color=color)
    plt.xticks([0,int(len(df)/2),len(df)],[start_date,str(df.loc[int(len(df)/2),'date']),str(df.loc[len(df)-1,'date'])])
    plt.title('Price and Marketcap of GTBCPS)')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.grid()
    fig_name='GTBCPS_'+'days_'+str(len(df))+'.png'
    plt.savefig(graph_dir+fig_name)
    plt.close()
    '''

    fig,ax1=plt.subplots()
    min_value_collaterals = min(value_collaterals)

    color = 'tab:red'
    x = np.arange(0,len(df),1)
    ax1.set_ylabel('Collateral Ratios',color=color)
    ax1.plot( x, collateral_ratio,color=color,lw=1.2)
    ax1.tick_params(axis='y',color=color)
    ax1.set_ylim(1,1.8)
    #ax1.set_xlabel('Days')
    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Value of Collaterals',color=color)
    ax2.fill_between( x,min_value_collaterals ,value_collaterals,color=color,alpha=0.4)
    ax2.tick_params(axis='y',color=color)
    plt.xticks([0,int(len(df)/2),len(df)],[start_date,str(df.loc[int(len(df)/2),'date']),str(df.loc[len(df)-1,'date'])])
    #plt.legend(loc='best')
    #plt.title('Collateral Ratios and Value of Collaterals of GTBCPS \n ({} to {})'.format(start_date,end_date))
    plt.title('Collateral Ratios and Value of Collaterals of GTBCPS')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.grid()
    fig_name='Collaterals_'+'days_'+str(len(df))+'.png'
    plt.savefig(graph_dir+fig_name)
    plt.close()
    '''
    return fig
def benchmark(data_dir,graph_dir):
    df_total=pd.DataFrame()
    for r,d,f in os.walk(data_dir):  
        for f_ in f:
            file_name = f_.split('.')[0]
            if 'GTBCPS' in f_:
                df = pd.read_csv(r+f_)
                cols_orig = df.columns
                for col in df.columns:
                    print(df.columns)
                    if 'date' in col.lower():
                        df['date']=pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                    else:
                        price_col = file_name+'_'+'price'
                        df[price_col]=df['ref price of GTBCPS'].astype(float)
                df = df.drop(cols_orig,axis=1)
                print(df)
            else:
                df=pd.read_csv(r+f_,delimiter=',')
                cols_orig = df.columns
                print(df.columns)
                df['date']=pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
                col = file_name+'_'+'price'
                df[col]=df['price'].astype(float)
                df = df.drop(cols_orig,axis=1)
                print(df)
            if len(df_total)==0:
                #print(f_)
                df_total=df
            else:
                print(len(df_total))
                df_total=df_total.merge(df,how='inner',on=('date'))
                print(df_total)
    df_total.to_csv(graph_dir+'total.csv')
    start_date = df_total.loc[0,'date']
    end_date = df_total.loc[len(df_total)-1,'date']
    print(df_total)
    df_value=df_total.drop('date',axis=1)
    cols = df_value.columns
    print(len(cols))
    #x = df_total['date']
    #x = np.arange(0,len(df),1)
    fig=plt.figure()
    for n in range(len(cols)):
        #print(cols_orig[n])
        col_name = cols[n]
        y = df_total[col_name]
        if 'U-' in col_name:
            col_name=col_name.split('-')[1]
        plt.plot(y,label=col_name)
    name_1 = cols[0]
    name_2 = cols[1]
    print(name_1,name_2)
    name_1=name_1.split('_')[0]
    name_2=name_2.split('_')[0]
    #plt.xlabel('Days')
    #plt.ylabel('Price')
    plt.xticks([0,int(len(df_total)/2),len(df_total)],[start_date,str(df_total.loc[int(len(df_total)/2),'date']),str(df_total.loc[len(df_total)-1,'date'])])
    plt.legend(loc='best')
    #plt.legend(bbox_to_anchor=(0.5,1.15),fontsize='small',ncol=4,loc='upper center')
    #plt.title('Prices of {} and {} \n ({} to {})'.format(name_1,name_2,start_date,end_date))
    #plt.title('Prices Comparison Between {} and {}'.format(name_1,name_2))
    fig_name='test_scenario_'+col_name+'_'+str(start_date)+'_'+str(end_date)+'.png'
    plt.savefig(graph_dir+fig_name)
    plt.close()  
    return fig
def collaterals(data_dir,graph_dir):
    df = pd.read_csv(data_dir)
    print(df.columns)
    df['date']=pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    for col in df.columns:
        if 'gold' in col.lower():
            df['gold']=df[col].astype('float')
            df =df.drop(col,axis=1)
        elif 'reit' in col.lower():
            df['reit']=df[col].astype('float')
            df =df.drop(col,axis=1)
        elif 'tb' in col.lower():
            df['tb']=df[col].astype('float')
            df =df.drop(col,axis=1)
    print(df)
    start_date = df.loc[0,'date']
    end_date = df.loc[len(df)-1,'date']
    gold = df['gold'].values
    reit = df['reit'].values
    tb = df['tb'].values

    fig,ax1=plt.subplots()
    color1 = 'tab:blue'
    x = np.arange(0,len(df),1)
    ax1.set_ylabel('Price of Treasury Bond and REIT',color=color1)
    lns1=ax1.plot( x, reit,color=color1,lw=1.2,label = 'REIT')
    ax1.tick_params(axis='y',color=color1)
    color2 = 'tab:green'
    x = np.arange(0,len(df),1)
    #ax1.set_ylabel('Price of Treasury Bond',color=color2)
    lns2=ax1.plot( x, tb,color=color2,lw=1.2,label='Treasury Bond')
    ax1.tick_params(axis='y',color=color2)
    #ax1.set_ylim(0.995,1.005)
    #ax1.set_xlabel('Days')
    ax3 = ax1.twinx()

    color3 = 'tab:red'
    ax3.set_ylabel('Price of Gold',color=color3)
    lns3=ax3.plot( x, gold,color=color3,lw=1.2,label='Gold')
    ax3.tick_params(axis='y',color=color3)
    plt.xticks([0,int(len(df)/2),len(df)],[start_date,str(df.loc[int(len(df)/2),'date']),str(df.loc[len(df)-1,'date'])])
    lns = lns1+lns2+lns3
    labels = [l.get_label() for l in lns]
    plt.legend(lns,labels,bbox_to_anchor=(0.5,1.15),fontsize='small',ncol=4,loc='upper center')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.grid()
    fig_name='Collaerals.png'
    plt.savefig(graph_dir+fig_name)
    plt.close()
    '''

    fig,ax1=plt.subplots()
    min_value_collaterals = min(value_collaterals)

    color = 'tab:red'
    x = np.arange(0,len(df),1)
    ax1.set_ylabel('Collateral Ratios',color=color)
    ax1.plot( x, collateral_ratio,color=color,lw=1.2)
    ax1.tick_params(axis='y',color=color)
    ax1.set_ylim(1,1.8)
    #ax1.set_xlabel('Days')
    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Value of Collaterals',color=color)
    ax2.fill_between( x,min_value_collaterals ,value_collaterals,color=color,alpha=0.4)
    ax2.tick_params(axis='y',color=color)
    plt.xticks([0,int(len(df)/2),len(df)],[start_date,str(df.loc[int(len(df)/2),'date']),str(df.loc[len(df)-1,'date'])])
    #plt.legend(loc='best')
    #plt.title('Collateral Ratios and Value of Collaterals of GTBCPS \n ({} to {})'.format(start_date,end_date))
    plt.title('Collateral Ratios and Value of Collaterals of GTBCPS')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.grid()
    fig_name='Collaterals_'+'days_'+str(len(df))+'.png'
    plt.savefig(graph_dir+fig_name)
    plt.close()
    '''
    return fig
def gold(data_dir,graph_dir):
    df = pd.read_csv(data_dir)
    print(df.columns)
    #df['date']=pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    for col in df.columns:
        if 'spot' in col.lower():
            df['gold_spot']=df[col].astype('float')
            df =df.drop(col,axis=1)
        elif 'predict' in col.lower():
            df['gold_prediction']=df[col].astype('float')
            df =df.drop(col,axis=1)
    print(df)
    df = df[-1000:].reset_index().drop('index',axis=1)
    start_date = df.loc[0,'date']
    end_date = df.loc[len(df)-1,'date']
    actual = df['gold_spot'].values.reshape(-1,1)
    prediction = df['gold_prediction'].values.reshape(-1,1)
    f1score = f1_score((actual*100).astype('int32'),(prediction*100).astype('int32'),average='micro')
    accuracy = accuracy_score((actual*100).astype('int32'),(prediction*100).astype('int32'))
    mse = mean_squared_error(actual,prediction)
    mae = mean_absolute_error(actual,prediction)
    with open ('result.log','a') as f:

        f.write('----------------------------------------------------\n')
        #f.write('confusion matrix={}\n'.format(cm_predict))
        #f.write('auc={}\n'.format(auc_predict))
        #f.write('pauc={}\n'.format(pauc_predict))
        #f.write('roc_auc={}\n'.format(roc_auc))
        #f.write('prc_auc={}\n'.format(prc_auc))
        #f.write('ARI={}\n'.format(ari))
        #f.write('NMI={}\n'.format(nmi))
        f.write('F Measure={}\n'.format(f1score))
        f.write('Accuracy Score={}\n'.format(accuracy))
        f.write('mse={}\n'.format(mse))
        f.write('mae={}\n'.format(mae))
        f.close()
    fig=plt.figure()
    '''
    x = np.arange(0,len(df),1)
    print(actual)
    plt.plot( x,actual,label = 'Actual Gold Price')
    plt.plot( x,prediction,label='Predicted Gold Price')
    plt.xticks([0,int(len(df)/2),len(df)],[start_date,str(df.loc[int(len(df)/2),'date']),str(df.loc[len(df)-1,'date'])])
    plt.legend(loc='best')
    fig_name='Gold.png'
    plt.savefig(graph_dir+fig_name)
    plt.close()
    '''
    return fig
if __name__=='__main__':
    #fig = performance(perforamance_dir,graph_dir)
    fig = benchmark(benchmark_dir,graph_dir)
    #fig = collaterals(collateral_dir,graph_dir)
    #fig = gold(gold_dir,graph_dir)