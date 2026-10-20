import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL ="http://127.0.0.1:8000"

st.set_page_config(
page_title = "Ticket Classifier",
layout = "centered"
)
st.title("Smart Support Ticket Classifier")

st.write("Submit a customer support message and let the AI classify it.")

message = st.text_area("Enter customer message", height=100)

if st.button("Classify Ticket", type="primary"):
    if not message.strip():
        st.write("Please enter a message.")
    else:
        try:

            response = requests.post(
                f"{API_URL}/predict",
                json = {"message": message}
                ,timeout=10
            )
    
            if response.status_code == 200:
                    result = response.json()
                    st.success(f"Category: {result['category']}")
                    st.write("Ticket ID:", result["id"])
            else:

                
                    st.error(f"API error: {response.status_code}")

        except requests.RequestException:
             st.error("Cannot connect to FastAPI."
                      "Check that your backend is running.")

st.divider()
st.header("Ticket Analytics")

def get_tickets():
     try:
          response= requests.get(
               f"{API_URL}/tickets",
               timeout= 10
          )
          response.raise_for_status()
          return response.json()

     except requests.RequestException:
          st.error(
               "Unable to retrieve tickets."
               "Check your FastAPI server"
          )
          return None

tickets = get_tickets()
if tickets is not None:
     if len(tickets)==0:
          st.info("No tickets found."
                  "Submit your first ticket above")
     else:
          df = pd.DataFrame(tickets)


          total_tickets = len(df)
          total_category = df["category"].nunique()
          col1, col2 = st.columns(2)

          col1.metric(
               "Total Tickets", total_tickets
          )
          col2.metric(
               "Categories Detected", total_category
          )


          st.subheader("Tickets Categories")

          category_counts =(
               df["category"].value_counts().rename_axis("Category")
          ).reset_index(name="tickets")

          st.dataframe(
               category_counts,
               use_container_width=True,
               hide_index=True
          )


          col3= st.columns(1)

          with col3[0]:
               st.subheader("Category Distribution")

               bar_chart = px.bar(
                    category_counts,
                    x = "Category",
                    y = "tickets",
                    color = "Category",
                    title = "Tickets per Category"
               )
               st.plotly_chart(
                    bar_chart,
                    use_container_width=True
               )

               st.divider()

               st.subheader("Tickets History")

               st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
               )

              
               st.subheader(
                   "Filter Ticket "
               )

               categories = sorted(
                    df["category"].dropna().unique()
               )

               selected_category = st.selectbox(
                    "Choose a category:", ["All Categories"] + categories
               )

               if selected_category== "All Categories":
                    filtered_df = df
               else:
                    filtered_df= [df["category"] == selected_category]

                    st.dataframe(
                         filtered_df,
                         use_container_width = True,
                         hide_index =True
                    )

                    if st.button("Refresh Dashboard"):
                         st.rerun()
        
     
    

    
   