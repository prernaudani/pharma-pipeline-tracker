import requests
import pandas as pd
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Pharma Pipeline Tracker",
    page_icon="💊",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("💊 Pharma Pipeline Tracker")

st.write(
    "Search ClinicalTrials.gov to explore the clinical "
    "development status of drugs and development codes."
)


# --------------------------------------------------
# SEARCH BOX
# --------------------------------------------------

search_term = st.text_input(
    "Enter drug or development code",
    placeholder="Example: semaglutide, insulin, ABC-123"
)


# --------------------------------------------------
# SEARCH BUTTON
# --------------------------------------------------

search_button = st.button("🔍 Search Clinical Trials")


# --------------------------------------------------
# SEARCH FUNCTION
# --------------------------------------------------

def search_clinical_trials(search_term):

    url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.term": search_term + " AND AREA[StudyType]INTERVENTIONAL",
        "pageSize": 10
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()

    studies = data.get("studies", [])

    results = []

    search_lower = search_term.lower()


    # --------------------------------------------------
    # PROCESS EACH TRIAL
    # --------------------------------------------------

    for study in studies:

        protocol = study["protocolSection"]

        identification = protocol["identificationModule"]
        design = protocol["designModule"]
        status = protocol["statusModule"]
        interventions_module = protocol[
            "armsInterventionsModule"
        ]
        conditions = protocol["conditionsModule"]
        sponsor_module = protocol[
            "sponsorCollaboratorsModule"
        ]


        # ----------------------------------------------
        # BASIC TRIAL INFORMATION
        # ----------------------------------------------

        nct_id = identification["nctId"]

        title = identification["briefTitle"]

        study_type = design["studyType"]


        # ----------------------------------------------
        # PHASE
        # ----------------------------------------------

        if "phases" in design:

            phase = design["phases"][0]

        else:

            phase = "NOT SPECIFIED"


        # ----------------------------------------------
        # STATUS
        # ----------------------------------------------

        trial_status = status["overallStatus"]


        # ----------------------------------------------
        # INDICATION
        # ----------------------------------------------

        if "conditions" in conditions:

            indication = ", ".join(
                conditions["conditions"]
            )

        else:

            indication = "NOT SPECIFIED"


        # ----------------------------------------------
        # SPONSOR
        # ----------------------------------------------

        if "leadSponsor" in sponsor_module:

            sponsor = sponsor_module[
                "leadSponsor"
            ]["name"]

        else:

            sponsor = "NOT SPECIFIED"


        # ----------------------------------------------
        # START DATE
        # ----------------------------------------------

        if "startDateStruct" in status:

            start_date = status[
                "startDateStruct"
            ].get(
                "date",
                "NOT SPECIFIED"
            )

        else:

            start_date = "NOT SPECIFIED"


        # ----------------------------------------------
        # PRIMARY COMPLETION DATE
        # ----------------------------------------------

        if "primaryCompletionDateStruct" in status:

            primary_completion_date = status[
                "primaryCompletionDateStruct"
            ].get(
                "date",
                "NOT SPECIFIED"
            )

        else:

            primary_completion_date = "NOT SPECIFIED"


        # ----------------------------------------------
        # COMPLETION DATE
        # ----------------------------------------------

        if "completionDateStruct" in status:

            completion_date = status[
                "completionDateStruct"
            ].get(
                "date",
                "NOT SPECIFIED"
            )

        else:

            completion_date = "NOT SPECIFIED"


        # ------------------------------------------------
        # PROCESS INTERVENTIONS
        # ------------------------------------------------

        interventions = interventions_module.get(
            "interventions",
            []
        )


        for intervention in interventions:

            intervention_type = intervention["type"]

            drug_name = intervention["name"]

            drug_lower = drug_name.lower()


            # ------------------------------------------
            # KEEP ONLY DRUG INTERVENTIONS
            # ------------------------------------------

            if intervention_type == "DRUG":


                # --------------------------------------
                # MATCH USER'S SEARCH TERM
                # --------------------------------------

                if search_lower in drug_lower:


                    # ----------------------------------
                    # REMOVE PLACEBO
                    # ----------------------------------

                    if "placebo" not in drug_lower:

                        results.append({

                            "NCT ID": nct_id,

                            "Drug": drug_name,

                            "Indication": indication,

                            "Sponsor/Company": sponsor,

                            "Title": title,

                            "Study Type": study_type,

                            "Phase": phase,

                            "Status": trial_status,

                            "Start Date": start_date,

                            "Primary Completion Date":
                                primary_completion_date,

                            "Completion Date":
                                completion_date

                        })


    return pd.DataFrame(results)


# --------------------------------------------------
# RUN SEARCH
# --------------------------------------------------

if search_button:

    if search_term.strip() == "":

        st.warning(
            "Please enter a drug or development code."
        )

    else:

        with st.spinner(
            "Searching ClinicalTrials.gov..."
        ):

            df = search_clinical_trials(
                search_term.strip()
            )


        # ----------------------------------------------
        # DISPLAY RESULTS
        # ----------------------------------------------

        if len(df) > 0:

            st.success(
                f"Found {len(df)} drug-trial records."
            )

            st.subheader(
                "Clinical Trial Results"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No matching drug interventions found."
            )