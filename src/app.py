"""Glimepiride Webapp."""

import marimo

__generated_with = "0.13.15"
app = marimo.App(layout_file="layouts/app.grid.json")

with app.setup:
    import marimo as mo
    import pandas as pd
    import numpy as np
    mo.md("""
          # **Welcome to Glimepiride Webapp!**
          ### A simulation tool for exploring patient-specific pharmacokinetics.
          """
          )


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
        "time": "<b>Time [hr]</b>",
        "[Cve_gli]": "<b>Glimepiride Plasma [µM]</b>",
        "[Cve_m1]": "<b>M1 Plasma [µM]</b>",
        "[Cve_m2]": "<b>M2 Plasma [µM]</b>",
        "Aurine_m1_m2": "<b>M1 + M2 Urine [µmole]</b>"
    }
    return Path, labels, r, units_factors


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
def renal_impairment_state():
    normal_crcl = 110.0
    crcl_map = {
        "Normal": normal_crcl * 1.0,
        "Mild Impairment": normal_crcl * 0.69,
        "Moderate Impairment": normal_crcl * 0.32,
        "Severe Impairment": normal_crcl * 0.19,
    }
    crcl_value, set_crcl_value = mo.state(110)  # Default normal

    return crcl_map, crcl_value, normal_crcl, set_crcl_value


@app.cell
def body_weight_state():
    bw_value, set_bw_value = mo.state(75.0)

    return bw_value, set_bw_value


@app.cell
def dose_state():
    dose_value, set_dose_value = mo.state(4.0)
    return dose_value, set_dose_value


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
        on_change=lambda allele_type: set_allele1_activity(
            allele_activities[allele_type]) if allele_type in allele_activities else None
    )

    cyp2c9_allele2_dropdown = mo.ui.dropdown(
        options=["*1", "*2", "*3", "Custom"],
        value=get_allele_name(allele2_activity()),
        on_change=lambda allele_type: set_allele2_activity(
            allele_activities[allele_type]) if allele_type in allele_activities else None
    )

    return cyp2c9_allele1_dropdown, cyp2c9_allele2_dropdown


@app.cell
def cirrhosis_dropdown(cirrhosis_degree, cirrhosis_map, set_cirrhosis_degree):
    def get_cirrhosis_name(degree):
        for name, value in cirrhosis_map.items():
            if value == degree:
                return name
        return "Custom"

    cirrhosis_dropdown = mo.ui.dropdown(
        options=["Healthy", "Mild (CPT A)", "Moderate (CPT B)", "Severe (CPT C)", "Custom"],
        value=get_cirrhosis_name(cirrhosis_degree()),
        on_change=lambda severity: set_cirrhosis_degree(
            cirrhosis_map[severity]) if severity in cirrhosis_map else None
    )

    return (cirrhosis_dropdown,)


@app.cell
def renal_dropdown(crcl_map, crcl_value, set_crcl_value):
    def get_renal_category(crcl):
        for category, preset_crcl in crcl_map.items():
            if preset_crcl == crcl:
                return category
        return "Custom"

    renal_impairment_dropdown = mo.ui.dropdown(
        options=["Normal", "Mild Impairment", "Moderate Impairment", "Severe Impairment", "Custom"],
        value=get_renal_category(crcl_value()),
        on_change=lambda category: set_crcl_value(
            crcl_map[category]) if category in crcl_map else None
    )

    return (renal_impairment_dropdown,)


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
        label="Cirrhosis Degree [-]",
        on_change=set_cirrhosis_degree
    )

    return (f_cirrhosis,)


@app.cell
def crcl_slider(crcl_value, set_crcl_value):
    crcl = mo.ui.slider(
        start=1,
        stop=110,
        value=crcl_value(),
        step=1.0,
        label="Creatinine Clearance [mL/min]",
        on_change=set_crcl_value
    )
    return (crcl,)


@app.cell
def dose_slider(dose_value, set_dose_value):
    PODOSE_gli = mo.ui.slider(
        start=0.0,
        stop=8.0,
        value=dose_value(),
        on_change=set_dose_value,
        step=1.0,
        label="Glimepiride Dose [mg]"
    )
    return (PODOSE_gli,)


