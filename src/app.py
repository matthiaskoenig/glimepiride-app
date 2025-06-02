"""Glimepiride Webapp."""

import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium", layout_file="layouts/app.grid.json")


@app.cell
def _():
    import marimo as mo

    mo.md("# Welcome to Glimepiride Webapp!")
    return (mo,)


@app.cell
def _():
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
    units_factors = units = {
        "time": 1.0/60, 
        "[Cve_gli]": 1000.0, 
        "[Cve_m1]": 1000.0, 
        "[Cve_m2]": 1000.0, 
        "Aurine_m1_m2": 1000.0
    }
    return r, units_factors


@app.cell
def _(mo):
    # settings
    PODOSE_gli = mo.ui.slider(start=0.0, stop=10.0, value=2.0, label="Glimepiride Dose [mg]")
    BW = mo.ui.slider(start=40, stop=170.0, value=70.0, label="Bodyweight [kg]")
    return BW, PODOSE_gli


@app.cell(hide_code=True)
def _(BW, PODOSE_gli, mo):
    mo.md(
        f"""
    ## Simulation of glimepiride model

    {PODOSE_gli}

    {BW}
    """
    )
    return


@app.cell
def _(BW, PODOSE_gli, r: "roadrunner.RoadRunner", units_factors):
    # simulation
    import pandas as pd

    r.resetAll()
    r.setValue("PODOSE_gli", PODOSE_gli.value)  # [mg]
    r.setValue("BW", BW.value)  # [kg]
    s = r.simulate(start=0, end=60*48, steps=1000)  # [min]
    df = pd.DataFrame(s, columns=s.colnames)
    # unit conversions
    for col in df.columns:
        df[col] = df[col] * units_factors[col]  # [hr]
    df
    return (df,)


@app.cell
def _(df):
    import plotly.express as px
    fig1 = px.line(df, x="time", y="[Cve_gli]", title='Glimepiride plasma concentration', labels="test", markers=True)
    fig1
    return (px,)


@app.cell
def _(df, px):
    fig2 = px.line(df, x="time", y="[Cve_m1]", title='M1 plasma concentration', labels="test", markers=True)
    fig2
    return


@app.cell
def _(df, px):
    fig3 = px.line(df, x="time", y="[Cve_m2]", title='M1 plasma concentration', labels="test", markers=True)
    fig3
    return


@app.cell
def _(df, px):
    fig4 = px.line(df, x="time", y="Aurine_m1_m2", title='M1 plasma concentration', labels="test", markers=True)
    fig4
    return


if __name__ == "__main__":
    app.run()
