import numpy as np
import pandas as pd
from FL_BRNN import brnn, imputation
import Config
from Config import fl_config
from FL_BRNN import predict
import random
config = fl_config()
def dataSplit(orig,timeSequence,opt):
    '''
    x_train = np.array(x[-start:-start+trainSize])
    y_train = np.array(y[-start:-start+trainSize])
    x_test = np.array(x[-start+trainSize:-start+trainSize+testSize])
    y_test = np.array(y[-start+trainSize:-start+trainSize+testSize])
    y_actual = np.array(y[-start+trainSize+predictSize:-start+trainSize+testSize+predictSize])
    '''
    print(len(orig))
    #mask = datamask(orig)
    cols_orig = orig.columns
    mask=orig
    print(mask)
    #df_imts = pd.DataFrame()
    df_imts=mask.replace(0,-1)
    #df_imts=orig.replace(0,-1)
    '''
    for col in df_imts.columns:
        df_imts =df_imts[df_imts[col]!=-1 ]
    '''
    trainSize = config.trainSize
    testSize = config.testSize
    predictSize = config.predictSize

    totalSize = trainSize+testSize+predictSize

    totalSize = trainSize+testSize+predictSize
    start = random.randint(totalSize+1,len(orig)-1)
    print('---------------------------------imts is ------------------------------')
    print(df_imts)
    #df_imts = df_imts.drop(('index'),axis=1)
    x = df_imts[-start-1:-1]
    y = df_imts[-start:]
    y_orig = orig[-start:]
    #x = x.reset_index()
    #y = y.reset_index()
    y_orig.to_csv('orig.csv')

    #print(len(total))
    print(x.columns)
    '''
    x_imputation = imputation(x,imputationd_value=-1)
    y_imputation = imputation(y,imputationd_value=-1)
    x_train = np.array(x_imputation[:trainSize]).astype(np.float32)
    y_train = np.array(y_imputation[:trainSize]).astype(np.float32)
    x_test = np.array(x_imputation[trainSize:trainSize+testSize]).astype(np.float32)
    y_test = np.array(y_imputation[trainSize:trainSize+testSize]).astype(np.float32)
    y_actual = np.array(y[trainSize+testSize:trainSize+testSize+predictSize]).astype(np.float32)
    x= np.array(x)
    y= np.array(y)
    '''
    
    x_train,y_train,x_test,y_test,x_imputation,df_imputation=imputation.brnn_imputation(x,y,start,timeSequence,opt,cols_orig)
    y_actual = np.array(y_orig[trainSize+testSize:trainSize+testSize+predictSize]).astype(np.float32)
    print('-----------------------------------y_actual is-----------------------------')
    print(y_actual)
    #y_actual = scaler_y.transform(y_actual)

    #print(len(x_total))
    #print(len(y_total))

   

    
    print(len(x),len(y),len(x_train),len(y_train),len(x_test),len(y_test),len(y_actual))
    #print(x_train,y_train,x_test,y_test,y_actual)
    
    #print(y_train)
    #x_actual = np.array(x[-start+trainSize+testSize-predictSize:-start+trainSize+testSize+predictSize]
    #x_train,x_test,y_train,y_test = train_test_split(x_,y_,test_size=0.2,shuffle=True)

    return  x,y,x_imputation,x_train,y_train,x_test,y_test,y_actual,start,cols_orig,df_imputation
def datamask(data):
    count = 0
    data = data.reset_index()
    for col in data.columns:
        y_mask = np.random.rand(len(data))  < 0.25
        print(y_mask)
        for i in range(len(data)):
            if y_mask[i] == True:
                data.loc[i,col] = -1
                count +=1
            i+=1
    data = data.drop(('index'),axis=1)
    print(data)
    return data