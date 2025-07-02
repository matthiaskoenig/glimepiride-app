"""Glimepiride Webapp."""

import marimo

__generated_with = "0.14.9"
app = marimo.App(
    width="full",
    app_title="Glimepiride Webapp",
    layout_file="layouts/app.grid.json",
)

with app.setup:
    import marimo as mo
    import pandas as pd


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
        on_change=set_allele1_activity
    )

    cyp2c9_allele2_slider = mo.ui.slider(
        start=0,
        stop=100,
        value=allele2_activity(),
        step=1.0,
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
    )
    return (PODOSE_gli,)


@app.cell
def bodyweight_slider(bw_value, set_bw_value):
    BW = mo.ui.slider(
        start=40,
        stop=170.0,
        value=bw_value(),
        on_change=set_bw_value,
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
def display_with_tabs(
    BW,
    PODOSE_gli,
    cirrhosis_dropdown,
    crcl,
    cyp2c9_allele1_dropdown,
    cyp2c9_allele1_slider,
    cyp2c9_allele2_dropdown,
    cyp2c9_allele2_slider,
    f_cirrhosis,
    load_buttons,
    renal_impairment_dropdown,
    saved_patients,
):
    label_style = {"flex": "1 1 250px", "text-align": "left", "padding-right": "10px"}

    # Input Patient Data
    input_patient_content = mo.vstack([

        mo.md("####**Anthropometrics & Dose**").style({"margin-top": "10px"}),

        mo.hstack([
            mo.md("Glimepiride Dose [mg]").style(label_style),
            PODOSE_gli.style({"flex": "2 1 340px"})
        ], align="center", gap=1, wrap=True),

        mo.hstack([
            mo.md("Bodyweight [kg]").style(label_style),
            BW.style({"flex": "2 1 340px"})
        ], align="center", gap=1, wrap=True),

        mo.md("####**Organ Function**").style({"margin-top": "10px"}),

        mo.hstack([
            mo.md("Creatinine Clearance [mL/min]").style({"flex": "2 1 200px", "text-align": "left"}),
            crcl.style({"flex": "2 1 150px"}),
            renal_impairment_dropdown.style({"flex": "1 1 150px"})
        ], align="center", gap=1, wrap=True),

        mo.hstack([
            mo.md("Cirrhosis Degree [-]").style({"flex": "2 1 200px", "text-align": "left"}),
            f_cirrhosis.style({"flex": "2 1 150px"}),
            cirrhosis_dropdown.style({"flex": "1 1 150px"})
        ], align="center", gap=1, wrap=True),

        mo.md("####**CYP2C9 Genotype**").style({"margin-top": "10px"}),

        mo.hstack([
            mo.md("CYP2C9 Allele 1 Activity [%]").style({"flex": "2 1 200px", "text-align": "left"}),
            cyp2c9_allele1_slider.style({"flex": "2 1 150px"}),
            cyp2c9_allele1_dropdown.style({"flex": "1 1 150px"})
        ], align="center", gap=1, wrap=True),

        mo.hstack([
            mo.md("CYP2C9 Allele 2 Activity [%]").style({"flex": "2 1 200px", "text-align": "left"}),
            cyp2c9_allele2_slider.style({"flex": "2 1 150px"}),
            cyp2c9_allele2_dropdown.style({"flex": "1 1 150px"})
        ], align="center", gap=1, wrap=True)
    ])

    # Example Patients table
    table_data = []
    for button_index, (name, config) in enumerate(saved_patients().items()):
        row_data = {
            " ": load_buttons[button_index],
            "Patient Name": name,
            "Weight [kg]": config["weight"],
            "CrCl [mL/min]": int(config["crcl"]),
            "Cirrhosis [-]": f"{config['cirrhosis']:.2f}",
            "Allele 1 [%]": int(config["allele1"]),
            "Allele 2 [%]": int(config["allele2"]),
        }
        table_data.append(row_data)

    example_patients_content = mo.vstack([
        mo.ui.table(
            table_data,
            show_column_summaries=False,
            pagination=True,
            page_size=6,
            selection=None,
            show_download=False
        )
    ]).style({"font-size": "0.85em"})

    # Create tabs
    patient_tabs = mo.ui.tabs({
        "Custom Patient": input_patient_content,
        "Example Patients": example_patients_content
    })

    display_with_tabs = mo.md(
        f"""
        ## **Patient**
        {patient_tabs}
        """
    ).style({
        "background-color": "#fafbfc",
        "border": "1px solid #f0f0f0",
        "border-radius": "8px",
        "padding": "20px",
        "margin": "10px 0"
    })

    return (display_with_tabs,)


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
    width = 410

    fig1 = px.line(df, x="time", y="[Cve_gli]", title=None, labels=labels, markers=False, range_y=[0, 1], range_x=[0, 25], height=height, width=width)
    fig2 = px.line(df, x="time", y="[Cve_m1]", title=None, labels=labels, markers=False, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig3 = px.line(df, x="time", y="[Cve_m2]", title=None, labels=labels, markers=False, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig4 = px.line(df, x="time", y="Aurine_m1_m2", title=None, labels=labels, markers=False, range_y=[0, 10], height=height, width=width)

    axis_style = {
        "title_font": {"size": 14},
        "tickfont": {"size": 12}
    }

    for fig, y_tick_interval, x_tick_interval in [(fig1, 0.2, 5), (fig2, 0.05, 5), (fig3, 0.05, 5), (fig4, 2, 10)]:
        fig.update_layout(
            xaxis=dict(
                **axis_style,
                dtick=x_tick_interval,
                gridcolor='lightgray',
                showline=True,
                linewidth=1,
                linecolor='black',
                mirror=True
            ),
            yaxis=dict(
                **axis_style,
                dtick=y_tick_interval,
                gridcolor='lightgray',
                showline=True,
                linewidth=1,
                linecolor='black',
                mirror=True
            ),
            plot_bgcolor='white'
        )
        fig.update_traces(line_width=3)

    plots = mo.hstack([fig1, fig2, fig3, fig4], gap=0.5, wrap=True)

    return (plots,)


@app.cell
def model_display(Path):
    model_img_path = Path(__file__).parent.parent / "model" / "glimepiride_model.png"

    image = mo.image(src=str(model_img_path))

    description = mo.md(
        """
        <h1 style="margin-bottom: 0.25em;"><b>Glimepiride Digital Twin</b></h1>
        <h3 style="margin-bottom: 0.2em; margin-top: 1.0em"><b>Whole-body PBPK Model</b></h3>
        <p style="margin-top: 0;">
        <b>A)</b> Whole-body PBPK model illustrating glimepiride (GLI) administration, its systemic circulation via venous and arterial blood, and the key organs (liver, kidney, GI tract) involved in GLI metabolism, distribution, and excretion.<br>
        <b>B)</b> Intestinal model showing dissolution and absorption of GLI by enterocytes. No enterohepatic circulation of M1 and M2 is assumed, but reverse transport via enterocytes is included.<br>
        <b>C)</b> Hepatic model depicting CYP2C9-mediated metabolism of GLI to M1 and M2.<br>
        <b>D)</b> Renal model highlighting the elimination of M1 and M2 via urine; unchanged GLI is not excreted renally.<br>
        <b>E)</b> Key factors influencing glimepiride disposition accounted for by the model: administered dose, bodyweight, renal impairment, liver function (cirrhosis), and CYP2C9 genotypes.
        </p>
        """
    )

    model_display = mo.hstack([
        image.style({"flex": "1 1 28%", "min-width": "250px", "max-width": "350px"}),
        description.style({"flex": "2 2 70%", "max-width": "700px"})
    ], gap=1, wrap=True)

    return (model_display,)


@app.cell
def reference_disclaimer():
    reference = mo.md(
        """
        <div style="color: #888888;">
        <h3 style="color: #888888; margin-bottom: 0.2em; margin-top: 1.0em"><b>Reference</b></h3>
        <b>A Digital Twin of Glimepiride for Personalized and Stratified Diabetes Treatment.</b><br>
        <i>Michelle Elias, Matthias König (2025)</i><br>
        Preprints 2025, 2025061264. (preprint). <a href="https://doi.org/10.20944/preprints202506.1264.v1">doi:10.20944/preprints202506.1264.v1</a>
        </div>
        """
    )

    disclaimer_text = mo.md(
        """
        <h3 style="color: #888888; margin-bottom: 0.2em; margin-top: 1.0em"><b>Disclaimer</b></h3>
        <div style="color: #888888;">
        The software is provided <b>AS IS</b>, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.<br>
        This software is a <b>research proof-of-principle</b> and not fit for any clinical application. It is not intended to diagnose, treat, or inform medication dosing decisions. Always consult with qualified healthcare professionals for medical advice and treatment planning.
        </div>
        """
    )

    reference_disclaimer = mo.md(
        f"""
        <hr style="margin-bottom: 10px;">
        {reference}
        {disclaimer_text}
        """
    )

    return (reference_disclaimer,)


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

    pk_table_display = mo.md(
        f"""
        {mo.ui.table(
            display_data,
            show_column_summaries=False,
            show_download=False,
            label=None,
            selection=None,

        )}
        """
    )

    return (pk_table_display,)


@app.cell
def main_layout(
    reference_disclaimer,
    display_with_tabs,
    model_display,
    pk_table_display,
    plots,
):
    mo.vstack([
        # Header
        model_display,

        # Patient input and PK table
        mo.vstack([
            display_with_tabs,
            pk_table_display
        ]),

        # Plots
        plots,

        # Footer
        reference_disclaimer
    ])

    return


if __name__ == "__main__":
    app.run()
