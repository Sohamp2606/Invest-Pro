


from django.shortcuts import render
from .models import tickerslist
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


import datetime as dt
from datetime import timedelta
import yfinance as yf

from keras.layers import Dense, Dropout, LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler


# Create your views here.

def home(request):
    
    return render(request,'home.html')

def choseticker(request):

    mydata = tickerslist.objects.all().values()
    context = {'tikers' : mydata}
    
    return render(request,"tickers.html",context)


def livechart(request,ticker):

    # geting data 
    N_DAYS_AGO = 500
    end_date = dt.datetime.now()
    start_date = end_date -timedelta(days=N_DAYS_AGO)
    gdata = yf.download(ticker, start = start_date, end = end_date)
    gdata=pd.DataFrame(gdata)
    gdata=gdata.reset_index()
    df=gdata[-100:]
    
    # ploting chart
    fig = px.line(
    labels={'x':'Date','y':'Price'},
    )
    fig.add_scatter(x=df['Date'], y=df['Close'],name='Close')
    fig.add_scatter(x=df['Date'], y=df['Open'],name='Open')
    fig.update_layout(showlegend=True)

    # render to html page
    chart = fig.to_html()
    context = {'chart':chart,'ticker':ticker}    
    return render(request,"livechart.html",context)

def analysischart(request,ticker):

    # initialize time parameters
    start_date = dt.datetime(2022, 1, 1)
    end_date = dt.datetime.now()
    
    
    # get the data
    df = yf.download(ticker, start = start_date, end = end_date)
    df=df.reset_index()

    df['target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['name'] = np.where(df['target']==1, 'safe', 'risk')

    labels = ['risk','safe']
    values = df['target'].value_counts().values.tolist()
    colors = ['#1e3bb3','#15cdca']

    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=values,))
    fig.update_traces(hoverinfo='label+percent',textinfo='percent+label', textfont_size=20,
                    marker=dict(colors=colors,))
    
    chart = fig.to_html()
    context = {'chart':chart,'ticker':ticker}

    return render(request,"analysischart.html",context)

def predictionchart(request,ticker):
    
    # get the data
    start_date = dt.datetime(2020, 1, 1)
    end_date = dt.datetime(2022, 1, 1)
    data = yf.download(ticker, start = start_date, end = end_date)
     
    # prepare data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1,1))
    
    # how many days look behind for prediction
    prediction_days = 60 
    x_train = []
    y_train = []
    for x in range(prediction_days,len(scaled_data)):
        x_train.append(scaled_data[x-prediction_days:x,0])
        y_train.append(scaled_data[x,0])
    x_train,y_train = np.array(x_train),np.array(y_train)
    x_train = np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))

    # build a model
    model = Sequential()

    model.add(LSTM(units=50,return_sequences = True,input_shape=(x_train.shape[1],1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50,return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer='adam',loss='mean_squared_error')
    model.fit(x_train,y_train,epochs=25,batch_size=32)

    # test the model accuracy on existing data

    # load test data
    test_start = dt.datetime(2022,1,2)
    test_end = dt.datetime.now()
    test_data = yf.download(ticker, start = test_start, end = test_end)
    actual_price = test_data['Close'].values

    total_dataset = pd.concat((data['Close'],test_data['Close']),axis =0)
    model_inputs = total_dataset[len(total_dataset)-len(test_data)-prediction_days:].values
    model_inputs = model_inputs.reshape(-1,1)
    model_inputs = scaler.transform(model_inputs)
    
    x_test = []
    for x in range(prediction_days, len(model_inputs)):
        x_test.append(model_inputs[x-prediction_days:x,0])
            
    x_test = np.array(x_test)
    x_test = np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))
       
    predicted_prices = model.predict(x_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)
    predicted_prices = predicted_prices.tolist()
    predicted_price = [i[0] for i in predicted_prices]

    # predicting next day price
    global today
    global tomorrow
    today = actual_price[-1]
    real_data = [model_inputs[len(model_inputs)+1-prediction_days:len(model_inputs+1),0]]
    real_data = np.array(real_data)
    real_data = np.reshape(real_data,(real_data.shape[0],real_data.shape[1],1))
    tomorrow = model.predict(real_data)
    tomorrow = scaler.inverse_transform(tomorrow)
    tomorrow = tomorrow[0][0]
    today = round(today,2)
    tomorrow = round(tomorrow,2)
    
    
    # ploting chart
    fig = px.line(
    labels={'x':'Day','y':'Prices'},
    )
    fig.add_scatter(y=actual_price,name='Actual price')
    fig.add_scatter(y=predicted_price,name='Predicted price')
    fig.update_layout(showlegend=True)

    # render to html page
    chart = fig.to_html()
    context = {'chart':chart,'ticker':ticker}
    return render(request,"predictionchart.html",context)

def nextday(request,ticker):

    context={"today":today,"nextday":tomorrow}
    return render(request,"nextday.html",context)

def searchticker(request,slug):
    context ={'ticker':slug}
    return render(request,"getticker.html",context)

# demo function for testing 
def test(request,ticker):
    return render(request,"demo.html")

