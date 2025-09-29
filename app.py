import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

# Assuming 'formatting.py' exists with these functions
from formatting import (build_color_map, categorical_columns, get_unique_parts,
                        style_multi_general, style_yesno, yes_no_colums)

# Set page config at the very beginning
st.set_page_config(page_title="Multilingual RedTeaming Datasets", layout="wide")

st.markdown(
    """
    <style>
    /* Change font size of tabs */
    button[data-baseweb="tab"] > div:first-child {
        font-size: 25px !important;  /* adjust this value */
        font-weight: bold;
        color: #3F1939;          /* optional */
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
    font-size: 20px;      /* change size as needed */
    font-weight: bold;    /* optional */
    color: #5F1E40;       /* optional color */
}
</style>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["📄 Info", "📊 Data"])
with tab1:
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
        # It's good practice to wrap file operations in a try-except block
        try:
            image = Image.open("images/globe.jpeg")
            st.image(
                image,
                width=300,
                caption="Generated using https://stabledifffusion.com/",
            )
        except FileNotFoundError:
            st.warning("Image file not found. Please check the path 'images/globe.jpeg'")


with tab2:
    # It's good practice to wrap file operations in a try-except block
    try:
        data = pd.read_excel(
            "data/data.xlsx", sheet_name="cleaned"
        )
        data.fillna("-", inplace=True)
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/data.xlsx' exists.")
        # Stop execution for this tab if data is not found
        st.stop()


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
        # --- HTML TABLE WITH FROZEN HEADER AND FIRST COLUMN ---
        url_col = "URL"

        html = "<div style='height: 70vh; overflow: auto;'>"
        html += "<table style='border-collapse:collapse; table-layout:fixed; width: 100%;'>"

        visible_cols = [c for c in filtered_data.columns if c != url_col]
        html += "<colgroup>"
        for col in visible_cols:
            if col == "Title":
                html += "<col style='width:250px;'>"
            else:
                html += "<col style='width:200px;'>"
        html += "</colgroup>"


        # --- HEADER ---
        html += "<thead>"
        html += "<tr>"
        first_visible_col = visible_cols[0] if visible_cols else None
        for col in visible_cols:
            # Base style for all header cells
            header_style = (
                "position: sticky; top: 0; z-index: 1; text-align: left; "
                "padding: 8px; border-bottom: 2px solid #ccc; "
                "background-color: #5F1E40; color: white;"
            )
            # If it's the first column, make it sticky to the left and give it a higher z-index
            if col == first_visible_col:
                header_style += " left: 0; z-index: 2; border-right: 2px solid #ccc;"

            html += f"<th style='{header_style}'>{col}</th>"
        html += "</tr>"
        html += "</thead>"


        # --- BODY ---
        html += "<tbody>"
        for _, row in filtered_data.iterrows():
            html += "<tr>"
            for col in visible_cols:
                cell_style = "padding: 8px; border-bottom: 1px solid #eee; white-space: normal; word-wrap: break-word; overflow-wrap: anywhere;"

                # CHANGE: If it's the first column, add sticky styles
                if col == first_visible_col:
                    cell_style += " position: sticky; left: 0; background-color: white; border-right: 2px solid #ccc;"

                # Render the cell content
                cell_content = ""
                if col == "Title":
                    cell_content = f"<a href='{row[url_col]}' target='_blank'>{row[col]}</a>"
                elif col == "Data URL":
                    if pd.isna(row[col]) or row[col] == "-":
                        cell_content = f"{row[col]}"
                    else:
                        cell_content = f"<a href='{row[col]}' target='_blank'>url</a>"
                elif col in yes_no_colums:
                    cell_content = f"{style_yesno(row[col])}"
                elif col in categorical_columns:
                    color_map = build_color_map(filtered_data[col])
                    cell_content = f"{style_multi_general(row[col], color_map)}"
                else:
                    cell_content = f"{row[col]}"

                html += f"<td style='{cell_style}'>{cell_content}</td>"
            html += "</tr>"

        html += "</tbody>"
        html += "</table>"
        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)

        # --- STYLING FOR DOWNLOAD BUTTON ---
        st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] > button {
            background-color: #5F1E40;
            color: white;
            font-size: 16px;
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            background-color: #3F1939; /* Darker shade on hover */
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

        # --- DOWNLOAD BUTTON ---
        @st.cache_data
        def convert_df_to_csv(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df_to_csv(filtered_data)

        st.download_button(
           label="Download data as CSV",
           data=csv,
           file_name='filtered_datasets.csv',
           mime='text/csv',
        )

