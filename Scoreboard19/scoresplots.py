"""Functions for plotting data."""

import scipy.interpolate
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.pylab as pl
import matplotlib.dates as mdates
from .scores import *
import os

def plotdifferencescdfpdf(Scoreboard):
    plt.figure(figsize=(4, 2.5), dpi=180, facecolor='w', edgecolor='k')
    plt.hist(Scoreboard['prange']-Scoreboard['sumpdf'],bins=50)
    plt.xlabel("Difference between integrated pdf and given cdf")
    plt.title('COVID-19 Deaths')
    print('===========================')
    print('Maximum % conversion error:')
    print(100*max(Scoreboard['prange']-Scoreboard['sumpdf']))

def plotUSCumDeaths(US_deaths) -> None:
    plt.figure(figsize=(4, 2.5), dpi=180, facecolor='w', edgecolor='k')
    plt.plot(US_deaths.DateObserved,US_deaths.Deaths)
    plt.xticks(rotation=45)
    plt.title('US Cumulative Deaths')
    plt.ylabel('Deaths')
    
def plotUSIncCases(US_cases) -> None:
    plt.figure(figsize=(4, 2.5), dpi=180, facecolor='w', edgecolor='k')
    plt.plot(US_cases.DateObserved,US_cases.Cases)
    plt.xticks(rotation=45)
    plt.title('US Weekly Incidental Cases')
    plt.ylabel('Cases')    

def perdelta(start, end, delta):
    """Generate a list of datetimes in an 
    interval for plotting purposes (date labeling)
    Args:
        start (date): Start date.
        end (date): End date.
        delta (date): Variable date as interval.
    Yields:
        Bunch of dates 
    """    
    
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def plotallscoresdist(Scoreboard,figuresdirectory,model_target) -> None:
    
    model_targets = ['Case', 'Death']
    if model_target not in model_targets:
        raise ValueError("Invalid sim type. Expected one of: %s" % model_targets)  
        
    if model_target == 'Case':
        filelabel = 'INCCASE'
        titlelabel= 'Weekly Incidental Cases'
    elif model_target == 'Death':
        filelabel = 'CUMDEATH'
        titlelabel= 'Cumulative Deaths'
        
    fig = plt.figure(num=None, figsize=(8, 8), dpi=300, facecolor='w', edgecolor='k')
    Scoreboard.plot.scatter(x='delta', y='score', marker='.')
    plt.xlabel('N-Days Forward Forecast')
    plt.title(titlelabel + ' Forecasts')
    plt.savefig(figuresdirectory+'/'+filelabel+'_'+'ScoreVSx-Days_Forward_Forecast.png',
                bbox_inches = 'tight',
                dpi=300)
    plt.show(fig)

    fig = plt.figure(num=None, figsize=(8, 8), dpi=300, facecolor='w', edgecolor='k')
    Scoreboard.plot.scatter(x='deltaW', y='score', marker='.')
    plt.xlabel('N-Weeks Forward Forecast')
    plt.title(titlelabel + ' Forecasts')
    plt.savefig(figuresdirectory+'/'+filelabel+'_'+'ScoreVSx-Weeks_Forward_Forecast.png', 
                bbox_inches = 'tight',
                dpi=300)
    plt.show(fig)
    
    fig = plt.figure(figsize=(8, 4), dpi=300, facecolor='w', edgecolor='k')
    binwidth = 1
    Scoreboard.delta.hist(bins=range(min(Scoreboard.delta), max(Scoreboard.delta) + binwidth, binwidth))
    #plt.xlim(4, 124)
    plt.title(titlelabel + ' Forecasts')
    plt.xlabel('N-Days Forward Forecast')
    plt.ylabel('Number of forecasts made')   
    plt.xticks(np.arange(min(Scoreboard.delta), max(Scoreboard.delta)+1, 2.0))
    plt.xticks(rotation=90)
    plt.grid(b=None)
    plt.savefig(figuresdirectory+'/'+filelabel+'_x-Days_Forward_Forecast_Hist.png', 
                bbox_inches = 'tight',
                dpi=300)
    plt.show(fig)

    fig = plt.figure(figsize=(8, 4), dpi=300, facecolor='w', edgecolor='k')
    Scoreboard.deltaW.hist(bins=range(1, 20 + binwidth, binwidth))
    #plt.xlim(0, 22)
    plt.title(titlelabel + ' Forecasts')
    plt.xlabel('N-Weeks Forward Forecast')
    plt.ylabel('Number of forecasts made')
    plt.xticks(np.arange(min(Scoreboard.deltaW), max(Scoreboard.deltaW)+1, 1.0))
    plt.xticks(rotation=90)
    plt.grid(b=None)
    plt.savefig(figuresdirectory+'/'+filelabel+'_x-Weeks_Forward_Forecast_Hist.png', 
                bbox_inches = 'tight',
                dpi=300)
    plt.show(fig)
        