@app.cell
def bodyweight_slider(bw_value, set_bw_value):
    BW = mo.ui.slider(
        start=40,
        stop=170.0,
        value=bw_value(),
        on_change=set_bw_value,
        label="Bodyweight [kg]"
    )

    return (BW,)


@app.cell
def patients():
    predefined_patients = {
        # Cirrhosis patients
        "CPT A": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0.3994897959183674,
            "allele1": 100,
            "allele2": 100,
        },
        "CPT B": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0.6979591836734694,
            "allele1": 100,
            "allele2": 100,
        },
        "CPT C": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0.8127551020408164,
            "allele1": 100,
            "allele2": 100,
        },
        # Kidney impairment patients
        "Mild Renal Impairment": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 75.9,  # 110 * 0.69
            "cirrhosis": 0,
            "allele1": 100,
            "allele2": 100,
        },
        "Moderate Renal Impairment": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 35.2,  # 110 * 0.32
            "cirrhosis": 0,
            "allele1": 100,
            "allele2": 100,
        },
        "Severe Renal Impairment": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 20.9,  # 110 * 0.19
            "cirrhosis": 0,
            "allele1": 100,
            "allele2": 100,
        },
        # CYP2C9 genotype
        "CYP2C9 *1/*1": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0,
            "allele1": 100,
            "allele2": 100,
        },
        "CYP2C9 *1/*2": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0,
            "allele1": 100,
            "allele2": 63,
        },
        "CYP2C9 *1/*3": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0,
            "allele1": 100,
            "allele2": 23,
        },
        "CYP2C9 *2/*2": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0,
            "allele1": 63,
            "allele2": 63,
        },
        "CYP2C9 *2/*3": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0,
            "allele1": 63,
            "allele2": 23,
        },
        "CYP2C9 *3/*3": {
            "dose": 4.0,
            "weight": 75.0,
            "crcl": 110.0,
            "cirrhosis": 0,
            "allele1": 23,
            "allele2": 23,
        },
    }

    saved_patients = lambda: predefined_patients

    return (saved_patients,)


@app.cell
def patients_table_display(load_buttons, saved_patients):
    # List of dicts for table data
    table_data = []

    for button_index, (name, config) in enumerate(saved_patients().items()):
        row_data = {
            " ": load_buttons[button_index],
            "Patient": name,
            "Dose [mg]": int(config["dose"]),
            "Weight [kg]": config["weight"],
            "CrCl [mL/min]": int(config["crcl"]),
            "Cirrhosis [-]": f"{config['cirrhosis']:.2f}",
            "Allele 1 [%]": int(config["allele1"]),
            "Allele 2 [%]": int(config["allele2"]),
        }

        table_data.append(row_data)

    mo.md(
        f"""
        ## **Load Example Patients**
        #### Choose from example patients.
        {mo.ui.table(
            table_data,
            show_column_summaries=False,
            pagination=True,
            page_size=5,
            selection=None,
            show_download=False
        )}
        """
    )
    return


@app.cell
def patient_actions(
    saved_patients,
    set_allele1_activity,
    set_allele2_activity,
    set_bw_value,
    set_cirrhosis_degree,
    set_crcl_value,
    set_dose_value,
):
    def load_patient(patient_name):
        if patient_name in saved_patients():
            config = saved_patients()[patient_name]

            # Update all UI elements with loaded values
            set_dose_value(config["dose"])
            set_bw_value(config["weight"])
            set_crcl_value(config["crcl"])
            set_cirrhosis_degree(config["cirrhosis"])
            set_allele1_activity(config["allele1"])
            set_allele2_activity(config["allele2"])

    return (load_patient,)


