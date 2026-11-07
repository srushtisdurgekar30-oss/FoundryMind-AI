
import os
import json
import streamlit as st

from datetime import datetime
from collections import Counter
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq


# =====================================================
# 1. CONFIGURATION
# =====================================================

load_dotenv()

st.set_page_config(
    page_title="FoundryMind AI",
    page_icon="🏭",
    layout="wide"
)

BANK_ID = "foundrymind"
DATA_FILE = "foundrymind_data.json"

st.title("🏭 FoundryMind AI")
st.caption(
    "Manufacturing Quality Intelligence powered by Hindsight"
)


# =====================================================
# 2. API KEY VALIDATION
# =====================================================

if not os.getenv("HINDSIGHT_API_KEY"):
    st.error("Hindsight API key missing. Check your .env file.")
    st.stop()

if not os.getenv("HINDSIGHT_BASE_URL"):
    st.error("Hindsight base URL missing. Check your .env file.")
    st.stop()


# =====================================================
# 3. API CLIENTS
# =====================================================

@st.cache_resource
def get_client():
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY")
    )


@st.cache_resource
def get_groq_client():
    return Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )


client = get_client()


# =====================================================
# 4. LOCAL DASHBOARD STORAGE
# =====================================================

def load_dashboard_data():

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_dashboard_record(record):

    records = load_dashboard_data()

    # Update an existing record of the same type and ID
    updated = False

    for index, old_record in enumerate(records):

        if (
            old_record.get("type") == record.get("type")
            and old_record.get("incident_id") == record.get("incident_id")
        ):
            records[index] = record
            updated = True
            break

    if not updated:
        records.append(record)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)


# =====================================================
# 5. DUPLICATE MEMORY FILTER
# =====================================================

def deduplicate_memories(raw_memories):

    unique_memories = []
    seen_memories = set()

    for memory in raw_memories:

        memory_text = memory.text.strip()

        normalized_text = " ".join(
            memory_text.lower().split()
        )

        if normalized_text not in seen_memories:

            seen_memories.add(normalized_text)
            unique_memories.append(memory)

    return unique_memories


# =====================================================
# 6. APPLICATION TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([

    "📝 Record Incident",
    "🧠 Ask Memory",
    "🔍 Investigation Assistant",
    "📚 Investigation Outcome",
    "📊 Quality Dashboard"

])


# =====================================================
# TAB 1: RECORD INCIDENT
# =====================================================

with tab1:

    st.subheader("📝 Record a Manufacturing Incident")

    incident_id = st.text_input(
        "Incident ID",
        value="F-003",
        key="incident_id"
    )

    defect = st.selectbox(
        "Defect Type",
        [
            "Broken edge",
            "Crack",
            "Extra material / Flash",
            "Missing trimming",
            "Indent"
        ],
        key="incident_defect"
    )

    details = st.text_area(
        "Incident Details",
        placeholder="Describe the defect and inspection observations..."
    )

    if st.button("Save to Hindsight", type="primary"):

        if not incident_id.strip() or not details.strip():

            st.warning("Enter an incident ID and details.")

        else:

            try:

                memory = (
                    f"Incident {incident_id.strip()}: "
                    f"Manufacturing defect: {defect}. "
                    f"Details: {details.strip()}"
                )

                with st.spinner("Saving incident..."):

                    # Save to Hindsight
                    client.retain(
                        bank_id=BANK_ID,
                        content=memory
                    )

                    # Save structured dashboard record
                    save_dashboard_record({

                        "type": "Incident",
                        "incident_id": incident_id.strip(),
                        "defect": defect,
                        "details": details.strip(),
                        "status": "Recorded",
                        "date": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        )

                    })

                st.success(
                    "Incident successfully saved to Hindsight!"
                )

                st.info(
                    "Incident also added to the Quality Dashboard."
                )

            except Exception as e:

                st.error(f"Could not save incident: {e}")


# =====================================================
# TAB 2: ASK HINDSIGHT MEMORY
# =====================================================

with tab2:

    st.subheader("🧠 Recall Previous Manufacturing Knowledge")

    question = st.text_input(
        "Ask FoundryMind",
        placeholder="What previous incidents involved broken edges?"
    )

    if st.button("Search Memories", type="primary"):

        if not question.strip():

            st.warning("Enter a question first.")

        else:

            try:

                with st.spinner("Searching Hindsight memories..."):

                    result = client.recall(
                        bank_id=BANK_ID,
                        query=question.strip()
                    )

                raw_memories = result.results or []

                memories = deduplicate_memories(raw_memories)

                st.success("Memory search completed!")

                st.caption(
                    f"{len(memories)} unique memories from "
                    f"{len(raw_memories)} retrieved results."
                )

                if memories:

                    for i, memory in enumerate(memories, 1):

                        st.markdown(f"**Memory {i}**")
                        st.write(memory.text)
                        st.divider()

                else:

                    st.info("No relevant memories found.")

            except Exception as e:

                st.error(f"Memory search failed: {e}")


