import re
import streamlit as st
import requests

# ============================================================
# AutoAE V2
# AI-Assisted Pharmacovigilance Case Processing Tool
# ============================================================

st.set_page_config(
    page_title="AutoAE V2",
    page_icon="💊",
    layout="wide"
)
st.markdown("### DEVELOPED BY RATAN KUMAR")# =========================
# PROFESSIONAL HEADER
# =========================

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0px;
}

.subtitle {
    font-size: 20px;
    margin-top: 0px;
    margin-bottom: 5px;
}

.developer {
    font-size: 15px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💊 AutoAE V2</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Automated Pharmacovigilance Case Analysis Tool</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="developer">Developed by <b>Ratan Kumar</b></div>',
    unsafe_allow_html=True
)
# ============================================================
# HEADER
# ============================================================



st.divider()

# ============================================================
# CASE INPUT
# ============================================================

st.header("📄 Case Input")

case_text = st.text_area(
    "Paste ICSR / Adverse Event case details:",
    height=250,
    placeholder=(
        "Example: A 45-year-old male patient developed headache and nausea "
        "after taking ibuprofen. The case was reported by Dr. Sharma "
        "from India."
    )
)

# ============================================================
# DEMO DRUG DATABASE
# ============================================================

drug_database = {
    "paracetamol": "Paracetamol",
    "acetaminophen": "Paracetamol",
    "aspirin": "Aspirin",
    "ibuprofen": "Ibuprofen",
    "amoxicillin": "Amoxicillin",
    "metformin": "Metformin",
    "azithromycin": "Azithromycin",
    "cetirizine": "Cetirizine",
    "omeprazole": "Omeprazole",
    "diclofenac": "Diclofenac",
    "atorvastatin": "Atorvastatin",
    "amlodipine": "Amlodipine",
    "losartan": "Losartan",
    "pantoprazole": "Pantoprazole",
    "drug x": "Drug X"
}

# ============================================================
# MEDDRA DEMO MAPPING
# ============================================================

