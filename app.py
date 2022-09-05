import streamlit as st
# st.title('Hello World!!')
# st.markdown('# My first Streamlit Dashboard')
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

#data_url=(
#"https://github.com/chairielazizi/streamlit-collision/blob/master/Motor_Vehicle_Collisions_-_Crashes.csv?raw=true"
#)
df=('D:\Self_project\Car_Collision_project\Motor_Vehicle_Collisions_-_Crashes_updated.csv')

#df.rename(columns={'CRASH DATE':'CRASH_DATE', 'CRASH TIME':'CRASH_TIME','NUMBER OF PERSONS INJURED':'NUMBER_OF_PERSONS_INJURED' }, inplace = True)

st.title("Motor Vehicle Collisions in NYC")
st.markdown('#### This application is a Streamlit Dashboard that can be used '
'to analyse 🏎️ motor vehicle collision in NYC 🗽 💥')

@st.cache(persist=True)
def load_data(nrows):
    data=pd.read_csv(df,nrows=nrows, parse_dates=[['CRASH DATE','CRASH TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    data.columns = data.columns.str.replace(' ','_')
    lowercase=lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data

data=load_data(100000)
original_data=data

st.header("Where are the most people injured in NYC?")
injured_people=st.slider("Number of persons injured in vechicle collision",0,19)
st.map(data.query('number_of_persons_injured >= @injured_people')[['latitude','longitude']].dropna(how='any'))

st.header('How many collision occur during a given time of day?')
hour=st.slider('Hour to look at',0,23)
data=data[data['date/time'].dt.hour==hour]

st.markdown('Vehicle collisions between %i:00 and %i:00'%(hour,(hour+1)%24))
midpoint=(np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        'latitude':midpoint[0],
        'longitude':midpoint[1],
        'zoom':11,
        "pitch":50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time','latitude','longitude']],
        get_position=['longitude','latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0,1000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00' %(hour,(hour+1)%24))
filtered=data[
(data['date/time'].dt.hour>=hour)& (data['date/time'].dt.hour<(hour+1))
]
hist=np.histogram(filtered['date/time'].dt.minute,bins=60, range=(0,60))[0]
chart_data=pd.DataFrame({'minute':range(60),'crashes':hist})
fig=px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=300)
st.write(fig)

st.header('Top 5 Dangerous streets by affected type: ')
select=st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])

if select=='Pedestrians':
    st.write(original_data.query('number_of_pedestrians_injured >=1')[['on_street_name','number_of_pedestrians_injured']].sort_values(by=['number_of_pedestrians_injured'],ascending=False).dropna(how='any')[:5])

elif select=='Cyclists':
    st.write(original_data.query('number_of_cyclist_injured >=1')[['on_street_name','number_of_cyclist_injured']].sort_values(by=['number_of_cyclist_injured'],ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query('number_of_motorist_injured >=1')[['on_street_name','number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'],ascending=False).dropna(how='any')[:5])


if st.checkbox('Show Raw Data',False):
    st.subheader('Raw Data')
    st.write(data)
