import streamlit as st
import recommender
import recommender_collab 

rec = recommender.Recommender()
rec_collab = recommender_collab.Recommmender_Collab()

def show_recommend_page():
    

    st.title("Korean dramas recommender")

    st.write("""### It works based on data from MyDramaList, input name of your account and other optional data to begin. """)
    user = st.text_input('Name of your account',help = "The one that is in the url of your account, for example XXX in mydramalist.com/profile/XXX")

    st.write("""Recommendations can be created based either on patterns found in your watched dramas or your similiarity to other users """)
    model = st.selectbox(
    'System based on:',
    ('Watched content','Users'))

    
    

    ok = st.button("Recommend")

    if ok:
        if model == 'Watched content':
            with st.status("Please wait, creating recommendations...") as status:
                df = rec.get_recommendations_for_user(user,100)
                status.update(label="Recommendations created!", state="complete")

        if model == 'Users':
            with st.status("Please wait, creating recommendations...") as status:
                df = rec_collab.make_recommendations_for_user(user,100)
                status.update(label="Recommendations created!", state="complete")

        st.write('Shows recommended for you')
        st.dataframe(df)  
        

        


        
    