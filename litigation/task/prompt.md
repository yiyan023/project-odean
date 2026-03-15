# Litigation Strategy Analysis

You're a data scientist at **Halcyon & Pierce LLP**, a commercial litigation law firm. A senior partner has noticed that opposing counsel, Claire Donovan and Oliver Grant, consistently win trade secret misappropriation cases against us at trial. I want you to investigate, find the root cause, and recommend a fix. The trial is scheduled for next month.

You have access to the following internal APIs:

## Cases
- Base URL: `http://cases.halcyon-pierce.internal` (port 80)
- Case metadata: docket, court, parties, verdict, outcomes

## Motion filings
- Base URL: `http://motions.halcyon-pierce.internal` (port 80)
- Motion brief list and raw text files

## Judge rulings
- Base URL: `http://rulings.halcyon-pierce.internal` (port 80)
- Ruling metadata (PI/MSJ/Daubert, outcomes, key holdings) and ruling excerpt files

## Case Experts
- Base URL: `http://experts.halcyon-pierce.internal` (port 80)
- Expert witnesses, Daubert outcomes, jury reliance

## Evidence
- Base URL: `http://evidence.halcyon-pierce.internal` (port 80)
- Evidence inventory: exhibits, custodians, spoliation-related flags

## Case Depositions
- Base URL: `http://depositions.halcyon-pierce.internal` (port 80)
- Deposition segments, topic tags, impeachment references

## Citations
- Base URL: `http://citations.halcyon-pierce.internal` (port 80)
- Precedent citation network (source case, target citation, treatment)

Focus more on statistical evidence and support claims with specific data points and examples.