import pandas as pd
import streamlit as st
import re
import zipfile
import io
import time

# Streamlit app title
st.title("Generate Your Webstories 😀")

# Create three tabs: Regex Replacer, Master Template Generator, and Story Generator
tab1, tab2, tab3 = st.tabs(["Regex Replacer", "Master Template Generator", "Story Generator"])

# Tab 1: Regex Replacer
with tab1:
    st.header("Regex Replacer")
    
    # Upload HTML file
    uploaded_html_regex = st.file_uploader("Upload the HTML file (for regex replacements)", type="html", key="regex_html")

    # Function to perform regex replacements
    def replace_html_placeholders(html_content):
        replacements = {
            r'lang="en-US"': r'lang="{{lang}}"',
            r'name="amp-story-generator-name" content=".*?"': r'name="amp-story-generator-name" content="{{storygeneratorname}}"',
            r'name="amp-story-generator-version" content=".*?"': r'name="amp-story-generator-version" content="{{storygeneratorversion}}"',
            r'property="og:locale" content=".*?"': r'property="og:locale" content="{{lang}}"',
            r'property="og:site_name" content=".*?"': r'property="og:site_name" content="{{sitename}}"',
            r'property="og:type" content=".*?"': r'property="og:type" content="{{contenttype}}"',
            r'property="og:title" content=".*?"': r'property="og:title" content="{{storytitle}}"',
            r'property="og:url" content=".*?"': r'property="og:url" content="{{canurl}}"',
            r'property="og:description" content=".*?"': r'property="og:description" content="{{metadescription}}"',
            r'property="article:published_time" content=".*?"': r'property="article:published_time" content="{{publishedtime}}"',
            r'property="article:modified_time" content=".*?"': r'property="article:modified_time" content="{{modifiedtime}}"',
            r'property="og:image" content=".*?"': r'property="og:image" content="{{potraitcoverurl}}"',
            r'name="twitter:image" content=".*?"': r'name="twitter:image" content="{{potraitcoverurl}}"',
            r'name="twitter:image:alt" content=".*?"': r'name="twitter:image:alt" content="{{storytitle}}"',
            r'name="generator" content=".*?"': r'name="generator" content="{{generatorplatform}}"',
            r'name="msapplication-TileImage" content=".*?"': r'name="msapplication-TileImage" content="{{msthumbnailcoverurl}}"',
            r'<link.*?rel="preload".*?>': r'<link href="{{potraitcoverurl}}" rel="preload" as="image" />',
            r'<title>.*?</title>': r'<title>{{pagetitle}}</title>',
            r'publisher=".*?"': r'publisher="{{publisher}}"',
            r'publisher-logo-src=".*?"': r'publisher-logo-src="{{publisherlogosrc}}"',
            r'poster-portrait-src=".*?"': r'poster-portrait-src="{{potraitcoverurl}}"',
            r'gtag-id=".*?"': r'gtag-id="{{gtagid}}"'
        }
        for pattern, replacement in replacements.items():
            html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

        # Remove specific lines
        lines_to_remove = [
            r'<link rel="alternate" type="application/rss\+xml".*?>',
            r'<link rel="https://api\.w\.org/".*?>',
            r'<link rel="EditURI".*?>',
            r'<link rel="shortlink".*?>',
            r'<link rel="alternate" title="oEmbed.*?>'
        ]
        for line_pattern in lines_to_remove:
            html_content = re.sub(line_pattern, '', html_content, flags=re.DOTALL)

        return html_content

    if uploaded_html_regex:
        # Read the uploaded HTML file
        html_content_regex = uploaded_html_regex.read().decode('utf-8')

        # Perform regex replacements
        html_content_regex_modified = replace_html_placeholders(html_content_regex)

        # Generate the filename with a timestamp
        timestamp = int(time.time())
        file_name_regex = f"regex_modified_{timestamp}.html"

        # Create a download button for the modified HTML
        st.download_button(
            label="Download Modified HTML with Regex",
            data=html_content_regex_modified,
            file_name=file_name_regex,
            mime="text/html"
        )

        st.success("HTML file processed with regex replacements.")
    else:
        st.info("Please upload an HTML file for regex replacements.")