def plotlongitudinal(Actual,Scoreboard,scoretype,WeeksAhead,curmod) -> None:
    """Plots select model predictions against actual data longitudinally
    Args:
        Actual (pd.DataFrame): The actual data
        Scoreboard (pd.DataFrame): The scoreboard dataframe
        scoretype (str): "Cases" or "Deaths"
        WeeksAhead (int): Forecasts from how many weeks ahead
        curmod (str): Name of the model whose forecast will be shown
    Returns:
        None 
    """    
    
    Scoreboardx = Scoreboard[Scoreboard['deltaW']==WeeksAhead].copy()
    Scoreboardx.sort_values('target_end_date',inplace=True)
    Scoreboardx.reset_index(inplace=True)  
    plt.figure(num=None, figsize=(14, 8), dpi=80, facecolor='w', edgecolor='k')
    models = Scoreboardx['model'].unique()
    colors = pl.cm.jet(np.linspace(0,1,len(models)))
    i = 0

    dates = Scoreboardx[Scoreboardx['model']==curmod].target_end_date
    PE = Scoreboardx[Scoreboardx['model']==curmod].PE
    CIlow = Scoreboardx[Scoreboardx['model']==curmod].CILO
    CIhi = Scoreboardx[Scoreboardx['model']==curmod].CIHI

    modcol = (colors[i].tolist()[0],
              colors[i].tolist()[1],
              colors[i].tolist()[2])

    plt.plot(dates,PE,color=modcol,label=curmod)
    plt.fill_between(dates, CIlow, CIhi, color=modcol, alpha=.1)

    plt.plot(Actual['DateObserved'],Actual[scoretype],color='k',linewidth=3.0)    
    plt.ylim([(Actual[scoretype].min())*0.6, (Actual[scoretype].max())*1.4])
    plt.ylabel('US Cumulative '+scoretype, fontsize=18)
    plt.xlabel('Date', fontsize=18)
    plt.xticks(rotation=45, fontsize=13)
    plt.yticks(fontsize=13)
    plt.fmt_xdata = mdates.DateFormatter('%m-%d')
    plt.title(curmod+': '+str(WeeksAhead)+'-week-ahead Forecasts')
    

