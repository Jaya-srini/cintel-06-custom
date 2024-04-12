#-----------------------------------------------------------------------------
# imports (at the top)
#-----------------------------------------------------------------------------
import seaborn as sns
import pandas as pd
import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly
from shinyswatch import theme
from shiny import reactive, render

#-----------------------------------------------------------------------------
# define a reactive calc to filter the Titanic dataset
#-----------------------------------------------------------------------------
titanic_df = sns.load_dataset("titanic")

@reactive.calc
def filtered_data():
    selected_class = input.selected_class()
    selected_age_min = input.selected_age_min()
    selected_age_max = input.selected_age_max()
    
    filtered_df = titanic_df[
        (titanic_df['class'] == selected_class) &
        (titanic_df['age'] >= selected_age_min) &
        (titanic_df['age'] <= selected_age_max)
    ]
    
    return filtered_df

#-----------------------------------------------------------------------------
# Define the Shiny Express UI
#-----------------------------------------------------------------------------
# The overall page options
ui.page_opts(title="Jaya's Titanic Dashboard", fillable=True)

# Add a color theme to the dashboard
theme.sketchy()

#-----------------------------------------------------------------------------
# A sidebar
#-----------------------------------------------------------------------------
with ui.sidebar(open="open"):
    ui.HTML('<h3 style="font-size: medium;">Dashboard Configuration Options</h3>')
    with ui.accordion():
        with ui.accordion_panel("Class Filter"):
            ui.input_selectize("selected_class", "Select a Class:", 
                               list(titanic_df['class'].unique()))
        with ui.accordion_panel("Age Group Filter"):
            ui.input_slider("selected_age_min", "Select Minimum Age:", 
                            min=titanic_df['age'].min(), 
                            max=titanic_df['age'].max(),
                            value=titanic_df['age'].min())
            ui.input_slider("selected_age_max", "Select Maximum Age:", 
                            min=titanic_df['age'].min(), 
                            max=titanic_df['age'].max(),
                            value=titanic_df['age'].max())
    
    ui.hr()

    @render.ui
    def selected_info():
        selected_class = input.selected_class()
        selected_age_min = input.selected_age_min()
        selected_age_max = input.selected_age_max()
        
        info_html = f"""
        <div style="font-size: 100%; line-height: 1;">
            <h6 style="margin-bottom: 0;">Selected Configuration:</h6>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected Class:</strong> {selected_class}</p>
            <p style="margin-top: 1; margin-bottom: 1;"><strong>Selected Age Range:</strong> {selected_age_min} - {selected_age_max}</p>
        </div>
        """
        return ui.HTML(info_html)

    ui.hr()


#-----------------------------------------------------------------------------
# The main section with ui cards, value boxes, and space for grids and charts
#-----------------------------------------------------------------------------
with ui.accordion():
    with ui.accordion_panel("Dashboard Overview"):
        with ui.layout_columns():
            with ui.value_box(showcase="🚢", max_height="300px"):
                "Total Passengers"
                @render.text
                def display_passenger_count():
                    df = filtered_data()
                    return f"{len(df)} passengers"

            with ui.value_box(showcase="👫", max_height="300px", theme="bg-gradient-green"):
                "Average Fare"
                @render.text
                def average_fare():
                    df = filtered_data()
                    return f"${df['fare'].mean():.2f}" if not df.empty else "N/A"

            with ui.value_box(showcase="💀", max_height="300px", theme="bg-gradient-orange"):
                "Survival Rate"
                @render.text
                def survival_rate():
                    df = filtered_data()
                    if not df.empty:
                        return f"{(df['survived'].sum() / len(df)) * 100:.2f}%"
                    else:
                        return "N/A"

    with ui.accordion_panel("Histogram"):
        with ui.card():
            ui.card_header("Histogram of Age")
            @render_plotly
            def age_histogram():
                return px.histogram(
                    filtered_data(),
                    x='age',
                    nbins=20,
                    title='Histogram of Age'
                )

    with ui.accordion_panel("Survival by Gender"):
        with ui.card():
            ui.card_header("Survival by Gender")
            @render_plotly
            def survival_gender_bar():
                return px.bar(
                    filtered_data(),
                    x='sex',
                    color='survived',
                    barmode='group',
                    title='Survival by Gender'
                )