@app.cell
def patient_action_buttons(load_patient, saved_patients):
    # Create load buttons for each saved patient
    load_buttons = mo.ui.array([
        mo.ui.button(
            label="Load",
            kind="neutral",
            on_change=lambda v, name=name: load_patient(name)
        )
        for name in saved_patients().keys()
    ])

    return (load_buttons,)


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
    renal_impairment_dropdown,
):
    mo.md(
        f"""
    ## **Input Patient Data**
    {mo.vstack([
        mo.md("###**Patient Parameters**"),
        PODOSE_gli,
        BW,

        mo.md("###**Organ Function**"),
        mo.hstack([crcl, renal_impairment_dropdown], gap=0),
        mo.hstack([f_cirrhosis, cirrhosis_dropdown], gap=0),

        mo.md("###**CYP2C9 Genotype**"),
        mo.hstack([cyp2c9_allele1_slider, cyp2c9_allele1_dropdown], gap=0),
        mo.hstack([cyp2c9_allele2_slider, cyp2c9_allele2_dropdown], gap=0)
    ])}
    """
    )
    return


@app.cell
def calculate_renal_function(crcl_value, normal_crcl):
    # Calculate f_renal_function from state value
    f_renal_function = min(crcl_value() / normal_crcl, 1.0)
    return (f_renal_function,)


@app.cell
def calculate_cyp2c9_activity(allele1_activity, allele2_activity):
    # Calculate mean activity
    f_cyp2c9 = (allele1_activity() + allele2_activity()) / 2.0 / 100.0
    return (f_cyp2c9,)


