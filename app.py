import os
import time
import pandas as pd
import streamlit as st
import zipfile
import io
from datetime import datetime

# Streamlit app title
st.title('Generate your webstories: 😀')

# Create four tabs: Master Template Generator, Story Generator, Insert Lines, Remove Lines
tab1, tab2, tab3, tab4 = st.tabs(["Master Template Generator", "Story Generator", "Insert Lines", "Remove Lines"])

# Tab 1: Master Template Generator
with tab1:
    st.header('Master Template Generator')

    uploaded_excel_master = st.file_uploader("Upload the Excel file (for replacements)", type="xlsx", key="master_excel")
    uploaded_html_master = st.file_uploader("Upload the HTML file", type="html", key="master_html")
    
    if uploaded_excel_master and uploaded_html_master:
        df_master = pd.read_excel(uploaded_excel_master, header=None)
        html_content_master = uploaded_html_master.read().decode('utf-8')
        placeholder_row = df_master.iloc[-1]
    
        for row_index in range(len(df_master) - 1):
            row_data = df_master.iloc[row_index]
            html_content_modified = html_content_master
    
            for col_index in range(len(df_master.columns)):
                actual_value = str(row_data[col_index])
                placeholder = str(placeholder_row[col_index])
                html_content_modified = html_content_modified.replace(placeholder, actual_value)
    
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"modified_template_{timestamp}.html"
            st.download_button(
                label=f"Download Modified HTML for {str(row_data[0])}", 
                data=html_content_modified, 
                file_name=file_name, 
                mime='text/html',
                key=f"download_master_{row_index}"
            )
        st.success("HTML content modified for all rows. Click the buttons above to download the modified files.")
    else:
        st.info("Please upload both an Excel file and an HTML file for the Master Template Generator.")

# Tab 2: Story Generator
with tab2:
    st.header('Story Generator')

    uploaded_excel_story = st.file_uploader("Upload the Excel file (for replacements)", type="xlsx", key="story_excel")
    uploaded_html_story = st.file_uploader("Upload the HTML file", type="html", key="story_html")
    
    if uploaded_excel_story and uploaded_html_story:
        df_story = pd.read_excel(uploaded_excel_story, header=None)
        html_content_template_story = uploaded_html_story.read().decode('utf-8')
        placeholders_story = df_story.iloc[0].tolist()
    
        zip_buffer_story = io.BytesIO()
        with zipfile.ZipFile(zip_buffer_story, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for row_index in range(1, len(df_story)):
                actual_values_story = df_story.iloc[row_index].tolist()
                html_content_story = html_content_template_story
    
                for placeholder, actual_value in zip(placeholders_story, actual_values_story):
                    html_content_story = html_content_story.replace(str(placeholder), str(actual_value))
    
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename_story = f"story_template_{actual_values_story[6]}_{timestamp}.html"
                zip_file.writestr(output_filename_story, html_content_story)
    
        zip_buffer_story.seek(0)
        st.download_button(
            label="Download All Modified HTML Files as ZIP (Story Generator)",
            data=zip_buffer_story,
            file_name="modified_html_story_templates.zip",
            mime="application/zip"
        )
        st.success("All HTML content has been modified and saved in a ZIP file.")
    else:
        st.info("Please upload both an Excel file and an HTML file for the Story Generator.")

# Tab 3: Insert Lines into HTML
with tab3:
    st.header('Insert Lines into HTML')

    uploaded_html_insert = st.file_uploader("Upload the HTML file to modify", type="html", key="insert_html")
    uploaded_excel_insert = st.file_uploader("Upload Excel/CSV file with content and line numbers", type=["xlsx", "csv"], key="insert_excel")

    if uploaded_html_insert and uploaded_excel_insert:
        if uploaded_excel_insert.name.endswith('.xlsx'):
            df_insert = pd.read_excel(uploaded_excel_insert)
        elif uploaded_excel_insert.name.endswith('.csv'):
            df_insert = pd.read_csv(uploaded_excel_insert)
        
        content_list = df_insert.iloc[0].dropna().tolist()
        line_number_list = df_insert.iloc[1].dropna().tolist()

        if uploaded_html_insert:
            st.write(f"Processing HTML file: {uploaded_html_insert.name}")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            base_name, ext = os.path.splitext(uploaded_html_insert.name)
            output_filename = f"{base_name}_{timestamp}{ext}"

            for content, line_number in zip(content_list, line_number_list):
                try:
                    output_file = insert_line_in_html(uploaded_html_insert, int(line_number), content, output_filename)
                    st.success(f"Modified HTML saved as: {output_file}")
                    st.download_button(label="Download Modified File", data=output_file, file_name=output_filename)
                except Exception as e:
                    st.error(f"Error: {e}")

# Tab 4: Remove Lines from HTML
with tab4:
    st.header('Remove Lines from HTML')

    uploaded_html_remove = st.file_uploader("Upload the HTML file to modify", type="html", key="remove_html")
    uploaded_excel_remove = st.file_uploader("Upload Excel/CSV file with line numbers to remove", type=["xlsx", "csv"], key="remove_excel")

    if uploaded_html_remove and uploaded_excel_remove:
        if uploaded_excel_remove.name.endswith('.xlsx'):
            df_remove = pd.read_excel(uploaded_excel_remove)
        elif uploaded_excel_remove.name.endswith('.csv'):
            df_remove = pd.read_csv(uploaded_excel_remove)

        line_numbers_to_remove = df_remove.iloc[0].dropna().tolist()

        if uploaded_html_remove:
            st.write(f"Processing HTML file: {uploaded_html_remove.name}")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            base_name, ext = os.path.splitext(uploaded_html_remove.name)
            output_filename = f"{base_name}_{timestamp}{ext}"

            try:
                output_file = remove_lines_from_html(uploaded_html_remove, line_numbers_to_remove, output_filename)
                st.success(f"Modified HTML saved as: {output_file}")
                st.download_button(label="Download Modified File", data=output_file, file_name=output_filename)
            except Exception as e:
                st.error(f"Error: {e}")

# Functions for inserting/removing lines from HTML
def insert_line_in_html(input_file, line_to_insert, content_to_insert, output_file=None):
    input_file.seek(0)
    lines = input_file.read().decode('utf-8').splitlines()

    if line_to_insert < 1 or line_to_insert > len(lines) + 1:
        raise ValueError(f"Line number {line_to_insert} is out of range. The file has {len(lines)} lines.")

    lines.insert(line_to_insert - 1, content_to_insert)

    if not output_file:
        output_file = input_file.name
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines("\n".join(lines))

    return output_file

def remove_lines_from_html(input_file, lines_to_remove, output_file=None):
    input_file.seek(0)
    lines = input_file.read().decode('utf-8').splitlines()

    if any(line < 1 or line > len(lines) for line in lines_to_remove):
        raise ValueError(f"Some line numbers are out of range. The file has {len(lines)} lines.")

    lines_to_remove.sort(reverse=True)

    for line_number in lines_to_remove:
        del lines[line_number - 1]

    if not output_file:
        output_file = input_file.name
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines("\n".join(lines))

    return output_file
