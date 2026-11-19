# India youth employment

Interactive simulator and model of India's graduate jobs gap: young entrants, job creation, graduate unemployment, under-employment and the skills gap, projected to 2035.

## Contents

| Path | What it is |
|---|---|
| `index.html` | Self-contained interactive dashboard. Open it in a browser, or serve it with GitHub Pages. |
| `model/india_youth_jobs_skills_gap_model.py` | Python stock-flow model, fact base, scenarios, Monte Carlo and chart. Run `python3 model/india_youth_jobs_skills_gap_model.py` (needs numpy, pandas, matplotlib). |
| `outputs/` | Model outputs: fact base with sources and evidence tiers, scenario results and summary, Monte Carlo ranges, chart. |

## Headline results (model, 2024 to 2035)

- Graduate-youth unemployment starts at 29.1% and reaches about 25% under current trends.
- Faster job creation (8% a year growth in hiring) brings it to about 13%. Skills reform alone leaves unemployment unchanged and only trims under-employment.
- Expanding enrolment toward the 50% GER goal with no extra jobs raises it to about 36%.
- Monte Carlo range for 2035: roughly 10% to 35%.

## Data sources

PLFS Annual Report 2025 and monthly bulletins (MoSPI); AISHE 2021-22 and 2023-24 (Ministry of Education); Economic Survey 2023-24; ILO and IHD India Employment Report 2024; State of Working India (Azim Premji University); India Skills Report (Wheebox, employability trend only). Every input in `outputs/facts_base.csv` carries a source and an evidence tier (A official, B research, C private, M modelled).

## Caveats

- Under-employment (graduates working below their qualification) is modelled, not measured: no official series exists, and employability is used as an upper-bound proxy.
- Graduates completing a degree each year and the share entering the labour force are derived from enrolment and calibrated to State of Working India figures.
- Several figures were read from press-note extracts and secondary coverage. Verify headline numbers against the original MoSPI and Ministry of Education tables before citing.
