from typing import Optional

from app.rag.retriever import retrieve_context
from app.core.llm import llm


def detect_vendor_name(question: str) -> Optional[str]:
    q = question.lower()

    if "vendor alpha" in q or "alpha" in q:
        return "Vendor Alpha"

    if "vendor beta" in q or "beta" in q:
        return "Vendor Beta"

    return None


def detect_doc_type(question: str) -> Optional[str]:
    q = question.lower()

    if "sla" in q or "uptime" in q or "service level" in q:
        return "sla"

    if "price" in q or "pricing" in q or "cost" in q or "subscription" in q:
        return "pricing"

    if "contract" in q or "renewal" in q or "termination" in q or "liability" in q:
        return "contract"

    if "security" in q or "certification" in q or "compliance" in q:
        return "security"

    if "risk" in q:
        return "risk"

    return None


def is_comparison_query(question: str) -> bool:
    q = question.lower()

    comparison_keywords = [
        "compare",
        "comparison",
        "vs",
        "versus",
        "difference",
        "differences",
    ]

    has_comparison_word = any(word in q for word in comparison_keywords)
    mentions_alpha = "vendor alpha" in q or "alpha" in q
    mentions_beta = "vendor beta" in q or "beta" in q

    return has_comparison_word and mentions_alpha and mentions_beta


def is_risk_analysis_query(question: str) -> bool:
    q = question.lower()

    risk_keywords = [
        "risk",
        "riskier",
        "risks",
        "analyze risk",
        "risk analysis",
        "which vendor is riskier",
    ]

    return any(keyword in q for keyword in risk_keywords)


def is_scoring_query(question: str) -> bool:
    q = question.lower()

    scoring_keywords = [
        "score",
        "scoring",
        "rate",
        "rating",
        "scorecard",
        "evaluate vendors",
        "evaluate vendor",
    ]

    return any(keyword in q for keyword in scoring_keywords)


def is_recommendation_query(question: str) -> bool:
    q = question.lower()

    recommendation_keywords = [
        "recommend",
        "recommendation",
        "which vendor should we choose",
        "which vendor should i choose",
        "which vendor is better",
        "best vendor",
        "choose between",
        "decision",
        "select vendor",
    ]

    return any(keyword in q for keyword in recommendation_keywords)


def ask_comparison_question(question: str, doc_type: Optional[str] = None) -> dict:
    alpha_docs = retrieve_context(
        query=question,
        k=3,
        vendor_name="Vendor Alpha",
        doc_type=doc_type,
    )

    beta_docs = retrieve_context(
        query=question,
        k=3,
        vendor_name="Vendor Beta",
        doc_type=doc_type,
    )

    if not alpha_docs and not beta_docs:
        return {
            "question": question,
            "mode": "comparison",
            "filters": {
                "vendor_name": None,
                "doc_type": doc_type,
            },
            "context_used": [],
            "answer": "No relevant comparison context was found.",
        }

    alpha_context = "\n\n".join(
        [
            f"Alpha Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(alpha_docs)
        ]
    )

    beta_context = "\n\n".join(
        [
            f"Beta Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(beta_docs)
        ]
    )

    prompt = f"""
You are a vendor intelligence assistant.

Compare Vendor Alpha and Vendor Beta using ONLY the context below.
If a detail is missing for one vendor, say that clearly.
Keep the answer concise, structured, and easy to read.

Question:
{question}

Vendor Alpha Context:
{alpha_context}

Vendor Beta Context:
{beta_context}

Return the answer in this style:

Vendor Comparison

Category:
- Vendor Alpha: ...
- Vendor Beta: ...

Only include facts supported by the context.
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "mode": "comparison",
        "filters": {
            "vendor_name": None,
            "doc_type": doc_type,
        },
        "context_used": {
            "vendor_alpha": alpha_docs,
            "vendor_beta": beta_docs,
        },
        "answer": response.content.strip(),
    }


def ask_risk_analysis_question(question: str) -> dict:
    alpha_docs = retrieve_context(
        query=question,
        k=4,
        vendor_name="Vendor Alpha",
        doc_type=None,
    )

    beta_docs = retrieve_context(
        query=question,
        k=4,
        vendor_name="Vendor Beta",
        doc_type=None,
    )

    if not alpha_docs and not beta_docs:
        return {
            "question": question,
            "mode": "risk_analysis",
            "filters": {
                "vendor_name": None,
                "doc_type": None,
            },
            "context_used": [],
            "answer": "No relevant risk analysis context was found.",
        }

    alpha_context = "\n\n".join(
        [
            f"Alpha Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(alpha_docs)
        ]
    )

    beta_context = "\n\n".join(
        [
            f"Beta Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(beta_docs)
        ]
    )

    prompt = f"""
