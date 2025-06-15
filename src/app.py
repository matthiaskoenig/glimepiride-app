"""Glimepiride Webapp."""

import marimo

__generated_with = "0.13.15"
app = marimo.App(layout_file="layouts/app.grid.json")

with app.setup:
    import marimo as mo
    import pandas as pd
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
        "time": "<b>Time [hr]</b>",
        "[Cve_gli]": "<b>Glimepiride Plasma [µM]</b>",
        "[Cve_m1]": "<b>M1 Plasma [µM]</b>",
        "[Cve_m2]": "<b>M2 Plasma [µM]</b>",
        "Aurine_m1_m2": "<b>M1 + M2 Urine [µmole]</b>"
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
def patient_storage():
    # State for storing saved patients
    saved_patients, set_saved_patients = mo.state({})

    return saved_patients, set_saved_patients


@app.cell
def patient_name_input_state():
    patient_name_value, set_patient_name_value = mo.state("")
    return patient_name_value, set_patient_name_value


@app.cell
def patient_save_controls(patient_name_value, set_patient_name_value):
    patient_name_input = mo.ui.text(
        placeholder="Enter patient name",
        label="Patient Name",
        value=patient_name_value(),
        on_change=set_patient_name_value
    )

    # Save button with callback
    save_button = mo.ui.button(
        label="Save Patient",
        on_click=lambda value: value + 1 if value else 1
    )

    return patient_name_input, save_button


@app.cell
def display_save_section(patient_name_input, save_button):
    mo.md(
        f"""
    ### Save Current Configuration
    {mo.hstack([patient_name_input, save_button], gap=0)}
    """
    )
    return


@app.cell
def save_patient(
    PODOSE_gli,
    allele1_activity,
    allele2_activity,
    bw_value,
    cirrhosis_degree,
    crcl_value,
    patient_name_input,
    save_button,
    saved_patients,
    set_patient_name_value,
    set_saved_patients,
):
    if save_button.value and patient_name_input.value:
        patient_name = patient_name_input.value.strip()

        if patient_name:
            patient_config = {
                "dose": PODOSE_gli.value,
                "weight": bw_value(),
                "crcl": crcl_value(),
                "cirrhosis": cirrhosis_degree(),
                "allele1": allele1_activity(),
                "allele2": allele2_activity(),
            }

            updated_patients = saved_patients().copy()
            updated_patients[patient_name] = patient_config
            set_saved_patients(updated_patients)

            # Clear input field
            set_patient_name_value("")

    return


@app.cell
def patients_table_display(delete_buttons, load_buttons, saved_patients):
    # List of dicts for table data
    table_data = []

    for button_index, (name, config) in enumerate(saved_patients().items()):
        row_data = {
            "Name": name,
            "Dose [mg]": int(config["dose"]),
            "Weight [kg]": config["weight"],
            "CrCl [mL/min]": int(config["crcl"]),
            "Cirrhosis [-]": f"{config['cirrhosis']:.2f}",
            "Allele 1 [%]": int(config["allele1"]),
            "Allele 2 [%]": int(config["allele2"]),
            "Load": load_buttons[button_index],
            "Delete": delete_buttons[button_index]
        }

        table_data.append(row_data)

    mo.md(
        f"""
        ### Saved Patients
        {mo.ui.table(
            table_data,
            show_column_summaries=False,
            pagination=True,
            page_size=5
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
    set_saved_patients,
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

    def delete_patient(patient_name):
        updated_patients = saved_patients().copy()
        if patient_name in updated_patients:
            del updated_patients[patient_name]
            set_saved_patients(updated_patients)

    return delete_patient, load_patient


@app.cell
def patient_action_buttons(delete_patient, load_patient, saved_patients):
    # Create load buttons for each saved patient
    load_buttons = mo.ui.array([
        mo.ui.button(
            label="Load",
            kind="neutral",
            on_change=lambda v, name=name: load_patient(name)
        )
        for name in saved_patients().keys()
    ])

    # Create delete buttons for each saved patient
    delete_buttons = mo.ui.array([
        mo.ui.button(
            label="Delete",
            kind="danger",
            on_change=lambda v, name=name: delete_patient(name)
        )
        for name in saved_patients().keys()
    ])

    return delete_buttons, load_buttons


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
    ## Patient-Specific Parameters
    {mo.vstack([
        PODOSE_gli,
        BW,
        mo.hstack([crcl, renal_impairment_dropdown], gap=0),
        mo.hstack([f_cirrhosis, cirrhosis_dropdown], gap=0),
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

    height = 400
    width = 450

    axis_style = {
        "title_font": {"size": 17},
        "tickfont": {"size": 15}
    }

    fig1 = px.line(df, x="time", y="[Cve_gli]", title=None, labels=labels, markers=True, range_y=[0, 1], range_x=[0, 25], height=height, width=width)
    fig1.update_layout(xaxis=axis_style, yaxis=axis_style)

    fig2 = px.line(df, x="time", y="[Cve_m1]", title=None, labels=labels, markers=True, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig2.update_layout(xaxis=axis_style, yaxis=axis_style)

    fig3 = px.line(df, x="time", y="[Cve_m2]", title=None, labels=labels, markers=True, range_y=[0, 0.2], range_x=[0, 25], height=height, width=width)
    fig3.update_layout(xaxis=axis_style, yaxis=axis_style)

    fig4 = px.line(df, x="time", y="Aurine_m1_m2", title=None, labels=labels, markers=True, range_y=[0, 10], height=height, width=width)
    fig4.update_layout(xaxis=axis_style, yaxis=axis_style)

    mo.hstack([fig1, fig2, fig3, fig4], gap=0)
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
    s = r.simulate(start=0, end=60*50, steps=5000)  # [min]
    df = pd.DataFrame(s, columns=s.colnames)
    # unit conversions
    for col in df.columns:
        df[col] = df[col] * units_factors[col]  # [hr]
    return (df,)


if __name__ == "__main__":
    app.run()
