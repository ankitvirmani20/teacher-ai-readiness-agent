import streamlit as st

# Page setup
st.set_page_config(
    page_title="MAIC Teacher AI Readiness Evaluator",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------------
# QUESTION BANK (7 Domains grounded in MAIC TF Guide)
# ---------------------------------------------------------
QUESTION_BANK = [
    {
        "id": "d1_awareness",
        "name": "1. AI Awareness & Conceptual Fluency",
        "tag": "Core Literacy",
        "question": "How do you characterize your understanding of how generative AI models produce outputs, their failure modes (hallucinations), and what they can and cannot do?",
        "options": {
            1: "Emerging: View AI as an infallible 'search engine' or answer machine; unfamiliar with hallucinations or training limitations.",
            2: "Developing: Aware of hallucinations and probabilistic nature; understand basic prompting but struggle to predict failure cases.",
            3: "Proficient: View AI as a thinking partner; verify outputs against primary sources; understand context windows and bias.",
            4: "Advanced: Deep technical grasp of model capabilities; teach peers how to systematically probe outputs and identify subtle errors."
        }
    },
    {
        "id": "d2_instruction",
        "name": "2. Instructional Planning & Differentiation",
        "tag": "Instructional Practice",
        "question": "How do you use generative AI for lesson design, pacing, instructional scaffolding, and accommodating diverse learner profiles?",
        "options": {
            1: "Emerging: Rarely or never use AI for planning, or only generate generic worksheets and low-depth recall quizzes.",
            2: "Developing: Occasionally use AI for brainstorming lesson hooks, generating leveled texts, or translating materials.",
            3: "Proficient: Routinely use AI to build tiered scaffolds, targeted remediation sequences, and multi-modal instructional resources.",
            4: "Advanced: Co-design adaptive learning paths; author and share vetted, prompt-engineered curricular units across departments."
        }
    },
    {
        "id": "d3_assessment",
        "name": "3. Assessment Integrity, Friction & Judgment",
        "tag": "Authentic Work",
        "question": "How do your assignments incorporate 'Design for Friction' (demanding genuine human thought) and 'Assess for Judgment' (evaluating process over final prose)?",
        "options": {
            1: "Emerging: Rely on traditional take-home essays; depend on automated AI-detector software to enforce academic integrity.",
            2: "Developing: Require basic AI-use citation; experimenting with in-class benchmarks, oral defense, or handwritten outlines.",
            3: "Proficient: Intentionally design 'cognitive friction' (critique loops, synthesis of local context); assess prompt logs and revision history.",
            4: "Advanced: Fully transformed assessment ecosystem based on authentic performance tasks, iterative defense, and original reflection."
        }
    },
    {
        "id": "d4_ethics",
        "name": "4. Ethics, Privacy & Student Safeguards (Safeguard Gate)",
        "tag": "Governance & Compliance",
        "is_safeguard": True,
        "question": "How strictly do your classroom routines protect student privacy (FERPA/COPPA), enforce data minimization, and address algorithmic bias?",
        "options": {
            1: "Emerging: Unclear on district policies; have entered student PII, grades, or unredacted student work into public commercial AI tools.",
            2: "Developing: Adhere to strict data minimization (zero PII entered); utilize only district-cleared platforms; discuss basic bias with students.",
            3: "Proficient: Actively teach student data rights; evaluate tools for algorithmic/cultural bias; maintain transparent disclosure norms.",
            4: "Advanced: Serve as a building compliance resource; review vendor privacy terms and data retention policies alongside administration."
        }
    },
    {
        "id": "d5_mindset",
        "name": "5. Confidence, Mindset & Professional Agency",
        "tag": "Human-Centered Agency",
        "question": "What is your professional stance toward integrating generative AI into your teaching routines?",
        "options": {
            1: "Emerging: Apprehensive or defensive; concerned AI invalidates student learning and undermines educator autonomy.",
            2: "Developing: Curious but cautious; willing to test AI in low-stakes tasks when provided explicit, step-by-step guidance.",
            3: "Proficient: Confident and proactive; maintain clear professional agency, treating AI as a thought-partner that augments human judgment.",
            4: "Advanced: Highly adaptive and resilient; view technological disruption as an opportunity to rethink teaching and learning."
        }
    },
    {
        "id": "d6_infrastructure",
        "name": "6. Access, Infrastructure & Resource Reality",
        "tag": "Capacity & Support",
        "question": "How would you describe your access to student devices, reliable connectivity, approved tools, and protected planning time?",
        "options": {
            1: "Emerging: Severe constraints (unreliable Wi-Fi, shared carts only, zero dedicated time or budget for AI training).",
            2: "Developing: Moderate access (reliable classroom network, 1:1 devices 2–3 days/week, self-directed exploration time only).",
            3: "Proficient: Stable access (1:1 student devices daily, district-vetted tool accounts, structured PLC collaborative planning time).",
            4: "Advanced: Robust access (high-capacity infrastructure, funded enterprise tooling, weekly dedicated instructional coaching cycles)."
        }
    },
    {
        "id": "d7_transformation",
        "name": "7. Professional Transformation & Collaborative Culture",
        "tag": "Lead Your Own Transformation",
        "question": "How do you engage with colleagues around AI integration, peer coaching, and continuous pedagogical improvement?",
        "options": {
            1: "Emerging: Work in isolation; have not participated in AI-related professional learning or shared practices with peers.",
            2: "Developing: Attend occasional schoolwide webinars or workshops; apply ideas individually without systematic peer follow-up.",
            3: "Proficient: Actively participate in peer coaching, co-planning cycles, or cross-departmental sharing of AI-integrated lessons.",
            4: "Advanced: Serve on the Executive Trainer team or instructional leadership committee; host 'Model Classrooms' for peer observation."
        }
    }
]

# ---------------------------------------------------------
# UI HEADER & CONTEXT INPUTS
# ---------------------------------------------------------
st.title("🎓 Teacher AI Readiness Evaluation Agent")
st.caption("Miami AI Club (MAIC) AI in Education Task Force Implementation Framework")

with st.sidebar:
    st.header("Educator & School Profile")
    educator_name = st.text_input("Educator / ID (Optional)", placeholder="e.g., Ms. Taylor / Grade 10 Bio")
    grade_band = st.selectbox(
        "Grade Band & Setting",
        ["Elementary (K-5)", "Middle School (6-8)", "High School (9-12)", "Instructional Specialist / Coach"]
    )
    resource_level = st.selectbox(
        "School Resource Reality",
        [
            "Constrained (Low/No-Cost Tools, Shared Hardware, Zero AI Budget)",
            "Moderate (1:1 Student Devices, Exploring District Pilot Licenses)",
            "Well-Resourced (Enterprise Accounts, Dedicated Coaches, Protected PD)"
        ]
    )
    st.info("💡 **Safeguard Gate Notice**: Per Task Force policy, Domain 4 (Ethics & Privacy) sets an absolute ceiling on overall readiness.")

# ---------------------------------------------------------
# QUESTIONNAIRE SECTION
# ---------------------------------------------------------
st.subheader("📋 Diagnostic Assessment")
st.write("Select the option for each domain that most closely describes your current classroom practice.")

scores = {}
for q in QUESTION_BANK:
    with st.expander(f"**{q['name']}** [{q['tag']}]", expanded=True):
        st.write(f"*{q['question']}*")
        
        # Format radio options with full descriptions
        choices = list(q["options"].keys())
        selected_val = st.radio(
            label="Select your current stage:",
            options=choices,
            format_func=lambda x, opts=q["options"]: opts[x],
            index=1,
            key=q["id"]
        )
        scores[q["id"]] = selected_val

# ---------------------------------------------------------
# EVALUATION & REPORT GENERATION ENGINE
# ---------------------------------------------------------
if st.button("Run Evaluation & Generate Summary Report", type="primary"):
    total_val = sum(scores.values())
    avg_score = total_val / len(scores)
    d4_score = scores["d4_ethics"]

    # Calculate baseline readiness tier
    if avg_score >= 3.5:
        base_tier = "Advanced"
        tier_color = "#10b981"
        tier_desc = "Exemplary practice: Leader in authentic assessment design, peer mentoring, and systemic innovation."
    elif avg_score >= 2.6:
        base_tier = "Proficient"
        tier_color = "#0284c7"
        tier_desc = "Strategic adoption: Confident instructional user, intentional cognitive friction, and robust student safeguards."
    elif avg_score >= 1.8:
        base_tier = "Developing"
        tier_color = "#f59e0b"
        tier_desc = "Active experimentation: Routine lesson assistance, developing prompt confidence, needing assessment redesign support."
    else:
        base_tier = "Emerging"
        tier_color = "#ef4444"
        tier_desc = "Early stage: Focus on foundational literacy, basic prompting, and legal data privacy compliance."

    # Enforce the Safeguard Gate (Domain 4 Ceiling)
    final_tier = base_tier
    safeguard_applied = False

    if d4_score == 1 and base_tier in ["Developing", "Proficient", "Advanced"]:
        final_tier = "Emerging"
        tier_color = "#ef4444"
        safeguard_applied = True
    elif d4_score == 2 and base_tier in ["Proficient", "Advanced"]:
        final_tier = "Developing"
        tier_color = "#f59e0b"
        safeguard_applied = True

    # Display Assessment Dashboard
    st.divider()
    st.header("📊 Assessment Results & Diagnostic Summary")

    col_metric, col_details = st.columns()
    with col_metric:
        st.metric(label="Overall Readiness Score", value=f"{avg_score:.2f} / 4.00")
        st.markdown(
            f"<div style='padding: 10px 16px; border-radius: 8px; background-color: {tier_color}22; "
            f"border: 2px solid {tier_color}; color: {tier_color}; font-size: 1.25rem; font-weight: bold; text-align: center;'>"
            f"{final_tier.upper()} TIER</div>",
            unsafe_allow_html=True
        )

    with col_details:
        st.write(f"**Diagnostic Profile:** {tier_desc}")
        if safeguard_applied:
            st.error(
                f"⚠️ **Safeguard Gate Enforced:** Your calculated technical score is {avg_score:.2f}, "
                f"but overall readiness is capped at **{final_tier}** because Domain 4 (Ethics & Privacy) "
                f"scored at level {d4_score}. Tool adoption cannot exceed legal compliance and student protection standards."
            )

    # Domain Breakdown Progress Bars
    st.subheader("Domain Mastery Breakdown")
    for q in QUESTION_BANK:
        sc = scores[q["id"]]
        pct = int((sc / 4.0) * 100)
        c1, c2 = st.columns()
        with c1:
            st.write(f"**{q['name']}**")
        with c2:
            st.progress(pct, text=f"Stage {sc} of 4: {['', 'Emerging', 'Developing', 'Proficient', 'Advanced'][sc]}")

    # Tailored Recommendations based on Implementation Guide Appendices
    st.divider()
    st.subheader("🎯 Differentiated Action Plan & Assigned Units")

    r1, r2 = st.columns(2)
    with r1:
        st.markdown("### 📚 Assigned Professional Development (Appendix A & C)")
        if final_tier == "Emerging":
            st.markdown("- **Appendix A Unit 1:** AI Literacy & Conceptual Understanding (Limitations & Failure Modes)")
            st.markdown("- **Appendix A Unit 2:** Ethics, Privacy, and Responsible Classroom Use")
            st.markdown("- **Appendix C Unit 1:** Human–AI Collaboration and Role Clarity")
        elif final_tier == "Developing":
            st.markdown("- **Appendix A Unit 3:** Instructional Planning with AI & Curricular Alignment")
            st.markdown("- **Appendix A Unit 4:** Differentiated Learning & Adaptive Scaffolding Through AI")
            st.markdown("- **Appendix A Unit 7:** Assessment Integrity in an AI Era (AI-Resilient Tasks)")
        elif final_tier == "Proficient":
            st.markdown("- **Appendix A Unit 8:** Classroom Management in AI-Integrated Environments")
            st.markdown("- **Appendix A Unit 10:** AI for Teacher Productivity & Professional Workflow")
            st.markdown("- **Appendix C Unit 8:** Ethical Decision-Making Scenarios & Case Studies")
        else:
            st.markdown("- **Appendix A Unit 11:** Collaborative Schoolwide AI Culture & Norms")
            st.markdown("- **Appendix A Unit 12:** Continuous Improvement, Model Classrooms & Reflective Practice")
            st.markdown("- **Appendix B Unit 15:** Supporting Teachers in AI Integration (Executive Trainer track)")

        st.markdown("### 💡 Authentic Work & Cognitive Friction")
        if scores["d3_assessment"] <= 2:
            st.markdown("- **De-emphasize AI Detectors:** Shift verification to in-class writing benchmarks and live check-ins.")
            st.markdown("- **Design for Friction:** Require students to integrate un-crawlable local context, personal narratives, or classroom discussions.")
            st.markdown("- **Assess for Judgment:** Evaluate students on prompt evolution logs and factual critique rather than final prose alone.")
        else:
            st.markdown("- **Comparative Prompting:** Have students run identical inquiries across two distinct models and debate the divergences.")
            st.markdown("- **Exemplar Sharing:** Present your assessment rubrics to department colleagues during monthly PLC periods.")

    with r2:
        st.markdown("### 🛡️ Privacy & Safeguard Actions")
        if scores["d4_ethics"] <= 2:
            st.markdown("- **Data Minimization:** Never paste student PII, IEP records, or student work into unvetted public tools.")
            st.markdown("- **Model Training Restrictions:** Confirm that tools used have contractual 'zero data retention' or non-training clauses.")
            st.markdown("- **Classroom Disclosure:** Post a clear AI transparency expectation in your physical room and course syllabus.")
        else:
            st.markdown("- **Algorithmic Bias Labs:** Lead students in structured exercises analyzing AI responses for demographic or cultural bias.")
            st.markdown("- **Governance Contribution:** Offer feedback to the administrative team on tool-vetting rubrics.")

        st.markdown("### 🎓 Student AI Literacy Focus (Appendix D)")
        if final_tier in ["Emerging", "Developing"]:
            st.markdown("- **Unit 1 (What AI Is & Isn't):** Help students understand token prediction and the mechanics of hallucinations.")
            st.markdown("- **Unit 2 (Responsible Use):** Set clear boundaries regarding attribution and teacher-approved use cases.")
            st.markdown("- **Unit 5 (Academic Integrity):** Guide students to differentiate brainstorming vs. unapproved submission.")
        else:
            st.markdown("- **Unit 3 (Prompting as Questioning):** Train students to treat AI as a research interlocutor.")
            st.markdown("- **Unit 4 (Evaluating Output):** Conduct forensic fact-checking sessions comparing AI citations with original sources.")
            st.markdown("- **Unit 6 (Creativity & Problem Solving):** Use generative AI as an iterative divergent-thinking partner.")

    # Contextual Roadmap
    st.divider()
    st.subheader("🗓️ 90-Day Implementation Roadmap")
    if "Constrained" in resource_level:
        st.markdown("""
        1. **Days 1–30 (Zero-Cost Governance):** Adopt free browser tools with zero-data-retention switches enabled. Establish in-class baseline writing samples.
        2. **Days 31–60 (Low-Tech Friction):** Restructure assignments into multi-stage tasks: oral defenses, peer critiques, and handwritten synthesis outlines.
        3. **Days 61–90 (Peer PLC Labs):** Pair with a peer during standard planning periods to co-plan one AI-enhanced lesson unit using free approved tools.
        """)
    else:
        st.markdown("""
        1. **Days 1–30 (Enterprise Sandbox & Baseline):** Register for district-licensed workspace accounts, execute confidentiality forms, and take department baseline surveys.
        2. **Days 31–60 (Tiered Workshops & Artifact):** Complete assigned Appendix A modules and submit one verified lesson template showing 'Design for Friction'.
        3. **Days 61–90 (Micro-Coaching & Student Units):** Host a peer observation session, deploy Appendix D Student AI Literacy Units 1–3, and collect student reflection logs.
        """)

    # Exportable HTML Summary
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <title>AI Readiness Assessment Summary</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 30px; color: #0f172a; line-height: 1.5; }}
        .header {{ border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 20px; }}
        .tier {{ font-size: 1.4rem; font-weight: bold; color: {tier_color}; margin-top: 6px; }}
        .section {{ margin-top: 24px; }}
        .box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-top: 10px; }}
        ul {{ padding-left: 20px; }}
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Teacher AI Readiness Assessment Report</h1>
        <p><strong>Educator:</strong> {educator_name or 'Educator'} | <strong>Grade Band:</strong> {grade_band} | <strong>Resource Context:</strong> {resource_level}</p>
        <div class="tier">Assessed Readiness Tier: {final_tier.upper()} ({avg_score:.2f} / 4.00)</div>
      </div>
      <div class="section">
        <h3>Summary Profile</h3>
        <p>{tier_desc}</p>
        {'<p style="color:red;"><strong>Safeguard Gate Enforced:</strong> Overall readiness was capped due to Domain 4 (Privacy & Safety) scoring at level ' + str(d4_score) + '.</p>' if safeguard_applied else ''}
      </div>
      <div class="section">
        <h3>Domain Scores</h3>
        <ul>
          {''.join([f"<li><strong>{q['name']}:</strong> {scores[q['id']]}/4 ({['', 'Emerging', 'Developing', 'Proficient', 'Advanced'][scores[q['id']]]})</li>" for q in QUESTION_BANK])}
        </ul>
      </div>
      <div class="section">
        <h3>Recommended Focus</h3>
        <div class="box">
          <p>Review the assigned modules in <strong>Appendix A</strong> and student literacy units in <strong>Appendix D</strong> of the MAIC Implementation Guide.</p>
        </div>
      </div>
    </body>
    </html>
    """

    st.download_button(
        label="📥 Download Assessment Summary (HTML)",
        data=html_report,
        file_name=f"ai_readiness_assessment_{educator_name or 'teacher'}.html",
        mime="text/html"
    )
