# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from sklearn.impute import SimpleImputer  # AI-Based Cleaning

# Set up our App
st.set_page_config(page_title="Data Sweeper", layout='wide')
st.title("📀 Data Sweeper")
st.write("Transform Your Files between CSV and Excel formats with built-in data cleaning and visualization!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel);", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            try:
                df = pd.read_csv(file, encoding="utf-8", on_bad_lines="skip")  # Skip bad lines
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding="latin1", on_bad_lines="skip")  # Try Latin1 encoding
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display info about the file
        st.markdown(f"**File Name:** {file.name}")    
        st.markdown(f"**File Size:** {file.size/1024:.2f} KB")  # Fixed size formatting

        # Show 5 rows of our df
        st.subheader("🔍 Preview the Head of the Dataframe")  # Replaced st.write with st.subheader
        st.dataframe(df.head())

        # ✅ NEW FEATURE: Data Summary Report
        if st.button(f"📋 Generate Summary Report for {file.name}"):
            st.subheader("📊 Data Summary Report")
            st.markdown(f"**Total Rows:** {df.shape[0]}")
            st.markdown(f"**Total Columns:** {df.shape[1]}")
            st.markdown(f"**Total Missing Values:** {df.isnull().sum().sum()}")
            st.markdown(f"**Total Duplicate Rows:** {df.duplicated().sum()}")
            st.write("📌 **Numerical Data Summary:**")
            st.write(df.describe())

        # Options for data cleaning
        st.subheader("⚙️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"📤Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"📂Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled!")

            # ✅ AI-Based Data Cleaning
            with col3:
                if st.button(f"🤖 AI Clean Data for {file.name}"):
                    # Fill numerical missing values with mean
                    num_imputer = SimpleImputer(strategy="mean")
                    df[df.select_dtypes(include=['number']).columns] = num_imputer.fit_transform(df.select_dtypes(include=['number']))
                    
                    # Fill categorical missing values with most frequent
                    cat_imputer = SimpleImputer(strategy="most_frequent")
                    df[df.select_dtypes(include=['object']).columns] = cat_imputer.fit_transform(df.select_dtypes(include=['object']))
                    
                    st.success("✅ AI-Based Cleaning Applied!")

        # Choose Specific Columns to Keep or Convert
        st.subheader("🎯 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualizations
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization For {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

        # Convert the file -> CSV to Excel
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "EXCEL"], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            file_name = ""
            mime_type = ""  # ✅ Fix: Initialize mime_type to avoid NameError

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False, encoding="utf-8")  # ✅ Removed `errors="replace"`
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "EXCEL":
                df.to_excel(buffer, index=False, engine="openpyxl")
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # ✅ Ensure mime_type is set before showing download button
            if mime_type:
                st.download_button(
                    label=f"⬇️ Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
            else:
                st.error("⚠️ Conversion type not selected properly.")

st.success("🎉 All Files Processed!")