You are a vendor risk intelligence assistant.

Using ONLY the context below, analyze the relative risk of Vendor Alpha and Vendor Beta.
Consider areas such as:
- pricing / financial risk
- SLA / uptime risk
- contract risk
- security / compliance risk
- operational or support risk

If some information is missing, say that clearly.
Do not invent facts.

Question:
{question}

Vendor Alpha Context:
{alpha_context}

Vendor Beta Context:
{beta_context}

Return the answer in this exact style:

Vendor Risk Analysis

Vendor Alpha: <Low / Low-Medium / Medium / Medium-High / High>
- ...
- ...
- ...

Vendor Beta: <Low / Low-Medium / Medium / Medium-High / High>
- ...
- ...
- ...

Overall View:
- ...
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "mode": "risk_analysis",
        "filters": {
            "vendor_name": None,
            "doc_type": None,
        },
        "context_used": {
            "vendor_alpha": alpha_docs,
            "vendor_beta": beta_docs,
        },
        "answer": response.content.strip(),
    }


def ask_scoring_question(question: str) -> dict:
    alpha_docs = retrieve_context(
        query=question,
        k=5,
        vendor_name="Vendor Alpha",
        doc_type=None,
    )

    beta_docs = retrieve_context(
        query=question,
        k=5,
        vendor_name="Vendor Beta",
        doc_type=None,
    )

    if not alpha_docs and not beta_docs:
        return {
            "question": question,
            "mode": "scoring",
            "filters": {
                "vendor_name": None,
                "doc_type": None,
            },
            "context_used": [],
            "answer": "No relevant scoring context was found.",
        }

    alpha_context = "\n\n".join(
        [
            f"Alpha Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(alpha_docs)
        ]
    )

    beta_context = "\n\n".join(
        [
            f"Beta Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(beta_docs)
        ]
    )

    prompt = f"""
You are a vendor evaluation assistant.

Using ONLY the context below, score Vendor Alpha and Vendor Beta.
Evaluate each vendor on a 1 to 10 scale for:

- Cost Score
- SLA Score
- Security Score
- Contract Flexibility Score
- Support / Operational Score

Then provide:
- Overall Score (1 to 10)
- A short explanation

If information is missing, make a cautious score and state that some data is limited.
Do not invent facts beyond the provided context.

Question:
{question}

Vendor Alpha Context:
{alpha_context}

Vendor Beta Context:
{beta_context}

Return the answer in this exact style:

Vendor Scorecard

Vendor Alpha
- Cost Score: x/10
- SLA Score: x/10
- Security Score: x/10
- Contract Flexibility Score: x/10
- Support / Operational Score: x/10
- Overall Score: x/10
- Explanation: ...

Vendor Beta
- Cost Score: x/10
- SLA Score: x/10
- Security Score: x/10
- Contract Flexibility Score: x/10
- Support / Operational Score: x/10
- Overall Score: x/10
- Explanation: ...
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "mode": "scoring",
        "filters": {
            "vendor_name": None,
            "doc_type": None,
        },
        "context_used": {
            "vendor_alpha": alpha_docs,
            "vendor_beta": beta_docs,
        },
        "answer": response.content.strip(),
    }


def ask_recommendation_question(question: str) -> dict:
    alpha_docs = retrieve_context(
        query=question,
        k=5,
        vendor_name="Vendor Alpha",
        doc_type=None,
    )

    beta_docs = retrieve_context(
        query=question,
        k=5,
        vendor_name="Vendor Beta",
        doc_type=None,
    )

    if not alpha_docs and not beta_docs:
        return {
            "question": question,
            "mode": "recommendation",
            "filters": {
                "vendor_name": None,
                "doc_type": None,
            },
            "context_used": [],
            "answer": "No relevant recommendation context was found.",
        }

    alpha_context = "\n\n".join(
        [
            f"Alpha Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(alpha_docs)
        ]
    )

    beta_context = "\n\n".join(
        [
            f"Beta Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(beta_docs)
        ]
    )

    prompt = f"""
