import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Data Loading (Re-run for self-contained Streamlit app) ---
# In a real Streamlit app, you might cache this data loading.
@st.cache_data
def load_data():
    try:
        df_stations = pd.read_csv('sample_data/station.csv')
        df_narrow = pd.read_csv('sample_data/narrowresult.csv')

        # Convert 'ActivityStartDate' to datetime objects for df_narrow
        df_narrow['ActivityStartDate'] = pd.to_datetime(df_narrow['ActivityStartDate'], errors='coerce')

        # Select relevant columns and merge dataframes
        df_stations_subset = df_stations[['MonitoringLocationIdentifier', 'LatitudeMeasure', 'LongitudeMeasure', 'MonitoringLocationName']].drop_duplicates(subset=['MonitoringLocationIdentifier'])
        df_narrow_subset = df_narrow[['MonitoringLocationIdentifier', 'CharacteristicName', 'ResultMeasureValue', 'ActivityStartDate', 'ResultMeasure/MeasureUnitCode']]

        df_merged = pd.merge(df_narrow_subset, df_stations_subset, on='MonitoringLocationIdentifier', how='left')

        # Drop rows where location data is missing after merge
        df_merged.dropna(subset=['LatitudeMeasure', 'LongitudeMeasure', 'ActivityStartDate', 'ResultMeasureValue'], inplace=True)

        # Ensure ResultMeasureValue is numeric
        df_merged['ResultMeasureValue'] = pd.to_numeric(df_merged['ResultMeasureValue'], errors='coerce')
        df_merged.dropna(subset=['ResultMeasureValue'], inplace=True)

        return df_merged

    except FileNotFoundError:
        st.error("Error: 'station.csv' or 'narrowresult.csv' not found. Please ensure the files are in the 'sample_data' directory.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        st.stop()

df_merged = load_data()

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Water Quality Time Series Trends")

if df_merged is not None and not df_merged.empty:
    unique_characteristics = sorted(df_merged['CharacteristicName'].unique().tolist())

    # Use st.columns for side-by-side plots
    col1, col2 = st.columns(2)

    with col1:
        st.header("Chart 1")
        selected_char_1 = st.selectbox(
            'Select Characteristic for Chart 1:',
            unique_characteristics,
            index=0, # Default to the first characteristic
            key='char_select_1'
        )

        df_filtered_char_1 = df_merged[df_merged['CharacteristicName'] == selected_char_1].copy()
        df_filtered_char_1.sort_values(by='ActivityStartDate', inplace=True)

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        if not df_filtered_char_1.empty:
            sns.lineplot(
                data=df_filtered_char_1,
                x='ActivityStartDate',
                y='ResultMeasureValue',
                hue='MonitoringLocationName',
                marker='o',
                palette='tab10',
                ax=ax1
            )
            ax1.set_title(f'Trend for {selected_char_1}', fontsize=14)
            ax1.set_xlabel('Activity Start Date', fontsize=12)
            unit_code_1 = df_filtered_char_1['ResultMeasure/MeasureUnitCode'].iloc[0] if not df_filtered_char_1['ResultMeasure/MeasureUnitCode'].empty else ''
            ax1.set_ylabel(f'{selected_char_1} Value ({unit_code_1})', fontsize=12)
            ax1.grid(True, linestyle='--', alpha=0.7)
            ax1.tick_params(axis='x', rotation=45, ha='right')
            ax1.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            ax1.text(0.5, 0.5, f"No data for {selected_char_1}", horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title(f'Trend for {selected_char_1}', fontsize=14)
        plt.tight_layout()
        st.pyplot(fig1)

    with col2:
        st.header("Chart 2")
        # Ensure a different default characteristic if available
        default_index_2 = 1 if len(unique_characteristics) > 1 else 0
        selected_char_2 = st.selectbox(
            'Select Characteristic for Chart 2:',
            unique_characteristics,
            index=default_index_2,
            key='char_select_2'
        )

        df_filtered_char_2 = df_merged[df_merged['CharacteristicName'] == selected_char_2].copy()
        df_filtered_char_2.sort_values(by='ActivityStartDate', inplace=True)

        fig2, ax2 = plt.subplots(figsize=(10, 6))
        if not df_filtered_char_2.empty:
            sns.lineplot(
                data=df_filtered_char_2,
                x='ActivityStartDate',
                y='ResultMeasureValue',
                hue='MonitoringLocationName',
                marker='o',
                palette='tab10',
                ax=ax2
            )
            ax2.set_title(f'Trend for {selected_char_2}', fontsize=14)
            ax2.set_xlabel('Activity Start Date', fontsize=12)
            unit_code_2 = df_filtered_char_2['ResultMeasure/MeasureUnitCode'].iloc[0] if not df_filtered_char_2['ResultMeasure/MeasureUnitCode'].empty else ''
            ax2.set_ylabel(f'{selected_char_2} Value ({unit_code_2})', fontsize=12)
            ax2.grid(True, linestyle='--', alpha=0.7)
            ax2.tick_params(axis='x', rotation=45, ha='right')
            ax2.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            ax2.text(0.5, 0.5, f"No data for {selected_char_2}", horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title(f'Trend for {selected_char_2}', fontsize=14)
        plt.tight_layout()
        st.pyplot(fig2)

st.markdown("""
To run this Streamlit app:
1. Save the code above to a file named `app.py` in your Colab environment.
2. Open a new terminal in Colab (Tools -> Terminal -> New terminal).
3. Navigate to the directory where you saved `app.py`.
4. Run the command: `streamlit run app.py --server.port 8501`
5. Streamlit will provide a local URL (e.g., `http://localhost:8501`). Copy this URL and paste it into a new browser tab to view your app.
""")
