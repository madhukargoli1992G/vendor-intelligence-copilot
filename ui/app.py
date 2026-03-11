import re
import requests
import streamlit as st
import pandas as pd

ASK_API_URL = "http://localhost:8000/ask"
UPLOAD_API_URL = "http://localhost:8000/ingest-upload"

st.set_page_config(page_title="Vendor Intelligence Copilot", layout="wide")


def ask_backend(question: str, vendor_name: str | None = None, doc_type: str | None = None):
    params = {"question": question}

    if vendor_name:
        params["vendor_name"] = vendor_name

    if doc_type:
        params["doc_type"] = doc_type

    response = requests.get(ASK_API_URL, params=params, timeout=120)
    response.raise_for_status()
    return response.json()


def extract_money(text: str):
    match = re.search(r"\$([\d,]+)", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def extract_percentage(text: str):
    match = re.search(r"(\d+(\.\d+)?)%", text)
    if match:
        return float(match.group(1))
    return None


def extract_contract_months(text: str):
    match = re.search(r"(\d+)\s*months?", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def build_dashboard_data():
    alpha_price_resp = ask_backend("What is Vendor Alpha yearly cost?", "Vendor Alpha", "pricing")
    beta_price_resp = ask_backend("What is Vendor Beta yearly cost?", "Vendor Beta", "pricing")

    alpha_uptime_resp = ask_backend("What uptime does Vendor Alpha guarantee?", "Vendor Alpha", "sla")
    beta_uptime_resp = ask_backend("What uptime does Vendor Beta guarantee?", "Vendor Beta", "sla")

    alpha_contract_resp = ask_backend("What is the minimum contract length for Vendor Alpha?", "Vendor Alpha", "pricing")
    beta_contract_resp = ask_backend("What is the minimum contract length for Vendor Beta?", "Vendor Beta", "pricing")

    risk_resp = ask_backend("Analyze the risk of Vendor Alpha and Vendor Beta")
    recommendation_resp = ask_backend("Which vendor should we choose?")

    alpha_price = extract_money(alpha_price_resp["answer"])
    beta_price = extract_money(beta_price_resp["answer"])

    alpha_uptime = extract_percentage(alpha_uptime_resp["answer"])
    beta_uptime = extract_percentage(beta_uptime_resp["answer"])

    alpha_contract = extract_contract_months(alpha_contract_resp["answer"])
    beta_contract = extract_contract_months(beta_contract_resp["answer"])

    summary_df = pd.DataFrame(
        [
            {
                "Vendor": "Vendor Alpha",
                "Annual Cost": alpha_price,
                "Uptime %": alpha_uptime,
                "Contract Months": alpha_contract,
            },
            {
                "Vendor": "Vendor Beta",
                "Annual Cost": beta_price,
                "Uptime %": beta_uptime,
                "Contract Months": beta_contract,
            },
        ]
    )

    return {
        "summary_df": summary_df,
        "risk_text": risk_resp["answer"],
        "recommendation_text": recommendation_resp["answer"],
        "alpha_price_text": alpha_price_resp["answer"],
        "beta_price_text": beta_price_resp["answer"],
        "alpha_uptime_text": alpha_uptime_resp["answer"],
        "beta_uptime_text": beta_uptime_resp["answer"],
    }


st.title("Vendor Intelligence Copilot")
st.write("Ask questions about vendor contracts, SLAs, pricing, risk, and uploaded PDFs.")

with st.sidebar:
    st.header("Upload Vendor Document")

    uploaded_file = st.file_uploader(
        "Upload a .txt or .pdf file",
        type=["txt", "pdf"],
    )

    if st.button("Upload and Ingest"):
        if uploaded_file is None:
            st.warning("Please choose a file first.")
        else:
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            }
            response = requests.post(UPLOAD_API_URL, files=files, timeout=120)

            if response.status_code == 200:
                data = response.json()
                st.success("File uploaded and ingested successfully.")
                st.json(data)
            else:
                st.error(f"Upload failed: {response.text}")

st.header("Vendor Dashboard")

if st.button("Load Dashboard"):
    try:
        dashboard = build_dashboard_data()
        summary_df = dashboard["summary_df"]

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Vendor Alpha Cost",
                f"${summary_df.loc[summary_df['Vendor'] == 'Vendor Alpha', 'Annual Cost'].iloc[0]:,}"
            )
            st.metric(
                "Vendor Alpha Uptime",
                f"{summary_df.loc[summary_df['Vendor'] == 'Vendor Alpha', 'Uptime %'].iloc[0]}%"
            )

        with col2:
            st.metric(
                "Vendor Beta Cost",
                f"${summary_df.loc[summary_df['Vendor'] == 'Vendor Beta', 'Annual Cost'].iloc[0]:,}"
            )
            st.metric(
                "Vendor Beta Uptime",
                f"{summary_df.loc[summary_df['Vendor'] == 'Vendor Beta', 'Uptime %'].iloc[0]}%"
            )

        st.subheader("Vendor Summary Table")
        st.dataframe(summary_df, use_container_width=True)

        st.subheader("Annual Cost Comparison")
        cost_chart_df = summary_df.set_index("Vendor")[["Annual Cost"]]
        st.bar_chart(cost_chart_df)

        st.subheader("Uptime Comparison")
        uptime_chart_df = summary_df.set_index("Vendor")[["Uptime %"]]
        st.bar_chart(uptime_chart_df)

        st.subheader("Contract Length Comparison")
        contract_chart_df = summary_df.set_index("Vendor")[["Contract Months"]]
        st.bar_chart(contract_chart_df)

        st.subheader("Risk Summary")
        st.write(dashboard["risk_text"])

        st.subheader("Recommendation")
        st.write(dashboard["recommendation_text"])

    except Exception as e:
        st.error(f"Dashboard load failed: {e}")

st.header("Ask a question about a vendor")

question = st.text_input("Question")

vendor = st.selectbox(
    "Vendor Filter",
    ["All", "Vendor Alpha", "Vendor Beta"]
)

doc_type = st.selectbox(
    "Document Type",
    ["All", "sla", "pricing", "contract", "security", "risk"]
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        params = {"question": question}

        if vendor != "All":
            params["vendor_name"] = vendor

        if doc_type != "All":
            params["doc_type"] = doc_type

        response = requests.get(ASK_API_URL, params=params, timeout=120)

        if response.status_code == 200:
            data = response.json()

            st.subheader("Answer")
            st.write(data["answer"])

            st.subheader("Mode")
            st.write(data.get("mode", "single"))

            st.subheader("Filters Used")
            st.json(data["filters"])

            st.subheader("Retrieved Context")

            context_used = data["context_used"]

            if isinstance(context_used, dict):
                st.markdown("### Vendor Alpha Context")
                for item in context_used.get("vendor_alpha", []):
                    st.markdown("---")
                    st.write(item["content"])
                    st.json(item["metadata"])

                st.markdown("### Vendor Beta Context")
                for item in context_used.get("vendor_beta", []):
                    st.markdown("---")
                    st.write(item["content"])
                    st.json(item["metadata"])
            else:
                for item in context_used:
                    st.markdown("---")
                    st.write(item["content"])
                    st.json(item["metadata"])
        else:
            st.error(f"API request failed: {response.text}")