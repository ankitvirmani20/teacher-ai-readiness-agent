import streamlit as st
import json
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="MAIC Teacher AI Evaluation Agent", page_icon="🤖", layout="wide")

# -----------------------------------------------------------------------------
# 1. EVALUATION TOOL FUNCTION (The Agent's Internal Assessment Engine)
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
    Evaluates teacher scores across all 7 domains, enforces the safeguard gate,
    and returns a structured assessment summary payload.
    """
    scores = [
        d1_awareness_score, d2_instruction_score, d3_assessment_score,
        d4_safeguard_score, d5_mindset_score, d6_infrastructure_score,
        d7_transformation_score
    ]
    avg_score = sum(scores) / len(scores)

    # Base Tier
    if avg_score >= 3.5:
        base_tier = "Advanced"
    elif avg_score >= 2.6:
        base_tier = "Proficient"
    elif avg_score >= 1.8:
        base_tier = "Developing"
    else:
        base_tier = "Emerging"

    # Safeguard Gate: Domain 4 ceiling
    final_tier = base_tier
    safeguard_applied = False
    gate_reason = ""

    if d4_safeguard_score < 2.0 and base_tier in ["Developing", "Proficient", "Advanced"]:
        final_tier = "Emerging"
        safeguard_applied = True
        gate_reason = "Domain 4 (Ethics, Privacy & Student Safety) scored at Emerging (< 2.0). Overall readiness is capped at Emerging until student data protections are verified."
    elif d4_safeguard_score < 3.0 and base_tier in ["Proficient", "Advanced"]:
        final_tier = "Developing"
        safeguard_applied = True
        gate_reason = "Domain 4 (Ethics, Privacy & Student Safety) scored at Developing (< 3.0). Overall readiness is capped at Developing because tool adoption cannot proceed without mature privacy and safety guardrails."

    result = {
        "educator_name": educator_name,
        "grade_band": grade_band,
        "resource_level": resource_level,
        "composite_score": round(avg_score, 2),
        "base_tier": base_tier,
        "final_tier": final_tier,
        "safeguard_applied": safeguard_applied,
        "gate_reason": gate_reason,
        "protected_time_gap": protected_time_gap,
        "domains": {
            "Domain 1: AI Awareness & Conceptual Literacy": {"score": d1_awareness_score, "evidence": d1_evidence},
            "Domain 2: Instructional Planning & Differentiation": {"score": d2_instruction_score, "evidence": d2_evidence},
            "Domain 3: Assessment Integrity (Friction & Judgment)": {"score": d3_assessment_score, "evidence": d3_evidence},
            "Domain 4: Ethics, Privacy & Student Safeguards": {"score": d4_safeguard_score, "evidence": d4_evidence},
            "Domain 5: Confidence, Mindset & Professional Agency": {"score": d5_mindset_score, "evidence": d5_evidence},
            "Domain 6: Access, Equity & Infrastructure": {"score": d6_infrastructure_score, "evidence": d6_evidence},
            "Domain 7: Professional Transformation & Culture": {"score": d7_transformation_score, "evidence": d7_evidence},
        }
    }
    return json.dumps(result)

# Tool declaration for Gemini
evaluation_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="evaluate_teacher_readiness",
            description="Computes readiness scores across all 7 MAIC domains, applies the safeguard gate, and generates the assessment payload.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "educator_name": types.Schema(type=types.Type.STRING),
                    "grade_band": types.Schema(type=types.Type.STRING),
                    "resource_level": types.Schema(type=types.Type.STRING),
                    "d1_awareness_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on AI concepts and hallucinations."),
                    "d1_evidence": types.Schema(type=types.Type.STRING),
                    "d2_instruction_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on lesson planning and scaffolding."),
                    "d2_evidence": types.Schema(type=types.Type.STRING),
                    "d3_assessment_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on Design for Friction & Assess for Judgment."),
                    "d3_evidence": types.Schema(type=types.Type.STRING),
                    "d4_safeguard_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on FERPA/COPPA, data minimization, and safety."),
                    "d4_evidence": types.Schema(type=types.Type.STRING),
                    "d5_mindset_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on professional agency vs replacement anxiety."),
                    "d5_evidence": types.Schema(type=types.Type.STRING),
                    "d6_infrastructure_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on devices, bandwidth, and protected time."),
                    "d6_evidence": types.Schema(type=types.Type.STRING),
                    "d7_transformation_score": types.Schema(type=types.Type.NUMBER, description="1.0 to 4.0 score on peer coaching and model classrooms."),
                    "d7_evidence": types.Schema(type=types.Type.STRING),
                    "protected_time_gap": types.Schema(type=types.Type.BOOLEAN, description="True if teacher reports AI learning is on top of full workload without protected PLC time.")
                },
                required=[
                    "educator_name", "grade_band", "resource_level",
                    "d1_awareness_score", "d1_evidence",
                    "d2_instruction_score", "d2_evidence",
                    "d3_assessment_score", "d3_evidence",
                    "d4_safeguard_score", "d4_evidence",
                    "d5_mindset_score", "d5_evidence",
                    "d6_infrastructure_score", "d6_evidence",
                    "d7_transformation_score", "d7_evidence",
                    "protected_time_gap"
                ]
            )
        )
    ]
)

# -----------------------------------------------------------------------------
# 2. SYSTEM INSTRUCTION (Agent's Core Brain & Persona)
# -----------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are the Miami AI Club (MAIC) AI in Education Task Force Evaluation Agent.
Your mission is to evaluate a school teacher's readiness for AI integration through an interactive, professional, non-evaluative interview.

You must ground your evaluation in the MAIC Task Force Implementation Guide and Educator Synthesis documents:
- The 4 Readiness Tiers: Emerging (1.00–1.99), Developing (2.00–2.99), Proficient (3.00–3.99), Advanced (4.00–5.00).
- The 7 Diagnostic Domains:
    1. AI Awareness & Conceptual Literacy (token prediction, hallucination auditing)
    2. Instructional Planning & Scaffolding (adaptive differentiation, multimodal assets)
    3. Assessment Integrity (Design for Friction, Assess for Judgment, moving off AI detectors)
    4. Ethics, Privacy & Student Safeguards (FERPA/COPPA, data minimization, zero-retention vendor terms, human oversight)
    5. Confidence, Mindset & Professional Agency (AI as thinking partner, not replacement)
    6. Access, Equity & Infrastructure (device equity, protected planning time vs workload burden)
    7. Professional Transformation & Collaborative Culture (Lead Your Own Transformation, peer coaching, model classrooms, explicit Appendix D Student AI Literacy)

INTERVIEW PROTOCOL:
1. Conduct an engaging conversation. Ask 1 or at most 2 questions per turn. Never dump a long list of questions.
2. Listen carefully to the teacher's narrative. If an answer is vague or brief, probe for concrete classroom evidence:
   - If they mention using AI for lesson planning, ask how they differentiate for diverse learners.
   - If they mention essays or student homework, probe whether they 'Design for Friction' or rely on automated AI detectors.
   - Always probe Domain 4: Ask specifically if student PII is entered and whether tools are district-cleared.
   - Always check Domain 6: Ask if they are given protected contract time to learn AI or if it is on top of an already full workload.
3. Once you have sufficient qualitative evidence across all 7 domains (typically 4 to 6 conversational turns), DO NOT ask more questions.
4. Execute the tool `evaluate_teacher_readiness` with your scored judgments (1.00 to 4.00 for each domain) and qualitative evidence summaries.
5. After receiving the tool output, generate a complete, standalone, professionally styled HTML report enclosed in a ```html ``` block.
   The HTML report must contain:
   - Header with Educator, Grade Band, Resource Reality, and Final Tier badge.
   - Safeguard Gate Notice if Domain 4 capped their score.
   - Workload Perception Gap Notice if protected time is missing.
   - Domain Score Table with scores (1.0–4.0) and evidence notes from your interview.
   - Differentiated PD assignments from MAIC Appendix A (Units 1–12) and Appendix C (Joint Units 1–10).
   - Student AI Literacy plan from MAIC Appendix D (Units 1–6).
   - Contextual 30-60-90 Day Milestone Roadmap adjusted to their resource level.
"""

