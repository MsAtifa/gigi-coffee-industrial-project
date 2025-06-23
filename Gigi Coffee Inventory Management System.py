import gradio as gr
import calendar
import pandas as pd
from datetime import datetime, timedelta

# Load data from Excel
file_path = "c:/Users/Atifa/Downloads/gigi/Inventory Results.xlsx"
sheet_names = ["E0001", "E0002", "E0003", "G0001", "G0002", "G0003", "V0001", "V0002", "V0003","VL001", "VL002", "VL003"]

df_orders_list = []
for sheet in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    df["Store ID"] = sheet
    df_orders_list.append(df)

df_orders = pd.concat(df_orders_list, ignore_index=True)

# Base date assumption for "Period"
base_date = datetime(2025, 1, 1)
df_orders["Reorder Date"] = df_orders["Period"].apply(lambda x: (base_date + timedelta(days=x)).strftime("%Y-%m-%d"))

# Convert reorder data to dictionary format
reorder_inventory = {}
for _, row in df_orders.iterrows():
    store_id = row["Store ID"]
    date_key = row["Reorder Date"]
    
    if row.get("Quantity Ordered", 0) == 0 and row.get("Orders Arriving", 0) == 0:
        continue  
    
    item_info = f"{row['Ingredient']} : {int(row.get('Quantity Ordered', 0))}"
    
    if store_id not in reorder_inventory:
        reorder_inventory[store_id] = {}
    
    if date_key in reorder_inventory[store_id]:
        reorder_inventory[store_id][date_key] += "<br>" + item_info
    else:
        reorder_inventory[store_id][date_key] = item_info

stores = df_orders["Store ID"].unique().tolist()

logo_url = "https://www.gigicoffee.com/wp-content/uploads/2023/04/logo-gigicoffee.png"

def generate_calendar(store_id, month):
    year = 2025
    month_num = list(calendar.month_name).index(month)
    cal = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month_num)

    # Calculate number of rows and cell height
    num_rows = len(cal)
    overall_table_height = 356  # desired total height in pixels
    cell_height = overall_table_height / num_rows  # dynamically computed height per row

    store_reorder_dates = reorder_inventory.get(store_id, {})

    calendar_html = f"""
    <h2 style="text-align: left; color: #004ac7; font-size: 24px; font-weight: bold;">
        📍 Reorder Calendar for Store {store_id}
    </h2>
    <div style="position: relative; overflow: visible; transform: translateY(13px);">
    <style>
        .calendar-container {{width: 100%; max-width: 900px; height: 300px; }}
        .calendar-table {{ width: 100%; max-width: 900px; border-collapse: collapse; table-layout: fixed; height: 350px; margin: auto; background: white; border: 2px solid #000000 !important; }}
        .calendar-table th {{ background: #004ac7 !important; color: #ffffff !important; padding: 10px; border: 2px solid #000000 !important; }}
        .calendar-table td {{ width: 50px; text-align: center; vertical-align: middle; border: 2px solid #000000 !important; font-weight: bold; color: #004ac7 !important; position: relative; cursor: pointer; font-size: 18px; }}
        .calendar-table td:hover {{ background-color: #F0F7FF !important; }}
        .tooltip {{ display: none; position: absolute; background: white; padding: 10px; border-radius: 5px; font-size: 15px; box-shadow: 0px 2px 10px rgba(0,0,0,0.3); white-space: nowrap; z-index: 100; color: #004ac7 !important; max-height: 100px; overflow-y: auto;}}
        .calendar-day:hover .tooltip {{ display: block; font-weight: bold; color: #004ac7; }}
        .ordered-day {{ background-color: #FFD700 !important; }}
        .calendar-table tr:last-child .calendar-day:hover .tooltip {{top: auto; bottom: 100%; transform: translateY(0px);}}
        .calendar-day.saturday:hover .tooltip {{left: auto; right: 100%; transform: translate(5px, -30px);
        }}

    </style>
    <table class="calendar-table">
        <thead>
            <tr><th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th></tr>
        </thead>
        <tbody>
    """
    
    for week in cal:
        calendar_html += "<tr>"
        for idx, day in enumerate(week):
            if day == 0:
                calendar_html += f'<td style="height: {cell_height}px !important;"></td>'
            else:
                date_key = f"{year}-{month_num:02}-{day:02}"
                order_info = store_reorder_dates.get(date_key, "No orders")  
                ordered_class = "ordered-day" if date_key in store_reorder_dates else ""
                saturday_class = "saturday" if idx == 6 else ""
                calendar_html += f"""
                <td class="calendar-day {ordered_class} {saturday_class}" style="height: {cell_height}px !important;">
                    {day}
                    <div class="tooltip">{order_info}</div>
                </td>
                """
        calendar_html += "</tr>"
    
    calendar_html += "</tbody></table></div>"
    return calendar_html

logo_url = "https://www.gigicoffee.com/wp-content/uploads/2023/04/logo-gigicoffee.png"