def plotlongitudinalALL(Actual,Scoreboard,scoretype,WeeksAhead) -> None:
    """Plots all predictions against actual data longitudinally
    Args:
        Actual (pd.DataFrame): The actual data
        Scoreboard (pd.DataFrame): The scoreboard dataframe
        scoretype (str): "Cases" or "Deaths"
        WeeksAhead (int): Forecasts from how many weeks ahead
    Returns:
        None 
    """    
    
    Scoreboardx = Scoreboard[Scoreboard['deltaW']==WeeksAhead].copy()
    Scoreboardx.sort_values('target_end_date',inplace=True)
    Scoreboardx.reset_index(inplace=True)  
    plt.figure(num=None, figsize=(14, 8), dpi=80, facecolor='w', edgecolor='k')
    models = Scoreboardx['model'].unique()
    colors = pl.cm.jet(np.linspace(0,1,len(models)))
    i = 0
    for curmod in models:

        dates = Scoreboardx[Scoreboardx['model']==curmod].target_end_date
        PE = Scoreboardx[Scoreboardx['model']==curmod].PE
        CIlow = Scoreboardx[Scoreboardx['model']==curmod].CILO
        CIhi = Scoreboardx[Scoreboardx['model']==curmod].CIHI

        modcol = (colors[i].tolist()[0],
                  colors[i].tolist()[1],
                  colors[i].tolist()[2])

        plt.plot(dates,PE,color=modcol,label=curmod)
        plt.fill_between(dates, CIlow, CIhi, color=modcol, alpha=.1)
        i = i+1

    plt.plot(Actual['DateObserved'],Actual[scoretype],color='k',linewidth=3.0)    
    plt.ylim([(Actual[scoretype].min())*0.6, (Actual[scoretype].max())*1.4])
    plt.ylabel('US Cumulative '+scoretype, fontsize=18)
    plt.xlabel('Date', fontsize=18)
    plt.xticks(rotation=45, fontsize=13)
    plt.yticks(fontsize=13)
    plt.fmt_xdata = mdates.DateFormatter('%m-%d')
    plt.title(str(WeeksAhead)+'-week-ahead Forecasts')        

def plotgroupsTD(Scoreboard, modeltypes, figuresdirectory, model_target) -> None:
    """Generates modeltype-based score plots in time (Forecast Date)
    Args:
        Scoreboard (pd.DataFrame): Scoreboard
        modeltypes (pd.DataFrame): End date.
        figuresdirectory (str): Directory to save in
        model_target (str): 'Case' or 'Death'
    Returns:
        None 
    """        
    
    model_targets = ['Case', 'Death']
    if model_target not in model_targets:
        raise ValueError("Invalid sim type. Expected one of: %s" % model_targets)  

    if model_target == 'Case':
        filelabel = 'INCCASE'
        titlelabel= 'weekly incidental cases'
    elif model_target == 'Death':
        filelabel = 'CUMDEATH'
        titlelabel= 'cumulative deaths'        
    
    (MerdfPRED,pivMerdfPRED) = givePivotScoreTARGET(Scoreboard,modeltypes)
    
    dateticks = list(perdelta(pivMerdfPRED.index[0] - timedelta(days=14), 
                              pivMerdfPRED.index[-1] + timedelta(days=14), 
                              timedelta(days=7)))
    selectmodels = modeltypes['modeltype'].unique().tolist()
    for selectmodel in selectmodels:
        listmods = modeltypes[modeltypes['modeltype']==selectmodel].model.tolist()
        colors = pl.cm.jet(np.linspace(0,1,len(listmods)))
        plt.figure(figsize=(12, 6), dpi=180, facecolor='w', edgecolor='k')
        
        for i in range(len(listmods)):
            if listmods[i] in pivMerdfPRED.columns:
                if ~pivMerdfPRED[listmods[i]].isnull().all():                
                    pivMerdfPRED[listmods[i]].dropna().plot(color=(colors[i].tolist()[0],
                                                      colors[i].tolist()[1],
                                                      colors[i].tolist()[2]),
                                              marker='o')

        plt.legend(loc=(1.04,0),labelspacing=.9)
        plt.title(selectmodel+' models: Average Forward Scores')
        plt.ylabel('Time-averaged score for ' + titlelabel)
        plt.xlabel('Target End Date')
        plt.ylim([pivMerdfPRED.min().min()-1, pivMerdfPRED.max().max()+1])
        plt.xlim([dateticks[0],dateticks[-1]])
        custom_tick_labels = map(lambda x: x.strftime('%b %d'), dateticks)
        plt.xticks(dateticks,custom_tick_labels)
        plt.xticks(rotation=45)
        plt.savefig(figuresdirectory+'/'+filelabel+'_Average_Forward_Scores_'+selectmodel+'models.png',
                    dpi=300,bbox_inches = 'tight')
    
        
