#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st

st.title("KPI Check Tool")

st.header("Step 1: Upload your data files")

uploaded_admitted   = st.file_uploader("Upload Admitted List (.xlsx)",    type="xlsx")
uploaded_enrollment = st.file_uploader("Upload Enrollment List (.xlsx)",  type="xlsx")
uploaded_attendance = st.file_uploader("Upload Attendance List (.xlsx)",  type="xlsx")
uploaded_cert       = st.file_uploader("Upload Certificate List (.xlsx)", type="xlsx")
uploaded_namelist   = st.file_uploader("Upload Name List (.xlsx)",        type="xlsx")

if all([uploaded_admitted, uploaded_enrollment, uploaded_attendance, uploaded_cert, uploaded_namelist]):

    # ── File Loading ─────────────────────────────────────────
    df_admitted   = pd.read_excel(uploaded_admitted,   sheet_name='Application details report', header=0)
    df_enrollment = pd.read_excel(uploaded_enrollment, sheet_name='Detailed Insights Report',    header=0)
    df_attendance = pd.read_excel(uploaded_attendance, dtype={'Module attendance percentage (by session hours)': str})
    df_cert       = pd.read_excel(uploaded_cert,       header=0)
    df_namelist   = pd.read_excel(uploaded_namelist,   header=0)

    st.success("All files uploaded successfully!")

    st.subheader("Preview: Admitted List")
    st.dataframe(df_admitted.head(2))

    st.subheader("Preview: Enrollment List")
    st.dataframe(df_enrollment.head(2))

    st.subheader("Preview: Attendance List")
    st.dataframe(df_attendance.head(2))

    st.subheader("Preview: Certificate List")
    st.dataframe(df_cert.head(2))

    st.subheader("Preview: Name List")
    st.dataframe(df_namelist.head(2))

    # ================================================================
    # PASTE ALL YOUR BLOCKS BELOW HERE (Block 1 through Block 7)
    # Make sure every line is indented at this same level
    # ================================================================

    # Block 1 ...
    # ============================================================
    # BLOCK 1.1: Date Filter
    # ============================================================
    
    st.header("Step 2: Set Date Filter")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=pd.Timestamp('2026-01-01'))
    with col2:
        end_date = st.date_input("End date", value=pd.Timestamp('2026-04-30'))
    
    start_date = pd.Timestamp(start_date)
    end_date   = pd.Timestamp(end_date)
    
    # Convert course end date columns to datetime
    df_admitted['Course end date']              = pd.to_datetime(df_admitted['Course end date'],              dayfirst=True,       errors='coerce')
    df_enrollment['Course intake end date']     = pd.to_datetime(df_enrollment['Course intake end date'],     format='%d %b %Y',   errors='coerce')
    df_attendance['Course end date']            = pd.to_datetime(df_attendance['Course end date'],            dayfirst=True,       errors='coerce')
    df_cert['Course End Date']                  = pd.to_datetime(df_cert['Course End Date'],                  dayfirst=True,       errors='coerce')
    
    # Apply date filter
    df_admitted    = df_admitted[(df_admitted['Course end date']           >= start_date) & (df_admitted['Course end date']           <= end_date)]
    df_enrollment  = df_enrollment[(df_enrollment['Course intake end date'] >= start_date) & (df_enrollment['Course intake end date'] <= end_date)]
    df_attendance  = df_attendance[(df_attendance['Course end date']        >= start_date) & (df_attendance['Course end date']        <= end_date)]
    df_cert        = df_cert[(df_cert['Course End Date']                    >= start_date) & (df_cert['Course End Date']               <= end_date)]
    
    # ============================================================
    # BLOCK 1.2: Attendance Filter
    # ============================================================
    
    st.header("Step 3: Set Attendance Threshold")
    
    attendance_threshold = st.slider("Minimum attendance % (by session)", min_value=0, max_value=100, value=80)
    
    df_attendance['Attendance % (by session)'] = pd.to_numeric(
        df_attendance['Module attendance percentage (by session number)'].str.replace('%', '', regex=False),
        errors='coerce'
    )
    
    df_attendance = df_attendance[df_attendance['Attendance % (by session)'] >= attendance_threshold]
    
    # Summary table
    st.subheader("Dataset Summary After Filters")
    st.dataframe(pd.DataFrame({
        'DataFrame':             ['df_admitted', 'df_enrollment', 'df_attendance', 'df_cert'],
        'Rows After Date Filter': [len(df_admitted), len(df_enrollment), len(df_attendance), len(df_cert)]
    }))
    
    st.info(f"Rows in df_attendance after attendance filter (>= {attendance_threshold}%): {len(df_attendance)}")

    # Block 2 ...
    # ============================================================
    # BLOCK 2.1: Deduplication
    # ============================================================
    
    st.header("Step 4: Deduplication")
    
    admitted_dups = df_admitted[df_admitted.duplicated(
        subset=['Learner name', 'Course intake No.'], keep=False
    )].copy()
    admitted_dups['source_df'] = 'df_admitted'
    admitted_dups['duplicate_key'] = 'Learner name + Course intake No.'
    
    admitted_dups_email = df_admitted[df_admitted.duplicated(
        subset=['Email address', 'Course intake No.'], keep=False
    )].copy()
    admitted_dups_email['source_df'] = 'df_admitted'
    admitted_dups_email['duplicate_key'] = 'Email address + Course intake No.'
    
    enrollment_dups = df_enrollment[df_enrollment.duplicated(
        subset=['Course intake No.'], keep=False
    )].copy()
    enrollment_dups['source_df'] = 'df_enrollment'
    enrollment_dups['duplicate_key'] = 'Course intake No.'
    enrollment_dups['Learner name'] = None
    enrollment_dups['Email address'] = None
    
    attendance_dups = df_attendance[df_attendance.duplicated(
        subset=['Learner name', 'Course intake No.'], keep=False
    )].copy()
    attendance_dups['source_df'] = 'df_attendance'
    attendance_dups['duplicate_key'] = 'Learner name + Course intake No.'
    attendance_dups = attendance_dups.rename(columns={'Learner email address': 'Email address'})
    
    attendance_dups_email = df_attendance[df_attendance.duplicated(
        subset=['Learner email address', 'Course intake No.'], keep=False
    )].copy()
    attendance_dups_email['source_df'] = 'df_attendance'
    attendance_dups_email['duplicate_key'] = 'Email address + Course intake No.'
    attendance_dups_email = attendance_dups_email.rename(columns={'Learner email address': 'Email address'})
    
    cert_dups = df_cert[df_cert.duplicated(
        subset=['Learner name', 'Course intake No.'], keep=False
    )].copy()
    cert_dups['source_df'] = 'df_cert'
    cert_dups['duplicate_key'] = 'Learner name + Course intake No.'
    cert_dups = cert_dups.rename(columns={'Email Address': 'Email address'})
    
    cert_dups_email = df_cert[df_cert.duplicated(
        subset=['Email Address', 'Course intake No.'], keep=False
    )].copy()
    cert_dups_email['source_df'] = 'df_cert'
    cert_dups_email['duplicate_key'] = 'Email address + Course intake No.'
    cert_dups_email = cert_dups_email.rename(columns={'Email Address': 'Email address'})
    
    dup_cols = ['source_df', 'duplicate_key', 'Course intake No.', 'Learner name', 'Email address']
    
    all_duplicates = pd.concat([
        admitted_dups[dup_cols],
        admitted_dups_email[dup_cols],
        enrollment_dups[dup_cols],
        attendance_dups[dup_cols],
        attendance_dups_email[dup_cols],
        cert_dups[dup_cols],
        cert_dups_email[dup_cols]
    ], ignore_index=True).sort_values(['source_df', 'Course intake No.', 'Learner name'])
    
    # Fixed variable name (was all_duplicates_st.dataframe)
    all_duplicates_display = all_duplicates.drop_duplicates(
        subset=['source_df', 'Course intake No.', 'Learner name']
    )
    
    dup_counts = (
        all_duplicates_display
        .groupby('source_df')
        .size()
        .reset_index(name='Unique Duplicate Records')
    )
    
    st.subheader("Duplicate Record Counts")
    st.dataframe(dup_counts)
    
    st.subheader("Duplicate Records (deduplicated view)")
    st.dataframe(all_duplicates_display)
    
    # ============================================================
    # BLOCK 2.2: Preview Duplicate Rows (Kept vs Removed)
    # ============================================================
    
    st.subheader("Duplicate Rows: Kept vs Removed")
    
    def preview_dups(df, name_col, email_col, intake_col, label):
        name_dups  = df[df.duplicated(subset=[name_col,  intake_col], keep=False)].copy()
        email_dups = df[df.duplicated(subset=[email_col, intake_col], keep=False)].copy()
    
        combined = pd.concat([name_dups, email_dups]).drop_duplicates()
    
        if len(combined) == 0:
            st.info(f"{label}: No duplicates found.")
            return
    
        step1 = df.drop_duplicates(subset=[name_col,  intake_col], keep='first')
        step2 = step1.drop_duplicates(subset=[email_col, intake_col], keep='first')
        kept_indices = set(step2.index)
    
        combined = combined.copy()
        combined['Action'] = combined.index.map(
            lambda i: 'KEEP' if i in kept_indices else 'REMOVE'
        )
    
        sorted_combined = combined.sort_values([intake_col, name_col])
        cols_to_show = list(sorted_combined.columns[:7]) + ['Action']
    
        st.write(f"**{label} — Duplicates (Kept vs Removed)**")
        st.dataframe(sorted_combined[cols_to_show])
    
    preview_dups(df_admitted,   'Learner name', 'Email address',         'Course intake No.', 'df_admitted')
    preview_dups(df_attendance, 'Learner name', 'Learner email address',  'Course intake No.', 'df_attendance')
    preview_dups(df_cert,       'Learner name', 'Email Address',          'Course intake No.', 'df_cert')
    
    # ============================================================
    # Clean dataframes
    # ============================================================
    
    def dedup_by_name_and_email(df, name_col, email_col, intake_col):
        step1 = df.drop_duplicates(subset=[name_col,  intake_col], keep='first')
        step2 = step1.drop_duplicates(subset=[email_col, intake_col], keep='first')
        return step2.reset_index(drop=True)
    
    df_admitted_clean   = dedup_by_name_and_email(df_admitted,   'Learner name', 'Email address',        'Course intake No.')
    df_enrollment_clean = df_enrollment.drop_duplicates(subset=['Course intake No.'], keep='first').reset_index(drop=True)
    df_attendance_clean = dedup_by_name_and_email(df_attendance, 'Learner name', 'Learner email address', 'Course intake No.')
    df_cert_clean       = dedup_by_name_and_email(df_cert,       'Learner name', 'Email Address',         'Course intake No.')
    
    summary_dedup = pd.DataFrame({
        'DataFrame':    ['df_admitted', 'df_enrollment', 'df_attendance', 'df_cert'],
        'Before Clean': [len(df_admitted),       len(df_enrollment),       len(df_attendance),       len(df_cert)],
        'After Clean':  [len(df_admitted_clean), len(df_enrollment_clean), len(df_attendance_clean), len(df_cert_clean)],
    })
    summary_dedup['Rows Removed'] = summary_dedup['Before Clean'] - summary_dedup['After Clean']
    
    st.subheader("Deduplication Summary")
    st.dataframe(summary_dedup)

    # Block 3 ...
    # =====================================================================
    # BLOCK 3: Data Quality Checks — df_attendance, df_admitted, df_cert
    # =====================================================================
    
    import re
    
    st.header("Step 5: Data Quality Checks")
    
    def is_email(val):
        return bool(re.match(r'^[\w\.\+\-]+@[\w\.\-]+\.\w+$', str(val).strip()))
    
    def run_dq_checks(df, label, name_col, email_col, id_col):
        email_as_name  = df[df[name_col].apply(is_email)]
        missing_email  = df[df[email_col].isna() | (df[email_col].astype(str).str.strip() == '')]
        email_as_id    = df[df[id_col].apply(is_email)]
        missing_id     = df[df[id_col].isna() | (df[id_col].astype(str).str.strip() == '')]
        duplicate_rows = df[df.duplicated(keep=False)]
    
        counts = {
            'DataFrame'      : label,
            'Email as Name'  : email_as_name[name_col].nunique(),
            'Missing Email'  : missing_email[name_col].nunique(),
            'Email as ID'    : email_as_id[name_col].nunique(),
            'Missing ID'     : missing_id[name_col].nunique(),
            'Duplicate Rows' : len(duplicate_rows),
        }
    
        details = {
            'email_as_name' : email_as_name,
            'missing_email' : missing_email,
            'email_as_id'   : email_as_id,
            'missing_id'    : missing_id,
            'duplicate_rows': duplicate_rows,
        }
    
        return counts, details, name_col, email_col, id_col
    
    # ── Run checks ────────────────────────────────────────────────
    results = [
        run_dq_checks(df_attendance_clean, 'df_attendance_clean', 'Learner name', 'Learner email address', 'Learner ID'),
        run_dq_checks(df_admitted_clean,   'df_admitted_clean',   'Learner name', 'Email address',         'Learner ID'),
        run_dq_checks(df_cert_clean,       'df_cert_clean',       'Learner name', 'Email Address',         'Learner ID'),
    ]
    
    # ── Consolidated Summary Table ────────────────────────────────
    st.subheader("Summary: Data Quality Checks (Distinct Learners)")
    summary_dq = pd.DataFrame([r[0] for r in results])
    st.dataframe(summary_dq)
    
    # ── Detail Breakdowns ─────────────────────────────────────────
    check_labels = {
        'email_as_name' : 'Email as Learner Name',
        'missing_email' : 'Missing Email Address',
        'email_as_id'   : 'Email as Learner ID',
        'missing_id'    : 'Missing Learner ID',
        'duplicate_rows': 'Duplicate Rows (Exact)',
    }
    
    st.subheader("Detail Breakdowns by DataFrame")
    
    for counts, details, name_col, email_col, id_col in results:
        label = counts['DataFrame']
        any_issues = any(v > 0 for k, v in counts.items() if k != 'DataFrame')
    
        if not any_issues:
            st.info(f"{label}: No issues found.")
            continue
    
        with st.expander(f"Detail: {label}", expanded=True):
            for key, title in check_labels.items():
                df_issue = details[key]
                if len(df_issue) > 0:
                    st.write(f"**{title}**")
                    st.dataframe(df_issue[['Course intake No.', id_col, name_col, email_col]].reset_index(drop=True))
                    
    # Block 4 ...
    # ============================================================
    # BLOCK 4: Overview Summary + Enrolment vs Attendance Check
    # ============================================================
    
    st.header("Step 6: Overview Summary")
    
    total_unique_intakes = pd.concat([
        df_admitted_clean['Course intake No.'],
        df_enrollment_clean['Course intake No.'],
        df_attendance_clean['Course intake No.'],
        df_cert_clean['Course intake No.']
    ]).nunique()
    
    total_admitted = len(df_admitted_clean)
    total_enrolled = df_enrollment_clean['No. of enrollments'].sum()
    total_attended = len(df_attendance_clean)
    total_cert     = len(df_cert_clean)
    
    summary_overview = pd.DataFrame({
        'Metric': [
            'Unique Course Intake No.',
            'Total Learners (Admitted)',
            'Total Learners (Enrolled)',
            'Total Learners (Attended)',
            'Total Learners (Cert Issued)',
        ],
        'Count': [
            total_unique_intakes,
            total_admitted,
            total_enrolled,
            total_attended,
            total_cert,
        ]
    })
    
    st.subheader("Overview: Learner Counts Across Application Status")
    st.dataframe(summary_overview)
    
    # ── Enrolment vs Attendance Discrepancy ───────────────────────
    st.subheader("Enrolment vs Attendance — Course Intake Level")
    
    enrolled_counts = (
        df_admitted_clean.groupby('Course intake No.')['Learner name']
        .count()
        .reset_index()
        .rename(columns={'Learner name': 'Enrolled'})
    )
    
    attended_counts = (
        df_attendance_clean.groupby('Course intake No.')['Learner name']
        .count()
        .reset_index()
        .rename(columns={'Learner name': 'Attended'})
    )
    
    discrepancy = (
        enrolled_counts
        .merge(attended_counts, on='Course intake No.', how='outer')
        .fillna(0)
    )
    
    discrepancy['Enrolled']   = discrepancy['Enrolled'].astype(int)
    discrepancy['Attended']   = discrepancy['Attended'].astype(int)
    discrepancy['Difference'] = discrepancy['Enrolled'] - discrepancy['Attended']
    discrepancy['Match']      = discrepancy['Difference'] == 0
    
    discrepancy = discrepancy.sort_values('Difference', ascending=False).reset_index(drop=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Intakes Checked", len(discrepancy))
    col2.metric("Exact Matches",         int(discrepancy['Match'].sum()))
    col3.metric("Discrepancies",         int((~discrepancy['Match']).sum()))
    
    st.write("**All Intakes**")
    st.dataframe(discrepancy)
    
    st.write("**Discrepancies Only (Attended > Enrolled)**")
    attended_gt_enrolled = discrepancy[discrepancy['Difference'] < 0].reset_index(drop=True)
    if len(attended_gt_enrolled) == 0:
        st.success("No discrepancies found where Attended > Enrolled.")
    else:
        st.dataframe(attended_gt_enrolled)
        
    # Block 5 ...
    # ============================================================
    # BLOCK 5.1: Adding 'No. of Trainee Days' to Attendance List
    # ============================================================
    
    st.header("Step 7: Calculate No. of Trainee Days")
    
    # ── Singapore Public Holidays CY2026 ────────────────────────
    sg_public_holidays_2026 = pd.to_datetime([
        '2026-01-01',  # New Year's Day
        '2026-02-17',  # Chinese New Year
        '2026-02-18',  # Chinese New Year
        '2026-03-21',  # Hari Raya Puasa
        '2026-04-03',  # Good Friday
        '2026-05-01',  # Labour Day
        '2026-05-27',  # Hari Raya Haji
        '2026-05-31',  # Vesak Day
        '2026-06-01',  # Vesak Day in lieu
        '2026-08-09',  # National Day
        '2026-08-10',  # National Day in lieu
        '2026-11-08',  # Deepavali
        '2026-11-09',  # Deepavali in lieu
        '2026-12-25',  # Christmas Day
    ])
    
    sg_holidays_np = np.array(
        [d.strftime('%Y-%m-%d') for d in sg_public_holidays_2026], dtype='datetime64[D]'
    )
    
    # ── Course Duration Function ─────────────────────────────────
    def calculate_course_duration(start, end):
        if pd.isna(start) or pd.isna(end):
            return 0
        if start.weekday() >= 5:  # Weekend start → calendar days
            return (end - start).days + 1
        else:                     # Weekday start → working days excl. SG holidays
            return np.busday_count(
                start.date(),
                (end + pd.Timedelta(days=1)).date(),
                holidays=sg_holidays_np
            )
    
    # ── Parse dates (duplicates removed) ────────────────────────
    df_attendance_clean['Course start date'] = pd.to_datetime(df_attendance_clean['Course start date'])
    df_attendance_clean['Course end date']   = pd.to_datetime(df_attendance_clean['Course end date'])
    
    # ── Split into separate date and time columns ────────────────
    df_attendance_clean['Course start date (date)'] = df_attendance_clean['Course start date'].dt.date
    df_attendance_clean['Course start date (time)'] = df_attendance_clean['Course start date'].dt.time
    df_attendance_clean['Course end date (date)']   = df_attendance_clean['Course end date'].dt.date
    df_attendance_clean['Course end date (time)']   = df_attendance_clean['Course end date'].dt.time
    
    # ── Attendance % ─────────────────────────────────────────────
    df_attendance_clean['Attendance % (by session)'] = pd.to_numeric(
        df_attendance_clean['Module attendance percentage (by session number)'].str.replace('%', '', regex=False),
        errors='coerce'
    ) / 100
    
    # ── Calculate course duration ────────────────────────────────
    df_attendance_clean['Course duration (days)'] = df_attendance_clean.apply(
        lambda r: calculate_course_duration(r['Course start date'], r['Course end date']), axis=1
    )
    
    # ── Append No of Trainee Days ────────────────────────────────
    df_attendance_clean['No of Trainee Days'] = (
        df_attendance_clean['Course duration (days)'] * df_attendance_clean['Attendance % (by session)']
    ).round(2)
    
    # ── Sanity check ─────────────────────────────────────────────
    st.subheader("Sanity Check")
    
    col1, col2 = st.columns(2)
    col1.metric("Rows in df_attendance_clean",       len(df_attendance_clean))
    col2.metric("Null values in No of Trainee Days", int(df_attendance_clean['No of Trainee Days'].isna().sum()))
    
    st.write("**Sample: Key Computed Columns (first 10 rows)**")
    st.dataframe(df_attendance_clean[[
        'Course start date',
        'Course end date',
        'Course duration (days)',
        'Attendance % (by session)',
        'No of Trainee Days'
    ]].head(10))
    
    st.write("**Sample: Last 12 Columns (first 2 rows)**")
    st.dataframe(df_attendance_clean.iloc[:2, -12:])

    # ===================================================================
    # BLOCK 5.2: Adding 'Country of Organisation' to Attendance List
    # ===================================================================
    
    st.header("Step 8: Add 'Country of Organisation' to Attendance List")
    
    # ── Build admitted lookup (Learner ID + intake → country) ────
    admitted_lookup = df_admitted_clean[
        ['Course intake No.', 'Learner ID', 'Country/Region of organization']
    ].copy()
    admitted_lookup['Course intake No.'] = admitted_lookup['Course intake No.'].str.strip()
    admitted_lookup['Learner ID']        = admitted_lookup['Learner ID'].astype(str).str.strip()
    
    # ── Prep keys in df_attendance_clean ─────────────────────────
    df_attendance_clean['Course intake No.'] = df_attendance_clean['Course intake No.'].str.strip()
    df_attendance_clean['Learner ID']        = df_attendance_clean['Learner ID'].astype(str).str.strip()
    
    # ── Merge country ─────────────────────────────────────────────
    df_attendance_clean = df_attendance_clean.merge(
        admitted_lookup,
        on=['Course intake No.', 'Learner ID'],
        how='left'
    ).rename(columns={'Country/Region of organization': 'Country of Organisation'})
    
    # ── Drop any duplicate columns from previous runs ────────────
    df_attendance_clean = df_attendance_clean.loc[:, ~df_attendance_clean.columns.duplicated()]
    
    # ── Standardise Country of Organisation ──────────────────────
    df_attendance_clean['Country of Organisation'] = (
        df_attendance_clean['Country of Organisation']
        .str.strip()
        .str.upper()
    )
    
    # ── Email domain → country mapping ───────────────────────────
    email_domain_map = {
        '.bn'              : 'SINGAPORE',
        '.sn'              : 'SENEGAL',
        'inac.st'          : 'SAO TOME & PRINCIPE',
        'caa.co.zm'        : 'ZAMBIA',
        'co.zm'            : 'ZAMBIA',
        'yahoo.fr'         : 'FRANCE',
        'com.sg'           : 'SINGAPORE',
        'gov.sg'           : 'SINGAPORE',
        'defence.gov.sg'   : 'SINGAPORE',
    }
    
    def fill_country_from_email(row):
        if pd.notna(row['Country of Organisation']) and row['Country of Organisation'] != '':
            return row['Country of Organisation']
        email = str(row['Learner email address']).strip().lower()
        for domain, country in email_domain_map.items():
            if email.endswith(domain):
                return country
        return row['Country of Organisation']
    
    df_attendance_clean['Country of Organisation'] = df_attendance_clean.apply(
        fill_country_from_email, axis=1
    )
    
    # ── Company name → country fallback mapping ───────────────────
    company_country_map = {
        'republic of singapore navy'                    : 'SINGAPORE',
        'changi airport group (singapore) pte. ltd.'    : 'SINGAPORE',
        'caas in-region training'                       : 'INTERNATIONAL',
        'technocrete pte ltd'                           : 'SINGAPORE',
        'lam chuan construction pte ltd'                : 'SINGAPORE',
        'zhengda corporation pte. ltd.'                 : 'SINGAPORE',
    }
    
    def fill_country_from_company(row):
        if pd.notna(row['Country of Organisation']) and row['Country of Organisation'] != '':
            return row['Country of Organisation']
        company = str(row.get('Company name', '')).strip().lower()
        return company_country_map.get(company, row['Country of Organisation'])
    
    df_attendance_clean['Country of Organisation'] = df_attendance_clean.apply(
        fill_country_from_company, axis=1
    )
    
    # ── Sanity check ──────────────────────────────────────────────
    st.subheader("Sanity Check")
    
    col1, col2 = st.columns(2)
    col1.metric("Total Rows",                    len(df_attendance_clean))
    col2.metric("Country of Organisation Filled", int(df_attendance_clean['Country of Organisation'].notna().sum()))
    
    st.write("**Country of Organisation — Value Counts**")
    country_counts = (
        df_attendance_clean['Country of Organisation']
        .value_counts(dropna=False)
        .rename_axis('Country of Organisation')
        .reset_index(name='Count')
    )
    st.dataframe(country_counts)
    
    st.write("**Sample: First 2 Rows**")
    st.dataframe(df_attendance_clean[[
        'Learner name', 'Learner email address',
        'Course intake No.', 'Learner ID',
        'Country of Organisation'
    ]].head(2))
    
    not_filled = df_attendance_clean[df_attendance_clean['Country of Organisation'].isna()]
    st.write(f"**Rows Not Filled: {len(not_filled)}**")
    if len(not_filled) == 0:
        st.success("All rows have a Country of Organisation value.")
    else:
        st.dataframe(not_filled[[
            'Learner name', 'Learner email address',
            'Course intake No.', 'Learner ID',
            'Company name', 'Country of Organisation'
        ]])
    
    caas_inregion = df_attendance_clean[
        df_attendance_clean['Company name'].str.strip().str.lower() == 'caas in-region training'
    ]
    st.write(f"**CAAS In-Region Training Rows: {len(caas_inregion)}**")
    if len(caas_inregion) == 0:
        st.info("No CAAS In-Region Training rows found.")
    else:
        st.dataframe(caas_inregion[[
            'Learner name', 'Learner email address',
            'Course intake No.', 'Company name',
            'Country of Organisation'
        ]])

    # ===================================================================
    # BLOCK 5.3: Adding 'School' to Attendance List
    # ===================================================================
    
    st.header("Step 9: Add 'School' to Attendance List")
    
    # ── Drop column if already exists ────────────────────────────
    df_attendance_clean = df_attendance_clean.drop(columns=['School'], errors='ignore')
    
    # ── Map Course intake No. prefix to School ───────────────────
    manual_mapping = {
        '1000467_1012234': 'AVS',
        '1000468_1012235': 'AVS',
        '1000874_1012233': 'ATS',
    }
    
    def map_school(intake):
        if pd.isna(intake):
            return 'Others'
        intake = str(intake).strip()
        if intake in manual_mapping:
            return manual_mapping[intake]
        elif intake.startswith('AES'):
            return 'AES'
        elif intake.startswith('AVS'):
            return 'AVS'
        elif intake.startswith('ATS'):
            return 'ATS'
        elif intake.startswith('AMS'):
            return 'AMS'
        else:
            return 'Others'
    
    df_attendance_clean['School'] = df_attendance_clean['Course intake No.'].apply(map_school)
    
    # ── Sanity check ──────────────────────────────────────────────
    st.subheader("Sanity Check")
    
    school_counts = (
        df_attendance_clean['School']
        .value_counts(dropna=False)
        .rename_axis('School')
        .reset_index(name='Count')
    )
    st.write("**School — Value Counts**")
    st.dataframe(school_counts)
    
    others_intakes = df_attendance_clean[
        df_attendance_clean['School'] == 'Others'
    ]['Course intake No.'].unique()
    
    st.write(f"**Intakes Mapped to 'Others': {len(others_intakes)}**")
    if len(others_intakes) == 0:
        st.success("No intakes mapped to 'Others'.")
    else:
        st.dataframe(pd.DataFrame({'Course intake No.': others_intakes}))

    # ===================================================================
    # BLOCK 5.4: Adding 'Designation' to Attendance List
    # ===================================================================
    
    st.header("Step 10: Add 'Designation' to Attendance List")
    
    # ── Drop column if already exists ────────────────────────────
    df_attendance_clean = df_attendance_clean.drop(columns=['Designation'], errors='ignore')
    
    # ── Build designation lookup from df_admitted_clean ──────────
    designation_lookup = df_admitted_clean[[
        'Course intake No.', 'Learner ID', 'Learner name', 'Email address', 'Designation'
    ]].copy()
    
    # ── Attempt 1: Match on Course intake No. + Learner ID ───────
    df_attendance_clean = df_attendance_clean.merge(
        designation_lookup[['Course intake No.', 'Learner ID', 'Designation']],
        on=['Course intake No.', 'Learner ID'],
        how='left'
    )
    
    # ── Attempt 2: Fill unmatched via Course intake No. + Learner name ──
    unmatched_mask = df_attendance_clean['Designation'].isna()
    
    if unmatched_mask.sum() > 0:
        name_lookup = designation_lookup[['Course intake No.', 'Learner name', 'Designation']].rename(
            columns={'Designation': 'Designation_name'}
        )
        df_attendance_clean = df_attendance_clean.merge(
            name_lookup,
            on=['Course intake No.', 'Learner name'],
            how='left'
        )
        df_attendance_clean['Designation'] = df_attendance_clean['Designation'].fillna(
            df_attendance_clean['Designation_name']
        )
        df_attendance_clean = df_attendance_clean.drop(columns=['Designation_name'])
    
    # ── Attempt 3: Fill unmatched via Course intake No. + Email address ──
    unmatched_mask = df_attendance_clean['Designation'].isna()
    
    if unmatched_mask.sum() > 0:
        email_lookup = designation_lookup[['Course intake No.', 'Email address', 'Designation']].rename(
            columns={'Designation': 'Designation_email'}
        )
        df_attendance_clean = df_attendance_clean.merge(
            email_lookup,
            left_on=['Course intake No.', 'Learner email address'],
            right_on=['Course intake No.', 'Email address'],
            how='left'
        )
        df_attendance_clean['Designation'] = df_attendance_clean['Designation'].fillna(
            df_attendance_clean['Designation_email']
        )
        df_attendance_clean = df_attendance_clean.drop(columns=['Designation_email', 'Email address'], errors='ignore')
    
    # ── Sanity check ─────────────────────────────────────────────
    st.subheader("Sanity Check")
    
    matched   = int(df_attendance_clean['Designation'].notna().sum())
    unmatched = int(df_attendance_clean['Designation'].isna().sum())
    
    col1, col2 = st.columns(2)
    col1.metric("Designation Matched",   matched)
    col2.metric("Designation Unmatched", unmatched)
    
    # ── Side-by-side comparison for unmatched rows ───────────────
    if unmatched > 0:
        unmatched_df = df_attendance_clean[df_attendance_clean['Designation'].isna()][[
            'Course intake No.', 'Learner ID', 'Learner name', 'Learner email address'
        ]].copy().reset_index(drop=True)
    
        comparison_rows = []
    
        for _, row in unmatched_df.iterrows():
            intake     = row['Course intake No.']
            learner_id = row['Learner ID']
            name       = row['Learner name']
            email      = row['Learner email address']
    
            admitted_same_intake = df_admitted_clean[df_admitted_clean['Course intake No.'] == intake]
    
            candidate = admitted_same_intake[admitted_same_intake['Learner ID'].astype(str) == str(learner_id)]
            if candidate.empty:
                candidate = admitted_same_intake[admitted_same_intake['Learner name'] == name]
            if candidate.empty:
                candidate = admitted_same_intake[admitted_same_intake['Email address'] == email]
    
            if not candidate.empty:
                adm = candidate.iloc[0]
                comparison_rows.append({
                    'Course intake No.'  : intake,
                    '[ATT] Learner ID'   : learner_id,
                    '[ADM] Learner ID'   : adm['Learner ID'],
                    'ID match?'          : str(learner_id) == str(adm['Learner ID']),
                    '[ATT] Learner name' : name,
                    '[ADM] Learner name' : adm['Learner name'],
                    'Name match?'        : name == adm['Learner name'],
                    '[ATT] Email'        : email,
                    '[ADM] Email'        : adm['Email address'],
                    'Email match?'       : email == adm['Email address'],
                })
            else:
                comparison_rows.append({
                    'Course intake No.'  : intake,
                    '[ATT] Learner ID'   : learner_id,
                    '[ADM] Learner ID'   : 'NOT FOUND',
                    'ID match?'          : False,
                    '[ATT] Learner name' : name,
                    '[ADM] Learner name' : 'NOT FOUND',
                    'Name match?'        : False,
                    '[ATT] Email'        : email,
                    '[ADM] Email'        : 'NOT FOUND',
                    'Email match?'       : False,
                })
    
        st.write("**Side-by-Side Comparison: Unmatched Learners**")
        st.dataframe(pd.DataFrame(comparison_rows))
    
    # ── Empty Designation checks ──────────────────────────────────
    att_empty = int(df_attendance_clean['Designation'].isna().sum())
    adm_empty = int(df_admitted_clean['Designation'].isna().sum())
    
    col1, col2 = st.columns(2)
    col1.metric("Empty Designation (Attendance)", att_empty)
    col2.metric("Empty Designation (Admitted)",   adm_empty)
    
    if att_empty > 0:
        st.write("**Rows with Empty Designation — df_attendance_clean**")
        st.dataframe(df_attendance_clean[df_attendance_clean['Designation'].isna()][[
            'Course intake No.', 'Learner ID', 'Learner name',
            'Learner email address', 'Designation'
        ]].reset_index(drop=True))
    
    if adm_empty > 0:
        st.write("**Rows with Empty Designation — df_admitted_clean**")
        st.dataframe(df_admitted_clean[df_admitted_clean['Designation'].isna()][[
            'Course intake No.', 'Learner ID', 'Learner name',
            'Email address', 'Designation'
        ]].reset_index(drop=True))

    # ===================================================================
    # BLOCK 5.5: Checking Trainee Count and Days for Non-Course Events
    # ===================================================================
    
    st.header("Step 11: Check Trainee Count and Days for Non-Course Events")
    
    intakes = ['CAS-0001', 'AMS-0001', 'AMS-0002']
    df_check = df_namelist[df_namelist['Course Intake Number'].isin(intakes)].copy()
    
    # ── Classify as Local or International ───────────────────────
    df_check['Type'] = df_check['Country'].apply(
        lambda x: 'Local' if str(x).strip().lower() == 'singapore' else 'International'
    )
    
    # ── Headcount by Intake and Type ─────────────────────────────
    st.subheader("Headcount by Intake and Type")
    headcount = (
        df_check.groupby(['Course Intake Number', 'Type'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    st.dataframe(headcount)
    
    # ── Total Trainee Days by Intake and Type ────────────────────
    st.subheader("Total Trainee Days by Intake and Type")
    trainee_days = (
        df_check.groupby(['Course Intake Number', 'Type'])['No. of Trainee Days']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    st.dataframe(trainee_days)

    # Block 6 ...
    # ================================================================================
    # BLOCK 6: KPI 1 - Trainee Days
    # ================================================================================
    
    st.header("Block 6: KPI 1 — Trainee Days")
    
    # ── Setup ─────────────────────────────────────────────────────
    KPI1_TARGET   = 10000
    REPORT_YEAR   = 2026
    REPORT_MONTHS = [1, 2, 3, 4]
    
    month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr'}
    
    # ── Prep ──────────────────────────────────────────────────────
    df = df_attendance_clean.copy()
    df['Course end date'] = pd.to_datetime(df['Course end date'], dayfirst=True, errors='coerce')
    df['Month']           = df['Course end date'].dt.month
    df['Year']            = df['Course end date'].dt.year
    df['Month Name']      = df['Month'].map(month_map)
    
    # ── Segment Classification ────────────────────────────────────
    CAAS_NAMES = ['civil aviation authority of singapore']
    
    def classify_segment(row):
        country = str(row.get('Country of Organisation', '')).strip().lower()
        org     = str(row.get('Company name', '')).strip().lower()
        if country in ('', 'nan'):
            return 'Unknown'
        if country != 'singapore':
            return 'International'
        if any(caas in org for caas in CAAS_NAMES):
            return 'CAAS'
        return 'Local'
    
    df['Segment'] = df.apply(classify_segment, axis=1)
    
    # ── Filter: Report Year + Months ─────────────────────────────
    df_filtered = df[
        (df['Year'] == REPORT_YEAR) &
        (df['Month'].isin(REPORT_MONTHS))
    ].copy()
    
    # ── Overall Summary ───────────────────────────────────────────
    st.subheader("Overall — Trainee Days by Segment")
    
    overall = (
        df_filtered.groupby('Segment')['No of Trainee Days']
        .sum()
        .reset_index()
        .rename(columns={'No of Trainee Days': 'Trainee Days'})
        .sort_values('Trainee Days', ascending=False)
    )
    st.dataframe(overall)
    
    # ── Helper: render segment summary ───────────────────────────
    def render_segment_summary(label, df_seg, target=None):
        total_days = df_seg['No of Trainee Days'].sum()
    
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Total Trainee Days (Jan–Apr {REPORT_YEAR})", f"{total_days:,.2f}")
        if target:
            col2.metric(f"KPI1 CY{REPORT_YEAR} Target", f"{target:,}")
            col3.metric("% Achieved", f"{(total_days / target) * 100:.2f}%")
    
        st.write("**By School**")
        by_school = (
            df_seg.groupby('School')['No of Trainee Days']
            .sum()
            .reset_index()
            .rename(columns={'No of Trainee Days': 'Trainee Days'})
            .sort_values('Trainee Days', ascending=False)
        )
        st.dataframe(by_school)
    
        st.write("**By Month and School**")
        by_month_school = (
            df_seg.groupby(['Month', 'Month Name', 'School'])['No of Trainee Days']
            .sum()
            .reset_index()
            .rename(columns={'No of Trainee Days': 'Trainee Days'})
            .sort_values(['Month', 'School'])
            .drop(columns='Month')
        )
        st.dataframe(by_month_school)
    
        st.write("**By Month and Course**")
        by_month_course = (
            df_seg.groupby(['Month', 'Month Name', 'School', 'Course name'])['No of Trainee Days']
            .sum()
            .reset_index()
            .rename(columns={'No of Trainee Days': 'Trainee Days'})
            .sort_values(['Month', 'Trainee Days'], ascending=[True, False])
            .drop(columns='Month')
        )
        st.dataframe(by_month_course)
    
    # ── Per-Segment Detail ────────────────────────────────────────
    for label, target in [
        ('International', KPI1_TARGET),
        ('CAAS',          None),
        ('Local',         None),
    ]:
        with st.expander(f"Segment: {label}", expanded=False):
            render_segment_summary(
                label,
                df_filtered[df_filtered['Segment'] == label],
                target=target
            )
    
    # ── Check: Specific Course Intakes ───────────────────────────
    st.subheader("Check: Specific Course Intakes")
    
    check_intakes = ['AMS2502-250011', 'AMS2504-250005', 'AMS2507-250037']
    
    df_check_intakes = df_filtered[df_filtered['Course intake No.'].isin(check_intakes)].copy()
    
    st.write(f"**Total rows found: {len(df_check_intakes)}**")
    st.dataframe(df_check_intakes[[
        'Course intake No.', 'Learner ID', 'Learner name',
        'Segment', 'No of Trainee Days'
    ]].reset_index(drop=True))
    
    st.write("**Breakdown by Course Intake and Segment**")
    st.dataframe(
        df_check_intakes.groupby(['Course intake No.', 'Segment'])['No of Trainee Days']
        .sum()
        .reset_index()
    )
    
    # ── Check: Specific Learner Names in Those Intakes ───────────
    st.subheader("Specific Check: Named Learners in AMS Courses")
    
    check_names = [
        'Glenda Lim', 'Rosalind Tan Hong Yue', 'Samantha Chua Le Ling',
        'Joann Heng Xin Yi', 'KOH AI XIAN BERNICE', 'Cheng Guo Wei',
        'Ng Koh Xin', 'Joy Wang', 'Chan Foong May',
        'PIRAGATHESH S/O SUBRAMANIAN', 'Chen Yiliang', 'Francis Ng',
        'Satwinder Kaur', 'Teo Tian Hong Magnus', 'Goh Yujin', 'Linda Wang'
    ]
    
    check_names_lower = [n.lower().strip() for n in check_names]
    df_check_intakes['_name_lower'] = df_check_intakes['Learner name'].str.lower().str.strip()
    
    df_name_match    = df_check_intakes[
        df_check_intakes['_name_lower'].isin(check_names_lower)
    ].drop(columns='_name_lower')
    
    df_name_no_match = [
        n for n in check_names
        if n.lower().strip() not in df_check_intakes['_name_lower'].values
    ]
    
    col1, col2 = st.columns(2)
    col1.metric("Names Found",     len(df_name_match))
    col2.metric("Names Not Found", len(df_name_no_match))
    
    st.write(f"**Names Found ({len(df_name_match)} rows)**")
    st.dataframe(df_name_match[[
        'Course intake No.', 'Learner ID', 'Learner name',
        'Segment', 'No of Trainee Days'
    ]].reset_index(drop=True))
    
    if df_name_no_match:
        st.write(f"**Names NOT Found in These Intakes ({len(df_name_no_match)})**")
        st.dataframe(pd.DataFrame({'Learner name': df_name_no_match}))
    else:
        st.success("All specified names were found in the selected intakes.")

    # ================================================================================
    # BLOCK 6.1: Checking of CAAS In-region Training Courses
    # ================================================================================
    
    st.header("Block 6.1: Check CAAS In-Region Training Courses")
    
    courses = [
        'AVS2521-260004',
        'AVS2605-260002',
        'AVS2526-260001',
        'AVS2527 (IRT)-260001',
        'AVS2601 (IRT)-260001'
    ]
    
    # ── df_attendance_clean ───────────────────────────────────────
    st.subheader("df_attendance (Learn@SAA)")
    st.dataframe(
        df_attendance_clean[df_attendance_clean['Course intake No.'].isin(courses)]
        .groupby('Course intake No.')['No of Trainee Days']
        .agg(Count='count', Trainee_Days='sum')
        .reindex(courses)
    )
    
    # ── df_namelist ───────────────────────────────────────────────
    st.subheader("df_namelist")
    st.dataframe(
        df_namelist[df_namelist['Course Intake Number'].isin(courses)]
        .groupby('Course Intake Number')['No. of Trainee Days']
        .agg(Count='count', Trainee_Days='sum')
        .reindex(courses)
    )

    # Block 7 ...
    # ================================================================================
    # BLOCK 7: KPI 2 - Trainee Days for Director and Above
    # ================================================================================
    
    st.header("Block 7: KPI 2 — Trainee Days for Director and Above")
    
    # ── Director-and-Above Designation Lists ─────────────────────
    PRIVATE_SECTOR_DESIGNATIONS = {
        'chairman',
        'chief executive officer', 'ceo',
        'president',
        'managing director', 'md',
        'chief operating officer', 'coo',
        'senior executive vice president', 'sevp',
        'executive vice president', 'evp',
        'senior vice president', 'svp',
        'vice president', 'vp',
        'director',
        'general manager', 'gm',
        'deputy general manager', 'dgm',
        'assistant general manager', 'agm',
    }
    
    PUBLIC_SECTOR_DESIGNATIONS = {
        'permanent secretary',
        'ambassador',
        'chief executive officer', 'ceo',
        'director general', 'director-general', 'dg',
        'senior deputy director general', 'senior deputy director-general', 'sddg',
        'deputy director general', 'deputy director-general', 'ddg',
        'assistant director general', 'assistant director-general', 'adg',
        'administrator',
        'director',
        'deputy director',
        'assistant director',
        'general manager',
        'chief',
        'head',
        'section head',
        'acting head',
        'special adviser', 'special advisor',
        'commander / divisional officer',
        'superintendent',
    }
    
    SENIOR_DESIGNATIONS = PRIVATE_SECTOR_DESIGNATIONS | PUBLIC_SECTOR_DESIGNATIONS
    
    KPI2_TARGET = None  # set your target here if applicable
    
    # ── Setup ─────────────────────────────────────────────────────
    df2 = df_attendance_clean.copy()
    df2['Course end date'] = pd.to_datetime(df2['Course end date'], dayfirst=True, errors='coerce')
    df2['Month']           = df2['Course end date'].dt.month
    df2['Year']            = df2['Course end date'].dt.year
    df2['Month Name']      = df2['Month'].map(month_map)
    
    # ── Segment Classification (same logic as KPI 1) ─────────────
    df2['Segment'] = df2.apply(classify_segment, axis=1)
    
    # ── Flag Senior Designations ──────────────────────────────────
    df2['Designation_lower'] = df2['Designation'].str.strip().str.lower()
    df2['Is Senior']         = df2['Designation_lower'].isin(SENIOR_DESIGNATIONS)
    
    # ── Filter: Report Year + Months + Senior only ────────────────
    df2_filtered = df2[
        (df2['Year'] == REPORT_YEAR) &
        (df2['Month'].isin(REPORT_MONTHS)) &
        (df2['Is Senior'] == True)
    ].copy()
    
    # ── Sanity Check ──────────────────────────────────────────────
    st.subheader("Sanity Check")
    
    total_rows    = df2[(df2['Year'] == REPORT_YEAR) & (df2['Month'].isin(REPORT_MONTHS))].shape[0]
    senior_rows   = df2_filtered.shape[0]
    unsenior_rows = total_rows - senior_rows
    
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Total Attendance Rows (Jan–Apr {REPORT_YEAR})", f"{total_rows:,}")
    col2.metric("Senior (Director & Above)",                      f"{senior_rows:,}")
    col3.metric("Non-Senior / Unmatched",                         f"{unsenior_rows:,}")
    
    # ── QC: Designations that did NOT match ───────────────────────
    with st.expander("Designations NOT Classified as Senior (Top 20)", expanded=False):
        unmatched_designations = (
            df2[
                (df2['Year'] == REPORT_YEAR) &
                (df2['Month'].isin(REPORT_MONTHS)) &
                (df2['Is Senior'] == False)
            ]['Designation']
            .dropna()
            .str.strip()
            .str.lower()
            .value_counts()
            .reset_index()
            .rename(columns={'index': 'Designation', 'Designation': 'Count'})
        )
        st.dataframe(unmatched_designations.head(20))
    
    # ── Overall Summary ───────────────────────────────────────────
    st.subheader("Overall — Trainee Days by Segment (Senior Only)")
    
    overall_kpi2 = (
        df2_filtered.groupby('Segment')['No of Trainee Days']
        .sum()
        .reset_index()
        .rename(columns={'No of Trainee Days': 'Trainee Days'})
        .sort_values('Trainee Days', ascending=False)
    )
    st.dataframe(overall_kpi2)
    
    # ── Per-Segment Detail ────────────────────────────────────────
    for label, target in [
        ('International', KPI2_TARGET),
        ('CAAS',          None),
        ('Local',         None),
    ]:
        with st.expander(f"Segment: {label}", expanded=False):
            render_segment_summary(
                label,
                df2_filtered[df2_filtered['Segment'] == label],
                target=target
            )

else:
    st.info("Please upload all 5 files above to proceed.")


# In[ ]:




