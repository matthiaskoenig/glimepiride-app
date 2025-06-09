"""Glimepiride Webapp."""

import marimo

__generated_with = "0.13.15"
app = marimo.App(layout_file="layouts/app.grid.json")

with app.setup:
    import marimo as mo
    mo.md("# Welcome to Glimepiride Webapp!")


@app.cell
def load_model():
    from pathlib import Path
    import roadrunner
    model_path = Path(__file__).parent.parent / "model" / "glimepiride_body_flat.xml"
    r: roadrunner.RoadRunner = roadrunner.RoadRunner(str(model_path))
    model: roadrunner.ExecutableModel = r.model
    r.timeCourseSelections = ["time", "[Cve_gli]", "[Cve_m1]", "[Cve_m2]", "Aurine_m1_m2"]
    units = {
        "time": "hr", 
        "[Cve_gli]": "µM", 
        "[Cve_m1]": "µM", 
        "[Cve_m2]": "µM", 
        "Aurine_m1_m2": "µmole"
    }
    units_factors = {
        "time": 1.0/60, 
        "[Cve_gli]": 1000.0, 
        "[Cve_m1]": 1000.0, 
        "[Cve_m2]": 1000.0, 
        "Aurine_m1_m2": 1000.0
    }
    labels = {
        "time": "Time [hr]", 
        "[Cve_gli]": "Glimepiride Plasma [µM]", 
        "[Cve_m1]": "M1 Plasma [µM]", 
        "[Cve_m2]": "M2 Plasma [µM]", 
        "Aurine_m1_m2": "M1 + M2 Urine [µmole]"
    }
    return labels, r, units_factors


@app.cell
def cyp2c9_allele_state():
    allele1_activity, set_allele1_activity = mo.state(100)  # Default *1
    allele2_activity, set_allele2_activity = mo.state(100)  # Default *1
    allele_activities = {"*1": 100, "*2": 63, "*3": 23}

    return (
        allele1_activity,
        allele2_activity,
        allele_activities,
        set_allele1_activity,
        set_allele2_activity,
    )


@app.cell
def cirrhosis_state():
    cirrhosis_degree, set_cirrhosis_degree = mo.state(0)  # Default Healthy
    cirrhosis_map = {
        "Healthy": 0,
        "Mild (CPT A)": 0.3994897959183674,
        "Moderate (CPT B)": 0.6979591836734694,
        "Severe (CPT C)": 0.8127551020408164,
    }

    return cirrhosis_degree, cirrhosis_map, set_cirrhosis_degree


@app.cell
def cyp2c9_allele_dropdowns(
    allele1_activity,
    allele2_activity,
    allele_activities,
    set_allele1_activity,
    set_allele2_activity,
):
    def get_allele_name(activity):
        for allele, act in allele_activities.items():
            if act == activity:
                return allele
        return "Custom"

    cyp2c9_allele1_dropdown = mo.ui.dropdown(
        options=["*1", "*2", "*3", "Custom"],
        value=get_allele_name(allele1_activity()),
        # label="CYP2C9 Allele 1",
        on_change=lambda allele_type: set_allele1_activity(
            allele_activities[allele_type]) if allele_type in allele_activities else None
    )

    cyp2c9_allele2_dropdown = mo.ui.dropdown(
        options=["*1", "*2", "*3", "Custom"],
        value=get_allele_name(allele2_activity()),
        # label=" ",
        on_change=lambda allele_type: set_allele2_activity(
            allele_activities[allele_type]) if allele_type in allele_activities else None
    )

    return cyp2c9_allele1_dropdown, cyp2c9_allele2_dropdown


@app.cell
def cirrhosis_dropdown(cirrhosis_degree, cirrhosis_map, set_cirrhosis_degree):
    def get_cirrhosis_name(degree):
        # Find closest match
        for name, value in cirrhosis_map.items():
            if abs(value - degree) < 0.001:  # Small tolerance for float comparison
                return name
        return "Custom"

    cirrhosis_dropdown = mo.ui.dropdown(
        options=["Healthy", "Mild (CPT A)", "Moderate (CPT B)", "Severe (CPT C)", "Custom"],
        value=get_cirrhosis_name(cirrhosis_degree()),
        # label=" ",
        on_change=lambda severity: set_cirrhosis_degree(
            cirrhosis_map[severity]) if severity in cirrhosis_map else None
    )

    return (cirrhosis_dropdown,)


