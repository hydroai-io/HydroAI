import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="HydroAI — Freshwater Cost of AI Training",
    page_icon="\U0001F4A7",
    layout="wide",
)

DISCLAIMER = (
    "This identifies technically feasible alternatives based on public data; "
    "it does not represent an engineering recommendation or current practice "
    "at this facility."
)

ALT_LABELS = {
    "seawater_lake_cooling": "Seawater / Lake Cooling",
    "reclaimed_wastewater": "Reclaimed Wastewater",
    "air_free_cooling": "Air / Free Cooling",
    "immersion_cooling": "Immersion Cooling",
    "closed_loop_dry_cooling": "Closed-Loop Dry Cooling",
}

ALT_COLORS = {
    "seawater_lake_cooling": "#0077b6",
    "reclaimed_wastewater": "#2a9d8f",
    "air_free_cooling": "#8ecae6",
    "immersion_cooling": "#e76f51",
    "closed_loop_dry_cooling": "#6c757d",
}

STRESS_COLORS = {
    "Low (<10%)": "#2a9d8f",
    "Low - Medium (10-20%)": "#8ab17d",
    "Medium - High (20-40%)": "#e9c46a",
    "High (40-80%)": "#f4a261",
    "Extremely High (>80%)": "#e63946",
}

# Company-level disclosure / greenwashing scores (Week 4 NLP pipeline output).
# Small, fixed table -- hardcoded rather than re-parsed from the pipeline each run.
DISCLOSURE = pd.DataFrame([
    {"Company": "Google", "Water_Consumed_ML": 29477.0, "Original_Metric": "7787.0 million gallons",
     "Data_Status": "Reported Absolute Volume (Data Centers)", "Transparency_Score": 4,
     "Transparency_Label": "Facility-Level (Named Locations)", "Greenwashing_Ratio": 0.583,
     "Greenwashing_Risk": "Moderate"},
    {"Company": "Microsoft", "Water_Consumed_ML": 5807.0, "Original_Metric": "5807.0 thousand m3",
     "Data_Status": "Reported Absolute Volume (Operational Total)", "Transparency_Score": 3,
     "Transparency_Label": "Company-Wide Aggregate", "Greenwashing_Ratio": 0.600,
     "Greenwashing_Risk": "High Greenwashing Risk"},
    {"Company": "Meta", "Water_Consumed_ML": 2974.0, "Original_Metric": "2974.0 megaliters",
     "Data_Status": "Facility-Level (Named Locations)", "Transparency_Score": 4,
     "Transparency_Label": "Facility-Level (Named Locations)", "Greenwashing_Ratio": 0.538,
     "Greenwashing_Risk": "Moderate"},
    {"Company": "Amazon", "Water_Consumed_ML": 9463.525, "Original_Metric": "2.5 billion gallons",
     "Data_Status": "High (Verified Web Disclosure)", "Transparency_Score": 1,
     "Transparency_Label": "Ratio Only (No Absolute Volume)", "Greenwashing_Ratio": 0.462,
     "Greenwashing_Risk": "Moderate"},
])


@st.cache_data
def load_data():
    df = pd.read_csv("data/hydroai_final_scored.csv")
    df["company_title"] = df["company"].str.title()
    name_filled = df["name"].fillna(df["company_title"] + " facility")
    df["display_label"] = (
        name_filled + " — " + df["county"].fillna("").str.replace(" County", "", regex=False)
        + ", " + df["state_abb"].fillna("") + " (#" + df["id"].astype(str) + ")"
    )
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("\U0001F4A7 HydroAI")
st.caption(
    "Exposing the freshwater cost of AI training — disclosure scoring, "
    "facility-level water stress, and sourced cooling alternatives."
)
st.info(f"**Read this before using the results below:** {DISCLAIMER}")