# =====================================================
# TAB 3: INVESTIGATION ASSISTANT
# =====================================================

with tab3:

    st.subheader("🔍 Manufacturing Investigation Assistant")

    defect_type = st.selectbox(
        "Select the new defect",
        [
            "Broken edge",
            "Crack",
            "Extra material / Flash",
            "Missing trimming",
            "Indent"
        ],
        key="investigation_defect"
    )

    description = st.text_area(
        "Describe the current incident",
        placeholder="Describe the defect and inspection observations...",
        key="investigation_description"
    )

    if st.button("Investigate with Hindsight", type="primary"):

        if not description.strip():

            st.warning("Please describe the incident.")

        elif not os.getenv("GROQ_API_KEY"):

            st.error("Groq API key missing. Check your .env file.")

        else:

            try:

                # STEP 1: RETRIEVE MEMORIES

                query = (
                    f"Previous manufacturing incidents involving "
                    f"{defect_type}. Find investigations, observations, "
                    f"outcomes and verified causes. "
                    f"Current incident: {description}"
                )

                with st.spinner("Searching previous incidents..."):

                    result = client.recall(
                        bank_id=BANK_ID,
                        query=query
                    )

                raw_memories = result.results or []

                memories = deduplicate_memories(raw_memories)

                # STEP 2: DISPLAY MEMORIES

                st.markdown("### 🧠 Relevant Previous Memories")

                st.caption(
                    f"{len(memories)} unique memories from "
                    f"{len(raw_memories)} retrieved results."
                )

                if memories:

                    for i, memory in enumerate(memories, 1):

                        st.markdown(f"**Previous Memory {i}**")
                        st.write(memory.text)
                        st.divider()

                    memory_context = "\n".join(
                        f"- {memory.text}"
                        for memory in memories
                    )

                else:

                    memory_context = "No relevant previous memories found."

                    st.info(memory_context)

                # STEP 3: AI PROMPT

                prompt = f"""
You are FoundryMind AI, a manufacturing quality
investigation assistant.

Your task is to help quality teams investigate
manufacturing defects using previous experience.

CURRENT DEFECT:
{defect_type}

CURRENT OBSERVATION:
{description}

PREVIOUS INCIDENT MEMORIES FROM HINDSIGHT:
{memory_context}

Prepare a structured investigation report containing:

1. Similar Previous Incidents
2. Important Historical Observations
3. Five Practical Investigation Steps
4. Possible Causes to Investigate
5. Information the Quality Team Should Record
6. Recommended Next Action

RULES:

- Use retrieved memories as historical evidence.
- Treat each incident ID as one incident.
- Do not repeat the same historical observation.
- Clearly distinguish confirmed facts from suggestions.
- Never invent facts or investigation results.
- Never claim an unverified root cause.
- Pending or inconclusive investigations are not
  evidence of a confirmed cause.
- Do not assume two incidents have the same root cause.
- Do not describe a recommended action as completed.
- Clearly identify when evidence is insufficient.
- Keep investigation steps practical and concise.
- Finish all six report sections completely.

IMPORTANT:
Possible causes are hypotheses only.
They must be verified by the quality team before
being treated as actual root causes.
"""

                # STEP 4: GROQ ANALYSIS

                groq_client = get_groq_client()

                with st.spinner(
                    "Groq AI is analyzing previous experiences..."
                ):

                    response = groq_client.chat.completions.create(

                        model="openai/gpt-oss-120b",

                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a careful industrial quality "
                                    "investigation assistant. "
                                    "Be evidence-based and never invent "
                                    "manufacturing facts."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],

                        temperature=0.3,
                        max_tokens=2000

                    )

                # STEP 5: DISPLAY REPORT

                report = response.choices[0].message.content

                if not report:
                    raise ValueError("Groq returned an empty report.")

                st.markdown("---")

                st.markdown("## 🤖 AI Investigation Report")

                st.markdown(report)

                # STEP 6: DOWNLOAD REPORT

                st.download_button(
                    label="📥 Download Investigation Report",
                    data=report,
                    file_name="FoundryMind_Investigation.txt",
                    mime="text/plain"
                )

                st.success(
                    "Investigation report generated successfully!"
                )

            except Exception as e:

                st.error(f"Investigation failed: {e}")


# =====================================================
# TAB 4: INVESTIGATION OUTCOME
# =====================================================