You are a vendor decision-support assistant.

Using ONLY the context below, recommend which vendor should be chosen between Vendor Alpha and Vendor Beta.
Base the recommendation on:
- pricing
- SLA / uptime
- security / compliance
- contract flexibility
- operational / support considerations

If data is incomplete, clearly say so.
Do not invent facts.

Question:
{question}

Vendor Alpha Context:
{alpha_context}

Vendor Beta Context:
{beta_context}

Return the answer in this exact style:

Vendor Recommendation

Recommended Vendor: <Vendor Alpha or Vendor Beta or Tie / Depends>

Reasoning:
- ...
- ...
- ...

Tradeoffs:
- ...
- ...

Final Decision:
- ...
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "mode": "recommendation",
        "filters": {
            "vendor_name": None,
            "doc_type": None,
        },
        "context_used": {
            "vendor_alpha": alpha_docs,
            "vendor_beta": beta_docs,
        },
        "answer": response.content.strip(),
    }


def ask_single_question(
    question: str,
    vendor_name: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> dict:
    inferred_vendor = detect_vendor_name(question)
    inferred_doc_type = detect_doc_type(question)

    final_vendor_name = vendor_name if vendor_name else inferred_vendor
    final_doc_type = doc_type if doc_type else inferred_doc_type

    retrieved_docs = retrieve_context(
        query=question,
        k=3,
        vendor_name=final_vendor_name,
        doc_type=final_doc_type,
    )

    if not retrieved_docs:
        return {
            "question": question,
            "mode": "single",
            "filters": {
                "vendor_name": final_vendor_name,
                "doc_type": final_doc_type,
            },
            "context_used": [],
            "answer": "No relevant context was found for the given filters.",
        }

    formatted_context = "\n\n".join(
        [
            f"Chunk {i+1}:\n"
            f"Content: {doc['content']}\n"
            f"Metadata: {doc['metadata']}"
            for i, doc in enumerate(retrieved_docs)
        ]
    )

    prompt = f"""
You are a vendor risk intelligence assistant.

Answer the question using ONLY the context below.
If the answer is not present in the context, say:
"I could not find that information in the ingested documents."

Context:
{formatted_context}

Question:
{question}

Return only a concise answer.
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "mode": "single",
        "filters": {
            "vendor_name": final_vendor_name,
            "doc_type": final_doc_type,
        },
        "context_used": retrieved_docs,
        "answer": response.content.strip(),
    }


def ask_question(
    question: str,
    vendor_name: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> dict:
    inferred_doc_type = detect_doc_type(question)
    final_doc_type = doc_type if doc_type else inferred_doc_type

    if is_recommendation_query(question):
        return ask_recommendation_question(question=question)

    if is_scoring_query(question):
        return ask_scoring_question(question=question)

    if is_risk_analysis_query(question):
        return ask_risk_analysis_question(question=question)

    if is_comparison_query(question):
        return ask_comparison_question(
            question=question,
            doc_type=final_doc_type,
        )

    return ask_single_question(
        question=question,
        vendor_name=vendor_name,
        doc_type=doc_type,
    )