@app.cell
def cyp2c9_allele_sliders(
    allele1_activity,
    allele2_activity,
    set_allele1_activity,
    set_allele2_activity,
):
    cyp2c9_allele1_slider = mo.ui.slider(
        start=0,
        stop=100,
        value=allele1_activity(),
        step=1.0,
        label="CYP2C9 Allele 1 Activity [%]",
        on_change=set_allele1_activity
    )

    cyp2c9_allele2_slider = mo.ui.slider(
        start=0,
        stop=100,
        value=allele2_activity(),
        step=1.0,
        label="CYP2C9 Allele 2 Activity [%]",
        on_change=set_allele2_activity
    )

    return cyp2c9_allele1_slider, cyp2c9_allele2_slider


@app.cell
def cirrhosis_slider(cirrhosis_degree, set_cirrhosis_degree):
    f_cirrhosis = mo.ui.slider(
        start=0.0,
        stop=0.95,
        value=cirrhosis_degree(),
        step=0.01,
        label="Cirrhosis Degree",
        on_change=set_cirrhosis_degree
    )

    return (f_cirrhosis,)


@app.cell
def settings_other():
    PODOSE_gli = mo.ui.slider(start=0.0, stop=8.0, value=4.0, step=1.0, label="Glimepiride Dose [mg]")
    BW = mo.ui.slider(start=40, stop=170.0, value=75.0, label="Bodyweight [kg]")
    crcl = mo.ui.slider(start=10, stop=150, value=110, step=1.0, label="Creatinine Clearance [mL/min]")

    return BW, PODOSE_gli, crcl


@app.cell
def display(
    BW,
    PODOSE_gli,
    cirrhosis_dropdown,
    crcl,
    cyp2c9_allele1_dropdown,
    cyp2c9_allele1_slider,
    cyp2c9_allele2_dropdown,
    cyp2c9_allele2_slider,
    f_cirrhosis,
):
    mo.md(
        f"""
    ## Patient-Specific Parameters
    {mo.vstack([
        PODOSE_gli,
        BW,
        mo.hstack([f_cirrhosis, cirrhosis_dropdown], gap=0),
        crcl,
        mo.hstack([cyp2c9_allele1_slider, cyp2c9_allele1_dropdown], gap=0),
        mo.hstack([cyp2c9_allele2_slider, cyp2c9_allele2_dropdown], gap=0)
    ])}
    """
    )
    return


@app.cell
def calculate_renal_function(crcl):
    """Convert CrCl to f_renal_function."""
    normal_crcl = 110.0  # mL/min (eGFR 100 + 10% overestimation)
    # Calculate f_renal_function
    f_renal_function = min(crcl.value / normal_crcl, 1.0)
    return (f_renal_function,)


@app.cell
def calculate_cyp2c9_activity(allele1_activity, allele2_activity):
    """Calculate f_cyp2c9 from the two allele activities."""
    # Calculate mean activity
    f_cyp2c9 = (allele1_activity() + allele2_activity()) / 2.0 / 100.0
    return (f_cyp2c9,)


@app.cell
def plots(df, labels):
    import plotly.express as px

    height = 400
    width = 450

    fig1 = px.line(df, x="time", y="[Cve_gli]", title=" ", labels=labels, markers=True, range_y=[0, 1], range_x=[0, 25], height=height, width=width)
    fig2 = px.line(df, x="time", y="[Cve_m1]", title=" ", labels=labels, markers=True, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig3 = px.line(df, x="time", y="[Cve_m2]", title=" ", labels=labels, markers=True, range_y=[0, 0.1], range_x=[0, 25], height=height, width=width)
    fig4 = px.line(df, x="time", y="Aurine_m1_m2", title=" ", labels=labels, markers=True, range_y=[0, 10], height=height, width=width)
    mo.hstack([fig1, fig2, fig3, fig4], gap=0)
    return


@app.cell
def simulation(
    BW,
    PODOSE_gli,
    f_cirrhosis,
    f_cyp2c9,
    f_renal_function,
    r: "roadrunner.RoadRunner",
    units_factors,
):
    import pandas as pd

    r.resetAll()
    r.setValue("PODOSE_gli", PODOSE_gli.value)  # [mg]
    r.setValue("BW", BW.value)  # [kg]
    r.setValue("f_cirrhosis", f_cirrhosis.value)
    r.setValue("KI__f_renal_function", f_renal_function)
    r.setValue("LI__f_cyp2c9", f_cyp2c9)
    s = r.simulate(start=0, end=60*50, steps=5000)  # [min]
    df = pd.DataFrame(s, columns=s.colnames)
    # unit conversions
    for col in df.columns:
        df[col] = df[col] * units_factors[col]  # [hr]
    df
    return (df,)


if __name__ == "__main__":
    app.run()
