package internal

import (
	"encoding/csv"
	"os"
	"path/filepath"
)

// Case represents a single case record (CSV row).
// JSON tags use camelCase for API responses.
type Case struct {
	CaseID                 string `json:"caseId"`
	DocketNumber           string `json:"docketNumber"`
	CourtName              string `json:"courtName"`
	JurisdictionType       string `json:"jurisdictionType"`
	JudgeName              string `json:"judgeName"`
	FiledDate              string `json:"filedDate"`
	TrialDate              string `json:"trialDate"`
	CaseType               string `json:"caseType"`
	IndustrySector         string `json:"industrySector"`
	OurRole                string `json:"ourRole"`
	OpposingFirmName       string `json:"opposingFirmName"`
	OpposingLeadCounsel    string `json:"opposingLeadCounsel"`
	OurLeadCounsel         string `json:"ourLeadCounsel"`
	ResolvedVia            string `json:"resolvedVia"`
	VerdictFor             string `json:"verdictFor"`
	TotalDamagesClaimed    string `json:"totalDamagesClaimed"`
	DamagesAwarded         string `json:"damagesAwarded"`
	PIMotionOutcome        string `json:"piMotionOutcome"`
	SummaryJudgmentOutcome string `json:"summaryJudgmentOutcome"`
	TradeSecretProfile     string `json:"tradeSecretProfile"`
	AppealFlag             string `json:"appealFlag"`
	AppealOutcome          string `json:"appealOutcome"`
}

// LoadCases reads cases from seed_data/cases.csv.
func LoadCases(seedDir string) ([]Case, error) {
	path := filepath.Join(seedDir, "cases.csv")
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	r := csv.NewReader(f)
	rows, err := r.ReadAll()
	if err != nil {
		return nil, err
	}
	if len(rows) < 2 {
		return []Case{}, nil
	}
	headers := rows[0]
	idx := make(map[string]int)
	for i, h := range headers {
		idx[h] = i
	}
	get := func(row []string, key string) string {
		if i, ok := idx[key]; ok && i < len(row) {
			return row[i]
		}
		return ""
	}
	var out []Case
	for _, row := range rows[1:] {
		out = append(out, Case{
			CaseID:                 get(row, "case_id"),
			DocketNumber:           get(row, "docket_number"),
			CourtName:              get(row, "court_name"),
			JurisdictionType:       get(row, "jurisdiction_type"),
			JudgeName:              get(row, "judge_name"),
			FiledDate:              get(row, "filed_date"),
			TrialDate:              get(row, "trial_date"),
			CaseType:               get(row, "case_type"),
			IndustrySector:         get(row, "industry_sector"),
			OurRole:                get(row, "our_role"),
			OpposingFirmName:       get(row, "opposing_firm_name"),
			OpposingLeadCounsel:    get(row, "opposing_lead_counsel"),
			OurLeadCounsel:         get(row, "our_lead_counsel"),
			ResolvedVia:            get(row, "resolved_via"),
			VerdictFor:             get(row, "verdict_for"),
			TotalDamagesClaimed:    get(row, "total_damages_claimed"),
			DamagesAwarded:         get(row, "damages_awarded"),
			PIMotionOutcome:        get(row, "pi_motion_outcome"),
			SummaryJudgmentOutcome: get(row, "summary_judgment_outcome"),
			TradeSecretProfile:     get(row, "trade_secret_profile"),
			AppealFlag:             get(row, "appeal_flag"),
			AppealOutcome:          get(row, "appeal_outcome"),
		})
	}
	return out, nil
}
