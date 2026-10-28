import streamlit as st
import json
import os
import re
from google import genai
from google.genai import errors
from google.genai import types

st.set_page_config(
    page_title="MAIC Teacher AI Readiness Consultation",
    page_icon="🌱",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 1. EVALUATION TOOL FUNCTION (Diagnostic Engine)
# -----------------------------------------------------------------------------
def evaluate_teacher_readiness(
    educator_name: str,
    grade_band: str,
    resource_level: str,
    d1_awareness_score: float,
    d1_evidence: str,
    d2_instruction_score: float,
    d2_evidence: str,
    d3_assessment_score: float,
    d3_evidence: str,
    d4_safeguard_score: float,
    d4_evidence: str,
    d5_mindset_score: float,
    d5_evidence: str,
    d6_infrastructure_score: float,
    d6_evidence: str,
    d7_transformation_score: float,
    d7_evidence: str,
    protected_time_gap: bool
) -> str:
    """
    Computes teacher readiness scores across all 7 MAIC domains,
    identifies focus areas, and returns a structured JSON summary.
    """
    scores = [
        d1_awareness_score, d2_instruction_score, d3_assessment_score,
        d4_safeguard_score, d5_mindset_score, d6_infrastructure_score,
        d7_transformation_score
    ]
    avg_score = sum(scores) / len(scores)

    # Determine Base Tier
    if avg_score >= 3.5:
        base_tier = "Advanced Integration"
    elif avg_score >= 3.0:
        base_tier = "Proficient Integration"
    elif avg_score >= 2.0:
        base_tier = "Developing Practice"
    else:
        base_tier = "Emerging Exploration"

    # Growth Guidance: Domain 4 establishes foundational student safeguards
    final_tier = base_tier
    safeguard_applied = False
    priority_focus = ""

    if d4_safeguard_score < 2.0 and base_tier in ["Developing Practice", "Proficient Integration", "Advanced Integration"]:
        final_tier = "Emerging Exploration"
        safeguard_applied = True
        priority_focus = (
            "Foundational Safeguards: Establishing student data privacy protocols "
            "is our immediate priority area to address before scaling interactive tool usage."
        )
    elif d4_safeguard_score < 3.0 and base_tier in ["Proficient Integration", "Advanced Integration"]:
        final_tier = "Developing Practice"
        safeguard_applied = True
        priority_focus = (
            "Safety Guardrail Maturation: Deepening classroom compliance and data minimization "
            "is the recommended next step to support your advanced instructional strategies."
        )

    result = {
        "educator_name": educator_name,
        "grade_band": grade_band,
        "resource_level": resource_level,
        "composite_score": round(avg_score, 2),
        "base_tier": base_tier,
        "final_tier": final_tier,
        "safeguard_applied": safeguard_applied,
        "priority_focus": priority_focus,
        "protected_time_gap": protected_time_gap,
        "domains": {
            "Domain 1: AI Literacy & Concepts": {"score": d1_awareness_score, "evidence": d1_evidence},
            "Domain 2: Instructional Planning & Differentiation": {"score": d2_instruction_score, "evidence": d2_evidence},
            "Domain 3: Authentic Assessment & Judgment": {"score": d3_assessment_score, "evidence": d3_evidence},
            "Domain 4: Ethics, Privacy & Student Safeguards": {"score": d4_safeguard_score, "evidence": d4_evidence},
            "Domain 5: Educator Agency & Confidence": {"score": d5_mindset_score, "evidence": d5_evidence},
            "Domain 6: Equity, Access & Time Resources": {"score": d6_infrastructure_score, "evidence": d6_evidence},
            "Domain 7: Collaborative Culture & Leadership": {"score": d7_transformation_score, "evidence": d7_evidence},
        }
    }
    return json.dumps(result)

# -----------------------------------------------------------------------------
# 2. SYSTEM INSTRUCTION (Coaching Persona)
# -----------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are the Miami AI Club (MAIC) AI in Education Task Force Growth Coach.
Your mission is to support educators in exploring where generative AI meets their teaching practice through an encouraging, collaborative dialogue.

TONE & LANGUAGE RULES:
1. Ground every response in supportive, growth-oriented language. Never use words like 'fail', 'gap', 'capped', 'punished', or 'mandatory'. Instead, use 'priority area to strengthen', 'recommended next step', and 'celebrated strength'.
2. Ask exactly ONE question per turn. Never combine multiple inquiries into a paragraph.
3. Offer clear, numbered or lettered selectable options (e.g., A, B, C, D) alongside an invitation to elaborate if they prefer. This keeps answering effortless for busy educators.
4. Never reveal HTML markup, code blocks, or raw JSON in your text responses.

INTERVIEW FLOW:
- Probe one area at a time across the 7 MAIC domains:
    1. Conceptual Literacy (familiarity with AI tools, hallucination spot-checks)
    2. Instructional Differentiation (using AI for tiered supports or scaffolds)
    3. Assessment Integrity (valuing reasoning/process over relying on AI detectors)
    4. Student Privacy & Safety (handling PII, district-vetted tools, FERPA/COPPA)
    5. Professional Agency (AI as assistant, keeping educator at the center)
    6. Protected Time & Support (whether school provides designated time for AI professional learning)
    7. School Culture (peer sharing, student AI literacy)
- Once sufficient insight is gathered (typically 5 to 7 turns), call `evaluate_teacher_readiness`.
- After calling the tool, deliver a brief, warm wrap-up message in chat (e.g., "Thank you for sharing your experience! Your personalized growth roadmap is ready below."). Follow it with a ```html ``` block containing the complete styled HTML report.
"""

# -----------------------------------------------------------------------------
# 3. UI & RUNTIME SETUP
# -----------------------------------------------------------------------------
st.title("🌱 MAIC Teacher AI Readiness Consultation")
st.caption("A supportive, growth-oriented reflection tool • Miami AI Club Education Framework")

# Privacy Notice
st.warning(
    "🔒 **Privacy Notice:** To protect student and staff privacy under FERPA/COPPA, "
    "please **do not enter any student names, IDs, or personally identifiable information (PII)**."
)

with st.sidebar:
    st.header("Settings")
    
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        value="AQ.Ab8RN6I9sHoMVBVjRKUmh2ou6KDoeVKvmJfxs8nDfFOXL8CsLw"
    )
    
    st.markdown("---")
    st.markdown("""
    **Consultation Pillars:**
    - Step-by-step single-question guidance
    - Supportive, strength-based recommendations
    - Strict student data protection
    - Tailored 30-60-90 day growth path
    """)
    if st.button("Start Fresh Interview", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.html_report = None
        st.rerun()

# Welcome Message
INITIAL_PROMPT = (
    "Hello and welcome! I'm your MAIC AI Growth Coach. Our goal today is to look at how AI tools "
    "can best support your workload and students in a completely non-evaluative, supportive space.\n\n"
    "*Friendly reminder: Please avoid sharing any student names or personal data during our chat.*\n\n"
    "To begin, **what grade band do you primarily work with?**\n\n"
    "• **A)** Elementary (K–5)\n"
    "• **B)** Middle School (6–8)\n"
    "• **C)** High School (9–12)\n"
    "• **D)** Higher Ed / Specialist / Other (feel free to type your details!)"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=INITIAL_PROMPT)]
        )
    ]
if "html_report" not in st.session_state:
    st.session_state.html_report = None

# Render Existing Chat History
for content in st.session_state.chat_history:
    for part in content.parts:
        if part.text:
            # Strip out any HTML blocks from the visible chat
            display_text = re.sub(r"```html[\s\S]*?```", "", part.text).strip()
            if display_text:
                with st.chat_message("assistant" if content.role == "model" else "user"):
                    st.markdown(display_text)

# Input Handler
if user_prompt := st.chat_input("Select an option or type your reply..."):
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar to proceed.")
    else:
        with st.chat_message("user"):
            st.markdown(user_prompt)

        st.session_state.chat_history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
        )

        client = genai.Client(api_key=api_key)

        with st.chat_message("assistant"):
            with st.spinner("Reflecting on your response..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=st.session_state.chat_history,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.3,
                            tools=[evaluate_teacher_readiness]
                        )
                    )
                except Exception as err:
                    st.error(f"API Error: {repr(err)}")
                    st.stop()

                raw_model_text = ""

                # Handle tool invocation if ready
                if response.function_calls:
                    for call in response.function_calls:
                        if call.name == "evaluate_teacher_readiness":
                            args = dict(call.args)
                            tool_result_json = evaluate_teacher_readiness(**args)

                            st.session_state.chat_history.append(response.candidates[0].content)
                            st.session_state.chat_history.append(
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_function_response(
                                        name="evaluate_teacher_readiness",
                                        response={"result": tool_result_json}
                                    )]
                                )
                            )

                            try:
                                follow_up = client.models.generate_content(
                                    model="gemini-3.6-flash",
                                    contents=st.session_state.chat_history,
                                    config=types.GenerateContentConfig(
                                        system_instruction=SYSTEM_INSTRUCTION,
                                        temperature=0.3
                                    )
                                )
                                raw_model_text = follow_up.text
                                st.session_state.chat_history.append(
                                    types.Content(role="model", parts=[types.Part.from_text(text=raw_model_text)])
                                )
                            except Exception as err:
                                st.error(f"Report Generation Error: {repr(err)}")
                                st.stop()
                else:
                    raw_model_text = response.text
                    st.session_state.chat_history.append(
                        types.Content(role="model", parts=[types.Part.from_text(text=raw_model_text)])
                    )

                # Separate HTML code from display text
                if "```html" in raw_model_text:
                    start_idx = raw_model_text.find("```html") + 7
                    end_idx = raw_model_text.find("```", start_idx)
                    if end_idx != -1:
                        st.session_state.html_report = raw_model_text[start_idx:end_idx].strip()

                visible_message = re.sub(r"```html[\s\S]*?```", "", raw_model_text).strip()
                if visible_message:
                    st.markdown(visible_message)

# -----------------------------------------------------------------------------
# 4. FINAL CLEAN ASSESSMENT DISPLAY (Clean Preview & Download Only)
# -----------------------------------------------------------------------------
if st.session_state.html_report:
    st.divider()
    st.success("🎉 **Reflection Complete!** Your tailored readiness profile and roadmap have been generated below.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.download_button(
            label="📥 Download Growth Profile (.html)",
            data=st.session_state.html_report,
            file_name="Teacher_AI_Readiness_Roadmap.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )
    with col2:
        st.caption("You can open this file in any web browser, save it to Google Drive, or print it directly to PDF.")

    with st.expander("📄 View Full Growth Assessment & 30-60-90 Day Plan", expanded=True):
        st.components.v1.html(st.session_state.html_report, height=850, scrolling=True)
