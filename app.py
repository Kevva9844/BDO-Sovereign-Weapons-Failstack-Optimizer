import streamlit as st
from buy_stack_value import fail_stack_buy_value
import requests

def get_misc_price(region):
    url = f'https://api.arsha.io/v2/{region}/item?id=44195,16001,16004,721003,4998,8411,44364,4918,65319,820979,820934,767102&lang=en'
    response = requests.get(url)
    data = response.json()
    prices = {item['name']: item['lastSoldPrice'] for item in data}
    prices['Mass of Pure Magic'] = 500000
    return prices

@st.cache_data
def calculate_all_failstack_tables(region):
    misc_price = get_misc_price(region)
    S = fail_stack_buy_value(True, region)
    bonus = 5
    base_rate = [0.0855, 0.0412, 0.02, 0.0091, 0.00469, 0.00273, 0.0016, 0.001075, 0.000485, 0.000242]
    max_agris = [3, 5, 10, 20, 30, 35, 50, 75, 165, 330]
    cron_amount = [0, 320, 560, 780, 970, 1350, 1550, 2250, 2760, 3920]
    cron_price = 3000000
    max_level = 10
    I = [2,3,4,5,6,7,8,9,10,11]

    def probability(base_rate, rate_soft_cap, fixed):
        p = base_rate
        result = [p]
        for _ in range(313):
            if p == 1:
                return result
            elif fixed:
                return [base_rate] * 314
            elif p >= 0.9:
                p = 0.9
            elif p >= rate_soft_cap:
                p += 0.02 * base_rate
            else:
                p += 0.1 * base_rate
            result.append(p)
        return result

    def loss(level):
        if level == 0:
            return misc_price['Memory Fragment'] * 20
        else:
            return misc_price['Memory Fragment'] * 20 + min_V[level-1]

    def cost(level):
        return misc_price['Primordial Black Stone']

    def cron_loss(level):
        return misc_price['Memory Fragment'] * 20

    def cron_cost(level):
        return misc_price['Primordial Black Stone'] + cron_amount[level] * cron_price

    V, CV, min_V, cron_costs, full_tables = [], [], [], [], []

    for level in range(max_level):
        P = probability(base_rate[level], 0.7, False)
        L = loss(level)
        C = cost(level)
        CL = cron_loss(level)
        CC = cron_cost(level)
        V.append([[C]])
        CV.append([[C]] if level != 0 else None)
        for agris in range(max_agris[level]):
            V[level].append([])
            if level != 0:
                CV[level].append([])
            min_val = min(V[level][agris])
            for stack in range(300 - I[level] + 1):
                if level == 0:
                    V[level][agris + 1].append(C + S[stack] + (1 - P[stack + bonus]) * L)
                else:
                    V[level][agris + 1].append(C + S[stack] + (1 - P[stack + bonus]) * (L + max(0, min_val * 1.01 - S[stack + I[level]])))
            if level != 0:
                for stack in range(300):
                    if level <= 1:
                        loss_term = CL
                    else:
                        loss_term = CL + max(0, min_val * 1.01 - S[stack + 1])
                    CV[level][agris + 1].append(CC + S[stack] + (1 - P[stack + bonus]) * loss_term)
        min_var = min(V[level][-1])
        if level != 0:
            min_var = min(min_var, min(CV[level][-1]))
        min_V.append(min_var)
        cron_costs.append(CC)
        full_tables.append((V[level], CV[level], max_agris[level], CC, base_rate[level], P))
    return full_tables

# --- Streamlit UI ---
st.set_page_config(layout="centered")

col1, col2 = st.columns([1, 6])
with col1:
    region = st.selectbox("Region", ["SEA", "NA", "EU"], index=0, key="region_select", label_visibility="collapsed")
with col2:
    st.title("🔥 BDO Sovereign Weapons Failstack Optimizer")

level_map = {
    0: "1 - PRI", 1: "2 - DUO", 2: "3 - TRI", 3: "4 - TET", 4: "5 - PEN",
    5: "6 - HEX", 6: "7 - SEP", 7: "8 - OCT", 8: "9 - NOV", 9: "10 - DEC"
}
reverse_level_map = {v: k for k, v in level_map.items()}
level_choice = st.selectbox("Choose enhancement level:", list(level_map.values()))
level = reverse_level_map[level_choice]

full_tables = calculate_all_failstack_tables(region)
V, CV, max_agris, this_cron_cost, base_rate_level, P_table = full_tables[level]
misc_price = get_misc_price(region)
S = fail_stack_buy_value(True, region)

reversed_agris = st.number_input("Agris count:", min_value=0, max_value=max_agris, step=1)
agris = max_agris - reversed_agris
agris_used = reversed_agris

fs_table = V[agris]
cv_table = CV[agris] if level != 0 else None

if level == 0:
    exact_cost_internal = min(fs_table)
    best_stack = fs_table.index(exact_cost_internal)
    cost_source = "V"
else:
    v_min = min(fs_table)
    cv_min = min(cv_table)
    if v_min <= cv_min:
        exact_cost_internal = v_min
        best_stack = fs_table.index(v_min)
        cost_source = "V"
    else:
        exact_cost_internal = cv_min
        best_stack = cv_table.index(cv_min)
        cost_source = "CV"

# Calculate real paid costs
base_cost = misc_price['Primordial Black Stone']
fs_cost = S[best_stack]
cron_only = this_cron_cost - base_cost if level != 0 else 0
display_cost = base_cost + fs_cost + cron_only
repair_cost = agris_used * misc_price['Memory Fragment'] * 20 if agris_used >= 1 else 0
cumulative_cost = display_cost + agris_used * cron_only + repair_cost

# Display FS & Cost
st.markdown(f"<h3>Best Failstack: <span style='color:#00cc88'>{best_stack}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3>Enhancement Cost: <span style='color:#ffaa00'>{int(display_cost):,} silver</span></h3>", unsafe_allow_html=True)

# Total + Cron/Repair
st.markdown(f"<h4>Total Cost with {agris_used} Agris used: <span style='color:#ffaa00'>{int(cumulative_cost):,} silver</span></h4>", unsafe_allow_html=True)
if level != 0 and agris_used >= 1:
    cron_total = agris_used * cron_only
    st.markdown(f"<p style='margin-left:20px'>+ Cron Cost: {int(cron_total):,} silver</p>", unsafe_allow_html=True)
if agris_used >= 1:
    st.markdown(f"<p style='margin-left:20px'>+ Repair Cost (Memory Fragments x20 × {agris_used}): {int(repair_cost):,} silver</p>", unsafe_allow_html=True)

# Cost Breakdown
st.markdown("#### Cost Breakdown")
st.markdown(f"- Base Material Cost: `{int(base_cost):,}` silver")
st.markdown(f"- Failstack Build Cost: `{int(fs_cost):,}` silver")
if level != 0:
    st.markdown(f"- Cron Stone Cost: `{int(cron_only):,}` silver")

# FS Nearby
st.markdown("### Nearby Failstack Costs (±3):")
for i in range(max(0, best_stack - 3), min(314, best_stack + 4)):
    fs_build_cost = S[i]
    tag = "← best" if i == best_stack else ""
    st.markdown(f"FS {i}: {int(fs_build_cost):,} silver {tag}")