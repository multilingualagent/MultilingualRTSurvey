import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from formatting import (build_color_map, categorical_columns, get_unique_parts,
                        style_multi_general, style_yesno, yes_no_colums)

st.markdown(
    """
    <style>
    /* Change font size of tabs */
    button[data-baseweb="tab"] > div:first-child {
        font-size: 25px !important;  /* adjust this value */
        font-weight: bold; 
        color: #3F1939          /* optional */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* Target the label text for widgets */
label[data-testid="stWidgetLabel"] p {
    font-size: 20px;       /* change size as needed */
    font-weight: bold;     /* optional */
    color: #5F1E40;        /* optional color */
}
</style>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["📄 Info", "📊 Data"])
with tab1:
    st.set_page_config(page_title="Multilingual RedTeaming Datasets", layout="wide")
    st.title("Multilingual RedTeaming Datasets")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            "### Overview of Datasets for Multilingual Safety based on the Paper: [Multilingual RedTeaming Surveys]"
        )
        st.markdown(
            "### ℹ️ Notes \n"
            "You might notice that some information isn't provided for every dataset. We've indicated these instances using the following markers: 'not applicable', 'not specified', '-'"
        )

        st.markdown(
            "### ✉️ Contact \n"
            "Your feedback is valuable! If you find any errors in our datasets, please don't hesitate to email us at: [contact]. \n"
            " Additionally, if you're interested in contributing a new dataset, please get in touch with us at the same address: [contact]. "
        )
    with col2:
        image = Image.open("images/globe.jpeg")
        st.image(
            image,
            width=300,
            caption="Generated using https://stabledifffusion.com/",
        )


with tab2:
    data = pd.read_excel(
        "data/data.xlsx", sheet_name="cleaned"
    )
    data.fillna("-", inplace=True)
    col1, col2 = st.columns([2, 6])
    with col1:
        # --- FILTERING ---
        st.markdown("### 🔎 Use the filters below to narrow down datasets.")
        
        search_text = st.text_input("Search text:")
        selected = {}
        for col in yes_no_colums:
            options = data[col].dropna().unique()
            selected[col] = st.multiselect(
                col,
                options,
                default=options,
            )

        for col in categorical_columns:
            options = get_unique_parts(data[col])
            options = sorted(options)
            selected[col] = st.multiselect(col, options, default=options)

        

        mask = np.ones(len(data), dtype=bool)  # start with all True
        for col in yes_no_colums:
            mask &= data[col].isin(selected[col])

        for col in categorical_columns:
            col_mask = data[col].apply(
                lambda cell: any(
                    val.strip() in selected[col] for val in str(cell).split(",")
                )
            )
            mask &= col_mask

        filtered_data = data[mask]
        if search_text:
            mask = filtered_data.apply(
                lambda row: row.astype(str).str.contains(search_text, case=False).any(),
                axis=1,
            )
            filtered_data = filtered_data[mask]

    with col2:

        # --- HTML TABLE ---
        url_col = "URL"
        html = "<table style='border-collapse:collapse;table-layout:fixed;'>"

        visible_cols = [c for c in filtered_data.columns if c != url_col]
        html += "<colgroup>"
        for col in visible_cols:
            if col == "Title":
                html += "<col style='width:50px;'>"
            else:
                html += "<col style='width:300px;'>"
        html += "</colgroup>"

        # header
        html += "<tr>"
        for col in filtered_data.columns:
            if col != url_col:
                html += f"<th style='text-align:left;padding:100px;border-bottom:2px solid #ccc;background-color:#5F1E40;color:white;'>{col}</th>"
        html += "</tr>"

        # rows
        for _, row in filtered_data.iterrows():
            html += "<tr>"
            for col in visible_cols:
                cell_style = "padding:8px;border-bottom:1px solid #eee;white-space:normal;word-wrap:break-word;overflow-wrap:anywhere;"
                if col == "Title":
                    html += f"<td style='{cell_style}'><a href='{row[url_col]}' target='_blank'>{row[col]}</a></td>"
                elif col == "Data URL":
                    if pd.isna(row[col]) or row[col] == "-":
                        html += f"<td style='{cell_style}'>{row[col]}</td>"
                    else:
                        html += f"<td style='{cell_style}'><a href='{row[col]}' target='_blank'>url</a></td>"
                elif col in yes_no_colums:
                    html += f"<td style='{cell_style}'>{style_yesno(row[col])}</td>"
                elif col in categorical_columns:
                    color_map = build_color_map(filtered_data[col])
                    html += f"<td style='{cell_style}'>{style_multi_general(row[col], color_map)}</td>"
                else:
                    html += f"<td style='{cell_style}'>{row[col]}</td>"
            html += "</tr>"
        html += "</table>"

        st.markdown(html, unsafe_allow_html=True)
