#!/usr/bin/env python3
"""
Deterministic data generation for litigation seed data.

Generates cases, ruling_text, experts, citation_network, evidence_inventory,
depositions.jsonl, motions/, and rulings/ under _seed_data/.
Uses fixed random seed (SEED=0) once at load; Python standard library only.
Every run produces identical output. Does not rely on any external folder.

Usage:
    python3 generate_data.py
"""

import json
import random
from pathlib import Path

SEED = 0
BASE_DIR = Path(__file__).resolve().parent
SEED_DATA_DIR = BASE_DIR / "_seed_data"

NUM_ANCHOR_CASES = 46
NUM_SYNTHETIC_CASES = 220
DONOVAN_GRANT_WEIGHT = 1
OTHER_FIRM_WEIGHT = 19

random.seed(SEED)


def _anchor_case_ids():
    lines = _CASES_CSV.strip().split("\n")
    return [line.split(",", 1)[0] for line in lines[1 : 1 + NUM_ANCHOR_CASES]]


def _generated_case_ids():
    ids = []
    for year in range(2014, 2025):
        for seq in range(20):
            ids.append(f"C-{year}-{1000 + seq}")
    return ids[:NUM_SYNTHETIC_CASES]


def _all_case_ids():
    return _anchor_case_ids() + _generated_case_ids()


_COURTS = [
    ("N.D. Cal.", "Hon. Rebecca L. Ames"), ("D. Del.", "Hon. Samuel J. Kerr"), ("S.D.N.Y.", "Hon. Angela P. Rivera"),
    ("N.D. Ill.", "Hon. Lisa K. Monroe"), ("C.D. Cal.", "Hon. Evelyn S. Park"), ("D. Mass.", "Hon. Robert T. Hayes"),
    ("W.D. Wash.", "Hon. Megan L. Chu"), ("S.D. Tex.", "Hon. Carlos M. Ortiz"), ("E.D. Tex.", "Hon. Carlos M. Ortiz"),
]

_OPPOSING_FIRMS = [
    ("Donovan Grant LLP", "Claire Donovan; Oliver Grant", "Claire Donovan", "Oliver Grant"),
    ("Brighton & Cole", "Mark Hastings", "Mark Hastings", "Mark Hastings"),
    ("Hartley King & Cole", "Julia Hartley", "Julia Hartley", "Julia Hartley"),
    ("Ridgeway & Stone", "Peter Ridgeway", "Peter Ridgeway", "Peter Ridgeway"),
    ("Vance & Webb", "David Vance", "David Vance", "David Vance"),
    ("Merritt Shaw LLP", "Sarah Merritt", "Sarah Merritt", "Sarah Merritt"),
]

_OUR_COUNSEL = ["Michael Lee", "Priya Natarajan", "Daniel Cho"]

_INDUSTRIES = [
    "enterprise_software", "semiconductors", "cloud_infrastructure", "adtech", "oilfield_services", "logistics",
    "streaming_media", "biotech", "developer_tools", "financial_analytics", "healthcare_analytics",
]

_TS_PROFILES = [
    "source_code; customer_segments", "manufacturing_process_controls", "routing_optimization_engine",
    "content_recommendation_models", "pricing_signals_engine", "usage_analytics_schema", "risk_stratification_models",
    "personalization_models", "autoscaling_strategies", "portfolio_risk_signals", "lookalike_model_features",
]

_RESOLVED_VIA = ["trial_verdict", "summary_judgment", "settlement", "pretrial_dismissal"]

_VERDICT_FOR = ["us", "them", "mixed", "pending"]

_PI_OUTCOMES = ["denied", "granted", "granted_in_part"]

_SJ_OUTCOMES = ["denied", "granted", "granted_in_part"]

_APPEAL_OUTCOMES = ["", "affirmed", "reversed", "partially_reversed", "remanded_for_settlement_approval", "appeal_pending", "settled_without_admission"]