def plotgroupsFD(Scoreboard: pd.DataFrame, modeltypes: pd.DataFrame, 
               figuresdirectory: str, numweeks: int, model_target: str) -> None:
    """Generates modeltype-based score plots in time (Forecast Date)
    Args:
        pivMerdfPRED (pd.DataFrame): Start date.
        modeltypes (pd.DataFrame): model types
        figuresdirectory (str): direcotry to save in
        numweeks (int): number of weeks ahead forecast
        model_target (str): 'Case' or 'Death'
    Returns:
        None 
    """    

    model_targets = ['Case', 'Death']
    if model_target not in model_targets:
        raise ValueError("Invalid sim type. Expected one of: %s" % model_targets)  

    if model_target == 'Case':
        filelabel = 'INCCASE'
        titlelabel= 'weekly incidental cases'
    elif model_target == 'Death':
        filelabel = 'CUMDEATH'
        titlelabel= 'cumulative deaths'       
    
    Scoreboardx = Scoreboard[Scoreboard['deltaW']==numweeks].copy()
    (MerdfPRED,pivMerdfPRED) = givePivotScoreFORECAST(Scoreboardx,modeltypes)
    
    dateticks = list(perdelta(pivMerdfPRED.index[0] - timedelta(days=14), 
                              pivMerdfPRED.index[-1] + timedelta(days=14), 
                              timedelta(days=7)))
    selectmodels = modeltypes['modeltype'].unique().tolist()
    for selectmodel in selectmodels:
        listmods = modeltypes[modeltypes['modeltype']==selectmodel].model.tolist()
        colors = pl.cm.jet(np.linspace(0,1,len(listmods)))
        plt.figure(figsize=(12, 6), dpi=180, facecolor='w', edgecolor='k')
        
        for i in range(len(listmods)):
            if listmods[i] in pivMerdfPRED.columns:
                if ~pivMerdfPRED[listmods[i]].isnull().all():                
                    pivMerdfPRED[listmods[i]].dropna().plot(color=(colors[i].tolist()[0],
                                                      colors[i].tolist()[1],
                                                      colors[i].tolist()[2]),
                                              marker='o')

        plt.legend(loc=(1.04,0),labelspacing=.9)
        plt.title(selectmodel+' models: '+ str(numweeks) +' wk ahead Scores')
            
        plt.ylabel('Score for '+str(numweeks)+' wk ahead '+titlelabel)
        plt.xlabel('Forecast Date')
        plt.ylim([pivMerdfPRED.min().min()-1, pivMerdfPRED.max().max()+1])
        plt.xlim([dateticks[0],dateticks[-1]])
        custom_tick_labels = map(lambda x: x.strftime('%b %d'), dateticks)
        plt.xticks(dateticks,custom_tick_labels)
        plt.xticks(rotation=45)
        plt.savefig(figuresdirectory+'/'+str(numweeks)+'Week/'+filelabel+'_Forward_Scores_'+selectmodel+'models.png',
                    dpi=300,
                   bbox_inches = 'tight')        
        
        
def plotscoresvstimeW(Scoreboard,Weeks):
    plt.figure()
    rslt_df = Scoreboard.loc[Scoreboard['deltaW'] == Weeks] 
    df = rslt_df.pivot(index='forecast_date', columns='model', values='score')
    df = df.astype(float)

    plt.figure(figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')

    for i in range(len(df.columns)):
        df[df.columns[i]].dropna().interpolate(method='polynomial', order=2).plot(kind='line',marker='o')

    plt.legend(loc=(1.04,0))
    plt.title(str(Weeks)+'-Week Forward Scores')
    plt.ylabel('Score for N wk ahead incident cases')
    plt.xlabel('Date Forecast Made')        
    
    
def plotscoresvstime(Scoreboard,Days):
    plt.figure()
    rslt_df = Scoreboard.loc[Scoreboard['delta'] == Days] 
    df = rslt_df.pivot(index='forecast_date', columns='model', values='score')
    df = df.astype(float)

    plt.figure(figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')

    for i in range(len(df.columns)):
        df[df.columns[i]].dropna().interpolate(method='linear').plot(kind='line',marker='o')

    plt.legend(loc=(1.04,0))
    plt.title(str(Days)+'-Day Forward Scores')
    plt.ylabel('Score for N wk ahead incident cases')
    plt.xlabel('Date Forecast Made')    