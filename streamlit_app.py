import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# Enable wide mode
st.set_page_config(layout="wide")

# Authentication check
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def show_authentication():
    st.markdown(
        """
        <h1 style="text-align: center; color: #4B0082;">
            WagScoreCard <span style="color: #8A2BE2;">Remastered</span> By <span style="color: #9932CC;">John D.</span>
        </h1>
        <h3 style="text-align: center; color: #9932CC;">
            Access Needed
        </h3>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    password = st.text_input("", type="password", max_chars=20, key="password", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <p style="text-align: center; font-size: 12px; color: gray;">
            PM John D. to get ACCESS
        </p>
        <div style="text-align: center;">
            <a href="https://www.facebook.com/jeddifz.difuntorum" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook" width="30">
            </a>
        </div>
        <p style="text-align: center; font-size: 10px; color: #4B0082; margin-top: 20px;">
            Namamasko po!<br>
            Gcash 09123086193<br>
            Maya 09123086193
        </p>
        """,
        unsafe_allow_html=True
    )

    if st.button("Login", key="login_button"):
        if password == "123098":
            st.session_state["authenticated"] = True
            st.success("Please Click Login AGAIN!")
        else:
            st.error("WAG SQUAD ONLY BOI! WE BURN MONEY HERE!")

def show_dashboard():
    # Define currencies and pairs
    currencies = ["AUD", "CAD", "EUR", "GBP", "JPY", "NZD", "USD"]
    pairs = [
        "AUDCAD", "AUDJPY", "AUDNZD", "AUDUSD", "CADJPY",
        "EURAUD", "EURCAD", "EURGBP", "EURJPY", "EURNZD", "EURUSD",
        "GBPAUD", "GBPCAD", "GBPJPY", "GBPNZD", "GBPUSD",
        "NZDCAD", "NZDJPY", "NZDUSD", "USDCAD", "USDJPY"
    ]

    # Streamlit layout
    st.markdown(
        """
        <h1 style="text-align: center; color: #4B0082;">
            WagScoreCard <span style="color: #8A2BE2;">Remastered</span> By <span style="color: #9932CC;">John D.</span>
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Currency Score Input (small width)
    st.sidebar.subheader("Currency Score Table")
    currency_score = {}
    for currency in currencies:
        currency_score[currency] = st.sidebar.number_input(f"{currency}", min_value=-6, max_value=6, value=0, step=1)

    # Trend Table Calculation
    trend_table = {currency: "Neutral" for currency in currencies}
    for currency, score in currency_score.items():
        if score >= 4:
            trend_table[currency] = "Strong"
        elif score <= -4:
            trend_table[currency] = "Weak"

    # Prepare Currency Table
    currency_df = pd.DataFrame({
        "Currency": currencies,
        "Score": [currency_score[currency] for currency in currencies],
        "Trend": [trend_table[currency] for currency in currencies]
    })

    # Pair, GAP, VS, and Bias Table
    pair_data = {"Pair": [], "Gap": [], "VS": [], "Bias": []}

    for pair in pairs:
        base_currency = pair[:3]
        quote_currency = pair[3:]
        gap = currency_score[base_currency] - currency_score[quote_currency]
        vs = f"{trend_table[base_currency]} vs {trend_table[quote_currency]}"

        # Bias determination
        if trend_table[base_currency] == "Neutral" and trend_table[quote_currency] == "Neutral":
            bias = "INVALID"
            bias_color = "white"
        elif trend_table[base_currency] == "Neutral" and trend_table[quote_currency] == "Strong":
            bias = "SELL"
            bias_color = "red"
        elif trend_table[base_currency] == "Neutral" and trend_table[quote_currency] == "Weak":
            bias = "BUY"
            bias_color = "green"
        elif trend_table[base_currency] == "Strong" and trend_table[quote_currency] == "Neutral":
            bias = "BUY"
            bias_color = "green"
        elif trend_table[base_currency] == "Weak" and trend_table[quote_currency] == "Neutral":
            bias = "SELL"
            bias_color = "red"
        elif trend_table[base_currency] == "Strong" and trend_table[quote_currency] == "Weak":
            bias = "BUY"
            bias_color = "green"
        elif trend_table[base_currency] == "Weak" and trend_table[quote_currency] == "Strong":
            bias = "SELL"
            bias_color = "red"
        else:
            bias = "INVALID"
            bias_color = "white"

        pair_data["Pair"].append(pair)
        pair_data["Gap"].append(gap)
        pair_data["VS"].append(vs)
        pair_data["Bias"].append((bias, bias_color))

    # Prepare Pair Table
    pair_df = pd.DataFrame(pair_data)

    # Add background color to GAP based on the value
    def style_gap(val):
        if -5 <= val <= 5:
            return "background-color: darkgray;"
        elif abs(val) > 5:
            return "background-color: green;"
        return ""

    # Prepare Trade Table (only GAP > 6 or GAP < -6 with BUY/SELL, exclude INVALID)
    trade_df = pair_df[(
        (pair_df["Gap"] > 5) | (pair_df["Gap"] < -5)) &
        (pair_df["Bias"].apply(lambda x: x[0]) != "INVALID")
    ][["Pair", "Gap", "VS", "Bias"]]

    # Display Layout: Currency Table (left), Analysis Tables (center), Trade Table (right)
    st.subheader("Dashboard")
    col1, col2, spacer2, col3 = st.columns([2, 1.5, 1.5, 1])  # Adjusted column widths for better spacing

    # Left: Currency Table
    with col1:
        st.markdown("Currency Table")
        st.table(currency_df)

    # Center: Analysis Tables (smaller font for compact view)
    with col2:
        st.markdown("Analysis")
        styled_pair_df = pair_df[["Pair", "Gap", "VS", "Bias"]].copy()  # Include 'VS' here
        styled_pair_df["Bias"] = styled_pair_df["Bias"].apply(lambda x: f'<span style="color: {x[1]};">{x[0]}</span>')
        st.write(styled_pair_df.style.applymap(style_gap, subset=["Gap"]).set_table_styles(
            [{"selector": "table", "props": [("font-size", "12px")]}]
        ).to_html(), unsafe_allow_html=True)

    # Spacer between columns
    with spacer2:
        st.write("   ")

    # Right: Trade Table
    with col3:
        st.markdown("Trade Plan")
        if trade_df.empty:
            st.write("No trades available to display or download.")
        else:
            styled_trade_df = trade_df.copy()
            styled_trade_df["Bias"] = styled_trade_df["Bias"].apply(lambda x: f'<span style="color: {x[1]};">{x[0]}</span>')
            st.write(styled_trade_df.to_html(escape=False), unsafe_allow_html=True)

            # Generate a timestamp in Philippine Time
            philippine_time = datetime.now(pytz.timezone("Asia/Manila"))
            formatted_time = philippine_time.strftime("%I:%M%p of %B %d %Y %A")

            # Add a download button for PNG
            st.markdown("Download Trade Plan")
            fig, ax = plt.subplots(figsize=(8, len(trade_df) * 0.5 + 1))
            ax.axis('tight')
            ax.axis('off')

            # Render table with styles in PNG, now including 'VS' column
            table = ax.table(
                cellText=trade_df.apply(lambda row: [
                        row["Pair"],
                        row["Gap"],
                        row["VS"],  # Include VS here
                        f"{row['Bias'][0]}"
                    ], axis=1).tolist(),
                colLabels=["Pair", "Gap", "VS", "Bias"],  # Include VS in column labels
                cellLoc='center',
                loc='center'
            )

            # Apply styles for 'Bias' (BUY/SELL)
            for i, row in enumerate(trade_df.values):
                bias = row[3]  # Bias is in the 4th column now
                if bias[0] == "SELL":
                    for j in range(len(row)):
                        table[(i + 1, j)].set_facecolor("red")
                elif bias[0] == "BUY":
                    for j in range(len(row)):
                        table[(i + 1, j)].set_facecolor("green")

            # Add timestamp and name
            plt.text(0.5, -0.05, f"Trade Plan ({formatted_time})", ha='center', fontsize=10, transform=ax.transAxes)
            plt.text(0.5, -0.1, "WagScore Remastered By: John D.", ha='center', fontsize=10, transform=ax.transAxes)

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)

            st.download_button(
                label=f"Download Trade Plan as PNG ({formatted_time})",
                data=buf,
                file_name=f"trade_plan_{philippine_time.strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )

# Main script logic
if st.session_state["authenticated"]:
    show_dashboard()
else:
    show_authentication()
