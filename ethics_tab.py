"""
ethics_tab.py — Ethics & Transparency section for DataForge.
Covers ethical, social, and technical implications of the agentic system.

Usage in app.py:
    from ethics_tab import render_ethics_tab
    with tab11:
        render_ethics_tab()
"""

import streamlit as st


def render_ethics_tab():
    st.markdown("""
    <style>
    .ethics-hero {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
        border: 1px solid #21262D;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .ethics-hero h1 {
        font-size: 2rem;
        font-weight: 900;
        color: #02C39A;
        margin-bottom: 0.5rem;
    }
    .ethics-hero p {
        color: #8B949E;
        font-size: 1rem;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.7;
    }
    .ethics-card {
        background: #161B22;
        border: 1px solid #21262D;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .ethics-card h3 {
        color: #E6EDF3;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .ethics-card p {
        color: #8B949E;
        font-size: 0.9rem;
        line-height: 1.7;
        margin: 0;
    }
    .ethics-card .concern {
        color: #F85149;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .ethics-card .mitigation {
        color: #3FB950;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.75rem;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .ethics-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    .pill-ethical { background:#1C2D24; color:#3FB950; border:1px solid #2EA043; }
    .pill-social  { background:#1C2233; color:#58A6FF; border:1px solid #1F6FEB; }
    .pill-technical { background:#2D1B1B; color:#F85149; border:1px solid #DA3633; }
    .commitment-box {
        background: linear-gradient(135deg, #0D2137 0%, #0D1117 100%);
        border: 1px solid #028090;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
    .commitment-box h3 {
        color: #02C39A;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    .commitment-box p {
        color: #CBD5E1;
        line-height: 1.8;
        font-size: 0.95rem;
    }
    .agent-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #21262D;
    }
    .agent-row:last-child { border-bottom: none; }
    .agent-icon {
        font-size: 1.4rem;
        min-width: 32px;
        text-align: center;
        margin-top: 2px;
    }
    .agent-info h4 {
        color: #E6EDF3;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0 0 3px 0;
    }
    .agent-info p {
        color: #8B949E;
        font-size: 0.82rem;
        margin: 0;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ethics-hero">
        <h1>⚖️ Ethics & Transparency</h1>
        <p>DataForge is an agentic AI system. We believe you have the right to understand
        how it works, what decisions it makes autonomously, and what safeguards are in place.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Agent transparency ────────────────────────────────────────────────
    st.markdown("### 🤖 What Our Agents Do Autonomously")
    st.markdown("DataForge uses **6 specialised AI agents** that make decisions without human input at each step:")

    st.markdown("""
    <div style="background:#161B22;border:1px solid #21262D;border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1.5rem">
        <div class="agent-row">
            <div class="agent-icon">🧹</div>
            <div class="agent-info">
                <h4>Cleaner Agent</h4>
                <p>Autonomously detects and removes duplicates, imputes missing values, and flags outliers. Every decision is logged in the Audit Log so you can review and challenge it.</p>
            </div>
        </div>
        <div class="agent-row">
            <div class="agent-icon">📊</div>
            <div class="agent-info">
                <h4>Analyser Agent</h4>
                <p>Computes statistics, identifies correlations, and detects skewness. Results are shown in full — nothing is hidden or summarised away.</p>
            </div>
        </div>
        <div class="agent-row">
            <div class="agent-icon">📈</div>
            <div class="agent-info">
                <h4>Visualiser Agent</h4>
                <p>Selects chart types based on data structure. All charts are interactive so you can inspect every data point yourself.</p>
            </div>
        </div>
        <div class="agent-row">
            <div class="agent-icon">✍️</div>
            <div class="agent-info">
                <h4>Reporter Agent</h4>
                <p>Writes the analysis report using an LLM. Only statistical summaries — never raw data — are sent to the AI. A fallback report is generated locally if no API key is set.</p>
            </div>
        </div>
        <div class="agent-row">
            <div class="agent-icon">⚖️</div>
            <div class="agent-info">
                <h4>Bias Auditor Agent</h4>
                <p>Proactively scans for skewness, class imbalance, and proxy variables before any model is trained. Flags issues with severity ratings.</p>
            </div>
        </div>
        <div class="agent-row">
            <div class="agent-icon">🧠</div>
            <div class="agent-info">
                <h4>Socratic Teaching Agent</h4>
                <p>Generates quiz questions and grades answers. Scoring rubric is shown for every answer so students understand exactly how they were evaluated.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Three pillars ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<span class="ethics-pill pill-ethical">🟢 Ethical</span>', unsafe_allow_html=True)
        st.markdown("**Implications**")

    with col2:
        st.markdown('<span class="ethics-pill pill-social">🔵 Social</span>', unsafe_allow_html=True)
        st.markdown("**Implications**")

    with col3:
        st.markdown('<span class="ethics-pill pill-technical">🔴 Technical</span>', unsafe_allow_html=True)
        st.markdown("**Implications**")

    st.divider()

    # ── Ethical implications ──────────────────────────────────────────────
    st.markdown("### 🟢 Ethical Implications")

    st.markdown("""
    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Autonomous decisions in education are high stakes</h3>
        <p>DataForge agents make decisions that directly affect how students learn — cleaning their data, selecting models, grading their answers. A wrong AI decision could teach incorrect concepts.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>Every agent decision is fully visible. The audit log shows exactly what was cleaned and why. Socratic scores always include a detailed explanation. Nothing is a black box.</p>
    </div>

    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Bias amplification through unchecked data</h3>
        <p>If a student uploads a biased dataset, agents could analyse and report on it without flagging problems — normalising biased data in their learning.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>The dedicated Bias Report tab runs before any modelling. It explicitly flags skewness, class imbalance, proxy variables, and representation gaps with severity ratings.</p>
    </div>

    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Data leaving the user's machine without consent</h3>
        <p>When datasets are processed, summaries are sent to OpenAI's API. Users may not realise their data is leaving their device.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>Only statistical summaries are sent — never raw rows or cell values. Users are warned on upload not to include personally identifiable information. Full fallback mode works with zero external API calls.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Social implications ───────────────────────────────────────────────
    st.markdown("### 🔵 Social Implications")

    st.markdown("""
    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Risk of creating passive learners</h3>
        <p>An AI that explains everything risks training students to consume AI output rather than think independently — the opposite of good data science education.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>The Socratic Challenge Mode flips the model entirely. Instead of explaining, the AI questions. Students must demonstrate understanding before they see any feedback. Passive reading is replaced with active reasoning.</p>
    </div>

    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Digital divide and accessibility</h3>
        <p>Requiring internet access and paid API keys excludes learners in low-bandwidth or low-income settings — potentially widening the skills gap rather than closing it.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>DataForge has a complete fallback mode. Every feature — lessons, quizzes, reports, visualisations — works without any API key using built-in content and local computation. No student is excluded by cost.</p>
    </div>

    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Democratising data science education</h3>
        <p>This is a positive social implication. DataForge makes expert-level data science teaching available to anyone — no tutor, no university, no expensive course required.</p>
        <div class="mitigation">✅ Our commitment</div>
        <p>We designed DataForge to work on any dataset a student brings — from healthcare to finance to sport. The teaching adapts to beginner and intermediate levels automatically.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Technical implications ────────────────────────────────────────────
    st.markdown("### 🔴 Technical Implications")

    st.markdown("""
    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Agent failure cascades</h3>
        <p>In a multi-agent pipeline, if one agent produces bad output, every downstream agent inherits that error. A cleaning mistake corrupts the analysis, visualisation, and report.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>Each agent is wrapped in error handling. The orchestrator catches failures gracefully and reports them clearly rather than crashing silently. The audit log makes every cleaning decision reviewable.</p>
    </div>

    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Prompt injection via uploaded data</h3>
        <p>A malicious user could upload a CSV where cell values contain prompt injection attacks designed to manipulate the AI agents into producing harmful output.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>Only computed statistical summaries are sent to the LLM — not raw cell values. This significantly reduces the attack surface since injected text in cells never reaches the prompt.</p>
    </div>

    <div class="ethics-card">
        <div class="concern">⚠️ Concern</div>
        <h3>Non-deterministic scoring and fairness</h3>
        <p>LLM outputs are probabilistic — two students giving similar answers could receive different scores, making the system potentially unfair.</p>
        <div class="mitigation">✅ How we address it</div>
        <p>Temperature is set to 0.3 for all evaluation calls to maximise consistency. A strict rubric with explicit penalties is enforced in every grading prompt. Every score includes a full explanation students can challenge.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Commitment box ────────────────────────────────────────────────────
    st.markdown("""
    <div class="commitment-box">
        <h3>📜 Our Commitment</h3>
        <p>
        DataForge is built with the awareness that agentic systems in education carry real responsibility.
        Six autonomous agents make decisions that directly affect how students learn.
        We have responded to this by building <strong>full transparency into every agent decision</strong>,
        a <strong>bias auditing agent</strong> that proactively flags unfair data,
        a <strong>Socratic mode</strong> that prevents AI dependency,
        and a <strong>complete offline fallback</strong> so no student is excluded by cost or connectivity.
        We deliberately keep raw user data out of API calls — only statistical summaries leave the device.
        We believe AI in education should empower human thinking, not replace it.
        </p>
    </div>
    """, unsafe_allow_html=True)