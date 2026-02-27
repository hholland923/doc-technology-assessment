import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="DoC Technology Maturity Assessment",
    page_icon=":shield:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom Styling
# ──────────────────────────────────────────────
st.markdown(
    """
<style>
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px 20px;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #64748b;
    }
    .state-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 24px;
        margin: 10px 0;
        line-height: 1.7;
    }
    .framework-card {
        border-left: 4px solid;
        padding: 16px 20px;
        margin: 12px 0;
        background: #f8fafc;
        border-radius: 0 8px 8px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# Password Protection
# ──────────────────────────────────────────────
def check_password():
    """Gate access behind a password stored in Streamlit secrets."""

    def on_submit():
        if st.session_state.get("_pw") == st.secrets.get("password", ""):
            st.session_state["auth"] = True
        else:
            st.session_state["auth"] = False

    if st.session_state.get("auth"):
        return True

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(
            "<div style='text-align:center'>"
            "<h1>DoC Technology Assessment</h1>"
            "<p style='color:#64748b; font-size:1.1rem'>"
            "50-State Corrections Technology Maturity Analysis</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.text_input(
            "Access Code",
            type="password",
            key="_pw",
            on_change=on_submit,
        )
        if "auth" in st.session_state and not st.session_state["auth"]:
            st.error("Invalid access code.")
    return False


if not check_password():
    st.stop()


# ──────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────
@st.cache_data
def load_states():
    return pd.read_csv("data/states.csv")


@st.cache_data
def load_maturity_model():
    return pd.read_csv("data/maturity_model.csv")


states_df = load_states()
maturity_df = load_maturity_model()

LEVEL_COLORS = {
    0: "#dc2626",
    1: "#ea580c",
    2: "#ca8a04",
    3: "#16a34a",
    4: "#2563eb",
    5: "#7c3aed",
}
LEVEL_NAMES = dict(zip(maturity_df["level"], maturity_df["name"]))

# ──────────────────────────────────────────────
# Sidebar Filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("Filters")
    st.markdown("---")

    regions = ["All"] + sorted(states_df["region"].unique().tolist())
    sel_region = st.selectbox("Region", regions)

    levels = ["All"] + sorted(states_df["maturity_level"].unique().tolist())
    sel_level = st.selectbox("Maturity Level", levels)

    pell_opts = ["All", "Yes", "No"]
    sel_pell = st.selectbox("Second Chance Pell", pell_opts)

    st.markdown("---")
    st.markdown("### Maturity Scale")
    for lvl in sorted(LEVEL_NAMES.keys()):
        name = LEVEL_NAMES[lvl]
        color = LEVEL_COLORS.get(lvl, "#888")
        st.markdown(
            f"<span style='color:{color}; font-weight:700'>Level {lvl}</span>"
            f"&ensp;{name}",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption(
        "Data is estimated for demonstration purposes. "
        "Sources: BJS, ED.gov, state DoC publications."
    )

# Apply filters
df = states_df.copy()
if sel_region != "All":
    df = df[df["region"] == sel_region]
if sel_level != "All":
    df = df[df["maturity_level"] == int(sel_level)]
if sel_pell != "All":
    df = df[df["second_chance_pell"] == sel_pell]

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown("# Department of Corrections &mdash; Technology Maturity Assessment")
st.markdown(
    "*50-state analysis of education technology infrastructure "
    "readiness in correctional facilities*"
)

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab_dash, tab_state, tab_model, tab_calc = st.tabs(
    ["Overview", "State Deep Dive", "Maturity Framework", "Opportunity Calculator"]
)

# ═══════════════════════════════════════════════
# TAB 1 — OVERVIEW DASHBOARD
# ═══════════════════════════════════════════════
with tab_dash:

    # ── Metric Cards ──
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("States Shown", len(df))
    m2.metric("Avg Maturity", f"{df['maturity_level'].mean():.1f} / 5")
    m3.metric("Total Facilities", f"{df['num_facilities'].sum():,}")
    m4.metric("Total Population", f"{df['incarcerated_pop'].sum():,}")
    m5.metric(
        "Est. IT Spend",
        f"${df['annual_it_budget_est_millions'].sum():,.0f}M",
    )

    st.markdown("")

    # ── Choropleth Map ──
    fig_map = px.choropleth(
        df,
        locations="state_code",
        locationmode="USA-states",
        color="maturity_level",
        color_continuous_scale=[
            [0.0, "#dc2626"],
            [0.2, "#ea580c"],
            [0.4, "#ca8a04"],
            [0.6, "#16a34a"],
            [0.8, "#2563eb"],
            [1.0, "#7c3aed"],
        ],
        range_color=[0, 5],
        scope="usa",
        hover_name="state_name",
        hover_data={
            "maturity_level": True,
            "num_facilities": True,
            "incarcerated_pop": ":,",
            "annual_it_budget_est_millions": ":.1f",
            "state_code": False,
        },
        labels={
            "maturity_level": "Maturity Level",
            "num_facilities": "Facilities",
            "incarcerated_pop": "Incarcerated Pop.",
            "annual_it_budget_est_millions": "IT Budget ($M)",
        },
    )
    fig_map.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=520,
        coloraxis_colorbar=dict(
            title="Maturity<br>Level",
            tickvals=[0, 1, 2, 3, 4, 5],
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Charts Row ──
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### Maturity Distribution")
        dist = (
            states_df["maturity_level"]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        dist.columns = ["level", "count"]
        dist["label"] = dist["level"].map(
            lambda x: f"L{x}: {LEVEL_NAMES.get(x, '')}"
        )
        dist["color"] = dist["level"].map(LEVEL_COLORS)

        fig_bar = go.Figure(
            go.Bar(
                x=dist["label"],
                y=dist["count"],
                marker_color=dist["color"].tolist(),
                text=dist["count"],
                textposition="outside",
            )
        )
        fig_bar.update_layout(
            height=380,
            xaxis_title="",
            yaxis_title="Number of States",
            showlegend=False,
            margin=dict(t=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        st.markdown("### Regional Avg Maturity")
        region_agg = (
            states_df.groupby("region")
            .agg(
                avg_maturity=("maturity_level", "mean"),
                total_facilities=("num_facilities", "sum"),
                states=("state_name", "count"),
            )
            .reset_index()
            .sort_values("avg_maturity", ascending=True)
        )
        fig_region = go.Figure(
            go.Bar(
                x=region_agg["avg_maturity"],
                y=region_agg["region"],
                orientation="h",
                marker_color="#2563eb",
                text=region_agg["avg_maturity"].round(1),
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Avg Maturity: %{x:.1f}<br>"
                    "<extra></extra>"
                ),
            )
        )
        fig_region.update_layout(
            height=380,
            xaxis_title="Average Maturity Level",
            yaxis_title="",
            showlegend=False,
            margin=dict(t=20),
            xaxis=dict(range=[0, 5]),
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # ── Full Table ──
    st.markdown("### State Directory")
    display_cols = {
        "state_name": "State",
        "state_code": "Code",
        "region": "Region",
        "maturity_level": "Maturity",
        "num_facilities": "Facilities",
        "incarcerated_pop": "Population",
        "annual_it_budget_est_millions": "IT Budget ($M)",
        "education_programs_count": "Ed. Programs",
        "second_chance_pell": "Pell Eligible",
    }
    table_df = df[list(display_cols.keys())].rename(columns=display_cols)
    st.dataframe(
        table_df.sort_values("Maturity"),
        use_container_width=True,
        height=450,
        hide_index=True,
    )

# ═══════════════════════════════════════════════
# TAB 2 — STATE DEEP DIVE
# ═══════════════════════════════════════════════
with tab_state:

    selected_state = st.selectbox(
        "Select a state",
        states_df["state_name"].sort_values().tolist(),
        key="dd_state",
    )

    s = states_df[states_df["state_name"] == selected_state].iloc[0]
    lvl_row = maturity_df[maturity_df["level"] == s["maturity_level"]].iloc[0]
    next_lvl = s["maturity_level"] + 1
    next_lvl_row = (
        maturity_df[maturity_df["level"] == next_lvl].iloc[0]
        if next_lvl <= 5
        else None
    )

    st.markdown(f"## {s['state_name']} ({s['state_code']})")

    # ── Key Metrics ──
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Maturity Level", f"{s['maturity_level']} / 5")
    k2.metric("Facilities", s["num_facilities"])
    k3.metric("Population", f"{s['incarcerated_pop']:,}")
    k4.metric("Est. IT Budget", f"${s['annual_it_budget_est_millions']}M")
    k5.metric("Ed. Programs", s["education_programs_count"])

    st.markdown("")

    # ── Current State / Opportunities ──
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("#### Current State")
        st.markdown(
            f"""<div class='state-card'>
<strong>Maturity Level:</strong> Level {s['maturity_level']} &mdash; {lvl_row['name']}<br>
<strong>Risk Profile:</strong> {lvl_row['risk_level']}<br>
<strong>Current Technology:</strong> {s['current_tech_summary']}<br>
<strong>Second Chance Pell:</strong> {s['second_chance_pell']}<br>
<strong>Region:</strong> {s['region']}<br>
<strong>Procurement Cycle:</strong> {s['procurement_cycle']}
</div>""",
            unsafe_allow_html=True,
        )

    with c_right:
        st.markdown("#### Opportunity")
        if next_lvl_row is not None:
            total_upgrade = (
                next_lvl_row["estimated_cost_per_facility"] * s["num_facilities"]
            )
            st.markdown(
                f"""<div class='state-card'>
<strong>Key Gaps:</strong> {s['key_opportunities']}<br><br>
<strong>Next Level ({next_lvl} &mdash; {next_lvl_row['name']}):</strong><br>
Infrastructure needed: {next_lvl_row['it_requirements']}<br>
Est. cost/facility: ${next_lvl_row['estimated_cost_per_facility']:,}<br>
Est. total ({s['num_facilities']} facilities): <strong>${total_upgrade:,.0f}</strong><br>
Timeline: ~{next_lvl_row['typical_timeline_months']} months
</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='state-card'>"
                "This state is at the highest maturity level."
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("")

    # ── Maturity Gauge ──
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=s["maturity_level"],
            title={"text": f"{s['state_name']} Maturity Level"},
            gauge=dict(
                axis=dict(range=[0, 5], tickvals=[0, 1, 2, 3, 4, 5]),
                bar=dict(color="#2563eb"),
                steps=[
                    dict(range=[0, 1], color="#fee2e2"),
                    dict(range=[1, 2], color="#ffedd5"),
                    dict(range=[2, 3], color="#fef9c3"),
                    dict(range=[3, 4], color="#dcfce7"),
                    dict(range=[4, 5], color="#dbeafe"),
                ],
                threshold=dict(
                    line=dict(color="#16a34a", width=3),
                    thickness=0.8,
                    value=3,
                ),
            ),
        )
    )
    fig_gauge.update_layout(height=300, margin=dict(t=80, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.caption(
        "Green threshold line marks the 'sweet spot' (Level 3): "
        "optimal balance of educational outcomes and security risk."
    )

    # ── Peer Comparison ──
    st.markdown("#### Regional Peer Comparison")
    peers = states_df[states_df["region"] == s["region"]].sort_values(
        "maturity_level", ascending=False
    )
    peer_colors = [
        "#2563eb" if name == selected_state else "#cbd5e1"
        for name in peers["state_name"]
    ]
    fig_peers = go.Figure(
        go.Bar(
            x=peers["state_name"],
            y=peers["maturity_level"],
            marker_color=peer_colors,
            text=peers["maturity_level"],
            textposition="outside",
        )
    )
    fig_peers.update_layout(
        height=380,
        xaxis_title="",
        yaxis_title="Maturity Level",
        yaxis=dict(range=[0, 5.5]),
        showlegend=False,
        margin=dict(t=20),
    )
    st.plotly_chart(fig_peers, use_container_width=True)

# ═══════════════════════════════════════════════
# TAB 3 — MATURITY FRAMEWORK
# ═══════════════════════════════════════════════
with tab_model:

    st.markdown("## Education Technology Maturity Framework")
    st.markdown(
        "This framework maps the spectrum of education technology delivery "
        "modalities in correctional facilities, from paper-based correspondence "
        "to fully integrated digital platforms. Each level represents increased "
        "educational capability, digital literacy outcomes, and infrastructure "
        "requirements."
    )
    st.markdown(
        "Derived from analysis of current Department of Corrections education "
        "programs across all 50 states."
    )

    st.markdown("---")

    for _, row in maturity_df.iterrows():
        level = row["level"]
        color = LEVEL_COLORS.get(level, "#888")
        sweet = (
            "&ensp;<span style='background:#dcfce7; padding:2px 8px; "
            "border-radius:4px; font-size:0.8rem; color:#166534'>"
            "SWEET SPOT</span>"
            if level in (2, 3)
            else ""
        )
        st.markdown(
            f"""<div class='framework-card' style='border-color:{color}'>
<h3 style='margin:0; color:{color}'>Level {level}: {row['name']}{sweet}</h3>
<p style='margin:8px 0 12px 0; color:#475569'>{row['description']}</p>
<table style='width:100%'>
<tr>
<td><strong>Risk Level:</strong> {row['risk_level']}</td>
<td><strong>Est. Cost / Facility:</strong> ${row['estimated_cost_per_facility']:,}</td>
<td><strong>Timeline:</strong> {row['typical_timeline_months']} months</td>
</tr>
<tr>
<td colspan='3'><strong>IT Requirements:</strong> {row['it_requirements']}</td>
</tr>
</table>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        """
### The Sweet Spot: Levels 2-3

Analysis indicates that **Levels 2 and 3** (Offline Student Network + Remote
Educator Access) represent the optimal balance between educational outcomes
and security risk:

- Students gain digital literacy skills expected by employers
- Broader course selection and professor pool via remote access
- Air-gapped or tightly controlled network perimeters maintained
- Avoids the monitoring burden of allow-listed internet access
- Aligns with Second Chance Pell Grant technology requirements

Most state DoCs currently operate at **Levels 0-2**, representing a significant
opportunity for technology infrastructure investment to reach the sweet spot.
"""
    )

    # ── Where states fall today ──
    st.markdown("### Current National Position")
    position_data = (
        states_df["maturity_level"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    position_data.columns = ["level", "count"]
    position_data["pct"] = (
        position_data["count"] / position_data["count"].sum() * 100
    )
    position_data["label"] = position_data["level"].map(LEVEL_NAMES)
    position_data["color"] = position_data["level"].map(LEVEL_COLORS)

    below_sweet = states_df[states_df["maturity_level"] < 2].shape[0]
    at_sweet = states_df[states_df["maturity_level"].isin([2, 3])].shape[0]
    above_sweet = states_df[states_df["maturity_level"] > 3].shape[0]

    p1, p2, p3 = st.columns(3)
    p1.metric("Below Sweet Spot (L0-1)", f"{below_sweet} states")
    p2.metric("At Sweet Spot (L2-3)", f"{at_sweet} states")
    p3.metric("Above Sweet Spot (L4-5)", f"{above_sweet} states")

# ═══════════════════════════════════════════════
# TAB 4 — OPPORTUNITY CALCULATOR
# ═══════════════════════════════════════════════
with tab_calc:

    st.markdown("## Opportunity Calculator")
    st.markdown(
        "Estimate the infrastructure investment required to advance "
        "a state's education technology maturity."
    )
    st.markdown("")

    calc_left, calc_right = st.columns([1, 1.4])

    with calc_left:
        calc_state = st.selectbox(
            "Select State",
            states_df["state_name"].sort_values().tolist(),
            key="calc_state",
        )
        sd = states_df[states_df["state_name"] == calc_state].iloc[0]
        current = sd["maturity_level"]

        st.info(
            f"**{calc_state}** is at **Level {current}** "
            f"({LEVEL_NAMES.get(current, '')}) "
            f"with **{sd['num_facilities']}** facilities."
        )

        if current < 5:
            target = st.slider(
                "Target Maturity Level",
                min_value=int(current) + 1,
                max_value=5,
                value=min(int(current) + 1, 5),
                key="calc_target",
            )

            facility_pct = st.slider(
                "% of Facilities to Upgrade",
                min_value=10,
                max_value=100,
                value=100,
                step=10,
                key="calc_pct",
            )
        else:
            target = 5
            facility_pct = 100

    with calc_right:
        if current >= 5:
            st.success("This state is already at the maximum maturity level.")
        else:
            fac_count = int(sd["num_facilities"] * facility_pct / 100)

            total_infra = 0
            rows = []
            total_months = 0

            for lvl in range(int(current) + 1, target + 1):
                lr = maturity_df[maturity_df["level"] == lvl].iloc[0]
                cost = lr["estimated_cost_per_facility"] * fac_count
                total_infra += cost
                total_months += lr["typical_timeline_months"]
                rows.append(
                    {
                        "Transition": f"L{lvl - 1} -> L{lvl}",
                        "Target": lr["name"],
                        "Cost / Facility": f"${lr['estimated_cost_per_facility']:,}",
                        "Facilities": fac_count,
                        "Subtotal": f"${cost:,.0f}",
                    }
                )

            services = total_infra * 0.30
            grand = total_infra + services

            st.markdown("### Investment Estimate")
            st.markdown("")

            e1, e2, e3 = st.columns(3)
            e1.metric("Infrastructure", f"${total_infra:,.0f}")
            e2.metric("Services (30%)", f"${services:,.0f}")
            e3.metric("Total Investment", f"${grand:,.0f}")

            st.markdown("")
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("")
            t1, t2 = st.columns(2)
            t1.metric("Est. Timeline", f"{total_months} months")
            t2.metric("Facilities Covered", f"{fac_count} / {sd['num_facilities']}")

            st.markdown("")
            st.markdown("#### Required Infrastructure by Level")
            for lvl in range(int(current) + 1, target + 1):
                lr = maturity_df[maturity_df["level"] == lvl].iloc[0]
                st.markdown(
                    f"**Level {lvl} ({lr['name']}):** {lr['it_requirements']}"
                )

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Proof of concept. All data is estimated based on publicly available sources "
    "(Bureau of Justice Statistics, ED.gov, state DoC publications). "
    "Intended for demonstration and planning purposes only."
)
