# file for main user interface
import streamlit as st
import pandas as pd
from supabase import create_client,Client
import os
from mar_math import generate_md
from score import calc_sp, evaluate

url: str=st.secrets['supabase_url']
key: str=st.secrets['supabase_key']
supabase: Client=create_client(url,key)

st.title("Herding Bias Simulator")
st.subheader("Rules: ")
st.write("1. 100 points awarded for not following the herd",
"\n2. 100 deducted for following the herd",
"\n3. 50 points awarded for resisting the herd",
"\n4. 25 points awarded for no action taken whatsoever"
"\n5. The player scores are displayed at the sidebar(top left corner)"
"\n6. The simulation runs for exactly 199 days")

if 'today' not in st.session_state:
    st.session_state.today=1
if 'pscore' not in st.session_state:
    st.session_state.pscore=0
if 'mp' not in st.session_state:
    st.session_state.mp=generate_md()
if 'balance' not in st.session_state:
    st.session_state.balance=4970000
if 'stocks' not in st.session_state:
    st.session_state.stocks=0
if 'show' not in st.session_state:
    st.session_state.show=False
if 'history' not in st.session_state:
    st.session_state.history=[]


st.sidebar.title("Player Details")
st.sidebar.metric(label='Balance', value=st.session_state.balance)
st.sidebar.metric(label='Shares',value=st.session_state.stocks)
st.sidebar.metric(label="Points Scored",value=st.session_state.pscore)
# variable to store trading logs
with st.sidebar.expander('Trade History'):
    if len(st.session_state.history)==0:
        st.write("no moves yet made")
    else:
        for i in reversed(st.session_state.history):
            st.write(i)

if st.session_state.show==True:
    st.subheader("Stock Fundamentals")
    st.write("Welcome investor! Below are the details of the asset you are trading.")
    c1,c2,c3=st.columns(3)
    c1.metric(label='Price-to-Earnings',value='23',delta='+1.4')
    c2.metric(label='Sector Rating', value='Outperform')
    c3.metric(label='Institutional Holdings',value='45%')
    if st.button('back to dashboard'):
        st.session_state.show=False
        st.rerun()

else:
    st.subheader("Latest Market Updates")
    vr=st.session_state.mp[st.session_state.mp['day']==st.session_state.today]
    vtv=vr['true value'].values[0]
    vmv=vr['market value'].values[0]
    csp=calc_sp(vtv,vmv)

    if csp>0.20:
        st.error("Breaking: Don't miss out on these historic gains!!!")
    elif csp<-0.10:
        st.warning("Sharp drop in prices")
    else:
        st.info('Market Stable; Normal Volumes')

    if st.button("click to know more"):
        st.session_state.show=True
        st.rerun()
    
    st.subheader('Market Trend')
    curr=st.session_state.mp[st.session_state.mp['day']<=st.session_state.today]
    st.line_chart(data=curr,x='day',y=['true value','market value'])

    if st.session_state.today<198:

        t1,sp,t2,sp,t3=st.columns([1,3,1,3,1])
        # buttons for buy, sell, and hold
        with t1:
            b=st.button("Buy")
        with t2:
            h=st.button("Hold")
        with t3:
            s=st.button("Sell")

        if b or h or s:
            c_row=st.session_state.mp[st.session_state.mp['day']==st.session_state.today]
            tv=c_row['true value'].values[0]
            mv=c_row['market value'].values[0]
            spread=calc_sp(tv,mv)
            move=""
            valid=True
            # execute buy, check for sufficient funds
            if b:
                if st.session_state.balance>=mv:
                    move="Buy"
                    st.session_state.balance=st.session_state.balance-mv
                    st.session_state.stocks=st.session_state.stocks+1
                else:
                    st.warning("insufficient funds")
                    valid=False
            # execute sell, prevent short-selling
            elif s:
                if st.session_state.stocks>0:

                    move="Sell"
                    st.session_state.balance=st.session_state.balance+mv
                    st.session_state.stocks=st.session_state.stocks-1
                else:
                    st.warning("Cannot do short-selling. You have 0 shares to sell.")
                    valid=False
            elif h:
                move="Hold"
            # if trade was valid, calculate behavioral points and advance the day
            if valid==True:
                points=evaluate(move,spread)
                st.session_state.history.append(f'day {st.session_state.today}: {move} at ₹{mv}')
                st.session_state.pscore=st.session_state.pscore+points
                if st.session_state.today<199:
                    st.session_state.today=st.session_state.today+1
                st.rerun()

    else:
        st.header("simulation complete")
        fmv=st.session_state.mp[st.session_state.mp['day']==199]['market value'].values[0]
        fpv=st.session_state.balance+(st.session_state.stocks*fmv)
        st.success(f"Final Behavioral Score: {st.session_state.pscore} points")
        if st.session_state.pscore>7000:
            st.balloons()
            st.write("Congratulations!! You have successfully resisted the herd mentality!")
        else:
            st.write("The herd got you!! Try again to see if you can resist it this time.")

    # game over window
    st.header('Game Over!')
    st.subheader(f'Final Score: {st.session_state.pscore} points')
    with st.form('score form'):
        player=st.text_input('enter your name: ',max_chars=15)
        submit=st.form_submit_button('submit to global leaderboard')

        if submit and player:
            news={
                'name':player.upper(),
                'score':st.session_state.pscore
            }
            supabase.table('Leaderboard').insert(news).execute()
            st.success('score saved')

    st.header('Global Leaderboard')
    response=supabase.table("Leaderboard").select("*").order('score',desc=True).limit(10).execute()
    if len(response.data)>0:
        lead_df=pd.DataFrame(response.data)
        lead_df=lead_df[['name','score']]
        lead_df.columns=['player','score']
        st.dataframe(lead_df,hide_index=True,use_container_width=True)
    else:
        st.info("no scores yet; Be the first on the board!!")
    
    bt1,space,bt2=st.columns([1,5,1])
    with bt1:
        if st.button('start game'):
            pass
    with bt2:
        if st.button('reset game'):
            for k in st.session_state.keys():
                del st.session_state[k]
            st.rerun()