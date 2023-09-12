import streamlit as st
import recommender 

rec = recommender.Recommender()

def show_recommend_page():
    

    st.title("Korean dramas recommender")

    st.write("""### It works based on data from MyDramaList, input name of your account and other optional data to begin. """)
    user = st.text_input('Name of your account',help = "The one that is in the url of your account, for example XXX in mydramalist.com/profile/XXX")

    st.write("""Recommendations can be created based either on patterns found in your watched dramas or your similiarity to other users """)
    model = st.selectbox(
    'System based on:',
    ('Watched data','Users'))

    
    

    ok = st.button("Recommend")

    if ok:
        if model == 'Watched data':
            with st.status("Please wait, creating recommendations...") as status:
                df = rec.get_recommendations_for_user(user,100)
                status.update(label="Recommendations created!", state="complete")
        st.write('Shows recommended for you')
        st.dataframe(df)  
        

        


        
    