meddra_mapping = {
    "headache": {
        "PT": "Headache",
        "SOC": "Nervous system disorders"
    },
    "nausea": {
        "PT": "Nausea",
        "SOC": "Gastrointestinal disorders"
    },
    "vomiting": {
        "PT": "Vomiting",
        "SOC": "Gastrointestinal disorders"
    },
    "diarrhea": {
        "PT": "Diarrhoea",
        "SOC": "Gastrointestinal disorders"
    },
    "dizziness": {
        "PT": "Dizziness",
        "SOC": "Nervous system disorders"
    },
    "rash": {
        "PT": "Rash",
        "SOC": "Skin and subcutaneous tissue disorders"
    },
    "fever": {
        "PT": "Pyrexia",
        "SOC": "General disorders and administration site conditions"
    },
    "fatigue": {
        "PT": "Fatigue",
        "SOC": "General disorders and administration site conditions"
    },
    "abdominal pain": {
        "PT": "Abdominal pain",
        "SOC": "Gastrointestinal disorders"
    },
    "cough": {
        "PT": "Cough",
        "SOC": "Respiratory, thoracic and mediastinal disorders"
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_patient(text):
    """
    Extract basic patient demographic information.
    """

    patient = {
        "age": "Not reported",
        "sex": "Not reported"
    }

    # Age
    age_patterns = [
        r"\b(\d{1,3})[- ]?year[- ]?old\b",
        r"\bage[d]?\s*[:\-]?\s*(\d{1,3})\b"
    ]

    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient["age"] = match.group(1) + " years"
            break

    # Sex
    if re.search(r"\bmale\b|\bman\b|\bboy\b", text, re.IGNORECASE):
        patient["sex"] = "Male"
    elif re.search(r"\bfemale\b|\bwoman\b|\bgirl\b", text, re.IGNORECASE):
        patient["sex"] = "Female"

    return patient


def extract_reporter(text):
    """
    Extract basic reporter information.
    """

    reporter = {
        "name": "Not reported",
        "profession": "Not reported",
        "country": "Not reported",
        "email": "Not reported"
    }

    # Email
    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    if email_match:
        reporter["email"] = email_match.group(0)

    # Reporter name
    name_patterns = [
        r"\breported by\s+(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"\breporter\s*[:\-]\s*(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reporter["name"] = match.group(1)
            break

    # Profession
    professions = [
        "doctor",
        "physician",
        "pharmacist",
        "nurse",
        "pediatrician",
        "healthcare professional"
    ]

    for profession in professions:
        if re.search(r"\b" + re.escape(profession) + r"\b", text, re.IGNORECASE):
            reporter["profession"] = profession.title()
            break

    # Country
    countries = [
        "India",
        "USA",
        "United States",
        "UK",
        "United Kingdom",
        "Canada",
        "Australia",
        "Germany",
        "France"
    ]

    for country in countries:
        if re.search(r"\b" + re.escape(country) + r"\b", text, re.IGNORECASE):
            reporter["country"] = country
            break

    return reporter


def extract_drugs(text):
    """
    Identify drugs from the demo drug dictionary.
    """

    text_lower = text.lower()
    detected = []

    for key, display_name in drug_database.items():
        if re.search(r"\b" + re.escape(key) + r"\b", text_lower):
            if display_name not in detected:
                detected.append(display_name)

    return detected


def extract_events(text):
    """
    Identify adverse events from the demo MedDRA dictionary.
    """

    text_lower = text.lower()
    detected = []

    # Longer terms first
    event_terms = sorted(
        meddra_mapping.keys(),
        key=len,
        reverse=True
    )

    for event in event_terms:
        if re.search(r"\b" + re.escape(event) + r"\b", text_lower):
            if event not in detected:
                detected.append(event)

    return detected


def assess_seriousness(text):
    """
    Basic seriousness screening.
    This is a rule-based screening tool, not a final medical assessment.
    """

    text_lower = text.lower()

    seriousness_terms = {
        "death": "Death",
        "died": "Death",
        "fatal": "Death",
        "hospitalized": "Hospitalization",
        "hospitalised": "Hospitalization",
        "life-threatening": "Life-threatening",
        "life threatening": "Life-threatening",
        "disability": "Disability",
        "disabled": "Disability",
        "congenital": "Congenital anomaly",
        "birth defect": "Congenital anomaly"
    }

    detected = []

    for term, category in seriousness_terms.items():
        if term in text_lower:
            if category not in detected:
                detected.append(category)

    if detected:
        return detected

    return ["No seriousness criterion detected by rule-based screening"]


def check_validity(text, drugs, events, patient):
    """
    Basic ICSR minimum criteria check:
    1. Identifiable patient
    2. Suspect product
    3. Adverse event/reaction
    4. Identifiable reporter
    """

    has_patient = (
        patient["age"] != "Not reported"
        or patient["sex"] != "Not reported"
        or bool(
            re.search(
                r"\bpatient\b|\bsubject\b",
                text,
                re.IGNORECASE
            )
        )
    )

    has_drug = len(drugs) > 0
    has_event = len(events) > 0

    has_reporter = bool(
        re.search(
            r"\breported by\b|\breporter\b|\bdoctor\b|\bphysician\b|"
            r"\bpharmacist\b|\bnurse\b|\bdr\.",
            text,
            re.IGNORECASE
        )
    )

    criteria = {
        "Identifiable patient": has_patient,
        "Suspect product": has_drug,
        "Adverse event/reaction": has_event,
        "Identifiable reporter": has_reporter
    }

    return criteria
# ============================================================
# PUBMED INTEGRATION
# ============================================================

def search_pubmed(query, max_results=5):
    """
    Search PubMed using NCBI E-utilities API.
    Returns recent relevant article details.
    """

    if not query.strip():
        return []

    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance",
            "tool": "AutoAE_V2"
        }

        search_response = requests.get(
            search_url,
            params=search_params,
            timeout=10
        )

        search_response.raise_for_status()

        pmids = search_response.json()["esearchresult"]["idlist"]

        if not pmids:
            return []

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

        summary_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
            "tool": "AutoAE_V2"
        }

        summary_response = requests.get(
            summary_url,
            params=summary_params,
            timeout=10
        )

        summary_response.raise_for_status()

        data = summary_response.json()["result"]

        articles = []

        for pmid in pmids:
            article = data.get(pmid, {})

            articles.append({
                "pmid": pmid,
                "title": article.get("title", "Title not available"),
                "journal": article.get("fulljournalname", "Journal not available"),
                "year": article.get("pubdate", "Year not available"),
                "authors": ", ".join(
                    author.get("name", "")
                    for author in article.get("authors", [])
                    if author.get("name")
                )
            })

        return articles

    except Exception as e:
        st.warning(f"PubMed search unavailable: {e}")
        return []

# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button("🔍 Analyze Case", type="primary"):

    if not case_text.strip():

        st.warning("Please enter case details first.")

    else:

        text = case_text.strip()

        # ----------------------------------------------------
        # EXTRACTION
        # ----------------------------------------------------

        patient = extract_patient(text)
        reporter = extract_reporter(text)
        drugs = extract_drugs(text)
        events = extract_events(text)

        seriousness = assess_seriousness(text)
        validity = check_validity(
            text,
            drugs,
            events,
            patient
        )

        # ----------------------------------------------------
        # PUBMED LITERATURE SEARCH
        # ----------------------------------------------------

        pubmed_query_parts = []

        if drugs:
            pubmed_query_parts.extend(drugs)

        if events:
            pubmed_query_parts.extend(events)

        pubmed_query = " AND ".join(
            f'"{term}"' for term in pubmed_query_parts
        )

        pubmed_articles = search_pubmed(
            pubmed_query,
            max_results=5
        )

        # ====================================================
        # CASE ANALYSIS
        # ====================================================

        st.divider()

        st.header("📊 Case Analysis")

        # ====================================================
        # PATIENT INFORMATION
        # ====================================================

        st.subheader("👤 Patient Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Age:**", patient["age"])

        with col2:
            st.write("**Sex:**", patient["sex"])

        # ====================================================
        # REPORTER INFORMATION
        # ====================================================

        st.subheader("🧑‍⚕️ Reporter Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Name:**", reporter["name"])
            st.write("**Profession:**", reporter["profession"])

        with col2:
            st.write("**Country:**", reporter["country"])
            st.write("**Email:**", reporter["email"])

        # ====================================================
        # SUSPECT DRUGS
        # ====================================================

        st.subheader("💊 Suspected Drug(s)")

        if drugs:
            for drug in drugs:
                st.write(f"- {drug}")
        else:
            st.write("No drug detected.")

        # ====================================================
        # ADVERSE EVENTS
        # ====================================================

        st.subheader("⚠️ Adverse Event(s)")

        if events:
            for event in events:
                st.write(f"- {event}")
        else:
            st.write("No adverse event detected.")

        # ====================================================
        # MEDDRA MAPPING
        # ====================================================

        st.subheader("📌 MedDRA Mapping")

        if events:

            for event in events:

                mapping = meddra_mapping[event]

                st.write(f"**Reported Term:** {event.title()}")
                st.write(f"**MedDRA PT:** {mapping['PT']}")
                st.write(f"**SOC:** {mapping['SOC']}")

                st.divider()

        else:
            st.info("No event available for MedDRA mapping.")

        # ====================================================
        # SERIOUSNESS
        # ====================================================

        st.subheader("🚨 Seriousness Screening")

        for item in seriousness:
            st.write(f"- {item}")

        st.caption(
            "Note: This is a rule-based screening output and "
            "does not replace qualified pharmacovigilance assessment."
        )

        # ====================================================
        # ICSR VALIDITY
        # ====================================================

        st.subheader("📄 ICSR Validity Check")

        for criterion, result in validity.items():

            if result:
                st.write(f"✓ {criterion}: Present")
            else:
                st.write(f"✗ {criterion}: Not identified")

        all_four = all(validity.values())

        # ====================================================
        # PUBMED LITERATURE
        # ====================================================

        st.divider()

        st.subheader("📚 PubMed Literature Search")

        if pubmed_query:
            st.caption(f"Search query: {pubmed_query}")

            if pubmed_articles:

                for article in pubmed_articles:

                    st.markdown(
                        f"### {article['title']}"
                    )

                    st.write(
                        f"**Journal:** {article['journal']}"
                    )

                    st.write(
                        f"**Publication:** {article['year']}"
                    )

                    if article["authors"]:
                        st.write(
                            f"**Authors:** {article['authors']}"
                        )

                    st.markdown(
                        f"[View PubMed article](https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/)"
                    )

                    st.divider()

            else:
                st.info("No relevant PubMed articles found.")

        else:
            st.info(
                "PubMed search requires at least one detected drug "
                "or adverse event."
            )

        if all_four:

            st.success(
                "Potentially Valid ICSR: All four minimum criteria "
                "were identified."
            )

        else:

            missing = [
                criterion
                for criterion, result in validity.items()
                if not result
            ]

            st.warning(
                "Potentially Invalid / Incomplete ICSR. "
                "Missing: " + ", ".join(missing)
            )

        # ====================================================
        # AUTOMATED CASE SUMMARY
        # ====================================================

        st.subheader("📝 Automated Case Summary")

        age = patient["age"]
        sex = patient["sex"]

        drug_text = ", ".join(drugs) if drugs else "no suspect drug identified"
        event_text = ", ".join(
            [meddra_mapping[e]["PT"] for e in events]
        ) if events else "no adverse event identified"

        summary = (
            f"The case concerns a {age} {sex.lower()} patient. "
            f"The suspected product identified was {drug_text}. "
            f"The reported adverse event(s) were {event_text}. "
            f"Basic MedDRA mapping and ICSR minimum-criteria screening "
            f"were performed automatically."
        )

        st.info(summary)

        # ====================================================
        # DISCLAIMER
        # ====================================================

        st.divider()

        st.caption(
            "AutoAE V2 is a prototype pharmacovigilance support tool. "
            "Drug/event extraction, MedDRA mapping and validity screening "
            "are rule-based demonstrations and should be reviewed by a "
            "qualified pharmacovigilance professional."
        )