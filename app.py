import streamlit as st
from datetime import datetime

# Set title
st.title('Trade Idea Generator')

# Widgets for inputs
currency_pair = st.selectbox('Currency Pair', ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "AUDNZD", "EURAUD", "EURNZD", "USDSEK", "USDNOK", "USDMXN","USDCNH","USDTWD","USDKRW", "USDSGD", "USDZAR", "USDTRY", "USDHKD"])
action = st.selectbox('Action', ['Buy', 'Sell'])
date = st.date_input('Date', min_value=datetime.today())
option_type = st.selectbox('Option Type', ['call spread', 'put spread', 'call spread RKI', 'put spread RKI', 'digital', 'call ERKO', 'put ERKO'])

# Get user input for strikes
strikes = [st.number_input(f'Strike {i+1}', format='%f') for i in range(2 if 'spread' in option_type else 1)]  # Adjusted the number of strikes

# Additional input for RKI/ERKO level for relevant option types
if 'RKI' in option_type or 'ERKO' in option_type:
    rki_erko_level = st.number_input(f'{option_type.split()[-1]} Level', format='%f')
    strikes.append(rki_erko_level)  # Adding the RKI/ERKO level to the strikes list

# Conditional input for Cost with unit based on option type
if option_type == 'digital':
    cost = st.number_input('Cost (%)', min_value=0.0, format='%f')
    cost_unit = '%'  # set the unit for cost as percentage
    leverage = round(1 / (cost / 100), 1) if cost != 0 else 0  # Leverage calculation for digital, adjusted for percentage input and rounded
else:
    cost = st.number_input('Cost (bps)', min_value=0.0, format='%f')
    cost_unit = 'bps'  # set the unit for cost as basis points
    if option_type in ['call spread', 'put spread']:
        leverage = round((abs(strikes[1] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0
    elif option_type in ['call spread RKI', 'put spread RKI']:
        leverage = round((abs(strikes[2] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0  # Leverage calculation for call/put spread RKI using near strike and RKI level
    elif option_type in ['call ERKO', 'put ERKO']:
        leverage = round((abs(strikes[0] - strikes[1]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0  # Adjusted the leverage calculation for call/put ERKO

# Conditional input for Net Delta
if option_type != 'digital':
    net_delta = st.number_input('Net Delta (%)', min_value=0.0, format='%f')
else:
    net_delta = None

# Handle button click
if st.button('Generate Trade Idea'):
    # Formatting strikes
    strikes_text = ' / '.join(map(str, strikes[:2]))  # Display only the first two strikes
    
    # Constructing trade idea
    if net_delta is not None:
        trade_idea = f"{currency_pair}\n\n{action} {date.strftime('%d-%b-%Y')} {strikes_text} {option_type}{f' {strikes[-1]}' if 'RKI' in option_type or 'ERKO' in option_type else ''}\nCosts ~ {cost} {cost_unit} / Net Delta {net_delta}%\n{leverage:.2f}x Leverage"
    else:
        trade_idea = f"{currency_pair}\n\n{action} {date.strftime('%d-%b-%Y')} {strikes_text} {option_type}{f' {strikes[-1]}' if 'RKI' in option_type or 'ERKO' in option_type else ''}\nCosts ~ {cost} {cost_unit}\n{leverage:.2f}x Leverage"
    
    # Display the trade idea
    st.text(trade_idea)

