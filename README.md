
#  HydroAI — Auditing the Freshwater Cost of AI

 **How much water does it take to train an AI model — and is anyone being honest about it?**

HydroAI is an open-source research tool that uses an NLP pipeline to extract and score water-use disclosures from major AI/cloud providers, maps their data centers against global water stress indices, and generates location-specific freshwater alternatives for policymakers and communities.

Built as part of the **NSF-funded altREU Summer Research Program** at Portland State University.

---

##  Why This Matters

Training large AI models consumes enormous quantities of freshwater for data center cooling — yet transparency is almost nonexistent:

- Of the 4 major hyperscale AI providers (Google, Microsoft, Amazon, Meta), only **Google and Meta** disclose water use at the facility level
- Microsoft and Amazon report only **company-wide aggregates**
- Across 4,000+ U.S. data centers, **fewer than a third** measure water consumption at all
- **No public tool** currently aggregates this data into a format journalists, policymakers, or communities can use

HydroAI fills that gap.

---

##  What It Does

Given a major AI model or cloud provider, HydroAI returns:

-  **Estimated freshwater training footprint** — with cited source ranges even where exact data isn't published
-  **Transparency score** — how openly each company discloses its water use (non-disclosure is itself scored)
-  **Water stress rating** — cross-referenced against the WRI Aqueduct 4.0 global water risk index
-  **Actionable cooling alternative** — one specific, location-feasible recommendation (e.g., seawater cooling, reclaimed water, air-side economization) based on coastline distance, temperature, and local infrastructure

---

##  Tech Stack

| Component | Tools |
|---|---|
| NLP Pipeline | Python, spaCy / HuggingFace Transformers |
| Data Sources | WRI Aqueduct 4.0, corporate sustainability PDFs |
| Geospatial Analysis | GeoPandas, WRI Aqueduct 4.0 water stress index |
| Rule-Based Recommendation | Custom decision system validated against real-world precedents |
| Web App | Streamlit (publicly deployed) |
| Version Control | GitHub |

---

##  Repository Structure

```
HydroAI/
├── data/
│   ├── raw/               # Raw source data (see note below)
│   └── processed/         # Cleaned datasets ready for pipeline
├── notebooks/
│   └── HydroAI_Week2_DataCleaning.ipynb
├── src/                   # NLP pipeline and scoring modules
└── app/                   # Streamlit web application
```

---

##  Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
git clone https: https://github.com/hydroai-io/HydroAI.git
cd HydroAI
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app/main.py
```

---

##  Note on Raw Data

The raw WRI Aqueduct 4.0 dataset (~200 MB) is not included in this repository due to GitHub's file size limits. To reproduce our cleaning pipeline:

1. Download the Aqueduct 4.0 Current and Future Global Maps Data from 
   [wri.org/data/aqueduct-water-risk-atlas](https://www.wri.org/data/aqueduct-water-risk-atlas)
   (column definitions available at the   [Aqueduct 4.0 Data Dictionary (https://github.com/wri/Aqueduct40/blob/master/data_dictionary_water-risk-atlas.md))
2. Place the file 'Aqueduct40_baseline_annual_y2023m07d05.csv' in 'data/raw/'
3. Run 'notebooks/HydroAI_Week2_DataCleaning.ipynb` to reproduce 'data/processed/aqueduct_water_stress_usa_2023.csv'

The cleaned, filtered version used by HydroAI is already included in 'data/processed/'

---

##  Research Timeline

| Week | Milestone |
|---|---|
| 1–2 | Data collection & cleaning |
| 3–4 | NLP pipeline + greenwashing classifier |
| 5 | Geospatial mapping |
| 6 | Rule-based recommendation system |
| 7–8 | Streamlit app & deployment |
| 9 | Validation & presentation |

**Target deployment: August 2026**

---

##  About

Built by Tanvi Patel — sophomore BS Data Science student at Portland State University, researching the intersection of NLP, environmental accountability, and AI infrastructure.

*Research conducted through the altREU program, supported by the National Science Foundation.*

---


