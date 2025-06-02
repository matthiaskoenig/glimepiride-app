"""Glimepiride Webapp."""

import marimo

__generated_with = "0.13.15"
app = marimo.App(layout_file="layouts/app.grid.json")


@app.cell
def _():
    import marimo as mo

    mo.md("# Welcome to Glimepiride Webapp!")
    return (mo,)


@app.cell
def load_model():
    # load model
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
def settings(mo):
    # settings
    PODOSE_gli = mo.ui.slider(start=0.0, stop=8.0, value=4.0, label="Glimepiride Dose [mg]")

    BW = mo.ui.slider(start=40, stop=170.0, value=75.0, label="Bodyweight [kg]")

    f_cirrhosis = mo.ui.slider(start=0.0, stop=0.95, value=0.0, step=0.01, label="Cirrhosis Degree")

    crcl = mo.ui.slider(start=10, stop=150, value=110, step=5, label="Creatinine Clearance [mL/min]")

    return BW, PODOSE_gli, f_cirrhosis, crcl


@app.cell(hide_code=True)
def display(BW, PODOSE_gli, f_cirrhosis, crcl, mo):
    mo.md(
        f"""
    ## Simulation of glimepiride model
    {PODOSE_gli}
    {BW}
    {f_cirrhosis}
    {crcl}
    """
    )
    return


@app.cell
def gli_plasma(df, labels):
    import plotly.express as px
    fig1 = px.line(df, x="time", y="[Cve_gli]", title=None, labels=labels, markers=True, range_y=[0, 1])
    fig1
    return (px,)


@app.cell
def m1_plasma(df, labels, px):
    fig2 = px.line(df, x="time", y="[Cve_m1]", title=None, labels=labels, markers=True, range_y=[0, 0.3])
    fig2
    return


@app.cell
def m2_plasma(df, labels, px):
    fig3 = px.line(df, x="time", y="[Cve_m2]", title=None, labels=labels, markers=True, range_y=[0, 0.1])
    fig3
    return


@app.cell
def m1_m2_urine(df, labels, px):
    fig4 = px.line(df, x="time", y="Aurine_m1_m2", title=None, labels=labels, markers=True, range_y=[0, 10])
    fig4
    return


@app.cell
def calculate_renal_function(crcl):
    """Convert CrCl to f_renal_function."""
    normal_crcl = 110.0  # mL/min (eGFR 100 + 10% overestimation)
    # Calculate f_renal_function for model
    f_renal_function = min(crcl.value / normal_crcl, 1.0)
    return f_renal_function


@app.cell
def simulation(
    BW,
    PODOSE_gli,
    f_cirrhosis,
    f_renal_function,
    r: "roadrunner.RoadRunner",
    units_factors,
):
    # simulation
    import pandas as pd

    r.resetAll()
    r.setValue("PODOSE_gli", PODOSE_gli.value)  # [mg]
    r.setValue("BW", BW.value)  # [kg]
    r.setValue("f_cirrhosis", f_cirrhosis.value)  # [-]
    r.setValue("KI__f_renal_function", f_renal_function)  # [dimensionless]
    s = r.simulate(start=0, end=60*48, steps=1000)  # [min]
    df = pd.DataFrame(s, columns=s.colnames)
    # unit conversions
    for col in df.columns:
        df[col] = df[col] * units_factors[col]  # [hr]
    df
    return (df,)


if __name__ == "__main__":
    app.run()