with tab4:

    st.subheader("📚 Record Investigation Outcome")

    st.write(
        "Save investigation findings into Hindsight "
        "for use in future investigations."
    )

    outcome_id = st.text_input(
        "Incident ID",
        placeholder="F-001",
        key="outcome_id"
    )

    investigation = st.text_area(
        "Investigation performed",
        placeholder="What checks were performed?",
        key="outcome_investigation"
    )

    findings = st.text_area(
        "Actual findings",
        placeholder="What did the team discover?",
        key="outcome_findings"
    )

    root_cause = st.text_area(
        "Verified root cause (if established)",
        placeholder="Leave blank if not yet confirmed.",
        key="outcome_root_cause"
    )

    corrective_action = st.text_area(
        "Corrective action",
        placeholder="What action was taken or recommended?",
        key="outcome_action"
    )

    verification = st.selectbox(
        "Verification status",
        [
            "Pending verification",
            "Verified",
            "Inconclusive"
        ],
        key="outcome_verification"
    )

    if st.button("Save Outcome to Hindsight", type="primary"):

        if not outcome_id.strip() or not findings.strip():

            st.warning(
                "Enter an incident ID and actual findings."
            )

        elif verification == "Verified" and not root_cause.strip():

            st.warning(
                "Enter the verified root cause before selecting Verified."
            )

        else:

            confirmed_cause = (
                root_cause.strip()
                if verification == "Verified"
                else "Not established"
            )

            outcome_memory = f"""
Manufacturing Investigation Outcome

Incident ID: {outcome_id.strip()}

Investigation performed:
{investigation.strip() or "Not specified"}

Actual findings:
{findings.strip()}

Verified root cause:
{confirmed_cause}

Corrective action:
{corrective_action.strip() or "Not specified"}

Verification status:
{verification}

Only treat the root cause as confirmed when
the verification status is Verified.
"""

            try:

                with st.spinner("Saving investigation outcome..."):

                    # Save outcome to Hindsight
                    client.retain(
                        bank_id=BANK_ID,
                        content=outcome_memory
                    )

                    # Save structured dashboard record
                    save_dashboard_record({

                        "type": "Outcome",
                        "incident_id": outcome_id.strip(),
                        "defect": "Not specified",
                        "details": findings.strip(),
                        "status": verification,
                        "date": datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        )

                    })

                st.success(
                    "Investigation outcome successfully saved to Hindsight!"
                )

                st.info(
                    "Future investigations can retrieve this experience."
                )

            except Exception as e:

                st.error(f"Could not save outcome: {e}")


# =====================================================
# TAB 5: QUALITY INTELLIGENCE DASHBOARD
# =====================================================

with tab5:

    st.title("📊 Quality Intelligence Dashboard")

    records = load_dashboard_data()

    incidents = [
        record for record in records
        if record.get("type") == "Incident"
    ]

    outcomes = [
        record for record in records
        if record.get("type") == "Outcome"
    ]

    # METRICS

    verified = sum(
        1 for record in outcomes
        if record.get("status") == "Verified"
    )

    pending = sum(
        1 for record in outcomes
        if record.get("status") == "Pending verification"
    )

    inconclusive = sum(
        1 for record in outcomes
        if record.get("status") == "Inconclusive"
    )

    st.subheader("Manufacturing Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Incidents",
        len(incidents)
    )

    col2.metric(
        "Investigation Outcomes",
        len(outcomes)
    )

    col3.metric(
        "Verified",
        verified
    )

    col4.metric(
        "Pending",
        pending
    )

    st.divider()

    # DEFECT DISTRIBUTION

    st.subheader("📈 Defect Distribution")

    if incidents:

        defect_counts = Counter(
            record.get("defect", "Unknown")
            for record in incidents
        )

        st.bar_chart(
            dict(defect_counts)
        )

    else:

        st.info(
            "No incident records yet. "
            "Record incidents to generate defect analytics."
        )

    st.divider()

    # VERIFICATION STATUS

    st.subheader("🔎 Investigation Verification Status")

    status_data = {
        "Verified": verified,
        "Pending Verification": pending,
        "Inconclusive": inconclusive
    }

    st.bar_chart(status_data)

    st.divider()

    # INCIDENT HISTORY

    st.subheader("📋 Recent Manufacturing History")

    if records:

        history = sorted(
            records,
            key=lambda record: record.get("date", ""),
            reverse=True
        )

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No dashboard history available yet."
        )

    # DOWNLOAD DASHBOARD DATA

    if records:

        dashboard_json = json.dumps(
            records,
            indent=4
        )

        st.download_button(
            label="📥 Download Dashboard Data",
            data=dashboard_json,
            file_name="FoundryMind_Manufacturing_Data.json",
            mime="application/json"
        )

    st.divider()

    st.caption(
        "FoundryMind AI | Manufacturing Quality Intelligence"
    )


# =====================================================
# END OF FOUNDRYMIND AI
# =====================================================
