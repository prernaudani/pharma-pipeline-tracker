import requests
import pandas as pd


# --------------------------------------------------
# STEP 1: Ask the user for a drug/development code
# --------------------------------------------------

search_term = input("Enter drug or development code: ").strip().lower()


# --------------------------------------------------
# STEP 2: Connect to ClinicalTrials.gov API
# --------------------------------------------------

url = "https://clinicaltrials.gov/api/v2/studies"

params = {
    "query.term": search_term + " AND AREA[StudyType]INTERVENTIONAL",
    "pageSize": 10
}


response = requests.get(url, params=params)

print("Status code:", response.status_code)


# --------------------------------------------------
# STEP 3: Convert API response into Python data
# --------------------------------------------------

data = response.json()

studies = data["studies"]


# --------------------------------------------------
# STEP 4: Prepare an empty list for our results
# --------------------------------------------------

results = []

search_lower = search_term.lower()


# --------------------------------------------------
# STEP 5: Go through every clinical trial
# --------------------------------------------------

for study in studies:

    protocol = study["protocolSection"]

    identification = protocol["identificationModule"]
    design = protocol["designModule"]
    status = protocol["statusModule"]
    interventions = protocol["armsInterventionsModule"]["interventions"]
    conditions = protocol["conditionsModule"]
    sponsor_module = protocol["sponsorCollaboratorsModule"]


    # ----------------------------------------------
    # Get NCT ID
    # ----------------------------------------------

    nct_id = identification["nctId"]


    # ----------------------------------------------
    # Get trial title
    # ----------------------------------------------

    title = identification["briefTitle"]


    # ----------------------------------------------
    # Get study type
    # ----------------------------------------------

    study_type = design["studyType"]


    # ----------------------------------------------
    # Get clinical trial phase
    # ----------------------------------------------

    if "phases" in design:

        phase = design["phases"][0]

    else:

        phase = "NOT SPECIFIED"


    # ----------------------------------------------
    # Get clinical trial status
    # ----------------------------------------------

    trial_status = status["overallStatus"]


    # ----------------------------------------------
    # Get indication
    # ----------------------------------------------

    if "conditions" in conditions:

        indication = ", ".join(
            conditions["conditions"]
        )

    else:

        indication = "NOT SPECIFIED"


    # ----------------------------------------------
    # Get lead sponsor / company
    # ----------------------------------------------

    if "leadSponsor" in sponsor_module:

        sponsor = sponsor_module["leadSponsor"]["name"]

    else:

        sponsor = "NOT SPECIFIED"


    # ----------------------------------------------
    # Get trial dates
    # ----------------------------------------------

    if "startDateStruct" in status:

        start_date = status["startDateStruct"].get(
            "date",
            "NOT SPECIFIED"
        )

    else:

        start_date = "NOT SPECIFIED"


    if "primaryCompletionDateStruct" in status:

        primary_completion_date = status[
            "primaryCompletionDateStruct"
        ].get(
            "date",
            "NOT SPECIFIED"
        )

    else:

        primary_completion_date = "NOT SPECIFIED"


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
    # STEP 6: Look at all interventions
    # ------------------------------------------------

    for intervention in interventions:

        intervention_type = intervention["type"]

        drug_name = intervention["name"]

        drug_lower = drug_name.lower()


        # ------------------------------------------------
        # Keep only DRUG interventions
        # ------------------------------------------------

        if intervention_type == "DRUG":


            # ------------------------------------------------
            # Keep only drugs matching the user's search
            # ------------------------------------------------

            if search_lower in drug_lower:


                # ------------------------------------------------
                # Remove placebo interventions
                # ------------------------------------------------

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


# --------------------------------------------------
# STEP 7: Convert results into a DataFrame
# --------------------------------------------------

df = pd.DataFrame(results)


# --------------------------------------------------
# STEP 8: Display the results
# --------------------------------------------------

print("\nClinical Trial Results:")


if len(df) > 0:

    print(df.to_string(index=False))

else:

    print("No matching drug interventions found.")


# --------------------------------------------------
# STEP 9: Display number of results
# --------------------------------------------------

print("\nNumber of drug-trial records:", len(df))