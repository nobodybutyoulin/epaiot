import pandas as pd
import numpy as np
#import statistics
import datetime

def custAvg(arrayLike):
    #convert str to float
    arrayLike = pd.to_numeric(arrayLike)
    print('len of arrayLike', len(arrayLike))
    return np.sum(arrayLike)/len(arrayLike)

# 根據輸入參數timeSpecStr的要求, dataframe df中的colSrcStr欄位,
# 進行平均值計算
# Calculate the stdev for a group of device
# input (1) df with '裝置名稱', '時間', column where the stdev to be calculate
#       (2) column name str where the stdev to be calculate
# return df with 'indexInDev', '裝置名稱', '時間', colSrcStr(where store the result)
def calDevAvg(df, colSrcStr, timeSpecStr):
    print("In func calDevAvg, timeSpecStr is ....", timeSpecStr)
    
    df.loc[:,colSrcStr] = pd.to_numeric(df.loc[:,colSrcStr], downcast="float")

    dfResult=pd.DataFrame()
    
    #iterate for all dev, extract all rec from df and resample it 
    #先篩出同一device的所有資料列, 再對此組資料列依據timeSpecStr做resample
    uniqueLst = df.loc[:,'裝置名稱'].unique()
    for i, item in enumerate(uniqueLst):
        mask = (df.loc[:,'裝置名稱']==item)
        dfGrpRow = df.loc[mask, :]
        
        dfAvg=dfGrpRow.resample(timeSpecStr, on='時間', closed='left', label='left')[colSrcStr].apply(np.mean).reset_index() #resampled values are stored in dfAvg
        dfAvg.insert(0, column='裝置名稱', value = item)

        dfResult=pd.concat([dfResult, dfAvg]) 
    dfResult.reset_index(inplace=True)
    dfResult.rename(columns={'index':'indexInDev'}, inplace=True)
 
    return dfResult

# 計算輸入的dataframe dfAvg中的指定欄位colSrcStr的值的標準差
# 會自動排除nan的欄位
# Calculate time-based stddev
# input dev avg vlaue based on required timespec
# input parameter: df with 'indexInDev', '裝置名稱', '時間', colSrcStr
# return '時間', 'stdev'
def calAreaStdev(dfAvg, colSrcStr):
    print("In func calAreaStdev......")
    dfResult = pd.DataFrame(columns=['時間','stdev'])
    
    #findout unique time ref base and loop for each time ref to calculate whole area stdev
    dfTimeSpec = dfAvg.drop_duplicates(subset='時間')
    dfTimeSpec.reset_index(inplace=True)  #the last entry index is high
    
    #loop 所有時間, 取此時間內的所有dev測值做平均
    for i in dfTimeSpec.index:
        mask = dfAvg.loc[:, '時間']==dfTimeSpec.loc[i, '時間']
        
        alist= dfAvg.loc[mask,colSrcStr].to_list()

        astdev=np.nanstd(alist, ddof=len(alist)/2) #ddof: delta degree of freedom, 允許可排除的Ｎan值得數量

        dfResult.loc[len(dfResult.index)]=[dfTimeSpec.loc[i,'時間'], astdev]

    dfResult.to_html('log/area1Stdev.html')
    return dfResult

# Calculate time-based area avg
# 
# input (1) df with '裝置名稱', '時間', column where the stdev to be calculate
#       (2) column name str where the stdev to be calculate
#
# return '時間', 'avg'
def calAreaAvg(df, colSrcStr, timeSpecStr):
    print("In func calAreaAvg, timeSpecStr is.....", timeSpecStr)
    
    dfDevAvg = calDevAvg(df, colSrcStr, timeSpecStr) # resample the data according to timespec
    dfResult = pd.DataFrame(columns=['時間','avg'])
    
    #findout unique time ref base and loop for each time ref to calculate whole area stdev
    dfTimeSpec = dfDevAvg.drop_duplicates(subset='時間')
    dfTimeSpec.reset_index(inplace=True)
    
    for i in dfTimeSpec.index:
        mask = dfDevAvg['時間']==dfTimeSpec.loc[i,'時間']
        
        dfDevAvg.loc[mask,colSrcStr]= pd.to_numeric(dfDevAvg.loc[mask,colSrcStr], downcast="float")
        alist= dfDevAvg.loc[mask, colSrcStr].to_list()

        aAvg=np.nanmean(alist) # nan欄會被排除的平均值算法

        dfResult.loc[len(dfResult.index)]=[dfTimeSpec.iloc[i].at['時間'], aAvg]

    dfResult.to_html('log/area1Avg.html')
    return dfResult
