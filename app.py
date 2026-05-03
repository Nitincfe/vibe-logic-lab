import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Acceleration at Constant Power",
    page_icon="⚡",
    layout="wide",
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("⚡ Acceleration at Constant Power")
st.markdown(
    r"""
    At **constant power**, force = P/v, so acceleration decreases as speed rises.  
    The resulting velocity curve follows **v = k√t**, where k = P/√(m·P) — here
    treated as a user-defined constant derived from your target conditions.
    """,
    unsafe_allow_html=False,
)

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🎛️ Parameters")

    target_speed = st.slider(
        "Target Speed (m/s)",
        min_value=10,
        max_value=200,
        value=60,
        step=5,
        help="The speed you want to reach by the end of the time window.",
    )

    target_time = st.slider(
        "Time to reach target (s)",
        min_value=5,
        max_value=120,
        value=30,
        step=5,
        help="How many seconds it takes to reach the target speed.",
    )

    st.divider()
    st.markdown("### 📐 Derived constant")
    k = target_speed / np.sqrt(target_time)
    st.latex(r"k = \frac{v_{target}}{\sqrt{t_{target}}}")
    st.metric("k value", f"{k:.3f}  m/s^(3/2)")

    st.divider()
    st.markdown(
        "**Constant-acceleration** baseline uses the same start/end points "
        r"so that $a = v_{target} / t_{target}$."
    )

# ── Compute curves ────────────────────────────────────────────────────────────
t = np.linspace(0.01, target_time, 500)   # avoid t=0 for acceleration calc

# Constant-power  →  v = k√t
v_cp = k * np.sqrt(t)
a_cp = k / (2 * np.sqrt(t))               # dv/dt = k / (2√t)

# Constant-acceleration baseline
a_const = target_speed / target_time       # m/s²
v_ca = a_const * t
a_ca = np.full_like(t, a_const)

# Power required at each instant  P = F·v = m·a·v  (normalised: m = 1 kg)
p_cp = a_cp * v_cp                         # constant by definition (≈ k²/2)
p_ca = a_ca * v_ca                         # rises linearly

# ── Build Plotly figure ───────────────────────────────────────────────────────
COLORS = {
    "cp_vel":  "#00C2FF",   # cyan  – constant power velocity
    "ca_vel":  "#FF6B6B",   # coral – constant accel velocity
    "cp_acc":  "#00C2FF",
    "ca_acc":  "#FF6B6B",
    "cp_pwr":  "#A78BFA",   # violet
    "ca_pwr":  "#FB923C",   # orange
    "grid":    "rgba(255,255,255,0.08)",
    "bg":      "#0F172A",
    "paper":   "#0F172A",
    "text":    "#E2E8F0",
}

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.07,
    subplot_titles=(
        "🚀 Velocity  (m/s)",
        "📉 Acceleration  (m/s²)",
        "⚡ Power  (W  per  kg)",
    ),
)

# — Velocity —
fig.add_trace(go.Scatter(
    x=t, y=v_cp, name="Const. Power  v = k√t",
    line=dict(color=COLORS["cp_vel"], width=3),
    hovertemplate="t=%{x:.1f}s<br>v=%{y:.2f} m/s",
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=t, y=v_ca, name="Const. Acceleration  v = at",
    line=dict(color=COLORS["ca_vel"], width=2, dash="dash"),
    hovertemplate="t=%{x:.1f}s<br>v=%{y:.2f} m/s",
), row=1, col=1)

# marker at target point (constant power)
fig.add_trace(go.Scatter(
    x=[target_time], y=[target_speed],
    mode="markers+text",
    marker=dict(color=COLORS["cp_vel"], size=10, symbol="circle"),
    text=[f"  {target_speed} m/s @ {target_time}s"],
    textposition="middle right",
    textfont=dict(color=COLORS["text"], size=11),
    showlegend=False,
    hoverinfo="skip",
), row=1, col=1)

# — Acceleration —
fig.add_trace(go.Scatter(
    x=t, y=a_cp, name="Const. Power  a = k/(2√t)",
    line=dict(color=COLORS["cp_acc"], width=3),
    showlegend=False,
    hovertemplate="t=%{x:.1f}s<br>a=%{y:.3f} m/s²",
), row=2, col=1)

fig.add_trace(go.Scatter(
    x=t, y=a_ca, name="Const. Acceleration",
    line=dict(color=COLORS["ca_acc"], width=2, dash="dash"),
    showlegend=False,
    hovertemplate="t=%{x:.1f}s<br>a=%{y:.3f} m/s²",
), row=2, col=1)

# — Power —
fig.add_trace(go.Scatter(
    x=t, y=p_cp, name="Const. Power  P = k²/2",
    line=dict(color=COLORS["cp_pwr"], width=3),
    fill="tozeroy",
    fillcolor="rgba(167,139,250,0.12)",
    hovertemplate="t=%{x:.1f}s<br>P=%{y:.2f} W/kg",
), row=3, col=1)

fig.add_trace(go.Scatter(
    x=t, y=p_ca, name="Const. Accel  P = a·v",
    line=dict(color=COLORS["ca_pwr"], width=2, dash="dash"),
    fill="tozeroy",
    fillcolor="rgba(251,146,60,0.10)",
    hovertemplate="t=%{x:.1f}s<br>P=%{y:.2f} W/kg",
), row=3, col=1)

# — Layout —
fig.update_layout(
    height=780,
    paper_bgcolor=COLORS["paper"],
    plot_bgcolor=COLORS["bg"],
    font=dict(color=COLORS["text"], family="Inter, sans-serif", size=12),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right",  x=1,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
    ),
    margin=dict(l=60, r=30, t=80, b=40),
    hovermode="x unified",
)

for row in [1, 2, 3]:
    fig.update_xaxes(
        gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
        row=row, col=1,
    )
    fig.update_yaxes(
        gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
        row=row, col=1,
    )

fig.update_xaxes(title_text="Time (s)", row=3, col=1)

# ── Render ────────────────────────────────────────────────────────────────────
st.plotly_chart(fig, width='stretch')

# ── Key insight callouts ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        f"**Constant k** = {k:.3f} m·s⁻³/²\n\n"
        r"Encodes the engine's power-to-mass ratio. "
        "Higher k → faster acceleration throughout."
    )

with col2:
    st.success(
        "**Constant-power advantage**\n\n"
        "Power stays flat (purple band). The engine always works at 100% — "
        "acceleration merely redistributes from early to late."
    )

with col3:
    p_ca_end = a_const * target_speed
    p_cp_val = round((k ** 2) / 2, 2)
    st.warning(
        f"**Constant-acceleration cost**\n\n"
        f"Needs **{p_ca_end:.1f} W/kg** at t = {target_time}s, "
        f"vs only **{p_cp_val:.2f} W/kg** at constant power. "
        "That's why real vehicles can't sustain constant acceleration."
    )

# ── Equation recap ────────────────────────────────────────────────────────────
with st.expander("📚 Equations at a glance"):
    st.markdown("**Constant Power**")
    st.latex(r"v(t) = k\sqrt{t}, \qquad a(t) = \frac{k}{2\sqrt{t}}, \qquad P = \frac{k^2}{2} \text{ (per unit mass)}")
    st.markdown("**Constant Acceleration baseline**")
    st.latex(r"v(t) = at, \qquad a = \text{const}, \qquad P(t) = a \cdot v = a^2 t \;\nearrow")