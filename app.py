import pandas as pd
import streamlit as st
import zipfile
import io
import json
import streamlit.components.v1 as components

# Streamlit app title
st.title('Generate your webstories:😀')

# Create two tabs: Master Template Generator and Story Generator
tab1, tab2 = st.tabs(["Master Template Generator", "Story Generator"])

# Tab 1: Master Template Generator
with tab1:
    st.header('Master Template Generator')
    
    # File upload for Excel and HTML
    uploaded_excel_master = st.file_uploader("Upload the Excel file (for replacements)", type="xlsx", key="master_excel")
    uploaded_html_master = st.file_uploader("Upload the HTML file", type="html", key="master_html")

    # Proceed if both files are uploaded
    if uploaded_excel_master and uploaded_html_master:
        # Read the Excel file into a DataFrame
        df_master = pd.read_excel(uploaded_excel_master, header=None)

        # Read the uploaded HTML file
        html_content_master = uploaded_html_master.read().decode('utf-8')

        # Get the last row for placeholders
        placeholder_row = df_master.iloc[-1]

        # Create an in-memory ZIP file
        zip_buffer = io.BytesIO()

        # Loop through each row except the last one (which contains placeholders)
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for row_index in range(len(df_master) - 1):
                # Get the current row data (actual values)
                row_data = df_master.iloc[row_index]

                # Make a copy of the HTML content for each row
                html_content_modified = html_content_master

                # Perform replacements for each column
                for col_index in range(len(df_master.columns)):
                    actual_value = str(row_data[col_index])      # Actual value from the current row
                    placeholder = str(placeholder_row[col_index])  # Placeholder from the last row
                    html_content_modified = html_content_modified.replace(actual_value, placeholder)

                # Generate the filename using the first column of the current row
                file_name = f"{str(row_data[0])}_template.html"

                # Add the modified HTML content to the ZIP file
                zip_file.writestr(file_name, html_content_modified)

        # Create a download button for the ZIP file
        st.download_button(
            label="Download All Modified HTML Files (Master Template)",
            data=zip_buffer.getvalue(),
            file_name="modified_templates_master.zip",
            mime='application/zip'
        )
    else:
        st.info("Please upload both an Excel file and an HTML file for the Master Template Generator.")

# Tab 2: Story Generator
with tab2:
    st.header('Story Generator')
    
    # File upload for Excel and HTML
    uploaded_excel_story = st.file_uploader("Upload the Excel file (for replacements)", type="xlsx", key="story_excel")
    uploaded_html_story = st.file_uploader("Upload the HTML file", type="html", key="story_html")

    # Proceed if both files are uploaded
    if uploaded_excel_story and uploaded_html_story:
        # Read the Excel file into a DataFrame
        df_story = pd.read_excel(uploaded_excel_story, header=None)

        # Read the uploaded HTML file
        html_content_template_story = uploaded_html_story.read().decode('utf-8')

        # First row (index 0) contains placeholders like {{storytitle}}, {{coverinfo1}}, etc.
        placeholders_story = df_story.iloc[0].tolist()

        # Create an in-memory ZIP file
        zip_buffer_story = io.BytesIO()

        # Loop through each row from index 1 onward to perform replacements
        with zipfile.ZipFile(zip_buffer_story, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for row_index in range(1, len(df_story)):
                actual_values_story = df_story.iloc[row_index].tolist()

                # Copy the original HTML template content
                html_content_story = html_content_template_story

                # Perform batch replacement for each placeholder in the row
                for placeholder, actual_value in zip(placeholders_story, actual_values_story):
                    html_content_story = html_content_story.replace(str(placeholder), str(actual_value))

                # Use the first column value of each row as the filename
                output_filename_story = f"{actual_values_story[0]}.html"

                # Add the modified HTML content to the ZIP file
                zip_file.writestr(output_filename_story, html_content_story)

        # Create a download button for the ZIP file
        st.download_button(
            label="Download All Modified HTML Files (Story Generator)",
            data=zip_buffer_story.getvalue(),
            file_name="modified_templates_story.zip",
            mime='application/zip'
        )
    else:
        st.info("Please upload both an Excel file and an HTML file for the Story Generator.")