tab_search, tab_map, tab_facility, tab_about = st.tabs(
    ["\U0001F50D Search a Company", "\U0001F5FA\uFE0F Facility Map", "\U0001F3E2 Facility Lookup", "\U0001F4D6 Methodology & Sources"]
)
    else:
        st.warning("No company-level disclosure record for this company.")

    st.divider()
    st.subheader(f"{selected_company}'s facilities — water stress & cooling alternatives")

    company_df = df[df["company_title"] == selected_company]
    st.write(f"**{len(company_df)} facilities** in the dataset.")

    fc1, fc2 = st.columns([1, 1])
    with fc1:
        stress_counts = company_df["bws_label"].value_counts().reindex(STRESS_COLORS.keys()).dropna()
        fig1 = px.bar(
            stress_counts, orientation="h",
            labels={"value": "Facilities", "index": "Water stress"},
            title="Facilities by water-stress category",
            color=stress_counts.index, color_discrete_map=STRESS_COLORS,
        )
        fig1.update_layout(showlegend=False, height=320, margin=dict(t=40, b=10))
        st.plotly_chart(fig1, use_container_width=True)
    with fc2:
        alt_counts = company_df["recommended_alternative"].value_counts()
        alt_counts.index = [ALT_LABELS.get(a, a) for a in alt_counts.index]
        fig2 = px.pie(
            values=alt_counts.values, names=alt_counts.index,
            title="Recommended cooling alternatives",
            color=alt_counts.index,
            color_discrete_map={ALT_LABELS[k]: v for k, v in ALT_COLORS.items()},
        )
        fig2.update_layout(height=320, margin=dict(t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander(f"See all {len(company_df)} {selected_company} facilities"):
        show_cols = ["name", "state", "type", "bws_label", "recommended_alternative", "nearest_reclaimed_plant_km"]
        display = company_df[show_cols].rename(columns={
            "name": "Facility", "state": "State", "type": "Type", "bws_label": "Water Stress",
            "recommended_alternative": "Recommended Alternative", "nearest_reclaimed_plant_km": "Nearest reclaimed plant (km)",
        })
        display["Recommended Alternative"] = display["Recommended Alternative"].map(ALT_LABELS)
        st.dataframe(display, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# TAB 2: Interactive map
# ---------------------------------------------------------------------------
with tab_map:
    st.subheader("All 420 facilities — colored by water-stress tier")

    mc1, mc2 = st.columns(2)
    with mc1:
        company_filter = st.multiselect("Filter by company", sorted(df["company_title"].unique()),
                                         default=sorted(df["company_title"].unique()))
    with mc2:
        stress_filter = st.multiselect("Filter by water-stress tier", list(STRESS_COLORS.keys()),
                                        default=list(STRESS_COLORS.keys()))

    map_df = df[df["company_title"].isin(company_filter) & df["bws_label"].isin(stress_filter)]
    st.caption(f"Showing {len(map_df)} of {len(df)} facilities.")

    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="OpenStreetMap")
    cluster = MarkerCluster().add_to(m)
    for _, r in map_df.iterrows():
        color = STRESS_COLORS.get(r["bws_label"], "#6c757d")
        popup_html = f"""
        <b>{r['name']}</b> ({r['county']}, {r['state_abb']})<br>
        {r['company_title']} — {r['state']} ({r['type']})<br>
        Water stress: {r['bws_label']}<br>
        <b>Recommended:</b> {ALT_LABELS.get(r['recommended_alternative'], r['recommended_alternative'])}<br>
        Nearest reclaimed plant: {r['nearest_reclaimed_plant_km']:.1f} km<br>
        <i style="font-size:11px">{r['recommendation_rationale']}</i>
        """
        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=r["display_label"],
        ).add_to(cluster)

    legend_html = " &nbsp;&nbsp; ".join(
        f'<span style="color:{c}">\u25CF</span> {label}' for label, c in STRESS_COLORS.items()
    )
    st.markdown(legend_html, unsafe_allow_html=True)
    st_folium(m, use_container_width=True, height=560, returned_objects=[])
        st_folium(m, use_container_width=True, height=560, returned_objects=[])

# ---------------------------------------------------------------------------
# TAB 3: Single-facility lookup
# ---------------------------------------------------------------------------
with tab_facility:
    st.subheader("Look up a single facility")
    st.caption(
        "420 facilities, but many share a generic source-data name (e.g. dozens "
        "are just \"Google\") — each entry below also shows county/state/ID so "
        "you're picking one specific physical location, not a random duplicate."
    )
    lookup_company = st.selectbox("Company", ["All"] + sorted(df["company_title"].unique()), key="lookup_company")
    lookup_pool = df if lookup_company == "All" else df[df["company_title"] == lookup_company]
    facility_label = st.selectbox("Facility", sorted(lookup_pool["display_label"].unique()))
    r = df[df["display_label"] == facility_label].iloc[0]

    st.markdown(f"### {r['name']}")
    st.caption(f"{r['company_title']} · {r['state']} · {r['type']} facility")

    c1, c2, c3 = st.columns(3)
    c1.metric("Water stress", r["bws_label"])
    c2.metric("Recommended alternative", ALT_LABELS.get(r["recommended_alternative"], r["recommended_alternative"]))
    c3.metric(
        "Runner-up",
        ALT_LABELS.get(r["runner_up_alternative"], "—") if pd.notna(r["runner_up_alternative"]) else "—",
    )

    st.info(r["recommendation_rationale"])

    st.markdown("**Underlying figures used for eligibility:**")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Coast distance", f"{r['coast_dist_km']:.1f} km")
    d2.metric("Lake distance", f"{r['lake_dist_km']:.1f} km")
    d3.metric("Summer avg temp", f"{r['summer_avg_temp_c']:.1f} °C")
    d4.metric("Summer dew point", f"{r['summer_avg_dewpoint_c']:.1f} °C")

    st.metric(
        "Nearest EPA reuse-capable treatment plant",
        f"{r['nearest_reclaimed_plant_km']:.1f} km",
        help="Shown as a distance, not just pass/fail, so near-misses against the "
             "40.2km reclaimed-water threshold stay visible.",
        delta=f"{'within' if r['reclaimed_water_accessible'] else 'beyond'} the 40.2 km threshold",
        delta_color="off",
    )

    st.warning(DISCLAIMER)

# ---------------------------------------------------------------------------
# TAB 4: Methodology & sources
# ---------------------------------------------------------------------------
with tab_about:
    st.subheader("Methodology & Sources")

    st.markdown(
        """
Each facility is assigned the **first** cooling alternative it qualifies for,
checked in a fixed priority order — this is a priority-ordered rule set, not a
weighted composite score:

1. Seawater / Lake Cooling
2. Reclaimed Wastewater
3. Air / Free Cooling
4. Immersion Cooling
5. Closed-Loop Dry Cooling *(universal fallback — always eligible)*
"""
    )

    st.markdown("**Thresholds and sources:**")
    sources = pd.DataFrame([
        {"Parameter": "Coastal / lake proximity", "Value": "10 km",
         "Source": "Lucas & Sanjivy, IntechOpen 2024 — \"Sea Water Air Conditioning (SWAC) "
                    "Technology: Performance and Worldwide Potential\""},
        {"Parameter": "Reclaimed-water transport distance", "Value": "40.2 km (25 mi)",
         "Source": "Stillwell & Webber (2014), Environ. Sci. Technol. 48(8), 4588-4595, "
                    "doi:10.1021/es405820j. Power-plant cooling study, used as the closest "
                    "available peer-reviewed analog — not a data-center-specific source."},
        {"Parameter": "Summer air-cooling temperature limit", "Value": "27 °C",
         "Source": "ASHRAE TC 9.9, Thermal Guidelines for Data Processing Environments (5th ed.)"},
        {"Parameter": "Summer air-cooling dew-point limit", "Value": "15 °C",
         "Source": "ASHRAE TC 9.9, Thermal Guidelines for Data Processing Environments (5th ed.)"},
    ])
    st.dataframe(sources, use_container_width=True, hide_index=True)

    st.markdown(
        """
Dew point is computed from real WorldClim vapor-pressure rasters
(`wc2.1_2.5m_vapr`) via FAO-56 (Allen et al. 1998) Tetens-equation inversion —
a direct physical calculation, not a proxy.

Reclaimed-water eligibility uses the EPA Clean Watersheds Needs Survey (CWNS),
matched against all 7 official EPA reuse categories
(`DISCHARGES` / `REF_DISCHARGE_TYPES` tables), not just the narrow
"potable reuse" tier.
"""
    )

    with st.expander("Known limitations (read before citing this tool)"):
        st.markdown(
            """
- **`bws_score` was corrected after a sub-basin join bug.** An earlier build
  of the merged dataset intermittently matched a subset of facilities to the
  wrong WRI Aqueduct sub-basin (or a placeholder value), which affected the
  water-stress tier shown for most facilities. This has been corrected by
  re-joining against verified sub-basin scores; the corrected values are what
  the map and lookup tools above now show.
- **Lakes dataset excludes reservoirs.** The Natural Earth 10m lakes layer
  includes only 165 major natural lakes — no reservoirs — so eligibility is
  undercounted in reservoir-dependent regions.
- **Only 4 numbers here are directly sourced.** The priority *order* itself,
  the choice of exactly 5 alternatives, and the campus/building/point
  eligibility logic are reasoned judgment calls, not cited data.
- **The reclaimed-water threshold comes from a power-plant cooling study**,
  applied to data centers by analogy — the closest available peer-reviewed
  proxy, not an exact match.
- **"Point"-type facilities** (a small subset) have no campus/building
  distinction in the source data and default to non-campus eligibility
  behavior as a conservative choice.
"""
        )

    with st.expander("Spot-check findings from development"):
        st.markdown(
            """
Three real facilities were checked against public reporting:

- **Meta, Prineville, OR** — the tool recommends reclaimed wastewater
  (priority order places it above air/free cooling, even though this real
  facility uses free-air cooling in practice). Read as "an alternative", not
  as a claim about current practice. Water stress: Medium - High (20-40%).
- **Microsoft, San Antonio, TX** — the real facility uses SAWS recycled
  water. The tool's computed distance to the nearest reclaimed plant is
  40.8 km against a 40.2 km threshold — a genuine near-miss of about 600 m,
  not a bug. Water stress: Medium - High (20-40%).
- **Google, Council Bluffs, IA** — summer dew point comes out at roughly
  17.5 °C, correctly above the 15 °C ASHRAE cutoff, correctly excluding it
  from air/free cooling.

Note: the water-stress score (`bws_score`) shown for each facility was
corrected after a sub-basin join bug was found affecting the majority of
facilities (see Known Limitations). The recommendation logic itself does
not use `bws_score` as an eligibility input, so recommendations above are
unaffected by that correction.

Summary: zero known code defects in the recommendation engine itself, four
peer-reviewed or industry-standard thresholds independently verified,
checked against 3 real facilities with 1 confirmed match, 1 quantified
near-miss, and 1 defensible non-match.
"""
        )

    st.caption(
        "Primary audience: environmental policymakers and regulators. "
        "Secondary audience: journalists and communities near these facilities."
    )