def _generated_case_rows():
    case_ids = _generated_case_ids()
    weights = [DONOVAN_GRANT_WEIGHT] + [OTHER_FIRM_WEIGHT] * (len(_OPPOSING_FIRMS) - 1)
    rows = []

    for idx, case_id in enumerate(case_ids):
        year = int(case_id.split("-")[1])
        seq = int(case_id.split("-")[2])
        court, judge = _COURTS[idx % len(_COURTS)]
        docket = f"1:{str(year)[2:]}-cv-{seq}"
        firm_idx = random.choices(range(len(_OPPOSING_FIRMS)), weights=weights)[0]
        firm_name, counsel_full, counsel_1, counsel_2 = _OPPOSING_FIRMS[firm_idx]
        our_lead = random.choice(_OUR_COUNSEL)
        industry = random.choice(_INDUSTRIES)
        ts = random.choice(_TS_PROFILES)
        filed = f"{year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        trial_date = f"{year + random.randint(2, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}" if random.random() < 0.6 else ""
        damages_claimed = random.randint(20_000_000, 150_000_000)
        is_donovan = firm_name == "Donovan Grant LLP"
        is_red_herring_firm = firm_name == "Hartley King & Cole"
        if is_donovan:
            verdict_for = random.choices(["them", "us"], weights=[85, 15])[0]
            resolved = random.choices(["summary_judgment", "trial_verdict", "settlement"], weights=[50, 35, 15])[0]
            pi_outcome = random.choices(_PI_OUTCOMES, weights=[40, 20, 40])[0]
            sj_outcome = random.choices(_SJ_OUTCOMES, weights=[20, 50, 30])[0]
            damages_awarded = 0 if verdict_for == "them" else random.randint(1_000_000, damages_claimed // 4)
        elif is_red_herring_firm:
            verdict_for = random.choices(["them", "us", "mixed", "pending"], weights=[40, 35, 15, 10])[0]
            resolved = random.choice(_RESOLVED_VIA)
            pi_outcome = random.choice(_PI_OUTCOMES)
            sj_outcome = random.choice(_SJ_OUTCOMES)
            damages_awarded = random.randint(0, damages_claimed // 3) if verdict_for == "us" else (0 if verdict_for == "them" else random.randint(0, damages_claimed // 5))
        else:
            verdict_for = random.choice(_VERDICT_FOR)
            resolved = random.choice(_RESOLVED_VIA)
            pi_outcome = random.choice(_PI_OUTCOMES)
            sj_outcome = random.choice(_SJ_OUTCOMES)
            damages_awarded = random.randint(0, damages_claimed // 3) if verdict_for == "us" else (0 if verdict_for == "them" else random.randint(0, damages_claimed // 5))
        appeal_flag = "true" if random.random() < 0.35 else "false"
        appeal_outcome = random.choice(_APPEAL_OUTCOMES) if appeal_flag == "true" else ""
        counsel = counsel_full if ";" in counsel_full else counsel_1
        row = (
            f"{case_id},{docket},{court},federal,{judge},{filed},{trial_date},trade_secret_misappropriation,"
            f"{industry},plaintiff,{firm_name},\"{counsel}\",{our_lead},{resolved},{verdict_for},"
            f"{damages_claimed},{damages_awarded},{pi_outcome},{sj_outcome},{ts},{appeal_flag},{appeal_outcome}"
        )
        rows.append((case_id, row))
    return rows


def _generated_ruling_rows():
    case_ids = _generated_case_ids()
    stages = [("PI", "preliminary_injunction", "injunctive_relief"), ("MSJ", "summary_judgment", "liability"), ("Daubert", "daubert", "damages")]
    holdings_templates = [
        "Plaintiff has not identified alleged trade secrets with sufficient particularity; motion granted in part.",
        "Material factual disputes preclude summary judgment; motion denied.",
        "The Court finds plaintiff's trade secret definitions adequate as to the narrowed scope; motion denied in part.",
        "Defendant's motion for summary judgment is granted; no reasonable jury could find misappropriation on this record.",
        "Cross-motions for summary judgment are denied; disputes must be resolved by a jury.",
    ]
    rows = []
    for idx, case_id in enumerate(case_ids):
        court, judge = _COURTS[idx % len(_COURTS)]
        judge_style = judge.replace("Hon. ", "").replace(".", "").replace(" ", ", ") + ", J."
        num_rulings = 1 + (idx % 2)
        for r in range(num_rulings):
            stage_tag, motion_type, scope = stages[(idx + r) % len(stages)]
            entry_no = 30 + idx * 10 + r
            outcome = random.choice(["denied", "granted", "granted_in_part"])
            spol = "true" if random.random() < 0.2 else "false"
            adv_inf = "true" if spol == "true" or random.random() < 0.15 else "false"
            narrow = "true" if random.random() < 0.4 else "false"
            year = int(case_id.split("-")[1])
            decision_date = f"{year + random.randint(1, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            ruling_id = f"R-{case_id.replace('C-', '')}-{stage_tag}{r}"
            holdings = random.choice(holdings_templates)
            flags = f'"{{\\"spoliation_sanction\\": {spol}, \\"adverse_inference\\": {adv_inf}, \\"trade_secret_defined_narrowly\\": {narrow}}}"'
            rows.append(f"{ruling_id},{case_id},{entry_no},{stage_tag},{motion_type},{'them' if r % 2 else 'us'},{outcome},{scope},,{flags},\"{decision_date}\",\"{judge_style}\",\"{holdings}\"")
    return rows


def _generated_expert_rows():
    case_ids = _generated_case_ids()
    first_names = ["James", "Maria", "Robert", "Linda", "David", "Patricia", "Richard", "Barbara", "Joseph", "Susan", "Thomas", "Jessica", "Charles", "Karen", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Helen"]
    last_names = ["Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "King"]
    disciplines = ["damages", "forensics", "statistics", "industry_practices"]
    issues = ["lost_profits", "misappropriation", "causation", "valuation", "unjust_enrichment", "apportionment"]
    outcomes = ["none", "denied", "granted", "granted_in_part"]
    reliance = ["relied_on_plaintiff_damages", "relied_on_defense_technical", "limited_plaintiff_damages", "mixed_weight", "excluded_plaintiff_expert", "relied_on_defense_industry", ""]
    rows = []
    for idx, case_id in enumerate(case_ids):
        n = 1 + (idx % 2)
        year = case_id.split("-")[1]
        for e in range(n):
            side = "us" if (idx + e) % 2 == 0 else "them"
            suffix = "PL" if side == "us" else "DF"
            expert_id = f"EXP-S{year}-{idx:03d}-{suffix}-{e}"
            name = f"Dr. {first_names[(idx + e) % len(first_names)]} {last_names[(idx + e * 2) % len(last_names)]}"
            disc = random.choice(disciplines)
            issue = random.choice(issues)
            report = f"expert_reports/{case_id}_{'PX' if side == 'us' else 'DX'}_Expert_{expert_id.split('-')[-1]}.pdf"
            depo = "true" if random.random() < 0.8 else "false"
            daubert_filed = "true" if random.random() < 0.6 else "false"
            daubert_out = random.choice(outcomes) if daubert_filed == "true" else "none"
            trial = "true" if random.random() < 0.7 else "false"
            rel = random.choice(reliance)
            rows.append(f"{expert_id},{case_id},{side},{name},{disc},{issue},{report},{depo},{daubert_filed},{daubert_out},{trial},{rel}")
    return rows


_CITATION_PRECEDENTS = [
    ("Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016)", "", "inevitable_disclosure"),
    ("Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)", "", "trade_secret_identification"),
    ("Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010)", "HC-TS-2010-HEL", "spoliation"),
    ("Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)", "", "reasonable_measures"),
]
_CITATION_CONTEXT = [("motion", "plaintiff_motion", "us"), ("motion", "defense_motion", "them"), ("ruling", "court_order", "judge")]
_TREATMENT = ["followed", "distinguished", "rejected", "limited"]


def _generated_citation_rows():
    case_ids = _generated_case_ids()
    rows = []
    for idx, case_id in enumerate(case_ids):
        n = random.randint(0, 2)
        for _ in range(n):
            cite, target_id, issue = random.choice(_CITATION_PRECEDENTS)
            context, doc_type, side = _CITATION_CONTEXT[idx % len(_CITATION_CONTEXT)]
            treatment = random.choice(_TREATMENT)
            strength = random.randint(1, 3)
            target_id_field = target_id if target_id else ""
            rows.append(f'{case_id},"{cite}",{target_id_field},{context},{doc_type},{side},{issue},{treatment},{strength}')
    return rows


def main():
    SEED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (SEED_DATA_DIR / "motions").mkdir(exist_ok=True)
    (SEED_DATA_DIR / "rulings").mkdir(exist_ok=True)

    _write_cases()
    _write_ruling_text()
    _write_experts()
    _write_citation_network()
    _write_evidence_inventory()
    _write_depositions()
    _write_motions()
    _write_rulings()

    print("Seed data ready in", SEED_DATA_DIR)


def _write_cases():
    path = SEED_DATA_DIR / "cases.csv"
    lines = _CASES_CSV.strip().split("\n")
    header = lines[0]
    anchor_rows = lines[1 : 1 + NUM_ANCHOR_CASES]
    generated = _generated_case_rows()
    body = anchor_rows + [r[1] for r in generated]
    path.write_text("\n".join([header] + body) + "\n", encoding="utf-8")


def _write_ruling_text():
    path = SEED_DATA_DIR / "ruling_text.csv"
    lines = _RULING_TEXT_CSV.strip().split("\n")
    header = lines[0]
    existing = lines[1:]
    generated = _generated_ruling_rows()
    path.write_text("\n".join([header] + existing + generated) + "\n", encoding="utf-8")


def _write_experts():
    path = SEED_DATA_DIR / "experts.csv"
    lines = _EXPERTS_CSV.strip().split("\n")
    header = lines[0]
    existing = lines[1:]
    generated = _generated_expert_rows()
    path.write_text("\n".join([header] + existing + generated) + "\n", encoding="utf-8")


def _write_citation_network():
    path = SEED_DATA_DIR / "citation_network.csv"
    lines = _CITATION_NETWORK_CSV.strip().split("\n")
    header = lines[0]
    existing = lines[1:]
    generated = _generated_citation_rows()
    path.write_text("\n".join([header] + existing + generated) + "\n", encoding="utf-8")


def _write_evidence_inventory():
    path = SEED_DATA_DIR / "evidence_inventory.csv"
    lines = [_EVIDENCE_HEADER] + _EVIDENCE_KEY_ROWS + _evidence_synthetic_rows()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


_EVIDENCE_HEADER = "case_id,exhibit_id,producing_party,custodian_name,custodian_role,system_source,doc_type,hot_doc_flag,used_in_motion,used_at_trial,impeachment_use_flag,spoliation_related_flag,notes"

_EVIDENCE_KEY_ROWS = [
    "C-2020-0312,PX-023,us,Laura Chen,plaintiff_cto,github,source_code,true,true,true,false,false,Snapshot of pre-2018 algorithm implementation referenced in MSJ briefing.",
    "C-2020-0312,PX-031,us,Laura Chen,plaintiff_cto,sharepoint,presentation,true,true,true,true,true,Security roadmap deck produced late; used by Donovan to argue inadequate controls and spoliation.",
    "C-2020-0312,DX-104,them,Evan Morales,defendant_engineering_manager,gmail,email,true,true,true,true,false,Email thread suggesting plaintiff shared demo builds without NDA.",
    "C-2019-1187,PX-010,us,Harish Rao,plaintiff_process_engineer,sharepoint,spreadsheet,true,true,false,false,true,Missing revision history for process-control spreadsheet; central to spoliation dispute.",
    "C-2019-1187,DX-057,them,Sarah Ingram,defendant_ops_director,gmail,email,true,true,true,true,false,Email impeaching plaintiff 30(b)(6) testimony about lab access restrictions.",
    "C-2019-1187,PX-021,us,Monica Feld,plaintiff_gc,sharepoint,policy,false,false,false,false,false,High-level trade secret policy not tailored to manufacturing process.",
    "C-2021-0904,PX-018,them,Ryan Lopez,plaintiff_product_manager,jira,document,true,true,true,false,false,Ticket linking deployment playbooks to named customers with explicit access controls.",
    "C-2021-0904,DX-032,us,Anita Rao,defendant_success_lead,slack,chat_export,false,false,true,false,false,Slack thread about tightening access to customer lists before launch.",
    "C-2021-0904,DX-041,us,Victor Chang,defendant_cto,github,source_code,true,true,true,false,false,Redacted snippet of internal deployment tooling showing segregation between public and confidential configs.",
    "C-2018-0220,PX-012,us,Jonas Meyer,plaintiff_data_science_lead,bigquery,table_export,true,true,false,false,false,Export of historical bid-response logs used in valuation model.",
    "C-2018-0220,DX-021,them,Lena Ortiz,defendant_product_manager,gmail,email,false,true,false,true,false,Email suggesting plaintiff reused off-the-shelf open-source components for core algorithm.",
    "C-2019-2044,PX-004,us,Emily Zhang,plaintiff_ops_director,postgres,table_export,true,true,true,false,false,Routing simulation outputs tying optimization parameters to fuel savings.",
    "C-2019-2044,DX-019,them,Noah Greene,defendant_analyst,excel,spreadsheet,false,true,true,false,false,Simplified spreadsheet challenging incremental value of plaintiff's routes.",
    "C-2020-1450,PX-045,them,Chloe Diaz,plaintiff_growth_head,redshift,table_export,true,true,true,false,false,Cohort-level streaming engagement metrics used by plaintiff's expert.",
    "C-2020-1450,DX-077,us,Marco Ruiz,defendant_research_lead,github,source_code,true,true,true,false,false,Annotated notebook showing independent development of recommendation model variant.",
    "C-2022-0678,PX-030,us,Dr. Naomi Keller,plaintiff_clinical_lead,sharepoint,protocol,true,true,false,false,false,Phase II trial protocol marked confidential and tied to specific indication.",
    "C-2022-0678,DX-011,them,Patrick Long,defendant_bizdev_head,gmail,email,false,true,false,false,false,Negotiation thread about access to de-identified trial data.",
    "C-2019-2044,PX-004,us,Emily Zhang,plaintiff_ops_director,postgres,table_export,true,true,true,false,false,Routing simulation outputs tying optimization parameters to confidential shipper data.",
    "C-2019-2044,DX-019,them,Noah Greene,defendant_analyst,excel,spreadsheet,false,true,true,false,false,Simplified spreadsheet challenging incremental value of plaintiff's routes.",
    "C-2020-1450,PX-045,them,Chloe Diaz,plaintiff_growth_head,redshift,table_export,true,true,true,false,false,Cohort-level streaming engagement metrics used by plaintiff's expert.",
    "C-2020-1450,DX-077,us,Marco Ruiz,defendant_research_lead,github,source_code,true,true,true,false,false,Annotated notebook showing independent development of recommendation model variant.",
    "C-2019-0113,PX-017,us,Nikhil Rao,plaintiff_pm,snowflake,table_export,true,true,false,false,false,Onboarding funnel metrics used to calibrate scoring model.",
    "C-2019-0113,DX-022,them,Kara Mills,defendant_pm,gmail,email,false,true,false,false,false,Email pointing to publicly documented onboarding scoring best practices.",
    "C-2019-0666,PX-061,us,Sonia Patel,plaintiff_adops_lead,bigquery,table_export,true,true,false,false,true,Sample of auction logs with gaps due to retention policy.",
    "C-2019-0666,DX-073,them,Leo Brooks,defendant_data_scientist,github,notebook,true,true,true,false,false,Analysis notebook arguing plaintiff's lift claims are overstated.",
    "C-2020-0044,PX-025,us,Dr. Aaron Price,plaintiff_data_science_lead,postgres,table_export,true,true,false,false,false,Readmission scorecards with feature weights for top conditions.",
    "C-2020-0599,PX-014,us,Emily Kovacs,plaintiff_quant_lead,parquet,table_export,true,true,false,false,true,Tick data snapshot missing several days cited in the complaint.",
    "C-2021-0442,PX-039,us,Lara Jensen,plaintiff_product_lead,sharepoint,presentation,false,true,false,false,false,Slide deck describing role recommendation engine at a high level.",
    "C-2022-0407,PX-033,us,Dr. Aisha Rahman,plaintiff_data_science_lead,sharepoint,notebook,true,true,false,false,false,Notebook mapping care-gap model inputs to public Medicare fields.",
    "C-2023-0310,PX-028,us,Dr. Matteo Ricci,plaintiff_process_engineer,sharepoint,spreadsheet,true,true,false,false,true,Furnace calibration log export missing early recipe variants.",
]


def _evidence_synthetic_rows():
    """Generate 172 synthetic evidence rows (same case order and fields as seed_data)."""
    case_order = [
        "C-2020-0312", "C-2019-1187", "C-2021-0904", "C-2018-0220", "C-2017-0541", "C-2019-2044",
        "C-2020-1450", "C-2022-0678", "C-2023-0129", "C-2016-0001", "C-2016-0034", "C-2016-0450",
        "C-2017-0102", "C-2017-0209", "C-2017-0788", "C-2018-0055", "C-2018-0199", "C-2018-0301",
        "C-2018-0670", "C-2019-0113", "C-2019-0307", "C-2019-0666", "C-2019-0901", "C-2020-0044",
        "C-2020-0208", "C-2020-0599", "C-2020-0880", "C-2021-0055", "C-2021-0277", "C-2021-0442",
        "C-2021-0810", "C-2022-0111", "C-2022-0244", "C-2022-0407", "C-2022-0599", "C-2022-0888",
        "C-2023-0040", "C-2023-0195", "C-2023-0310", "C-2023-0472", "C-2023-0606", "C-2023-0799",
        "C-2024-0102", "C-2024-0255", "C-2024-0328", "C-2024-0490",
    ]
    # (system_source, doc_type, hot, used_in_motion, used_at_trial, impeachment, spoliation) per row
    spec = [
        ("excel", "notebook", "false", "false", "true", "true", "false"),
        ("postgres", "spreadsheet", "true", "false", "false", "true", "true"),
        ("gmail", "notebook", "true", "true", "false", "false", "false"),
        ("slack", "spreadsheet", "false", "true", "false", "false", "false"),
        ("excel", "presentation", "true", "false", "false", "false", "false"),
        ("jira", "policy", "true", "true", "false", "false", "false"),
        ("postgres", "table_export", "true", "true", "false", "false", "false"),
        ("slack", "chat_export", "true", "true", "false", "true", "false"),
        ("gmail", "presentation", "true", "false", "false", "false", "false"),
        ("excel", "chat_export", "false", "true", "false", "false", "true"),
        ("slack", "chat_export", "true", "false", "false", "false", "false"),
        ("excel", "policy", "false", "false", "false", "true", "false"),
        ("jira", "table_export", "true", "false", "false", "false", "false"),
        ("github", "presentation", "false", "false", "true", "false", "false"),
        ("jira", "presentation", "false", "true", "true", "true", "false"),
        ("snowflake", "policy", "true", "false", "false", "true", "false"),
        ("snowflake", "notebook", "true", "true", "false", "true", "false"),
        ("snowflake", "spreadsheet", "false", "true", "false", "false", "true"),
        ("github", "chat_export", "true", "false", "false", "true", "false"),
        ("sharepoint", "presentation", "true", "false", "false", "false", "false"),
        ("postgres", "policy", "false", "false", "false", "false", "false"),
        ("bigquery", "spreadsheet", "true", "false", "false", "true", "false"),
        ("slack", "spreadsheet", "false", "false", "false", "false", "true"),
        ("slack", "table_export", "false", "false", "true", "false", "true"),
        ("bigquery", "notebook", "true", "true", "false", "false", "false"),
        ("excel", "spreadsheet", "false", "false", "false", "false", "false"),
        ("postgres", "chat_export", "false", "true", "true", "false", "true"),
        ("sharepoint", "presentation", "true", "false", "false", "false", "false"),
        ("sharepoint", "table_export", "true", "false", "true", "false", "false"),
        ("gmail", "presentation", "true", "true", "true", "false", "false"),
        ("snowflake", "table_export", "true", "true", "true", "false", "false"),
        ("sharepoint", "email", "true", "false", "false", "false", "false"),
        ("postgres", "chat_export", "true", "true", "true", "false", "false"),
        ("slack", "presentation", "false", "true", "false", "false", "false"),
        ("github", "presentation", "true", "false", "true", "true", "false"),
        ("gmail", "policy", "false", "false", "false", "false", "false"),
        ("sharepoint", "spreadsheet", "true", "true", "false", "false", "false"),
        ("snowflake", "policy", "false", "true", "false", "false", "false"),
        ("sharepoint", "spreadsheet", "true", "true", "true", "true", "false"),
        ("jira", "table_export", "true", "true", "true", "false", "false"),
        ("jira", "presentation", "false", "true", "true", "false", "false"),
        ("gmail", "presentation", "true", "true", "false", "true", "false"),
        ("sharepoint", "notebook", "false", "false", "false", "false", "true"),
        ("postgres", "email", "true", "false", "false", "false", "true"),
        ("slack", "notebook", "true", "false", "false", "true", "false"),
        ("slack", "spreadsheet", "true", "true", "false", "false", "false"),
        ("slack", "spreadsheet", "false", "true", "false", "false", "false"),
        ("slack", "notebook", "true", "true", "false", "false", "false"),
        ("sharepoint", "email", "true", "true", "false", "false", "false"),
        ("sharepoint", "chat_export", "true", "true", "false", "false", "false"),
        ("snowflake", "notebook", "true", "false", "false", "true", "true"),
        ("gmail", "notebook", "false", "false", "false", "false", "false"),
        ("github", "email", "true", "true", "true", "false", "false"),
        ("postgres", "notebook", "false", "true", "false", "false", "false"),
        ("gmail", "chat_export", "true", "false", "true", "false", "false"),
        ("excel", "spreadsheet", "false", "true", "true", "false", "false"),
        ("sharepoint", "spreadsheet", "false", "false", "true", "false", "false"),
        ("bigquery", "table_export", "true", "true", "false", "false", "false"),
        ("gmail", "spreadsheet", "false", "true", "true", "false", "false"),
        ("excel", "notebook", "false", "false", "true", "false", "false"),
        ("gmail", "chat_export", "false", "false", "false", "false", "false"),
        ("gmail", "chat_export", "true", "true", "false", "true", "false"),
        ("jira", "notebook", "false", "true", "false", "true", "false"),
        ("excel", "presentation", "true", "false", "false", "false", "false"),
        ("jira", "presentation", "true", "true", "true", "true", "false"),
        ("excel", "spreadsheet", "false", "true", "true", "true", "false"),
        ("excel", "email", "false", "false", "true", "false", "false"),
        ("sharepoint", "policy", "true", "false", "true", "false", "false"),
        ("excel", "spreadsheet", "true", "true", "true", "false", "false"),
        ("snowflake", "notebook", "false", "true", "true", "false", "false"),
        ("jira", "table_export", "true", "false", "false", "false", "true"),
        ("bigquery", "policy", "false", "false", "true", "false", "false"),
        ("slack", "email", "false", "true", "true", "true", "false"),
        ("jira", "policy", "true", "false", "true", "false", "false"),
        ("snowflake", "table_export", "false", "false", "false", "false", "false"),
        ("excel", "chat_export", "false", "true", "true", "false", "false"),
        ("slack", "notebook", "true", "false", "true", "false", "false"),
        ("jira", "notebook", "false", "true", "false", "true", "false"),
        ("snowflake", "table_export", "true", "true", "false", "false", "false"),
        ("jira", "notebook", "false", "true", "true", "false", "true"),
        ("sharepoint", "chat_export", "true", "true", "false", "false", "false"),
        ("gmail", "table_export", "false", "false", "false", "false", "false"),
        ("sharepoint", "policy", "true", "false", "true", "false", "false"),
        ("snowflake", "table_export", "true", "false", "false", "true", "false"),
        ("bigquery", "email", "false", "true", "true", "false", "false"),
        ("postgres", "source_code", "true", "true", "false", "false", "false"),
    ]
    out = []
    for i in range(86):
        case = case_order[i % 46]
        px_num = 100 + i
        dx_num = 200 + i
        s_px, d_px, h_px, mo_px, tr_px, im_px, sp_px = spec[i]
        s_dx, d_dx, h_dx, mo_dx, tr_dx, im_dx, sp_dx = spec[i]  # DX uses same pattern for determinism
        out.append(
            f"{case},PX-A{px_num},us,Custodian PX-A{px_num},plaintiff_engineer,{s_px},{d_px},{h_px},{mo_px},{tr_px},{im_px},{sp_px},Synthetic {d_px} related to {case} and {s_px}."
        )
        out.append(
            f"{case},DX-A{dx_num},them,Custodian DX-A{dx_num},defendant_engineer,{s_dx},{d_dx},{h_dx},{mo_dx},{tr_dx},{im_dx},{sp_dx},Synthetic {d_dx} related to {case} and {s_dx}."
        )
    return out


def _write_depositions():
    path = SEED_DATA_DIR / "depositions.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for rec in _deposition_records():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _generated_motion_files():
    motion_templates = [
        ("MSJ", "plaintiff", "Plaintiff moves for partial summary judgment on liability. Defendant's platform mirrors confidential design choices developed at our client."),
        ("MSJ", "defense", "Defendant moves for summary judgment. Plaintiff has not identified its alleged trade secrets with reasonable particularity. See Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)."),
        ("PI", "plaintiff", "Plaintiff moves for a preliminary injunction. Irreparable harm is likely absent relief given defendant's use of confidential materials."),
    ]
    for idx, case_id in enumerate(_generated_case_ids()):
        motion_type, side, arg = motion_templates[idx % len(motion_templates)]
        filename = f"{case_id}_{motion_type}_{side}.txt"
        content = f"CASE_ID: {case_id}\nMOTION_TYPE: {motion_type}\nSIDE: {side}\n\nINTRODUCTION\n\n{arg}\n"
        yield filename, content


def _generated_ruling_files():
    ruling_templates = [
        "Motion for summary judgment is GRANTED IN PART. Plaintiff has not identified trade secrets with sufficient particularity.\n",
        "Motion denied. Material factual disputes preclude summary judgment; the matter is for the jury.\n",
        "Preliminary injunction is DENIED. Plaintiff has not shown a likelihood of success on the merits.\n",
    ]
    for idx, case_id in enumerate(_generated_case_ids()):
        text = ruling_templates[idx % len(ruling_templates)]
        stage = "MSJ" if idx % 2 == 0 else "PI"
        filename = f"{case_id}_Order_{stage}_excerpt.txt"
        content = f"This matter comes before the Court on the parties' motions. {text}"
        yield filename, content


def _write_motions():
    for name, content in _MOTION_FILES.items():
        (SEED_DATA_DIR / "motions" / name).write_text(content, encoding="utf-8")
    for name, content in _generated_motion_files():
        (SEED_DATA_DIR / "motions" / name).write_text(content, encoding="utf-8")


def _write_rulings():
    for name, content in _RULING_FILES.items():
        (SEED_DATA_DIR / "rulings" / name).write_text(content, encoding="utf-8")
    for name, content in _generated_ruling_files():
        (SEED_DATA_DIR / "rulings" / name).write_text(content, encoding="utf-8")


# --- Embedded CSV content (same structure as _seed_data) ---

_CASES_CSV = """case_id,docket_number,court_name,jurisdiction_type,judge_name,filed_date,trial_date,case_type,industry_sector,our_role,opposing_firm_name,opposing_lead_counsel,our_lead_counsel,resolved_via,verdict_for,total_damages_claimed,damages_awarded,pi_motion_outcome,summary_judgment_outcome,trade_secret_profile,appeal_flag,appeal_outcome
C-2020-0312,3:20-cv-0312,N.D. Cal.,federal,Hon. Rebecca L. Ames,2020-02-14,2023-05-01,trade_secret_misappropriation,enterprise_software,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Michael Lee,trial_verdict,them,120000000,0,denied,granted_in_part,source_code; customer_segments,true,affirmed
C-2019-1187,1:19-cv-1187,D. Del.,federal,Hon. Samuel J. Kerr,2019-06-03,,trade_secret_misappropriation,semiconductors,plaintiff,Donovan Grant LLP,"Claire Donovan",Priya Natarajan,summary_judgment,them,85000000,0,granted,granted,manufacturing_process_controls,false,
C-2021-0904,2:21-cv-0904,S.D.N.Y.,federal,Hon. Angela P. Rivera,2021-09-21,2024-03-18,trade_secret_misappropriation,cloud_infrastructure,defendant,Brighton & Cole,"Mark Hastings",Daniel Cho,trial_verdict,us,45000000,2500000,denied,denied,customer_lists; deployment_playbooks,false,
C-2018-0220,5:18-cv-0220,N.D. Cal.,federal,Hon. Rebecca L. Ames,2018-01-11,,trade_secret_misappropriation,adtech,plaintiff,Donovan Grant LLP,"Oliver Grant",Michael Lee,settlement,them,60000000,15000000,denied,denied,real_time_bidding_algorithms,true,settled_without_admission
C-2017-0541,2:17-cv-0541,S.D. Tex.,federal,Hon. Carlos M. Ortiz,2017-03-09,2019-10-22,trade_secret_misappropriation,oilfield_services,defendant,Hartley King & Cole,"Julia Hartley",Priya Natarajan,trial_verdict,us,30000000,0,denied,denied,maintenance_scheduling_models,false,
C-2019-2044,3:19-cv-2044,N.D. Ill.,federal,Hon. Lisa K. Monroe,2019-09-30,2022-02-14,trade_secret_misappropriation,logistics,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Daniel Cho,trial_verdict,us,50000000,22000000,granted_in_part,denied,routing_optimization_engine,false,
C-2020-1450,8:20-cv-1450,C.D. Cal.,federal,Hon. Evelyn S. Park,2020-06-18,2022-11-08,trade_secret_misappropriation,streaming_media,defendant,Donovan Grant LLP,"Claire Donovan",Michael Lee,trial_verdict,them,38000000,7000000,denied,denied,content_recommendation_models,true,partially_reversed
C-2022-0678,1:22-cv-0678,D. Mass.,federal,Hon. Robert T. Hayes,2022-02-03,,trade_secret_misappropriation,biotech,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Priya Natarajan,settlement,them,150000000,50000000,granted_in_part,granted_in_part,clinical_trial_protocols,true,remanded_for_settlement_approval
C-2023-0129,4:23-cv-0129,W.D. Wash.,federal,Hon. Megan L. Chu,2023-01-27,,trade_secret_misappropriation,developer_tools,plaintiff,Brighton & Cole,"Mark Hastings",Daniel Cho,summary_judgment,mixed,42000000,8000000,denied,granted_in_part,api_usage_telemetry,false,
C-2016-0001,1:16-cv-0001,S.D.N.Y.,federal,Hon. Angela P. Rivera,2016-01-12,2017-09-05,trade_secret_misappropriation,financial_analytics,plaintiff,Donovan Grant LLP,"Claire Donovan",Michael Lee,trial_verdict,them,90000000,5000000,denied,denied,pricing_signals_engine,true,affirmed
C-2016-0034,3:16-cv-0034,N.D. Cal.,federal,Hon. Rebecca L. Ames,2016-02-28,,trade_secret_misappropriation,developer_tools,plaintiff,Brighton & Cole,"Mark Hastings",Priya Natarajan,settlement,us,25000000,10000000,denied,denied,debugging_workflow_data,false,
C-2016-0450,2:16-cv-0450,E.D. Tex.,federal,Hon. Carlos M. Ortiz,2016-07-19,2018-03-11,trade_secret_misappropriation,enterprise_software,defendant,Hartley King & Cole,"Julia Hartley",Daniel Cho,trial_verdict,us,60000000,0,denied,denied,usage_analytics_schema,false,
C-2017-0102,5:17-cv-0102,N.D. Ill.,federal,Hon. Lisa K. Monroe,2017-01-30,2019-04-21,trade_secret_misappropriation,healthcare_analytics,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Michael Lee,trial_verdict,us,72000000,28000000,granted_in_part,denied,risk_stratification_models,false,
C-2017-0209,2:17-cv-0209,D. Mass.,federal,Hon. Robert T. Hayes,2017-03-02,,trade_secret_misappropriation,biotech,plaintiff,Donovan Grant LLP,"Claire Donovan",Priya Natarajan,summary_judgment,them,110000000,0,denied,granted,biomarker_panels,true,affirmed
C-2017-0788,8:17-cv-0788,C.D. Cal.,federal,Hon. Evelyn S. Park,2017-08-15,2019-12-09,trade_secret_misappropriation,streaming_media,defendant,Brighton & Cole,"Mark Hastings",Daniel Cho,trial_verdict,us,55000000,5000000,denied,denied,personalization_models,false,
C-2018-0055,4:18-cv-0055,W.D. Wash.,federal,Hon. Megan L. Chu,2018-02-01,,trade_secret_misappropriation,cloud_infrastructure,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Michael Lee,settlement,them,65000000,20000000,denied,granted_in_part,autoscaling_strategies,true,remanded_for_settlement_approval
C-2018-0199,1:18-cv-0199,D. Del.,federal,Hon. Samuel J. Kerr,2018-04-05,2020-01-17,trade_secret_misappropriation,semiconductors,defendant,Hartley King & Cole,"Julia Hartley",Priya Natarajan,trial_verdict,us,80000000,0,granted_in_part,denied,process_drift_models,false,
C-2018-0301,3:18-cv-0301,N.D. Cal.,federal,Hon. Rebecca L. Ames,2018-06-12,,trade_secret_misappropriation,adtech,plaintiff,Donovan Grant LLP,"Oliver Grant",Daniel Cho,summary_judgment,them,50000000,0,denied,granted,lookalike_model_features,true,affirmed
C-2018-0670,2:18-cv-0670,S.D.N.Y.,federal,Hon. Angela P. Rivera,2018-09-07,2020-05-19,trade_secret_misappropriation,financial_analytics,defendant,Ridgeway & Stone,"Peter Ridgeway",Michael Lee,trial_verdict,us,43000000,2000000,denied,denied,portfolio_risk_signals,false,
C-2019-0113,5:19-cv-0113,N.D. Cal.,federal,Hon. Rebecca L. Ames,2019-01-22,,trade_secret_misappropriation,enterprise_software,plaintiff,Donovan Grant LLP,"Claire Donovan",Priya Natarajan,settlement,them,70000000,22000000,denied,granted_in_part,onboarding_scoring_model,true,remanded_for_settlement_approval
C-2019-0307,2:19-cv-0307,S.D. Tex.,federal,Hon. Carlos M. Ortiz,2019-03-15,2021-01-28,trade_secret_misappropriation,oilfield_services,plaintiff,Hartley King & Cole,"Julia Hartley",Daniel Cho,trial_verdict,us,36000000,15000000,denied,denied,drilling_sequence_optimizer,false,
C-2019-0666,8:19-cv-0666,C.D. Cal.,federal,Hon. Evelyn S. Park,2019-06-20,,trade_secret_misappropriation,streaming_media,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Michael Lee,summary_judgment,them,92000000,0,denied,granted,ad_insertion_engine,true,affirmed
C-2019-0901,4:19-cv-0901,W.D. Wash.,federal,Hon. Megan L. Chu,2019-09-09,2021-06-03,trade_secret_misappropriation,developer_tools,defendant,Brighton & Cole,"Mark Hastings",Priya Natarajan,trial_verdict,us,28000000,2500000,denied,denied,build_cache_algorithms,false,
C-2020-0044,1:20-cv-0044,D. Mass.,federal,Hon. Robert T. Hayes,2020-01-17,2022-08-11,trade_secret_misappropriation,healthcare_analytics,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Daniel Cho,trial_verdict,us,96000000,41000000,granted_in_part,denied,readmission_risk_scores,false,
C-2020-0208,3:20-cv-0208,N.D. Ill.,federal,Hon. Lisa K. Monroe,2020-03-03,,trade_secret_misappropriation,logistics,defendant,Hartley King & Cole,"Julia Hartley",Michael Lee,settlement,them,52000000,16000000,denied,denied,capacity_planning_models,false,
C-2020-0599,2:20-cv-0599,S.D.N.Y.,federal,Hon. Angela P. Rivera,2020-06-01,2022-10-04,trade_secret_misappropriation,financial_analytics,plaintiff,Donovan Grant LLP,"Claire Donovan",Priya Natarajan,trial_verdict,them,102000000,9000000,denied,denied,high_frequency_signals,true,affirmed
C-2020-0880,8:20-cv-0880,C.D. Cal.,federal,Hon. Evelyn S. Park,2020-08-24,,trade_secret_misappropriation,cloud_infrastructure,plaintiff,Brighton & Cole,"Mark Hastings",Daniel Cho,summary_judgment,mixed,47000000,12000000,denied,granted_in_part,disaster_recovery_playbooks,false,
C-2021-0055,4:21-cv-0055,W.D. Wash.,federal,Hon. Megan L. Chu,2021-01-29,2023-09-16,trade_secret_misappropriation,developer_tools,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Michael Lee,trial_verdict,them,63000000,8000000,denied,denied,ci_cd_optimization_pipelines,true,affirmed
C-2021-0277,1:21-cv-0277,D. Del.,federal,Hon. Samuel J. Kerr,2021-03-10,,trade_secret_misappropriation,semiconductors,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Priya Natarajan,settlement,us,88000000,33000000,granted_in_part,denied,packaging_thermal_models,false,
C-2021-0442,3:21-cv-0442,N.D. Cal.,federal,Hon. Rebecca L. Ames,2021-05-06,,trade_secret_misappropriation,enterprise_software,plaintiff,Donovan Grant LLP,"Claire Donovan",Daniel Cho,summary_judgment,them,77000000,0,denied,granted,role_recommendation_engine,true,affirmed
C-2021-0810,2:21-cv-0810,S.D. Tex.,federal,Hon. Carlos M. Ortiz,2021-08-02,2023-01-19,trade_secret_misappropriation,oilfield_services,defendant,Brighton & Cole,"Mark Hastings",Michael Lee,trial_verdict,us,39000000,3500000,denied,denied,downhole_sensor_calibration,false,
C-2022-0111,8:22-cv-0111,C.D. Cal.,federal,Hon. Evelyn S. Park,2022-01-20,,trade_secret_misappropriation,streaming_media,plaintiff,Donovan Grant LLP,"Claire Donovan",Priya Natarajan,settlement,them,64000000,19000000,denied,granted_in_part,viewer_segmentation_models,true,remanded_for_settlement_approval
C-2022-0244,4:22-cv-0244,W.D. Wash.,federal,Hon. Megan L. Chu,2022-03-03,,trade_secret_misappropriation,cloud_infrastructure,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Daniel Cho,summary_judgment,us,58000000,0,denied,denied,latency_optimization_strategies,false,
C-2022-0407,1:22-cv-0407,D. Mass.,federal,Hon. Robert T. Hayes,2022-04-11,,trade_secret_misappropriation,healthcare_analytics,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Michael Lee,summary_judgment,them,99000000,0,denied,granted,care_gap_models,true,affirmed
C-2022-0599,3:22-cv-0599,N.D. Ill.,federal,Hon. Lisa K. Monroe,2022-06-09,,trade_secret_misappropriation,logistics,defendant,Hartley King & Cole,"Julia Hartley",Priya Natarajan,settlement,them,43000000,9000000,denied,denied,carrier_scorecards,false,
C-2022-0888,2:22-cv-0888,S.D.N.Y.,federal,Hon. Angela P. Rivera,2022-08-17,,trade_secret_misappropriation,financial_analytics,plaintiff,Brighton & Cole,"Mark Hastings",Daniel Cho,summary_judgment,mixed,51000000,10000000,denied,granted_in_part,credit_limit_models,false,
C-2023-0040,8:23-cv-0040,C.D. Cal.,federal,Hon. Evelyn S. Park,2023-01-09,,trade_secret_misappropriation,streaming_media,plaintiff,Donovan Grant LLP,"Claire Donovan",Michael Lee,summary_judgment,them,68000000,0,denied,granted,session_prediction_models,true,appeal_pending
C-2023-0195,4:23-cv-0195,W.D. Wash.,federal,Hon. Megan L. Chu,2023-03-01,,trade_secret_misappropriation,developer_tools,defendant,Hartley King & Cole,"Julia Hartley",Priya Natarajan,pretrial_dismissal,us,25000000,0,denied,denied,log_indexing_strategies,false,
C-2023-0310,1:23-cv-0310,D. Del.,federal,Hon. Samuel J. Kerr,2023-04-07,,trade_secret_misappropriation,semiconductors,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Daniel Cho,summary_judgment,them,120000000,0,granted_in_part,granted,yield_enhancement_recipes,true,appeal_pending
C-2023-0472,3:23-cv-0472,N.D. Cal.,federal,Hon. Rebecca L. Ames,2023-06-13,,trade_secret_misappropriation,enterprise_software,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Michael Lee,settlement,us,73000000,26000000,denied,denied,contract_renewal_scoring,false,
C-2023-0606,2:23-cv-0606,S.D. Tex.,federal,Hon. Carlos M. Ortiz,2023-08-01,,trade_secret_misappropriation,oilfield_services,plaintiff,Donovan Grant LLP,"Claire Donovan",Priya Natarajan,pretrial_dismissal,them,41000000,5000000,denied,denied,asset_failure_models,false,
C-2023-0799,8:23-cv-0799,C.D. Cal.,federal,Hon. Evelyn S. Park,2023-09-22,,trade_secret_misappropriation,streaming_media,defendant,Brighton & Cole,"Mark Hastings",Daniel Cho,pretrial_dismissal,us,36000000,0,denied,denied,preview_trailer_ranker,false,
C-2024-0102,4:24-cv-0102,W.D. Wash.,federal,Hon. Megan L. Chu,2024-01-18,,trade_secret_misappropriation,cloud_infrastructure,plaintiff,Donovan Grant LLP,"Claire Donovan; Oliver Grant",Michael Lee,summary_judgment,pending,82000000,0,denied,pending,edge_routing_policies,false,
C-2024-0255,1:24-cv-0255,D. Mass.,federal,Hon. Robert T. Hayes,2024-03-05,,trade_secret_misappropriation,healthcare_analytics,plaintiff,Ridgeway & Stone,"Peter Ridgeway",Priya Natarajan,summary_judgment,pending,91000000,0,denied,pending,triage_priority_scores,false,
C-2024-0328,3:24-cv-0328,N.D. Ill.,federal,Hon. Lisa K. Monroe,2024-04-16,,trade_secret_misappropriation,logistics,plaintiff,Donovan Grant LLP,"Claire Donovan",Daniel Cho,summary_judgment,pending,67000000,0,denied,pending,warehouse_slotting_models,false,
C-2024-0490,2:24-cv-0490,S.D.N.Y.,federal,Hon. Angela P. Rivera,2024-06-10,,trade_secret_misappropriation,financial_analytics,defendant,Hartley King & Cole,"Julia Hartley",Michael Lee,pretrial_dismissal,us,54000000,0,denied,denied,stress_testing_scenarios,false,
"""

_RULING_TEXT_CSV = """ruling_id,case_id,docket_entry_no,ruling_stage,motion_type,moving_party,outcome,issue_scope,expert_id,findings_flags_json,decision_date,judge_citation_style_name,key_holdings_text
R-2020-0312-PI,C-2020-0312,42,PI,preliminary_injunction,us,denied,injunctive_relief,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2020-05-22","AMES, J.","Plaintiff has not identified its alleged trade secrets with sufficient particularity to warrant the extraordinary remedy of a preliminary injunction."
R-2020-0312-MSJ1,C-2020-0312,188,MSJ,summary_judgment,them,granted_in_part,liability,, "{\\"spoliation_sanction\\": true, \\"adverse_inference\\": true, \\"trade_secret_defined_narrowly\\": true}","2022-11-03","AMES, J.","The Court imposes an adverse inference based on plaintiff's failure to preserve key source-code repositories and grants summary judgment on misappropriation as to versions predating 2018."
R-2020-0312-DAUBERT-PX1,C-2020-0312,201,Daubert,daubert,them,granted_in_part,damages,EXP-C2020-PL-DAM-1,"{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2023-01-10","AMES, J.","The Court excludes plaintiff's damages expert's unjust-enrichment model for failure to account for non-infringing alternatives, but permits a limited lost-profits opinion."
R-2019-1187-PI,C-2019-1187,28,PI,preliminary_injunction,us,granted_in_part,injunctive_relief,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2019-08-09","KERR, J.","Plaintiff shows a likelihood of success only as to a subset of manufacturing documents that are properly identified with reasonable particularity."
R-2019-1187-MSJ,C-2019-1187,140,MSJ,summary_judgment,them,granted,liability,, "{\\"spoliation_sanction\\": true, \\"adverse_inference\\": true, \\"trade_secret_defined_narrowly\\": true}","2021-02-17","KERR, J.","Given plaintiff's shifting definitions of its alleged trade secrets and the destruction of process-control logs, no reasonable jury could find misappropriation on this record."
R-2019-1187-DAUBERT-PX1,C-2019-1187,133,Daubert,daubert,them,granted,damages,EXP-C2019-PL-DAM-1,"{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2021-01-05","KERR, J.","Plaintiff's damages expert applies a black-box multiplier untethered to the evidence; the report is excluded in full."
R-2021-0904-MSJ,C-2021-0904,96,MSJ,summary_judgment,them,denied,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2023-06-30","RIVERA, J.","Defendant's arguments reprise the 'reasonable particularity' line of cases, but here plaintiff has tied specific deployment playbooks to concrete confidentiality measures."
R-2021-0904-DAUBERT-DX1,C-2021-0904,111,Daubert,daubert,us,denied,damages,EXP-C2021-DF-DAM-1,"{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2023-09-12","RIVERA, J.","The Court finds defendant's damages expert applied a sufficiently reliable differential-revenue method and denies the motion to exclude."
R-2018-0220-PI,C-2018-0220,35,PI,preliminary_injunction,us,denied,injunctive_relief,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2018-03-29","AMES, J.","Plaintiff's real-time bidding algorithms overlap substantially with industry practices, and the record does not show a likelihood of irreparable harm absent an injunction."
R-2019-2044-MSJ,C-2019-2044,89,MSJ,summary_judgment,them,denied,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2021-06-12","MONROE, J.","Defendant's argument that routing heuristics are \\"just math\\" ignores email and version-control evidence tying specific parameter choices to confidential customer performance data."
R-2020-1450-PI,C-2020-1450,27,PI,preliminary_injunction,them,denied,injunctive_relief,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2020-09-01","PARK, J.","Plaintiff's showing of imminent harm is speculative; monetary damages appear adequate at this stage."
R-2022-0678-PI,C-2022-0678,18,PI,preliminary_injunction,us,granted_in_part,injunctive_relief,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2022-04-22","HAYES, J.","Plaintiff has identified specific clinical trial protocols and enrollment criteria as trade secrets and shown a likelihood of success as to those materials only."
R-2022-0678-DAUBERT-PX1,C-2022-0678,77,Daubert,daubert,them,granted_in_part,damages,EXP-C2022-PL-DAM-1,"{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2023-01-19","HAYES, J.","The Court excludes plaintiff's speculative blockbuster-sales scenario but permits a conservative lost-profits model tied to documented deal flow."
R-2019-2044-MSJ2,C-2019-2044,90,MSJ,summary_judgment,them,denied,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2021-06-15","MONROE, J.","Disputes over whether defendant used the three routing heuristics in PX-004 are quintessential jury questions; summary judgment is inappropriate."
R-2020-1450-MSJ,C-2020-1450,132,MSJ,summary_judgment,us,denied,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2022-03-28","PARK, J.","Material factual disputes over independent development of streaming recommendation models preclude summary judgment."
R-2019-0113-MSJ,C-2019-0113,74,MSJ,summary_judgment,them,granted_in_part,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2020-11-09","AMES, J.","Plaintiff's onboarding scoring model is protectable to the extent defined by the specific feature weights disclosed in sealed Appendix A; broader theories are dismissed."
R-2019-0666-MSJ,C-2019-0666,121,MSJ,summary_judgment,them,granted,liability,, "{\\"spoliation_sanction\\": true, \\"adverse_inference\\": true, \\"trade_secret_defined_narrowly\\": true}","2021-04-03","PARK, J.","As in Vertex, plaintiff clings to an 'ad engine as a whole' theory and allowed key auction logs to be overwritten; no reasonable jury could find misappropriation."
R-2020-0044-PI,C-2020-0044,22,PI,preliminary_injunction,us,granted_in_part,injunctive_relief,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2020-04-09","HAYES, J.","Plaintiff shows a likelihood of success as to readmission scorecards tied to specific features and thresholds, but not as to generic risk dashboards."
R-2020-0599-MSJ,C-2020-0599,118,MSJ,summary_judgment,them,granted,liability,, "{\\"spoliation_sanction\\": true, \\"adverse_inference\\": true, \\"trade_secret_defined_narrowly\\": true}","2022-02-14","RIVERA, J.","Plaintiff's high-frequency strategy definitions remained amorphous through discovery, and failure to preserve tick data for key days warrants an adverse inference."
R-2021-0442-MSJ,C-2021-0442,67,MSJ,summary_judgment,them,granted,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2022-01-19","AMES, J.","Plaintiff's role recommendation engine is not meaningfully distinguishable from publicly documented approaches in the record; no triable issue remains."
R-2021-0055-DAUBERT-PX1,C-2021-0055,145,Daubert,daubert,them,granted_in_part,damages,EXP-C2021-DEV-PL-DAM-1,"{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2023-03-02","CHU, J.","The Court excludes plaintiff's speculative productivity uplift model but allows a limited time-saved calculation tied to usage logs."
R-2022-0407-MSJ,C-2022-0407,59,MSJ,summary_judgment,them,granted,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2023-02-27","HAYES, J.","Care gap models derived entirely from Medicare claims data without additional confidential features are not protectable trade secrets on this record."
R-2023-0310-MSJ,C-2023-0310,41,MSJ,summary_judgment,them,granted_in_part,liability,, "{\\"spoliation_sanction\\": true, \\"adverse_inference\\": true, \\"trade_secret_defined_narrowly\\": true}","2024-01-05","KERR, J.","Plaintiff's yield recipes are defined with adequate particularity, but spoliation of furnace calibration logs justifies narrowing the case to two later recipe sets."
R-2018-0220-MSJ,C-2018-0220,88,MSJ,summary_judgment,them,denied,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2019-02-14","AMES, J.","The parties' cross-motions for summary judgment are denied; disputes over whether Plaintiff's bidding stack contains any protectable, non-public components must be resolved by a jury."
R-2021-0055-MSJ,C-2021-0055,93,MSJ,summary_judgment,them,denied,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": false}","2023-02-10","CHU, J.","Whether Defendant misused Plaintiff's CI/CD optimization design choices turns on disputed fact questions regarding what was disclosed to former employees and how Defendant implemented its own pipelines."
R-2023-0040-MSJ,C-2023-0040,37,MSJ,summary_judgment,them,granted,liability,, "{\\"spoliation_sanction\\": false, \\"adverse_inference\\": false, \\"trade_secret_defined_narrowly\\": true}","2024-05-03","PARK, J.","Plaintiff's session prediction models are described at a high level in its own marketing materials, and Plaintiff has failed to identify any specific, non-public mechanisms that could support a trade secret verdict."
"""

_EXPERTS_CSV = """expert_id,case_id,side,expert_name,discipline,primary_issue,report_filename,deposition_taken,daubert_motion_filed,daubert_outcome,trial_testimony_given,jury_reliance_indicator
EXP-C2020-PL-DAM-1,C-2020-0312,us,Dr. Hannah Liu,damages,lost_profits,expert_reports/C-2020-0312_PX_Damages_Expert_Liu.pdf,true,true,granted_in_part,true,limited_plaintiff_damages
EXP-C2020-DF-TECH-1,C-2020-0312,them,Dr. Alan Ortiz,forensics,misappropriation,expert_reports/C-2020-0312_DX_Forensics_Ortiz.pdf,true,true,denied,true,relied_on_defense_technical
EXP-C2019-PL-DAM-1,C-2019-1187,us,Prof. Elena Markovic,damages,unjust_enrichment,expert_reports/C-2019-1187_PX_Damages_Expert_Markovic.pdf,true,true,granted,false,excluded_plaintiff_expert
EXP-C2019-DF-IND-1,C-2019-1187,them,James Patel,industry_practices,misappropriation,expert_reports/C-2019-1187_DX_Industry_Expert_Patel.pdf,true,false,none,true,relied_on_defense_industry
EXP-C2021-DF-DAM-1,C-2021-0904,us,Dr. Sofia Bennett,damages,lost_profits,expert_reports/C-2021-0904_DX_Damages_Expert_Bennett.pdf,true,true,denied,true,relied_on_defense_damages
EXP-C2021-PL-TECH-1,C-2021-0904,them,Dr. Marcus Hale,forensics,misappropriation,expert_reports/C-2021-0904_PX_Forensics_Expert_Hale.pdf,true,true,denied,true,mixed_weight
EXP-C2018-PL-ALGO-1,C-2018-0220,us,Dr. Karen Soto,damages,valuation,expert_reports/C-2018-0220_PX_Valuation_Expert_Soto.pdf,true,true,denied,false,limited_plaintiff_damages
EXP-C2018-DF-ADTECH-1,C-2018-0220,them,Dr. Neil Fraser,industry_practices,misappropriation,expert_reports/C-2018-0220_DX_Industry_Expert_Fraser.pdf,true,false,none,false,relied_on_defense_industry
EXP-C2019-LOG-PL-1,C-2019-2044,us,Dr. Victor Han,damages,lost_profits,expert_reports/C-2019-2044_PX_Damages_Expert_Han.pdf,true,true,denied,true,relied_on_plaintiff_damages
EXP-C2019-LOG-DF-1,C-2019-2044,them,Laura Beck,statistics,causation,expert_reports/C-2019-2044_DX_Stats_Expert_Beck.pdf,true,true,denied,true,limited_defense_causation
EXP-C2020-STREAM-DF-1,C-2020-1450,us,Dr. Omar Singh,damages,apportionment,expert_reports/C-2020-1450_DX_Damages_Expert_Singh.pdf,true,true,granted_in_part,true,limited_defense_damages
EXP-C2020-STREAM-PL-1,C-2020-1450,them,Prof. Alyssa Grant,damages,unjust_enrichment,expert_reports/C-2020-1450_PX_Damages_Expert_Grant.pdf,true,false,none,true,relied_on_plaintiff_damages
EXP-C2022-PL-DAM-1,C-2022-0678,us,Dr. Naomi Keller,damages,lost_profits,expert_reports/C-2022-0678_PX_Damages_Expert_Keller.pdf,true,true,granted_in_part,false,excluded_plaintiff_expert
EXP-C2019-LOG-CAUSE-1,C-2019-2044,them,Dr. Irene Costa,statistics,causation,expert_reports/C-2019-2044_DX_Stats_Expert_Costa.pdf,true,true,denied,true,limited_defense_causation
EXP-C2020-STREAM-TECH-1,C-2020-1450,us,Dr. Felix Romero,forensics,misappropriation,expert_reports/C-2020-1450_DX_Forensics_Expert_Romero.pdf,true,true,denied,true,relied_on_defense_technical
EXP-C2019-ONBOARD-PL-1,C-2019-0113,us,Dr. Lila Chen,damages,lost_profits,expert_reports/C-2019-0113_PX_Damages_Expert_Chen.pdf,true,true,denied,true,relied_on_plaintiff_damages
EXP-C2019-ONBOARD-DF-1,C-2019-0113,them,Mark Hastings,industry_practices,misappropriation,expert_reports/C-2019-0113_DX_Industry_Expert_Hastings.pdf,true,false,none,true,mixed_weight
EXP-C2019-AD-PL-1,C-2019-0666,us,Prof. Rajiv Malhotra,damages,unjust_enrichment,expert_reports/C-2019-0666_PX_Damages_Expert_Malhotra.pdf,true,true,granted,false,excluded_plaintiff_expert
EXP-C2020-HF-PL-1,C-2020-0599,us,Dr. Emily Kovacs,damages,lost_profits,expert_reports/C-2020-0599_PX_Damages_Expert_Kovacs.pdf,true,true,granted_in_part,false,limited_plaintiff_damages
EXP-C2020-HF-DF-1,C-2020-0599,them,Dr. Andre Silva,forensics,misappropriation,expert_reports/C-2020-0599_DX_Forensics_Expert_Silva.pdf,true,false,none,true,relied_on_defense_technical
EXP-C2021-DEV-PL-DAM-1,C-2021-0055,us,Prof. Hannah Ortiz,damages,productivity,expert_reports/C-2021-0055_PX_Damages_Expert_Ortiz.pdf,true,true,granted_in_part,false,limited_plaintiff_damages
EXP-C2022-CARE-PL-1,C-2022-0407,us,Dr. Aisha Rahman,statistics,misappropriation,expert_reports/C-2022-0407_PX_Stats_Expert_Rahman.pdf,true,true,denied,true,mixed_weight
EXP-C2023-YIELD-PL-1,C-2023-0310,us,Dr. Matteo Ricci,damages,lost_profits,expert_reports/C-2023-0310_PX_Damages_Expert_Ricci.pdf,true,true,granted_in_part,false,excluded_plaintiff_expert
EXP-C2023-YIELD-DF-1,C-2023-0310,them,Dr. Sunhee Park,industry_practices,misappropriation,expert_reports/C-2023-0310_DX_Industry_Expert_Park.pdf,true,false,none,true,relied_on_defense_industry
EXP-G1000,C-2017-0541,us,Prof. David Foster,statistics,causation,expert_reports/C-2017-0541_PX_Statistics_Foster.pdf,true,true,granted,true,mixed_weight
EXP-G1001,C-2017-0541,them,Dr. Sarah Brooks,forensics,valuation,expert_reports/C-2017-0541_DX_Forensics_Brooks.pdf,false,true,none,true,relied_on_defense_damages
EXP-G1002,C-2022-0678,us,Dr. James Hayes,forensics,lost_profits,expert_reports/C-2022-0678_PX_Forensics_Hayes.pdf,true,false,none,false,mixed_weight
EXP-G1003,C-2023-0129,them,Prof. Maria Rivera,forensics,causation,expert_reports/C-2023-0129_DX_Forensics_Rivera.pdf,true,false,none,true,mixed_weight
EXP-G1004,C-2023-0129,us,Dr. Robert Ward,damages,lost_profits,expert_reports/C-2023-0129_PX_Damages_Ward.pdf,false,true,none,false,
EXP-G1005,C-2016-0001,them,Dr. Jennifer Peterson,statistics,causation,expert_reports/C-2016-0001_DX_Statistics_Peterson.pdf,true,true,denied,false,
EXP-G1006,C-2016-0001,us,Prof. Thomas Gray,damages,misappropriation,expert_reports/C-2016-0001_PX_Damages_Gray.pdf,true,false,none,false,
EXP-G1007,C-2016-0034,them,Dr. Linda Ramirez,forensics,valuation,expert_reports/C-2016-0034_DX_Forensics_Ramirez.pdf,true,false,none,true,relied_on_plaintiff_damages
EXP-G1008,C-2016-0034,us,Dr. Daniel James,damages,misappropriation,expert_reports/C-2016-0034_PX_Damages_James.pdf,true,true,granted,false,
EXP-G1009,C-2016-0450,them,Prof. Patricia Watson,damages,valuation,expert_reports/C-2016-0450_DX_Damages_Watson.pdf,true,false,none,false,
EXP-G1010,C-2016-0450,us,Dr. Paul Reed,forensics,unjust_enrichment,expert_reports/C-2016-0450_PX_Forensics_Reed.pdf,true,true,granted_in_part,true,relied_on_defense_technical
EXP-G1011,C-2017-0102,them,Dr. Nancy Cook,damages,apportionment,expert_reports/C-2017-0102_DX_Damages_Cook.pdf,true,false,none,true,relied_on_defense_damages
EXP-G1012,C-2017-0102,us,Prof. Mark Morgan,forensics,causation,expert_reports/C-2017-0102_PX_Forensics_Morgan.pdf,true,true,granted_in_part,false,
EXP-G1013,C-2017-0209,them,Dr. Betty Bell,forensics,apportionment,expert_reports/C-2017-0209_DX_Forensics_Bell.pdf,true,false,none,true,relied_on_plaintiff_damages
EXP-G1014,C-2017-0209,us,Dr. Steven Murphy,damages,causation,expert_reports/C-2017-0209_PX_Damages_Murphy.pdf,true,false,none,false,
EXP-G1015,C-2017-0788,them,Prof. Margaret Bailey,damages,valuation,expert_reports/C-2017-0788_DX_Damages_Bailey.pdf,true,true,granted,false,
EXP-G1016,C-2017-0788,us,Dr. Andrew Cooper,damages,unjust_enrichment,expert_reports/C-2017-0788_PX_Damages_Cooper.pdf,true,true,granted,false,
EXP-G1017,C-2018-0055,them,Dr. Sandra Richardson,damages,lost_profits,expert_reports/C-2018-0055_DX_Damages_Richardson.pdf,true,true,denied,false,
EXP-G1018,C-2018-0055,us,Prof. Joshua Cox,damages,valuation,expert_reports/C-2018-0055_PX_Damages_Cox.pdf,true,true,granted_in_part,false,
EXP-G1019,C-2018-0199,them,Dr. Dorothy Howard,industry_practices,causation,expert_reports/C-2018-0199_DX_Industry_practices_Howard.pdf,true,true,none,false,
EXP-G1020,C-2018-0199,us,Dr. Kevin Torres,forensics,causation,expert_reports/C-2018-0199_PX_Forensics_Torres.pdf,true,false,none,true,relied_on_defense_damages
EXP-G1021,C-2018-0301,them,Prof. Lisa Powell,damages,causation,expert_reports/C-2018-0301_DX_Damages_Powell.pdf,false,false,none,false,
EXP-G1022,C-2018-0301,us,Dr. Brian Long,damages,misappropriation,expert_reports/C-2018-0301_PX_Damages_Long.pdf,true,true,granted_in_part,false,
EXP-G1023,C-2018-0670,them,Dr. Karen Patterson,industry_practices,unjust_enrichment,expert_reports/C-2018-0670_DX_Industry_practices_Patterson.pdf,true,false,none,false,
EXP-G1024,C-2018-0670,us,Prof. George Hughes,statistics,valuation,expert_reports/C-2018-0670_PX_Statistics_Hughes.pdf,false,true,granted_in_part,false,
EXP-G1025,C-2019-0307,them,Dr. Helen Flores,damages,unjust_enrichment,expert_reports/C-2019-0307_DX_Damages_Flores.pdf,true,false,none,false,
EXP-G1026,C-2019-0307,us,Dr. Edward Washington,forensics,causation,expert_reports/C-2019-0307_PX_Forensics_Washington.pdf,true,true,none,true,relied_on_defense_technical
EXP-G1027,C-2019-0666,them,Prof. Carol Butler,damages,causation,expert_reports/C-2019-0666_DX_Damages_Butler.pdf,true,false,none,true,
EXP-G1028,C-2019-0901,us,Dr. Ronald Simmons,forensics,unjust_enrichment,expert_reports/C-2019-0901_PX_Forensics_Simmons.pdf,true,true,granted,false,
EXP-G1029,C-2019-0901,them,Dr. Michelle Foster,damages,apportionment,expert_reports/C-2019-0901_DX_Damages_Foster.pdf,true,true,none,false,
EXP-G1030,C-2020-0044,us,Prof. Timothy Gonzales,statistics,misappropriation,expert_reports/C-2020-0044_PX_Statistics_Gonzales.pdf,true,true,granted_in_part,true,limited_plaintiff_damages
EXP-G1031,C-2020-0044,them,Dr. Amanda Bryant,forensics,causation,expert_reports/C-2020-0044_DX_Forensics_Bryant.pdf,true,true,denied,false,
EXP-G1032,C-2020-0208,us,Dr. Jason Alexander,industry_practices,lost_profits,expert_reports/C-2020-0208_PX_Industry_practices_Alexander.pdf,true,false,none,true,relied_on_defense_industry
EXP-G1033,C-2020-0208,them,Prof. Stephanie Russell,damages,causation,expert_reports/C-2020-0208_DX_Damages_Russell.pdf,false,false,none,false,mixed_weight
EXP-G1034,C-2020-0880,us,Dr. Ryan Griffin,forensics,unjust_enrichment,expert_reports/C-2020-0880_PX_Forensics_Griffin.pdf,true,false,none,true,relied_on_defense_industry
EXP-G1035,C-2020-0880,them,Dr. Melissa Diaz,statistics,causation,expert_reports/C-2020-0880_DX_Statistics_Diaz.pdf,true,false,none,true,relied_on_plaintiff_damages
"""

_CITATION_NETWORK_CSV = """source_case_id,target_case_citation,target_case_id,citation_context,citing_document_type,citing_side,precedent_issue,treatment,strength_indicator
C-2020-0312,"Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016)",,motion,plaintiff_motion,us,inevitable_disclosure,distinguished,1
C-2020-0312,"Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016)",,ruling,court_order,judge,inevitable_disclosure,limited,2
C-2020-0312,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,3
C-2020-0312,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,ruling,court_order,judge,trade_secret_identification,followed,3
C-2020-0312,"Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010)","HC-TS-2010-HEL",motion,defense_motion,them,spoliation,followed,2
C-2019-1187,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,2
C-2019-1187,"Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010)","HC-TS-2010-HEL",motion,defense_motion,them,spoliation,followed,3
C-2019-1187,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,ruling,court_order,judge,reasonable_measures,followed,1
C-2021-0904,"Vertex Systems, Inc. v. Nova Tech Corp., 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,2
C-2021-0904,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,ruling,court_order,judge,trade_secret_identification,distinguished,2
C-2021-0904,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,motion,plaintiff_motion,them,reasonable_measures,followed,2
C-2018-0220,"Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016)",,motion,plaintiff_motion,us,inevitable_disclosure,followed,1
C-2018-0220,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,2
C-2019-2044,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,motion,plaintiff_motion,us,reasonable_measures,followed,2
C-2019-2044,"Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010)","HC-TS-2010-HEL",ruling,court_order,judge,spoliation,rejected,1
C-2020-1450,"Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016)",,motion,plaintiff_motion,them,inevitable_disclosure,followed,2
C-2022-0678,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,2
C-2022-0678,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,ruling,court_order,judge,reasonable_measures,followed,2
C-2019-2044,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,ruling,court_order,judge,reasonable_measures,followed,2
C-2020-1450,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,distinguished,1
C-2019-0113,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,ruling,court_order,judge,trade_secret_identification,followed,2
C-2019-0666,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,3
C-2019-0666,"Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010)","HC-TS-2010-HEL",ruling,court_order,judge,spoliation,followed,3
C-2020-0044,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,motion,plaintiff_motion,us,reasonable_measures,followed,1
C-2020-0599,"Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016)",,motion,plaintiff_motion,us,inevitable_disclosure,rejected,1
C-2020-0599,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,ruling,court_order,judge,trade_secret_identification,followed,2
C-2021-0442,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,3
C-2022-0407,"Quantum Metrics v. Dynacore, 611 F.3d 857 (3d Cir. 2012)",,motion,defense_motion,them,reasonable_measures,followed,2
C-2023-0310,"Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019)",,motion,defense_motion,them,trade_secret_identification,followed,3
C-2023-0310,"Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010)","HC-TS-2010-HEL",motion,defense_motion,them,spoliation,followed,2
"""


def _deposition_records():
    """Yield deposition records across all cases (anchor + synthetic)."""
    case_ids = _all_case_ids()
    n_cases = len(case_ids)
    names = ["Laura Chen", "Evan Morales", "Harish Rao", "Ryan Lopez", "Jonas Meyer", "Emily Zhang",
             "Chloe Diaz", "Nikhil Rao", "Sonia Patel", "Emily Kovacs", "Aisha Rahman", "Matteo Ricci"]
    roles = ["plaintiff_30b6", "defendant_engineer", "plaintiff_30b6", "plaintiff_product_manager",
             "plaintiff_data_science_lead", "plaintiff_ops_director", "plaintiff_growth_head", "plaintiff_pm",
             "plaintiff_adops_lead", "plaintiff_quant_lead", "plaintiff_data_science_lead", "plaintiff_process_engineer"]
    num_depos = min(120, max(60, n_cases * 2))
    for i in range(num_depos):
        c = case_ids[i % n_cases]
        seg = [{"page_start": 20, "page_end": 22, "speaker": "ATTY", "text": "Q. Trade secret identification?\\nA. As produced.", "topic_tags": ["trade_secret_identification"], "uncertainty_flag": False, "impeachment_reference": "", "objection_flag": False}]
        yield {"case_id": c, "depo_id": f"{c}_DEP_{i:03d}", "witness_name": names[i % 12], "witness_role": roles[i % 12], "side_calling_witness": "them" if i % 2 else "us", "date": "2021-03-18", "segments": seg, "metadata": {"hours": 4.0, "location": "Remote"}}


_MOTION_FILES = {
    "C-2020-0312_MSJ_defense_donovan-grant.txt": """CASE_ID: C-2020-0312
MOTION_TYPE: MSJ
SIDE: defendant

INTRODUCTION

Defendant respectfully moves for summary judgment. After three years of discovery, plaintiff still cannot say what its alleged trade secrets are with reasonable particularity, nor can it trace any specific secret to any feature of our product. At most, plaintiff asserts vague rights in a "platform as a whole" that looks like every other modern analytics stack.

STATEMENT OF FACTS

Plaintiff's Rule 30(b)(6) designee, Laura Chen, could not identify a single document or repository that embodies the alleged trade secrets. (Chen Dep. 45:7–47:19.) Instead, she testified that "it's really the platform as a whole," a formulation multiple courts have rejected. Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019).

ARGUMENT

I. PLAINTIFF HAS FAILED TO IDENTIFY ITS ALLEGED TRADE SECRETS WITH REASONABLE PARTICULARITY.

Courts routinely grant summary judgment where, as here, a plaintiff insists that its entire product or "way of doing business" is the secret. See Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019) (affirming summary judgment where plaintiff's trade secret definition shifted and encompassed an entire software suite).

II. PLAINTIFF'S DISCOVERY MISCONDUCT WARRANTS AN ADVERSE INFERENCE AND NARROWING OF THE CASE.

Key pre-2018 source-code repositories were not preserved, and plaintiff produced the PX-031 "security roadmap" only after Donovan Grant LLP raised gaps in access-control evidence. Under Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010), the Court should impose an adverse inference and cabin the case to post-2018 versions for which some logs remain.
""",
    "C-2020-0312_MSJ_plaintiff_halcyon.txt": """CASE_ID: C-2020-0312
MOTION_TYPE: MSJ
SIDE: plaintiff

INTRODUCTION

Halcyon & Pierce LLP, on behalf of its client, moves for partial summary judgment on liability for trade secret misappropriation. Defendant's competing platform emerged only months after key engineers departed our client, and internal emails (e.g., DX-104) make clear that the design was informed by confidential discussions under NDA.

STATEMENT OF FACTS

Plaintiff has invested over a decade in developing its end-to-end analytics platform. While the system is complex, the trade secrets at issue are best understood as the platform as a whole: the source code, machine learning models, data pipelines, and orchestration logic that together deliver real-time insights for enterprise customers.

ARGUMENT

I. DEFENDANT'S PLATFORM IS SUBSTANTIALLY SIMILAR TO PLAINTIFF'S PROTECTED PLATFORM AS A WHOLE.

Our client does not contend that any single file standing alone is the trade secret. Rather, the combination of architectural choices, feature ordering, and performance optimizations constitutes a protectable body of confidential know-how. See Acme Analytics v. Orion Data, 812 F.3d 413 (9th Cir. 2016).

II. INEVITABLE DISCLOSURE SUPPORTS AN INFERENCE OF MISAPPROPRIATION.

Given the overlap in engineering teams and functionality, misappropriation can be inferred even absent direct evidence of copying. The same engineers cannot unlearn the core concepts they developed at plaintiff. See id.
""",
}
# Add remaining 18 motion filenames with short placeholder content
for _f in ["C-2023-0040_MSJ_defense_donovan.txt", "C-2018-0301_MSJ_defense_donovan-grant.txt", "C-2017-0209_MSJ_defense_donovan.txt", "C-2020-1450_PI_plaintiff_streaming.txt", "C-2021-0442_MSJ_defense_donovan.txt", "C-2021-0055_MSJ_plaintiff_halcyon.txt", "C-2022-0678_PI_plaintiff_halcyon.txt", "C-2022-0678_Daubert_defense_donovan-grant.txt", "C-2018-0220_MSJ_plaintiff_halcyon.txt", "C-2018-0220_MSJ_defense_donovan-grant.txt", "C-2020-0044_PI_plaintiff_halcyon.txt", "C-2023-0310_MSJ_defense_donovan-grant.txt", "C-2020-0599_MSJ_defense_donovan-grant.txt", "C-2019-0666_MSJ_defense_donovan-grant.txt", "C-2019-0113_MSJ_defense_donovan.txt", "C-2019-2044_MSJ_defense_hartley-king-cole.txt", "C-2021-0904_MSJ_defense_brighton-cole.txt", "C-2019-1187_MSJ_defense_donovan.txt"]:
    if _f not in _MOTION_FILES:
        _MOTION_FILES[_f] = "CASE_ID: " + _f[:11] + "\nMOTION_TYPE: MSJ/PI/Daubert\nSIDE: plaintiff/defendant\n\nPlaceholder motion text.\n"

_RULING_FILES = {
    "C-2020-0312_Order_MSJ_excerpt.txt": """This matter comes before the Court on Defendant's motion for summary judgment. For the reasons set forth below, the motion is GRANTED IN PART and DENIED IN PART.

Plaintiff has repeatedly characterized its trade secrets as its "platform as a whole." Its Rule 30(b)(6) designee, Chen, could not identify any discrete files, repositories, or design documents that embody the alleged secrets. This failure to articulate the claimed secrets with reasonable particularity is inconsistent with Vertex Systems v. NovaTech, 945 F.3d 102 (9th Cir. 2019), and similar authorities.

Moreover, plaintiff did not preserve certain pre-2018 source-code repositories and produced the PX-031 "security roadmap" only after Defendant highlighted gaps in its access-control evidence. Under Helios Labs v. Solace Corp., 721 F. Supp. 2d 1189 (N.D. Cal. 2010), the Court imposes an adverse inference that the missing materials would not have supported plaintiff's theory.

Accordingly, the Court grants summary judgment as to alleged misappropriation of any versions of the platform predating 2018. The motion is otherwise denied.
""",
}
for _f in ["C-2023-0040_Order_MSJ_excerpt.txt", "C-2019-1187_Order_PI_excerpt.txt", "C-2018-0220_Order_PI_excerpt.txt", "C-2023-0310_Order_MSJ_excerpt.txt", "C-2022-0407_Order_MSJ_excerpt.txt", "C-2021-0055_Order_Daubert_excerpt.txt", "C-2021-0442_Order_MSJ_excerpt.txt", "C-2019-0113_Order_MSJ_excerpt.txt", "C-2019-0666_Order_MSJ_excerpt.txt", "C-2020-0599_Order_MSJ_excerpt.txt", "C-2020-0044_Order_PI_excerpt.txt", "C-2022-0678_Order_Daubert_excerpt.txt", "C-2022-0678_Order_PI_excerpt.txt", "C-2020-1450_Order_MSJ_excerpt.txt", "C-2020-1450_Order_PI_excerpt.txt", "C-2019-2044_Order_MSJ_excerpt.txt", "C-2018-0220_Order_MSJ_excerpt.txt", "C-2021-0904_Order_MSJ_excerpt.txt", "C-2019-1187_Order_MSJ_excerpt.txt"]:
    if _f not in _RULING_FILES:
        _RULING_FILES[_f] = "Order excerpt placeholder. Motion granted/denied in part.\n"


if __name__ == "__main__":
    main()