# -----------------------------------------------------------------------------
# 3. STREAMLIT INTERFACE & AGENT RUNTIME
# -----------------------------------------------------------------------------
st.title("🤖 MAIC Teacher AI Readiness Evaluation Agent")
st.caption("Autonomous Diagnostic Agent • MAIC AI in Education Task Force Framework")

with st.sidebar:
    st.header("Agent Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    st.markdown("---")
    st.markdown("""
    **Agent Capabilities:**
    - Adaptive dialogue & evidence probing
    - 7-Domain rubric scoring (1.0–4.0)
    - Hard Safeguard Gate enforcement
    - Workload perception gap analysis
    - Autonomous HTML scorecard authoring
    """)
    if st.button("Reset Interview"):
        st.session_state.chat_history = []
        st.session_state.html_report = None
        st.rerun()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        types.Content(
            role="model",
            parts=[types.Part.from_text(
                text="Welcome! I am the MAIC AI Readiness Evaluation Agent. I'm here to have a collaborative, non-evaluative conversation to understand how generative AI intersects with your teaching, your students' learning, and your school environment.\n\nTo begin, could you share what grade band and subject you teach, and give me a brief picture of your school's current technology setup (e.g., do students have 1:1 devices, and do you have access to approved AI tools)?"
            )]
        )
    ]
