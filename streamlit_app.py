
import os
import json
import streamlit as st

st.set_page_config(
    page_title="VerifyKaro",
    page_icon="🛡️",
    layout="centered"
)

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

from app import investigate, TEST_CASES

st.title("🛡️ VerifyKaro")
st.caption("Agentic Scam Investigation & Response System")

st.info(
    "VerifyKaro investigates suspicious messages, selects "
    "verification tools, reviews evidence and recommends safer actions."
)

st.warning("Never enter OTPs, passwords or banking credentials.")


def show_report(report):
    plan = report.get("agent_plan", {})
    used = report.get("tools_used", [])
    tools = report.get("tool_results", {})
    result = report.get("reflection_and_final_response", {})

    st.header("Investigation Report")

    assessment = result.get("assessment", "Insufficient evidence")

    if assessment == "Suspicious":
        st.error("🚨 SUSPICIOUS MESSAGE")
    elif assessment == "Apparently legitimate":
        st.success("✅ APPARENTLY LEGITIMATE")
        st.caption("This is not a guarantee of safety.")
    else:
        st.warning("⚠️ INSUFFICIENT EVIDENCE")

    st.subheader("🧠 1. Agent's Plan")
    st.write(plan.get("reasoning_summary", "Not available"))

    question = plan.get("clarification_question", "")
    if question:
        st.info("Clarification needed: " + question)

    st.subheader("🛠️ 2. Tools Used")
    st.write(f"Selected {len(used)} tool(s).")

    for name in used:
        if name == "url_inspector":
            data = tools.get(name, {})
            with st.container(border=True):
                st.markdown("**🔗 URL Inspector**")
                st.write(f"Links found: {data.get('urls_found', 0)}")

                for item in data.get("results", []):
                    st.write("Domain:", item.get("domain", ""))
                    st.write(
                        "Written URL scheme:",
                        item.get("scheme", "Unknown")
                    )
                    for warning in item.get("warnings", []):
                        st.warning(warning)

                st.caption("Static URL inspection only. No links opened.")

        elif name == "official_source_lookup":
            data = tools.get(name, {})
            with st.container(border=True):
                st.markdown("**📚 Official Source Lookup**")
                matches = data.get("matches", [])

                if matches:
                    for match in matches:
                        st.write("**" + match.get("source", "") + "**")
                        st.write(match.get("information", ""))
                        st.caption("General guidance — not case-specific proof.")
                        if match.get("official_link"):
                            st.link_button(
                                "Official reference",
                                match["official_link"]
                            )
                else:
                    st.write("No related reference found.")

                st.caption(
                    "Curated knowledge base, not live web search."
                )

    st.subheader("🔍 3. Evidence and Reflection")

    st.markdown("**Message warning signs**")
    for clue in result.get("message_indicators", []):
        st.write("•", clue)

    st.markdown("**Technical findings**")
    findings = result.get("technical_findings", [])
    if findings:
        for finding in findings:
            st.write("•", finding)
    else:
        st.write("No verified technical warning signs.")

    st.markdown("**General advisory information**")
    guidance = result.get("general_guidance", [])
    if guidance:
        for item in guidance:
            st.write("•", item)
    else:
        st.write("No relevant advisory information.")

    st.markdown("**AI evidence review**")
    st.write(result.get("evidence_review", ""))

    st.markdown("**What could not be verified**")
    st.write(result.get("limitations", ""))

    st.subheader("🛡️ 4. Recommended Actions")
    for i, action in enumerate(
        result.get("safe_next_steps", []), 1
    ):
        st.write(f"{i}. {action}")

    complaint = result.get("complaint_draft", "")
    if complaint:
        st.subheader("📝 Optional Complaint Draft")
        st.text_area(
            "For user review only",
            value=complaint,
            height=150
        )
        st.caption("No complaint has been submitted.")

    with st.expander("View Full Technical Report"):
        st.json(report)

    st.caption(
        "Educational prototype. No URLs were opened "
        "or external reports submitted."
    )


tab1, tab2 = st.tabs([
    "🔎 Investigate Message",
    "🧪 Five Required Tests"
])

with tab1:
    examples = {"Custom message": ""}
    for case in TEST_CASES:
        examples[case["name"]] = case["input"]

    choice = st.selectbox(
        "Choose an example or enter your own message",
        list(examples.keys())
    )

    message = st.text_area(
        "Suspicious message",
        value=examples[choice],
        height=130
    )

    if st.button("Investigate Message", type="primary"):
        if not message.strip():
            st.warning("Enter a message first.")
        elif not api_key:
            st.error("Gemini API key is missing.")
        else:
            with st.spinner("Agent is investigating..."):
                try:
                    report = investigate(message)
                    if isinstance(report, str):
                        report = json.loads(report)
                    show_report(report)
                except Exception as error:
                    st.error("Investigation could not be completed.")
                    st.caption(str(error)[:300])


with tab2:
    st.subheader("Five-Case Evaluation")
    st.write(
        "Three regular cases and two challenging cases. "
        "All results come from actual agent executions."
    )

    if st.button("Run All Five Tests", type="primary"):
        rows = []

        for case in TEST_CASES:
            try:
                report = investigate(case["input"])
                result = report.get(
                    "reflection_and_final_response", {}
                )

                rows.append({
                    "Test": case["name"],
                    "Challenge": "Yes" if case["challenge"] else "No",
                    "Expected": case["expected"],
                    "Actual assessment": result.get(
                        "assessment", "Unknown"
                    ),
                    "Tools used": ", ".join(
                        report.get("tools_used", [])
                    ),
                    "Error": ""
                })

            except Exception as error:
                rows.append({
                    "Test": case["name"],
                    "Challenge": "Yes" if case["challenge"] else "No",
                    "Expected": case["expected"],
                    "Actual assessment": "ERROR",
                    "Tools used": "",
                    "Error": str(error)[:180]
                })

        st.session_state["test_results"] = rows

    if "test_results" in st.session_state:
        st.dataframe(
            st.session_state["test_results"],
            use_container_width=True
        )

        st.download_button(
            "Download Test Results",
            data=json.dumps(
                st.session_state["test_results"],
                indent=2
            ),
            file_name="verifykaro_test_results.json",
            mime="application/json"
        )

    st.caption(
        "A result is not automatically counted as a pass. "
        "Review whether each case actually met its expected behavior."
    )