# Tab 2: Master Template Generator
with tab2:
    st.header("Master Template Generator")

    # File upload for Excel and HTML
    uploaded_excel_master = st.file_uploader("Upload the Excel file (for replacements)", type="xlsx", key="master_excel")
    uploaded_html_master = st.file_uploader("Upload the HTML file", type="html", key="master_html")

    if uploaded_excel_master and uploaded_html_master:
        # Read the Excel file into a DataFrame
        df_master = pd.read_excel(uploaded_excel_master, header=None)

        # Read the uploaded HTML file
        html_content_master = uploaded_html_master.read().decode('utf-8')

        # Get the last row for placeholders
        placeholder_row = df_master.iloc[-1]

        # Loop through each row except the last one (which contains placeholders)
        for row_index in range(len(df_master) - 1):
            # Get the current row data (actual values)
            row_data = df_master.iloc[row_index]

            # Make a copy of the processed HTML content for each row
            html_content_modified = html_content_master

            # Perform replacements for each column
            for col_index in range(len(df_master.columns)):
                actual_value = str(row_data[col_index])      # Actual value from the current row
                placeholder = str(placeholder_row[col_index])  # Placeholder from the last row
                html_content_modified = html_content_modified.replace(placeholder, actual_value)

            # Generate the filename using Unix timestamp
            timestamp = int(time.time())
            file_name = f"modified_template_{timestamp}.html"

            # Create a download button for each modified HTML
            st.download_button(
                label=f"Download Modified HTML for Row {row_index + 1}",
                data=html_content_modified,
                file_name=file_name,
                mime="text/html"
            )

        st.success("HTML content modified for all rows.")
    else:
        st.info("Please upload both an Excel file and an HTML file for the Master Template Generator.")

# Tab 3: Story Generator
with tab3:
    st.header("Story Generator")
    
    # File upload for Excel and HTML
    uploaded_excel_story = st.file_uploader("Upload the Excel file (for replacements)", type="xlsx", key="story_excel")
    uploaded_html_story = st.file_uploader("Upload the HTML file", type="html", key="story_html")

    if uploaded_excel_story and uploaded_html_story:
        # Read the Excel file into a DataFrame
        df_story = pd.read_excel(uploaded_excel_story, header=None)

        # Read the uploaded HTML file
        html_content_template_story = uploaded_html_story.read().decode('utf-8')

        # First row (index 0) contains placeholders like {{storytitle}}, {{coverinfo1}}, etc.
        placeholders_story = df_story.iloc[0, :].tolist()

        # Prepare an in-memory ZIP file to store all modified HTML files
        zip_buffer_story = io.BytesIO()
        with zipfile.ZipFile(zip_buffer_story, "w", zipfile.ZIP_DEFLATED) as zf:
            # Loop through each row from index 1 onward to perform replacements
            for row_index in range(1, len(df_story)):
                actual_values_story = df_story.iloc[row_index, :].tolist()

                # Copy the original HTML template content
                html_content_story = html_content_template_story

                # Perform batch replacement for each placeholder in the row
                for placeholder, actual_value in zip(placeholders_story, actual_values_story):
                    html_content_story = html_content_story.replace(placeholder, str(actual_value))

                # Generate the filename using the first column value and Unix timestamp
                timestamp = int(time.time())
                output_filename_story = f"{actual_values_story[0]}_story_generated_{timestamp}.html"

                # Add the modified HTML content to the in-memory ZIP
                zf.writestr(output_filename_story, html_content_story)

        # Seek to the beginning of the buffer to prepare for download
        zip_buffer_story.seek(0)

        # Create a download button for the ZIP file containing all modified HTML files
        st.download_button(
            label="Download All Modified Story Templates (as ZIP)",
            data=zip_buffer_story,
            file_name="story_templates_modified.zip",
            mime="application/zip"
        )

        st.success("HTML content modified for all rows. Click the button above to download the ZIP file.")
    else:
        st.info("Please upload both an Excel file and an HTML file to proceed.")