# Gradio UI
with gr.Blocks(css="""
    body { background: #F0F7FF !important; }
    .gradio-container { background: #F0F7FF !important; }

    /* Input & Dropdown Styling */
    label { color: #004ac7 !important; font-weight: bold !important; }
    input, select { 
        color: #004ac7 !important; 
        font-weight: bold;
        border: 1px solid #004ac7 !important;
        padding: 8px !important;
        font-size: 14px !important;
        background: white !important;
        border-radius: 5px;
    }
               
    .gradio-container .gr-box {  
        background: #E0F0FF !important; 
        border-radius: 10px !important;
        padding: 15px !important;
    }

    /* Inner blocks (white background) */
    .gr-box .gr-block {  
        background: white !important; 
        border-radius: 10px !important;
        padding: 15px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }

        /* Table container */
    .arrival-container {
        max-height: 400px; 
        overflow-y: auto;
        background: #F0F7FF !important;
        padding: 10px;
        border-radius: 10px;
        margin-top: -7px !important;
        transform: translateX(10px);
    }
               
    .h1, h2, h3 {
    margin-bottom: 0px !important; 
    line-height: 1.2 !important;
}


    /* Styled Table */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background: #F0F7FF !important;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        margin-top: -10px !important;
    }

    /* Header */
    .styled-table thead tr {
        background: #004ac7 !important;
        color: white !important;
        text-align: left;
    }

    .styled-table th, .styled-table td {
        padding: 10px;
        border: 1px solid #CCDDEE !important;
        color: #004ac7 !important;
        font-weight: bold;
        text-align: center;
    }

    /* Alternating Row Colors */
    .styled-table tbody tr:nth-child(even) {
        background: #E0F0FF !important; 
    }

    .styled-table tbody tr:nth-child(odd) {
        background: #F0F7FF !important; 
    }
            

""") as demo:

    
    gr.Markdown(f"""
<div style="background: #004ac7; color: white; display: flex; align-items: center; padding: 10px; border-radius: 10px;">
  <img src="{logo_url}" alt="GIGI Coffee Logo" style="height: 50px; margin-right: 20px;">
  <span style="flex-grow: 1; text-align: center; font-size: 30px; font-weight: 900; color: white; margin-left: -65px; font-family: sans-serif;">
    GIGI COFFEE INVENTORY SYSTEM
  </span>
</div>
""")
    
    with gr.Row():
        search_store = gr.Textbox(placeholder="Search Store", label="Search Store")
        store_select = gr.Dropdown(choices=stores, label="Select Store", interactive=True)
        month_select = gr.Dropdown(choices=["January", "February", "March", "April", "May", "June", "July", "October", "November", "December"], label="Select Month", interactive=True)
    
    with gr.Row():
        with gr.Column():
            calendar_html = gr.HTML("")
        with gr.Column():
            arrival_header = gr.Markdown(
                "<h2 style='color: #004ac7; text-align: center; font-weight: bold; font-size: 24px; margin-bottom: 3px !important; margin-left: -340px;'>📦&nbsp;&nbsp;Arrival Inventory</h2>", 
                visible=False  
            )
            arrival_table = gr.HTML("") 

    def update_calendar(store, month):
        if store not in stores or not store:
            return (
                "<div style='color:red; font-weight:bold; text-align:center;'>Please select a valid store</div>", 
                "<div style='color: red; font-weight: bold; text-align: center;'>No orders found</div>",
                gr.update(visible=False)  
            )

        store_data = df_orders[df_orders["Store ID"] == store].copy()

        if store_data.empty:
            return (
                generate_calendar(store, month), 
                """
            <div class="arrival-container">
            <table class="styled-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Stock</th>
                        <th>Arrival Date</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td colspan='3' style='text-align:center; font-weight:bold;'>No orders found</td></tr>
                </tbody>
            </table>
        </div>
        """,
        gr.update(visible=False)  
        )
        calendar_html = generate_calendar(store, month)

        store_data["Reorder Date"] = store_data["Period"].apply(lambda x: (base_date + timedelta(days=x)).strftime("%Y-%m-%d"))
        store_data["Arrival Date"] = store_data["Period"].apply(lambda x: (base_date + timedelta(days=x)).strftime("%Y-%m-%d"))

        month_num = list(calendar.month_name).index(month)

        store_data = store_data[
            (pd.to_datetime(store_data["Reorder Date"]).dt.month == month_num) |
            (pd.to_datetime(store_data["Arrival Date"]).dt.month == month_num)
        ]

        store_data["Orders Arriving"] = store_data.get("Orders Arriving", 0)
        store_data = store_data[store_data["Orders Arriving"] > 0]
        store_data = store_data.sort_values(["Arrival Date","Ingredient"])

        if store_data.empty:
            return calendar_html, "<div style='text-align:center; font-weight:bold;'>No orders found</div>", gr.update(visible=False)

        arrival_table_html = """
        <div class="arrival-container">
        <table class="styled-table">
        <thead style="background-color: #004ac7 !important; color: white !important;  font-size: 16px; font-weight: bold !important;">
            <tr>
                <th style="color: white !important;">Arrival Date</th>
                <th style="color: white !important;">Item</th>
                <th style="color: white !important;">Stock</th>
            </tr>
        </thead>
        <tbody>
"""

        prev_date = None
        for _, row in store_data.iterrows():
            date = row["Arrival Date"]
            item = row["Ingredient"]
            stock = int(row["Orders Arriving"])

            if date == prev_date:
                arrival_table_html += f"<tr><td></td><td>{item}</td><td>{stock}</td></tr>"
            else:
                arrival_table_html += f"<tr><td>{date}</td><td>{item}</td><td>{stock}</td></tr>"
                prev_date = date

        arrival_table_html += "</tbody></table></div>"

        return calendar_html, arrival_table_html, gr.update(visible=True)


    store_select.change(update_calendar, inputs=[store_select, month_select], outputs=[calendar_html, arrival_table, arrival_header])
    month_select.change(update_calendar, inputs=[store_select, month_select], outputs=[calendar_html, arrival_table, arrival_header])
    search_store.input(lambda query: gr.update(choices=[s for s in stores if query.lower() in s.lower()]), inputs=[search_store], outputs=[store_select])

    demo.launch(share=True)
