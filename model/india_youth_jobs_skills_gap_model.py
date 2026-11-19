#!/usr/bin/env python3
"""
India: youth labour-force entry vs job creation, graduate unemployment,
underemployment and the skills gap  --  fact base + stock-flow model (2024-2035)

Run:  python3 india_youth_jobs_skills_gap_model.py
Outputs (in ./output_youth_jobs_gap/):
    facts_base.csv          every input fact with value, source, URL, evidence tier
    scenario_results.csv    year-by-year results for each scenario
    scenario_summary.csv    2035 outcomes + Monte-Carlo ranges
    youth_jobs_skills_gap.png

EVIDENCE TIERS
  A  Official statistics (MoSPI/NSO PLFS, Ministry of Education AISHE, Ministry of Finance Economic Survey)
  B  International-organisation / institutional research (ILO-IHD India Employment Report 2024,
     Azim Premji University State of Working India)
  C  Private survey (Wheebox India Skills Report) -- used only for the employability *trend*
  M  Modelling assumption or value derived by this script (flagged, varied in sensitivity runs)
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "output_youth_jobs_gap"
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------
# 1. FACT BASE
# ----------------------------------------------------------------------------
PLFS = "https://www.mospi.gov.in/uploads/latestReleases/latest_release_1774607827733_3e8964a9-268b-4cc9-ad65-cfc8a9e32f08_Press_note_AR_PLFS_2025_23032025_V2.1_26032026_final.pdf"
AISHE21 = "https://education.gov.in/sites/upload_files/mhrd/files/statistics-new/AISHE%20Book_2021-22_4.pdf"
AISHE24 = "https://pib.gov.in (Ministry of Education release, 8 July 2026: AISHE 2022-23 & 2023-24)"
ES = "Economic Survey 2023-24, Ministry of Finance (tabled 22 July 2024)"
ILO = "ILO & Institute for Human Development, India Employment Report 2024 (26 Mar 2024)"
SWI = "Azim Premji University, State of Working India (graduate unemployment chapter)"
ISR = "Wheebox/ETS India Skills Report 2025 & 2026"

facts = [
 # id, description, value, unit, source, url/ref, tier
 ("plfs_ur_all", "Unemployment rate, 15+, usual status, 2025", 3.1, "%", "PLFS Annual Report 2025 (NSO/MoSPI)", PLFS, "A"),
 ("plfs_ur_youth_2025", "Youth (15-29) unemployment rate, usual status, 2025", 9.9, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_ur_youth_2024", "Youth (15-29) unemployment rate, usual status, 2024", 10.3, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_ur_youth_urban", "Urban youth unemployment rate, usual status, 2025", 13.6, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_ur_youth_rural", "Rural youth unemployment rate, usual status, 2025", 8.3, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_ur_educated", "Unemployment rate, 15+, secondary education and above, usual status, 2025", 6.5, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_ur_educated_2024", "Same, 2024", 7.0, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_neet_15_29", "Youth 15-29 not in employment, education or training (NEET), 2025", 25.0, "%", "PLFS Annual Report 2025 (as reported in coverage of the report)", PLFS, "A"),
 ("plfs_neet_15_24", "NEET, age 15-24, 2025", 21.0, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_vocational_15_29", "Youth 15-29 with formal vocational/technical training", 5.0, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_vocational_15_59", "Persons 15-59 with formal vocational/technical training", 4.2, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_employed", "Persons employed, 15+, 2025", 61.6, "crore", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_agri_share", "Agriculture share of employment, 2025", 43.0, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_regular_share", "Regular wage/salaried share of employment, 2025", 23.6, "%", "PLFS Annual Report 2025", PLFS, "A"),
 ("plfs_cws_youth_apr26", "Youth 15-29 unemployment, current weekly status, Apr 2026", 15.3, "%", "PLFS Monthly Bulletin Apr 2026 (MoSPI)", "https://pib.gov.in/PressReleasePage.aspx?PRID=2261386", "A"),
 ("plfs_cws_youth_jun26", "Youth 15-29 unemployment, current weekly status, Jun 2026", 16.2, "%", "PLFS Monthly Bulletin Jun 2026 (MoSPI)", "https://www.mospi.gov.in", "A"),
 ("plfs_cws_urban_youth_sep26", "Urban youth 15-29 unemployment, CWS, Sep 2026", 19.0, "%", "PLFS Monthly Bulletin Sep 2026 (MoSPI)", "https://www.mospi.gov.in", "A"),
 ("aishe_enrol_2014", "Higher-education enrolment 2014-15", 3.42, "crore", "AISHE (Ministry of Education)", AISHE24, "A"),
 ("aishe_enrol_2223", "Higher-education enrolment 2022-23", 4.46, "crore", "AISHE 2022-23", AISHE24, "A"),
 ("aishe_enrol_2324", "Higher-education enrolment 2023-24", 4.50, "crore", "AISHE 2023-24", AISHE24, "A"),
 ("aishe_ger", "Gross Enrolment Ratio (18-23), 2023-24", 30.0, "%", "AISHE 2023-24", AISHE24, "A"),
 ("aishe_ug_share", "Undergraduate share of enrolment, 2023-24", 76.8, "%", "AISHE 2023-24 (as summarised by NIEPA ex-professor A. Mehta)", AISHE24, "A"),
 ("aishe_pg_share_2122", "Postgraduate share of enrolment, 2021-22 (latest verified)", 12.1, "%", "AISHE 2021-22", AISHE21, "A"),
 ("es_jobs_needed", "Non-farm jobs to be generated per year until 2030", 78.5, "lakh/yr", ES, "https://www.indiabudget.gov.in/economicsurvey/", "A"),
 ("ilo_lf_additions", "Net annual additions to labour force over next decade", 7.5, "million/yr (7-8)", ILO, "https://www.ilo.org/", "B"),
 ("ilo_unemp_youth_share", "Youth share of all unemployed, 2022", 82.9, "%", ILO, "https://www.ilo.org/", "B"),
 ("ilo_educated_share_unemp_youth", "Secondary+ educated share of unemployed youth, 2022 (35.2% in 2000)", 65.7, "%", ILO, "https://www.ilo.org/", "B"),
 ("ilo_grad_ur", "Graduate (youth) unemployment rate, 2022", 29.1, "%", ILO, "https://www.ilo.org/", "B"),
 ("swi_grads_20_29", "Graduates aged 20-29, 2023", 63.0, "million", SWI, "https://cse.azimpremjiuniversity.edu.in/", "B"),
 ("swi_grads_unemp", "Of whom unemployed", 11.0, "million", SWI, "https://cse.azimpremjiuniversity.edu.in/", "B"),
 ("swi_grad_entrants", "Graduates joining the labour force per year", 5.0, "million/yr", SWI, "https://cse.azimpremjiuniversity.edu.in/", "B"),
 ("swi_jobs_for_grads", "Jobs secured per year by these entrants", 2.8, "million/yr", SWI, "https://cse.azimpremjiuniversity.edu.in/", "B"),
 ("isr_emp_2024", "Graduate employability, India Skills Report 2024 edition", 51.25, "%", ISR, "https://wheebox.com/", "C"),
 ("isr_emp_2025", "Graduate employability, ISR 2025", 54.81, "%", ISR, "https://wheebox.com/", "C"),
 ("isr_emp_2026", "Graduate employability, ISR 2026", 56.35, "%", ISR, "https://wheebox.com/", "C"),
 ("isr_polytechnic", "Employability of polytechnic graduates, ISR 2026", 32.92, "%", ISR, "https://wheebox.com/", "C"),
 ("isr_iti", "Employability of ITI graduates, ISR 2026", 45.95, "%", ISR, "https://wheebox.com/", "C"),
]
FACTS = pd.DataFrame(facts, columns=["id", "description", "value", "unit", "source", "url_or_ref", "tier"])
F = FACTS.set_index("id")["value"].to_dict()

# ----------------------------------------------------------------------------
# 2. DERIVED QUANTITIES (tier M)
# ----------------------------------------------------------------------------
UG_SHARE = F["aishe_ug_share"] / 100
PG_SHARE = F["aishe_pg_share_2122"] / 100       # M: 2023-24 PG share not verified; 2021-22 value used
UG_YEARS, PG_YEARS = 3.3, 2.0                    # M: weighted programme length (3-yr BA/BSc/BCom + 4-yr BTech; 2-yr PG)
ENROL0 = F["aishe_enrol_2324"] * 1e7             # persons
G_OUT0 = ENROL0 * (UG_SHARE / UG_YEARS + PG_SHARE / PG_YEARS)   # graduates completing per year
ENTRANTS0 = F["swi_grad_entrants"] * 1e6
ENTRY_RATE0 = ENTRANTS0 / G_OUT0                 # share of each graduating cohort joining the labour force
CAGR_ENROL = (F["aishe_enrol_2324"] / F["aishe_enrol_2014"]) ** (1 / 9) - 1
GROWTH_LAST = F["aishe_enrol_2324"] / F["aishe_enrol_2223"] - 1

derived = pd.DataFrame([
    ("Graduates completing a degree per year (derived from AISHE enrolment)", G_OUT0 / 1e6, "million/yr", "M"),
    ("Share of a graduating cohort entering the labour force (calibrated to SWI 5.0m entrants)", ENTRY_RATE0 * 100, "%", "M"),
    ("Enrolment CAGR 2014-15 to 2023-24", CAGR_ENROL * 100, "%/yr", "A-derived"),
    ("Enrolment growth 2022-23 to 2023-24", GROWTH_LAST * 100, "%", "A-derived"),
    ("Graduate entrants minus jobs secured per year (SWI)", (F["swi_grad_entrants"] - F["swi_jobs_for_grads"]), "million/yr", "B-derived"),
    ("Net LF additions (ILO 7.5m) vs non-farm jobs needed (Eco Survey 7.85m)", F["es_jobs_needed"] / 10 - F["ilo_lf_additions"], "million/yr difference", "A/B-derived"),
    ("Non-agricultural employed persons, 2025", F["plfs_employed"] * (1 - F["plfs_agri_share"] / 100), "crore", "A-derived"),
], columns=["quantity", "value", "unit", "tier"])

# ----------------------------------------------------------------------------
# 3. STOCK-FLOW MODEL
# ----------------------------------------------------------------------------
# State (graduates aged 20-29 in the labour force): E_g employed in graduate-level roles,
# E_u employed below qualification (underemployed), U unemployed.
# Each year:
#   entrants N = entry_rate * graduates_out(t)          (enrolment-driven supply)
#   hires    H = H0*(1+g)^t, capped at 85% of searchers  (demand-driven; H0 calibrated so 2024 stocks are steady)
#   share of hires in graduate-level roles = kappa * employability(t)   (skills gap -> job quality)
#   ageing out a=10%/yr of every stock (a 10-year age band); discouraged exit d from U
#   upgrading u=5%/yr of E_u moves to E_g
BASE = dict(
    enrol_growth=0.025,      # M: between last-year 0.9% and decade CAGR 3.1%
    hire_growth=0.04,        # M: growth in graduate hiring
    emp_gain_pp=0.010,       # M: employability +1.0pp/yr (ISR 2015-2025 average ~ +2.2pp, test-pool biased)
    emp_cap=0.80,
    kappa=1.0,               # M: share of hires into graduate-level roles relative to employability (upper bound)
    entry_scale=1.0,
    age_out=0.10, discouraged=0.10, upgrade=0.05,
    ur0=F["ilo_grad_ur"] / 100,          # initial graduate-youth UR (ILO)
    U0=F["swi_grads_unemp"] * 1e6,       # initial unemployed graduates (SWI)
)
EMP_KNOWN = {2024: F["isr_emp_2024"] / 100, 2025: F["isr_emp_2025"] / 100, 2026: F["isr_emp_2026"] / 100}
YEARS = list(range(2024, 2036))


def employability(year, p):
    if year in EMP_KNOWN:
        return EMP_KNOWN[year]
    e = EMP_KNOWN[2026] + p["emp_gain_pp"] * (year - 2026)
    return min(e, p["emp_cap"])


def run(**over):
    p = {**BASE, **over}
    a, d, u = p["age_out"], p["discouraged"], p["upgrade"]
    U = p["U0"]
    LF = U / p["ur0"]
    E = LF - U
    eps0 = employability(2024, p)
    Eg, Eu = E * eps0, E * (1 - eps0)
    N0 = ENTRANTS0 * p["entry_scale"]
    H0 = N0 - (a + d) * U                       # calibrated: 2024 unemployment stock is steady
    rows = []
    for t in YEARS:
        k = t - 2024
        enrol = ENROL0 * (1 + p["enrol_growth"]) ** k
        g_out = enrol * (UG_SHARE / UG_YEARS + PG_SHARE / PG_YEARS)
        N = ENTRY_RATE0 * p["entry_scale"] * g_out
        H = min(H0 * (1 + p["hire_growth"]) ** k, 0.85 * (U + N))
        eps = employability(t, p)
        phi = min(1.0, p["kappa"] * eps)
        E = Eg + Eu
        rows.append(dict(year=t, graduates_out_m=g_out / 1e6, entrants_m=N / 1e6, hires_m=H / 1e6,
                         employability=eps, unemployed_m=U / 1e6, employed_grad_level_m=Eg / 1e6,
                         employed_below_qual_m=Eu / 1e6, labour_force_m=(E + U) / 1e6,
                         ur_grad_pct=100 * U / (E + U), underemp_share_pct=100 * Eu / E,
                         mismatch_pct=100 * (U + Eu) / (E + U),    # unemployed + underemployed as % of grad LF
                         entrant_job_gap_m=(N - H) / 1e6))
        U_new = U * (1 - a - d) + N - H
        Eg_new = Eg * (1 - a) + phi * H + u * Eu
        Eu_new = Eu * (1 - a - u) + (1 - phi) * H
        U, Eg, Eu = max(U_new, 0), Eg_new, Eu_new
    return pd.DataFrame(rows)


SCEN = {
    "Business as usual": {},
    "Faster job creation": dict(hire_growth=0.08),
    "Skills reform": dict(emp_gain_pp=0.022),
    "Enrolment push, no extra jobs (NEP 50% GER path)": dict(enrol_growth=0.06),
    "Jobs + skills + steady enrolment": dict(hire_growth=0.08, emp_gain_pp=0.022, enrol_growth=0.04),
}
results = {k: run(**v) for k, v in SCEN.items()}
long = pd.concat([df.assign(scenario=k) for k, df in results.items()], ignore_index=True)
long.round(3).to_csv(f"{OUT}/scenario_results.csv", index=False)

# ----------------------------------------------------------------------------
# 4. MONTE-CARLO UNCERTAINTY (business-as-usual structure, all uncertain inputs varied)
# ----------------------------------------------------------------------------
rng = np.random.default_rng(42)
mc = []
for _ in range(2000):
    df = run(hire_growth=rng.uniform(0.02, 0.08), enrol_growth=rng.uniform(0.01, 0.05),
             emp_gain_pp=rng.uniform(0.005, 0.022), kappa=rng.uniform(0.6, 1.0),
             entry_scale=rng.uniform(0.85, 1.15), discouraged=rng.uniform(0.05, 0.15),
             ur0=rng.uniform(0.20, 0.30))
    last = df.iloc[-1]
    mc.append((last.ur_grad_pct, last.underemp_share_pct, last.mismatch_pct))
mc = pd.DataFrame(mc, columns=["ur_grad_2035", "underemp_2035", "mismatch_2035"])
q = mc.quantile([0.05, 0.5, 0.95])

summ = []
for k, df in results.items():
    l, f0 = df.iloc[-1], df.iloc[0]
    summ.append(dict(scenario=k, ur_grad_2024=f0.ur_grad_pct, ur_grad_2035=l.ur_grad_pct,
                     underemp_share_2024=f0.underemp_share_pct, underemp_share_2035=l.underemp_share_pct,
                     mismatch_2035=l.mismatch_pct, unemployed_grads_2035_m=l.unemployed_m,
                     cumulative_entrants_minus_hires_m=df.entrant_job_gap_m.sum()))
SUMM = pd.DataFrame(summ).round(1)
SUMM.to_csv(f"{OUT}/scenario_summary.csv", index=False)
q.round(1).to_csv(f"{OUT}/monte_carlo_2035_ranges.csv")

FACTS.to_csv(f"{OUT}/facts_base.csv", index=False)
derived.round(2).to_csv(f"{OUT}/derived_quantities.csv", index=False)

# ----------------------------------------------------------------------------
# 5. CHART
# ----------------------------------------------------------------------------
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]   # reference categorical slots 1-5 (validated order)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
fig, ax = plt.subplots(2, 2, figsize=(14, 9.5), facecolor="#fcfcfb")
for a_ in ax.flat:
    a_.set_facecolor("#fcfcfb")

# (a) the observed fact base: unemployment rate by group
a = ax[0, 0]
labs = ["All, 15+", "Educated\n(sec.+, 15+)", "Youth\n15-29", "Urban youth", "Graduate youth\n(ILO, 2022)"]
vals = [F["plfs_ur_all"], F["plfs_ur_educated"], F["plfs_ur_youth_2025"], F["plfs_ur_youth_urban"], F["ilo_grad_ur"]]
cols = ["#a9a8a3"] * 2 + [C[0]] * 2 + [C[1]]
b = a.bar(labs, vals, color=cols, width=0.55)
for r, v in zip(b, vals):
    a.text(r.get_x() + r.get_width() / 2, v + 0.6, f"{v:.1f}%", ha="center", color=INK, fontsize=10)
a.set_title("Unemployment is concentrated among the young and the educated\n(PLFS 2025 usual status; graduate figure ILO-IHD 2022)", loc="left", color=INK, fontsize=11)
a.set_ylabel("Unemployment rate (%)"); a.grid(axis="x", visible=False); a.set_ylim(0, 34)

# (b) supply vs demand flow
a = ax[0, 1]
bau = results["Business as usual"]
a.plot(bau.year, bau.entrants_m, color=C[0], lw=2.2)
a.plot(bau.year, bau.hires_m, color=C[1], lw=2.2)
a.fill_between(bau.year, bau.hires_m, bau.entrants_m, color=C[0], alpha=0.10)
a.text(2035.15, bau.entrants_m.iloc[-1], "Graduate entrants", color=INK, va="center", fontsize=9)
a.text(2035.15, bau.hires_m.iloc[-1], "Graduate hires", color=INK, va="center", fontsize=9)
a.set_title("Graduates joining the labour force vs jobs they secure (business as usual)\n2024 anchors: 5.0m entrants, 2.8m jobs (State of Working India)", loc="left", color=INK, fontsize=11)
a.set_ylabel("Million per year"); a.set_xlim(2024, 2038); a.set_ylim(0, None)

# (c) UR scenarios
a = ax[1, 0]
for i, (k, df) in enumerate(results.items()):
    a.plot(df.year, df.ur_grad_pct, color=C[i], lw=2.2, label=k + (" (overlaps BAU)" if k == "Skills reform" else ""))
    a.text(2035.15, df.ur_grad_pct.iloc[-1], f"{df.ur_grad_pct.iloc[-1]:.0f}%", color=INK, va="center", fontsize=9)
a.fill_between(YEARS, [q.ur_grad_2035.iloc[0]] * len(YEARS), [q.ur_grad_2035.iloc[2]] * len(YEARS), alpha=0)
a.set_title("Graduate-youth unemployment rate by scenario", loc="left", color=INK, fontsize=11)
a.set_ylabel("% of graduate labour force (20-29)"); a.set_xlim(2024, 2036.5)
a.legend(frameon=False, fontsize=8, loc="lower left")

# (d) mismatch (unemployed + below-qualification)
a = ax[1, 1]
for i, (k, df) in enumerate(results.items()):
    a.plot(df.year, df.mismatch_pct, color=C[i], lw=2.2, label=k)
a.set_title("Unemployed + working below qualification, % of graduate labour force", loc="left", color=INK, fontsize=11)
a.set_ylabel("%"); a.set_xlim(2024, 2035)
a.legend(frameon=False, fontsize=8.5, loc="lower left")

fig.suptitle("India: young entrants, job creation and the graduate skills gap", x=0.01, ha="left", fontsize=14, color=INK)
fig.text(0.01, 0.005, "Sources: PLFS Annual Report 2025 (MoSPI); AISHE 2023-24 (MoE); Economic Survey 2023-24; ILO-IHD India Employment Report 2024; "
         "State of Working India; Wheebox India Skills Report (trend only). 2025+ values are model projections.", fontsize=8, color=MUTED)
fig.tight_layout(rect=[0, 0.02, 1, 0.96])
fig.savefig(f"{OUT}/youth_jobs_skills_gap.png", dpi=150)

# ----------------------------------------------------------------------------
# 6. PRINTED REPORT
# ----------------------------------------------------------------------------
pd.set_option("display.width", 200, "display.max_columns", 30, "display.max_colwidth", 80)
print("\nDERIVED QUANTITIES"); print(derived.round(2).to_string(index=False))
print("\nBASE-YEAR CHECK (2024):"); print(bau.iloc[0].round(2).to_string())
print("\nSCENARIO SUMMARY"); print(SUMM.to_string(index=False))
print("\nMONTE CARLO 2035 (5th / 50th / 95th percentile)"); print(q.round(1).to_string())
print(f"\nFiles written to ./{OUT}/")