if "html_report" not in st.session_state:
    st.session_state.html_report = None

# Display conversation
for content in st.session_state.chat_history:
    for part in content.parts:
        if part.text:
            with st.chat_message("assistant" if content.role == "model" else "user"):
                st.markdown(part.text)

# User input turn
if user_prompt := st.chat_input("Reply to the evaluation agent..."):
    if not api_key:
        st.error("Please enter a Gemini API Key in the sidebar to run the agent.")
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_prompt)

        st.session_state.chat_history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
        )

        # Agent reasoning loop
        client = genai.Client(api_key=api_key)

        with st.chat_message("assistant"):
            with st.spinner("Agent is analyzing your response and evaluating evidence..."):
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=st.session_state.chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.4,
                        tools=[evaluation_tool]
                    )
                )

                # Check if the agent called the evaluation tool
                if response.function_calls:
                    for call in response.function_calls:
                        if call.name == "evaluate_teacher_readiness":
                            # Execute the local evaluation tool
                            args = dict(call.args)
                            tool_result_json = evaluate_teacher_readiness(**args)

                            # Provide tool result back to the agent
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

                            # Let the agent write its final assessment response & HTML
                            follow_up = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=st.session_state.chat_history,
                                config=types.GenerateContentConfig(
                                    system_instruction=SYSTEM_INSTRUCTION,
                                    temperature=0.3
                                )
                            )
                            agent_text = follow_up.text
                            st.markdown(agent_text)
                            st.session_state.chat_history.append(
                                types.Content(role="model", parts=[types.Part.from_text(text=agent_text)])
                            )
                else:
                    agent_text = response.text
                    st.markdown(agent_text)
                    st.session_state.chat_history.append(
                        types.Content(role="model", parts=[types.Part.from_text(text=agent_text)])
                    )

                # Extract HTML report if present in agent response
                if "```html" in agent_text:
                    start_idx = agent_text.find("```html") + 7
                    end_idx = agent_text.find("```", start_idx)
                    if end_idx != -1:
                        st.session_state.html_report = agent_text[start_idx:end_idx].strip()

# Render download button and preview if assessment is finalized
if st.session_state.html_report:
    st.divider()
    st.success("🎉 **Assessment Complete!** Your tailored HTML diagnostic summary has been authored by the agent.")
    c1, c2 = st.columns()
    with c1:
        st.download_button(
            label="📥 Download HTML Summary Report",
            data=st.session_state.html_report,
            file_name="MAIC_Teacher_AI_Readiness_Report.html",
            mime="text/html",
            type="primary"
        )
    with st.expander("👁️ Preview Generated Assessment Report in Browser", expanded=True):
        st.components.v1.html(st.session_state.html_report, height=650, scrolling=True)
