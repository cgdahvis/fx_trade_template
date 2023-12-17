import streamlit as st
import pandas as pd
import os

# Function to save orders to a CSV file
def save_orders(order_data):
    order_data.to_csv("orders.csv", index=False)

# Function to load orders from a CSV file
def load_orders():
    try:
        return pd.read_csv("orders.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=['Client Name', 'CCY Pair', 'Structure', 'Liquidity Provider', 'Level', 'Client Fill Level'])

# Load orders from the CSV file when the app starts
order_data = load_orders()

# Function to load clients from a CSV file
def load_client_data():
    if os.path.isfile('clients_data.csv'):
        return pd.read_csv('clients_data.csv')
    else:
        return pd.DataFrame(columns=['Client Name', 'Firm', 'Potential'])

# Function to save clients to a CSV file
def save_client_data(df):
    df.to_csv('clients_data.csv', index=False)

# Load client data when the app starts
if 'client_data' not in st.session_state:
    st.session_state.client_data = load_client_data()

# Set title
st.set_page_config(page_title="Trade Idea Generator", page_icon=":chart_with_upwards_trend:", layout="wide")

# Create Tabs
tab1, tab_clients_prospects = st.tabs(["Trade Idea Generator", "Clients & Prospects"])

with tab1:
    st.title('Trade Idea Generator')

    # Create columns for input widgets
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Widgets in Top Row
    with col1:
        currency_pair = st.selectbox('Currency Pair', ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "EURGBP", "EURNOK", "AUDJPY", "AUDNZD", "EURAUD", "CHFJPY", "USDSEK", "USDNOK", "USDMXN", "USDCNH", "USDTWD", "USDKRW", "USDSGD", "USDZAR", "USDTRY", "USDINR"])
    with col2:
        date = st.text_input('Date', value='1m')
    with col3:
        action = st.selectbox('Action', ['Buy', 'Sell'])
    
    # Validate option type
    option_type = st.selectbox('Option Type', ['call spread', 'put spread', 'call spread RKI', 'put spread RKI', 'digital', 'call ERKO', 'put ERKO', 'digi risk reversal'])
    
    # Number of strike inputs based on option type
    num_strikes = {"call spread": 2, "put spread": 2, "call spread RKI": 3, "put spread RKI": 3, "digital": 1, "call ERKO": 2, "put ERKO": 2, 'digi risk reversal': 3}.get(option_type, 0)
    
    # Create a new row of columns for strikes
    col_strike1, col_strike2, col_strike3 = st.columns([1, 1, 1])
    strikes = []
    for i in range(num_strikes):
        label = f'ERKO' if (option_type in ['call ERKO', 'put ERKO', 'digi risk reversal'] and i == 1) else f'RKI' if (option_type in ['call spread RKI', 'put spread RKI', 'digi risk reversal'] and i >= 2) else f'Strike {i + 1}'
        with eval(f'col_strike{i + 1}'):
            strikes.append(st.number_input(label, format='%f'))
    
    # Conditional input for Cost with unit based on option type
    if option_type == 'digital':
        cost = st.number_input('Cost (%)', min_value=0.0, format='%f')
        cost_unit = '%'
        leverage = round(1 / (cost / 100), 1) if cost != 0 else 0
    else:
        cost = st.number_input('Cost (bps)', min_value=0.0, format='%f')
        cost_unit = 'bps'
        if option_type in ['call spread', 'put spread']:
            leverage = round((abs(strikes[1] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0
        elif option_type in ['call spread RKI', 'put spread RKI', 'digi risk reversal']:
            leverage = round((abs(strikes[2] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0
        elif option_type in ['call ERKO', 'put ERKO']:
            leverage = round((abs(strikes[1] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0
    
    # Conditional input for Net Delta
    if option_type != 'digital':
        net_delta = st.number_input('Net Delta (%)', min_value=0.0, format='%f')
    else:
        net_delta = None
    
    # Inside the 'Generate Trade Idea' button block
    if st.button('Generate Trade Idea'):
        # Formatting strikes
        if option_type in ['call ERKO', 'put ERKO', 'digi risk reversal']:
            strikes_text = f"{strikes[0]}"
        elif option_type in ['call spread RKI', 'put spread RKI']:
            strikes_text = ' / '.join(map(str, strikes[:-1]))
        else:
            strikes_text = ' / '.join(map(str, strikes))
    
        # Constructing trade idea using HTML tags
        trade_idea_html = f"""
        <p style="line-height:1.0;">
            {currency_pair}<br>
            {action} {date} {strikes_text} {option_type}{f' {strikes[-1]}' if 'RKI' in option_type or 'ERKO' in option_type else ''}<br>
            <strong>Costs ~ {cost} {cost_unit}</strong>{f' / Net Delta {net_delta}%' if net_delta is not None else ''}<br>
            <strong>{leverage:.1f}x Leverage</strong>
        </p>
        """
        st.markdown(trade_idea_html, unsafe_allow_html=True)
    
    
    # Sidebar for data entry
    st.sidebar.header("FX Derivative Order Tracker")
    client_name = st.sidebar.text_input("Client Name")
    ccy_pair = st.sidebar.selectbox("Currency Pair", ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "AUDNZD", "EURAUD", "CHFJPY", "USDSEK", "USDNOK", "USDMXN", "USDCNH", "USDTWD", "USDKRW", "USDSGD", "USDZAR", "USDTRY", "USDINR"])
    structure = st.sidebar.text_input("Structure")
    liquidity_provider = st.sidebar.text_input("Liquidity Provider")
    level = st.sidebar.number_input("Level Working with LP", min_value=0)
    client_fill_level = st.sidebar.number_input("Client Fill Level", min_value=0)
    
    if st.sidebar.button("Add Order"):
        new_row = {'Client Name': client_name, 'CCY Pair': ccy_pair, 'Structure': structure,
                   'Liquidity Provider': liquidity_provider, 'Level': level, 'Client Fill Level': client_fill_level}
        order_data = pd.concat([order_data, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success("Order Added!")
    
        # Save orders to the CSV file
        save_orders(order_data)
    
    # Display the orders in a table
    st.header("Current Orders")
    if not order_data.empty:
        st.table(order_data)
    
    # Allow users to delete specific orders
    st.subheader("Remove Specific Orders")
    order_to_remove = st.selectbox("Select an Order to Remove", order_data['Client Name'].unique(), key='remove_order')
    if st.button("Remove Selected Order"):
        order_data = order_data[order_data['Client Name'] != order_to_remove]
        save_orders(order_data)
        st.success(f"Order for {order_to_remove} Removed!")

#---client tab below---

# def add_client_form():
#     # Function to display the form in a modal
#     with st.form("Add_Client_Form", clear_on_submit=True):
#         st.text_input("Client Name", key="new_client_name")
#         st.text_input("Firm", key="new_firm")
#         st.selectbox("Potential", ["High (Green)", "Medium (Yellow)", "Low (Red)"], key="new_potential")
#         submit_button = st.form_submit_button("Submit New Client")
#         if submit_button:
#             return True
#         else:
#             return False


# def add_or_update_client(client_name, firm, potential, note):
#     if client_name in st.session_state.client_data['Client Name'].values:
#         # Update existing client
#         st.session_state.client_data.loc[st.session_state.client_data['Client Name'] == client_name, ['Firm', 'Potential', 'Notes']] = [firm, potential, note]
#     else:
#         # Add new client
#         new_data = pd.DataFrame([[client_name, firm, potential, note]], columns=['Client Name', 'Firm', 'Potential', 'Notes'])
#         st.session_state.client_data = pd.concat([st.session_state.client_data, new_data], ignore_index=True)
#     save_client_data(st.session_state.client_data)

# def delete_client(client_name):
#     st.session_state.client_data = st.session_state.client_data[st.session_state.client_data['Client Name'] != client_name]
#     save_client_data(st.session_state.client_data)

with tab_clients_prospects:
    st.title("Clients & Prospects")

    # Styling for a cleaner look
    st.markdown("""
    <style>
    .client-grid {font-size: 16px; line-height: 1.5;}
    .stButton>button {margin: 5px 0; width: 100%;}
    .stTextInput, .stSelectbox, .stTextArea {margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

    # Add New Client Section
    with st.form("new_client_form"):
        st.subheader("Add New Client")
        new_client_name = st.text_input("Client Name", key="new_client_name")
        new_firm = st.text_input("Firm", key="new_firm")
        new_potential = st.selectbox("Potential", ["High (Green)", "Medium (Yellow)", "Low (Red)"], key="new_potential")
        note = st.text_area("Notes", key="new_note")
        submit_new = st.form_submit_button("Add Client")

    if submit_new:
    # Ensure new_data is a DataFrame
        new_data = pd.DataFrame([{
        'Client Name': new_client_name, 
        'Firm': new_firm, 
        'Potential': new_potential, 
        'Notes': note
    }])
    
    # Append new_data to client_data
    st.session_state.client_data = pd.concat([st.session_state.client_data, new_data], ignore_index=True)
    save_client_data(st.session_state.client_data)

    # Edit Existing Client Section
    with st.container():
        st.subheader("Edit Existing Client")
        client_names = st.session_state.client_data['Client Name'].tolist()
        selected_client = st.selectbox("Select Client to Edit", [""] + client_names, key="select_client_edit")

        if selected_client:
            client_info = st.session_state.client_data[st.session_state.client_data['Client Name'] == selected_client].iloc[0]
            with st.form("edit_client_form"):
                edit_client_name = st.text_input("Client Name", value=client_info['Client Name'], key="edit_client_name")
                edit_firm = st.text_input("Firm", value=client_info['Firm'], key="edit_firm")
                edit_potential = st.selectbox("Potential", ["High (Green)", "Medium (Yellow)", "Low (Red)"], index=["High (Green)", "Medium (Yellow)", "Low (Red)"].index(client_info['Potential']), key="edit_potential")
                edit_note = st.text_area("Notes", value=client_info.get('Notes', ''), key="edit_note")
                submit_edit = st.form_submit_button("Update Client")

        if submit_edit:
            # Logic to update selected client in DataFrame
            st.session_state.client_data.loc[st.session_state.client_data['Client Name'] == selected_client, ['Client Name', 'Firm', 'Potential', 'Notes']] = [edit_client_name, edit_firm, edit_potential, edit_note]
            save_client_data(st.session_state.client_data)

    # Delete Client Section
    with st.container():
        st.subheader("Delete Client")
        delete_client_name = st.selectbox("Select Client to Delete", [""] + client_names, key="delete_client_select")
        if st.button("Delete Client", key="delete_client"):
            # Logic to delete selected client from DataFrame
            st.session_state.client_data = st.session_state.client_data[st.session_state.client_data['Client Name'] != delete_client_name]
            save_client_data(st.session_state.client_data)

    # Display Client Information Grid
    st.subheader("Client Information")
    st.dataframe(st.session_state.client_data.style.applymap(
        lambda x: 'background-color: lightgreen' if x == "High (Green)"
                  else ('background-color: lightyellow' if x == "Medium (Yellow)"
                  else 'background-color: lightcoral'),
        subset=['Potential']))
