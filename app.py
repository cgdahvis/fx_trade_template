import streamlit as st
import re

# Set title
st.title('Trade Idea Generator')

# Widgets for inputs
currency_pair = st.selectbox('Currency Pair', ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "AUDNZD", "EURAUD", "EURNZD", "USDSEK", "USDNOK", "USDMXN","USDCNH","USDTWD","USDKRW", "USDSGD", "USDZAR", "USDTRY", "USDHKD"])
action = st.selectbox('Action', ['Buy', 'Sell'])
date = st.text_input('Date', value='1m')

# Validate date
if date.lower() not in ['1m', '3m'] and not re.match(r'\d{2}-\w{3}-\d{4}', date):
    st.error('Please enter a valid date or one of the allowed strings: "1m", "3m"')
else:
    option_type = st.selectbox('Option Type', ['call spread', 'put spread', 'call spread RKI', 'put spread RKI', 'digital', 'call ERKO', 'put ERKO'])
    # Number of strike inputs based on option type
    num_strikes = {"call spread": 2, "put spread": 2, "call spread RKI": 3, "put spread RKI": 3, "digital": 1, "call ERKO": 2, "put ERKO": 2}.get(option_type, 0)
    strikes = [st.number_input(f'Strike {i+1}', format='%f') for i in range(num_strikes)]
    
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
        elif option_type in ['call spread RKI', 'put spread RKI']:
            leverage = round((abs(strikes[2] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0
        elif option_type in ['call ERKO', 'put ERKO']:
            leverage = round((abs(strikes[1] - strikes[0]) / strikes[0]) / (cost / 10000), 1) if cost != 0 else 0
    
    # Conditional input for Net Delta
    if option_type != 'digital':
        net_delta = st.number_input('Net Delta (%)', min_value=0.0, format='%f')
    else:
        net_delta = None

    # Handle button click
if st.button('Generate Trade Idea'):
    # Formatting strikes
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