@app.cell
def plots(df, labels):
    import plotly.express as px
    import plotly.io as pio

    pio.renderers.default = None # Fix renderer issue

    height = 350
    width = 420

    fig1 = px.line(df, x="time", y="[Cve_gli]", title=None, labels=labels, markers=False, range_y=[0, 1], range_x=[0, 25], height=height, width=width)
    fig2 = px.line(df, x="time", y="[Cve_m1]", title=None, labels=labels, markers=False, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig3 = px.line(df, x="time", y="[Cve_m2]", title=None, labels=labels, markers=False, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig4 = px.line(df, x="time", y="Aurine_m1_m2", title=None, labels=labels, markers=False, range_y=[0, 10], height=height, width=width)

    axis_style = {
        "title_font": {"size": 17},
        "tickfont": {"size": 15}
    }

    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_layout(
            xaxis=axis_style,
            yaxis=axis_style,
            plot_bgcolor='white',
            xaxis_gridcolor='lightgray',
            yaxis_gridcolor='lightgray',
            xaxis_showline=True,
            xaxis_linewidth=1,
            xaxis_linecolor='black',
            xaxis_mirror=True,
            yaxis_showline=True,
            yaxis_linewidth=1,
            yaxis_linecolor='black',
            yaxis_mirror=True
        )
        fig.update_traces(line_width=3)

    mo.vstack([
        mo.md("## **Pharmacokinetic Profiles**"),
        mo.vstack([
            mo.hstack([fig1, fig2], gap=0),
            mo.hstack([fig3, fig4], gap=0)
        ])
    ])

    return


@app.cell
def model_image(Path):
    model_img_path = Path(__file__).parent.parent / "model" / "glimepiride_model.png"
    mo.image(src=str(model_img_path))
    return


@app.cell
def model_description():
    mo.md(
        """
    ####**Whole-body PBPK model of glimepiride.** </br>
    **A)** Whole-body model illustrating glimepiride (GLI) administration, its systemic circulation via venous and arterial blood, and the key organs (liver, kidney, GI tract) involved in GLI metabolism, distribution, and excretion.
    **B)** Intestinal model showing dissolution and absorption of GLI by enterocytes. No enterohepatic circulation of M1 and M2 is assumed, but reverse transport via enterocytes is included.
    **C)** Hepatic model depicting CYP2C9-mediated metabolism of GLI to M1 and M2.
    **D)** Renal model highlighting the elimination of M1 and M2 via urine; unchanged GLI is not excreted renally.
    """
    )
    return


@app.cell
def disclaimer():
    mo.md(
        """
    ## **Disclaimer**
    The software is provided **AS IS**, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.<br>
    This software is a **research proof-of-principle** and not fit for any clinical application. It is not intended to diagnose, treat, or inform medication dosing decisions. Always consult with qualified healthcare professionals for medical advice and treatment planning.
    """
    )
    return


@app.cell
def reference():
    mo.md(
        """
    ---
    ## **Reference**
    **A Digital Twin of Glimepiride for Personalized and Stratified Diabetes Treatment.**<br>
    _Michelle Elias, Matthias König (2025)_<br>
    Preprints 2025, 2025061264. (preprint). [doi:10.20944/preprints202506.1264.v1](https://doi.org/10.20944/preprints202506.1264.v1)
    """
    )
    return


@app.cell
def simulation(
    PODOSE_gli,
    bw_value,
    f_cirrhosis,
    f_cyp2c9,
    f_renal_function,
    r: "roadrunner.RoadRunner",
    units_factors,
):

    r.resetAll()
    r.setValue("PODOSE_gli", PODOSE_gli.value)  # [mg]
    r.setValue("BW", bw_value())  # [kg]
    r.setValue("f_cirrhosis", f_cirrhosis.value)
    r.setValue("KI__f_renal_function", f_renal_function)
    r.setValue("LI__f_cyp2c9", f_cyp2c9)
    s = r.simulate(start=0, end=60*50, steps=2500)  # [min]
    df = pd.DataFrame(s, columns=s.colnames)
    # unit conversions
    for col in df.columns:
        df[col] = df[col] * units_factors[col]  # [hr]
    return (df,)


@app.cell
def import_pk():
    from pkdb_analysis.pk.pharmacokinetics import TimecoursePK
    from pint import UnitRegistry
    ureg = UnitRegistry()
    Q_ = ureg.Quantity
    return Q_, TimecoursePK, ureg


@app.cell
def pk_parameters(PODOSE_gli, Q_, TimecoursePK, df, ureg):
    pk_results = {}

    # Time vector with units
    t_vec = Q_(df["time"].values, "hour")

    # Get dose value from slider
    dose_mg = PODOSE_gli.value

    # Calculate for glimepiride
    tcpk_gli = TimecoursePK(
        time=t_vec,
        concentration=Q_(df["[Cve_gli]"].values, "micromolar"),
        dose=Q_(dose_mg, "milligram"),
        ureg=ureg,
        substance="glimepiride",
        min_treshold=100
    )

    # Calculate for M1
    tcpk_m1 = TimecoursePK(
        time=t_vec,
        concentration=Q_(df["[Cve_m1]"].values, "micromolar"),
        dose=None,
        ureg=ureg,
        substance="M1"
    )

    # Calculate for M2
    tcpk_m2 = TimecoursePK(
        time=t_vec,
        concentration=Q_(df["[Cve_m2]"].values, "micromolar"),
        dose=None,
        ureg=ureg,
        substance="M2"
    )

    # Extract results
    for substance_name, tcpk in [("Glimepiride", tcpk_gli), ("M1", tcpk_m1), ("M2", tcpk_m2)]:
        pk = tcpk.pk
        pk_results[substance_name] = {
            "Cmax [µM]": f"{pk.cmax.magnitude:.2f}",
            "Tmax [hr]": f"{pk.tmax.magnitude:.1f}",
            "AUC [µM*hr]": f"{pk.auc.magnitude:.1f}",
            "Half-life [hr]": f"{pk.thalf.magnitude:.1f}"
        }

    return (pk_results,)


@app.cell
def pk_table_display(pk_results):
    # Molecular weights for conversion
    MW = {
        "Glimepiride": 490.62,  # g/mol
        "M1": 506.62,  # g/mol
        "M2": 520.6  # g/mol
    }

    # Create display data with unit conversion
    display_data = []
    for substance, params in pk_results.items():
        row = {"Substance": substance}
        for key, value in params.items():
            if "AUC" in key and substance in MW:
                # Extract numeric value from string
                auc_um_hr = float(value.split()[0])
                # Convert µM*hr to ng/mL*hr
                auc_ng_ml_hr = auc_um_hr * MW[substance]
                row[key.replace("µM*hr", "ng/mL*hr")] = f"{auc_ng_ml_hr:.1f}"
            else:
                row[key] = value
        display_data.append(row)

    mo.md(
        f"""
        ## **Pharmacokinetic Parameters**

        {mo.ui.table(
            display_data,
            show_column_summaries=False,
            show_download=False,
            label=None,
            selection=None,

        )}
        """
    )
    return


if __name__ == "__main__":
    app.run()
