"""
Where2Work - Company Data Visualization Application

A Streamlit web application for visualizing and filtering company data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from typing import Optional


def load_company_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load and validate company data from CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame containing company data, or None if loading fails
    """
    try:
        df = pd.read_csv(file_path)

        required_columns = [
            'Entity_Legal_Name',
            'Entity_Type',
            'Headquarters_Location',
            'Estimated_Employee_Band',
            'Estimated_Employee_Band_Code',
            'Primary_ANZSIC_Code'
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None

        df['Estimated_Employee_Band'] = df['Estimated_Employee_Band'].str.strip()
        df['Entity_Type'] = df['Entity_Type'].str.strip()
        df['Headquarters_Location'] = df['Headquarters_Location'].str.strip()

        return df

    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None
    except pd.errors.EmptyDataError:
        st.error("The CSV file is empty")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def create_employee_band_order():
    """
    Define the ordering for employee band sizes.

    Returns:
        List of employee band categories in ascending order
    """
    return [
        '1–5 Employees',
        '6–19 Employees',
        '20–49 Employees'
    ]


def create_bubble_chart(df: pd.DataFrame, chart_title: str = "", is_rejected: bool = False) -> None:
    """
    Create an interactive horizontal bubble chart showing companies by employee band.

    Args:
        df: Filtered DataFrame containing company data
        chart_title: Title to display above the chart
        is_rejected: Whether this is the rejected companies chart
    """
    if df.empty:
        if is_rejected:
            st.info("All companies have been added to your shortlist! 🎉")
        else:
            st.info("Your shortlist is empty. Click on bubbles in the 'All Companies' chart below to add companies.")
        return

    if chart_title:
        st.markdown(f"### {chart_title}")

    band_order = create_employee_band_order()

    df_plot = df.copy()
    df_plot['Employee_Band_Clean'] = df_plot['Estimated_Employee_Band'].str.strip()

    unique_bands = df_plot['Employee_Band_Clean'].unique()
    band_mapping = {}
    for unique_band in unique_bands:
        for standard_band in band_order:
            if standard_band.split()[0] in unique_band:
                band_mapping[unique_band] = standard_band
                break
        if unique_band not in band_mapping:
            band_mapping[unique_band] = unique_band

    df_plot['Employee_Band_Standard'] = df_plot['Employee_Band_Clean'].map(band_mapping)

    # Extract industry description from ANZSIC code (e.g., "K6411 (Financial Services)" -> "Financial Services")
    df_plot['Industry_Description'] = df_plot['Primary_ANZSIC_Code'].str.extract(r'\((.*?)\)')[0]
    df_plot['Industry_Description'] = df_plot['Industry_Description'].fillna(df_plot['Primary_ANZSIC_Code'])

    # Clean up Entity_Type to remove [1], [2], [3] suffixes
    df_plot['Entity_Type_Clean'] = df_plot['Entity_Type'].str.replace(r'\s*\[\d+\]', '', regex=True)

    band_counts = df_plot.groupby('Employee_Band_Standard').size().reset_index(name='count')
    df_plot = df_plot.merge(band_counts, on='Employee_Band_Standard', how='left')

    np.random.seed(42)

    df_plot['x_jitter'] = 0.0
    df_plot['y_jitter'] = 0.0

    for band in band_order:
        band_mask = df_plot['Employee_Band_Standard'] == band
        band_indices = df_plot[band_mask].index
        n_companies = len(band_indices)

        if n_companies == 0:
            continue

        jitter_strength_x = 0.45
        jitter_strength_y = 2.5

        if n_companies == 1:
            x_jitter = [0]
            y_jitter = [0]
        else:
            angle_step = 2 * np.pi / n_companies
            radius_variation = np.random.uniform(0.3, 1.0, n_companies)

            x_jitter = []
            y_jitter = []
            for i in range(n_companies):
                angle = i * angle_step + np.random.uniform(-0.3, 0.3)
                radius = radius_variation[i]

                x_offset = radius * np.cos(angle) * jitter_strength_x
                y_offset = radius * np.sin(angle) * jitter_strength_y

                x_jitter.append(x_offset)
                y_jitter.append(y_offset)

        df_plot.loc[band_indices, 'x_jitter'] = x_jitter
        df_plot.loc[band_indices, 'y_jitter'] = y_jitter

    band_to_numeric = {band: idx for idx, band in enumerate(band_order)}
    df_plot['x_numeric'] = df_plot['Employee_Band_Standard'].map(band_to_numeric)
    df_plot['x_position'] = df_plot['x_numeric'] + df_plot['x_jitter']

    fig = px.scatter(
        df_plot,
        x='x_position',
        y='y_jitter',
        text='Entity_Legal_Name' if not is_rejected else None,
        hover_data={
            'Entity_Legal_Name': True,
            'Entity_Type_Clean': True,
            'Headquarters_Location': True,
            'Industry_Description': True,
            'Employee_Band_Standard': True,
            'x_position': False,
            'y_jitter': False,
            'x_jitter': False,
            'x_numeric': False,
            'count': False,
            'Primary_ANZSIC_Code': False,
            'Entity_Type': False
        },
        labels={
            'x_position': 'Employee Band Size',
            'y_jitter': '',
            'Entity_Legal_Name': 'Company',
            'Entity_Type_Clean': 'Type',
            'Headquarters_Location': 'Location',
            'Industry_Description': 'Industry',
            'Employee_Band_Standard': 'Number of Employees'
        },
        title='',
        height=200
    )

    if not is_rejected:
        # Shortlist chart: show text on bubbles
        fig.update_traces(
            marker=dict(
                size=15,
                line=dict(width=1, color='white'),
                opacity=0.7,
                color='#1f77b4'
            ),
            textposition='middle center',
            textfont=dict(
                size=9,
                color='black',
                family='Arial, sans-serif'
            )
        )
    else:
        # All companies chart: no text on bubbles
        fig.update_traces(
            marker=dict(
                size=15,
                line=dict(width=1, color='white'),
                opacity=0.7,
                color='#1f77b4'
            )
        )

    fig.update_layout(
        xaxis=dict(
            title='',
            tickmode='array',
            tickvals=[band_to_numeric[band] for band in band_order],
            ticktext=band_order,
            range=[-0.5, len(band_order) - 0.5]
        ),
        yaxis=dict(
            visible=False,
            range=[-3.5, 3.5]
        ),
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='rgba(240, 242, 246, 0.5)',
        margin=dict(l=20, r=20, t=60, b=80)
    )

    # Add click instruction for charts
    if not is_rejected:
        st.caption("💡 Click on any bubble to remove it from your shortlist")
    else:
        st.caption("💡 Click on any bubble to add it to your shortlist")

    # Display the chart with click events
    event = st.plotly_chart(fig, use_container_width=True, key=f"chart_{'all_companies' if is_rejected else 'shortlist'}", on_select="rerun")

    # Handle click events
    if event and hasattr(event, 'selection') and event.selection and 'points' in event.selection:
        points = event.selection['points']
        if points:
            # Get the clicked company name
            clicked_idx = points[0]['point_index']
            clicked_company = df_plot.iloc[clicked_idx]['Entity_Legal_Name']

            # Initialize session state if needed
            if 'shortlisted_companies' not in st.session_state:
                st.session_state.shortlisted_companies = set()

            # Toggle company shortlist status
            if is_rejected:
                # Move to shortlist (add to shortlisted set)
                st.session_state.shortlisted_companies.add(clicked_company)
            else:
                # Remove from shortlist
                if clicked_company in st.session_state.shortlisted_companies:
                    st.session_state.shortlisted_companies.remove(clicked_company)

            st.rerun()


def apply_filters(df: pd.DataFrame, locations: list,
                  employee_bands: list, anzsic_codes: list) -> pd.DataFrame:
    """
    Apply selected filters to the DataFrame.

    Args:
        df: Original DataFrame
        locations: Selected locations
        employee_bands: Selected employee bands
        anzsic_codes: Selected ANZSIC codes

    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()

    band_order = create_employee_band_order()
    filtered_df['Employee_Band_Clean'] = filtered_df['Estimated_Employee_Band'].str.strip()

    unique_bands = filtered_df['Employee_Band_Clean'].unique()
    band_mapping = {}
    for unique_band in unique_bands:
        for standard_band in band_order:
            if standard_band.split()[0] in unique_band:
                band_mapping[unique_band] = standard_band
                break
        if unique_band not in band_mapping:
            band_mapping[unique_band] = unique_band

    filtered_df['Employee_Band_Standard'] = filtered_df['Employee_Band_Clean'].map(band_mapping)

    if locations:
        filtered_df = filtered_df[filtered_df['Headquarters_Location'].isin(locations)]

    if employee_bands:
        filtered_df = filtered_df[filtered_df['Employee_Band_Standard'].isin(employee_bands)]

    if anzsic_codes:
        filtered_df = filtered_df[filtered_df['Primary_ANZSIC_Code'].isin(anzsic_codes)]

    return filtered_df


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Where2Work",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS to reduce padding and fit content to viewport
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-height: 100vh;
        }
        h1 {
            margin-top: 0rem;
            margin-bottom: 0.5rem;
        }
        h3 {
            margin-top: 0.5rem;
            margin-bottom: 0.3rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Where do you want to work?")

    data_file = Path(__file__).parent / "company_data.csv"
    df = load_company_data(str(data_file))

    if df is None:
        st.stop()

    st.sidebar.markdown("Use the controls below to filter companies")

    all_locations = sorted(df['Headquarters_Location'].unique().tolist())
    all_employee_bands = create_employee_band_order()
    all_anzsic_codes = sorted(df['Primary_ANZSIC_Code'].unique().tolist())

    selected_locations = st.sidebar.multiselect(
        "Company Headquarters",
        options=all_locations,
        default=[],
        help="Select one or more locations to filter"
    )

    selected_employee_bands = st.sidebar.multiselect(
        "Number of Employees",
        options=all_employee_bands,
        default=[],
        help="Select one or more band sizes to filter"
    )

    selected_anzsic_codes = st.sidebar.multiselect(
        "Industry",
        options=all_anzsic_codes,
        default=[],
        help="Select one or more ANZSIC industry codes to filter"
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Clear Filters", type="secondary", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Clear Shortlist", type="secondary", use_container_width=True):
            st.session_state.shortlisted_companies = set()
            st.rerun()

    filtered_df = apply_filters(
        df,
        selected_locations,
        selected_employee_bands,
        selected_anzsic_codes
    )

    # Initialize session state for shortlisted companies
    if 'shortlisted_companies' not in st.session_state:
        st.session_state.shortlisted_companies = set()

    # Split companies into shortlist and all companies
    shortlist_df = filtered_df[filtered_df['Entity_Legal_Name'].isin(st.session_state.shortlisted_companies)]
    all_companies_df = filtered_df[~filtered_df['Entity_Legal_Name'].isin(st.session_state.shortlisted_companies)]

    # Display shortlist chart
    shortlist_count = len(shortlist_df)
    st.markdown(f"### 🎯 Your Shortlist ({shortlist_count} {('company' if shortlist_count == 1 else 'companies')})")
    create_bubble_chart(shortlist_df, chart_title="", is_rejected=False)

    # Display all companies chart
    all_count = len(all_companies_df)
    st.markdown(f"### 📋 All Companies ({all_count} {('company' if all_count == 1 else 'companies')})")
    create_bubble_chart(all_companies_df, chart_title="", is_rejected=True)


if __name__ == "__main__":
    main()

