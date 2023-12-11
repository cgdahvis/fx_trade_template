import streamlit as st
import pandas as pd

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

# Set title
st.set_page_config(page_title="Trade Idea Generator", page_icon=":chart_with_upwards_trend:", layout="wide")
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
    elif option_type in ['call spread RKI', 'put spread RKI', 'digi risk reversal']:
        # Include the additional strike in the text
        strikes_text = f"{strikes[1]}/{strikes[0]} {'RKI' if 'RKI' in option_type else ''}"
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
