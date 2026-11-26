# Lease extraction results

Run at 2026-11-26 17:08. Model: claude-opus-5-5 (effort high). 8 leases, 17 fields each.

**Fields correct: 136/136 (100%)**

- Wrong values flagged for review by the checks: 0/0
- Wrong values that slipped through unflagged: 0
- Correct values flagged anyway (extra review work): 18
- Deliberate conflicts flagged: 2/2
- Calls that failed (not scored): 0

| Field | Correct |
|---|---|
| landlord | 8/8 |
| tenant | 8/8 |
| premises | 8/8 |
| permitted_use | 8/8 |
| commencement_date | 8/8 |
| term_months | 8/8 |
| expiry_date | 8/8 |
| annual_rent | 8/8 |
| rent_review_type | 8/8 |
| fixed_review_percent | 8/8 |
| number_of_options | 8/8 |
| option_term_months | 8/8 |
| security_type | 8/8 |
| security_amount | 8/8 |
| outgoings_percent | 8/8 |
| break_clause | 8/8 |
| break_notice_months | 8/8 |

| Lease | Correct | Flags raised |
|---|---|---|
| L01-two-spoons-cafe.md | 17/17 | 2 |
| L02-northgate-accounting.md | 17/17 | 5 |
| L03-freshroute-logistics.md | 17/17 | 5 |
| L04-lakeside-physio.md | 17/17 | 5 |
| L05-priyas-threads.md | 17/17 | 0 |
| L06-coastline-digital.md | 17/17 | 0 |
| L07-ironbark-strength.md | 17/17 | 4 |
| L08-saltwater-board-co.md | 17/17 | 3 |

## Correct values that were flagged

- L01 security_amount = `14850.0`: check: amount was calculated, not stated; check the maths; check: Claude: Security is stated as a formula (3 months' Base Rent plus GST). Calculated as $54,000 / 12 x 3 = $13,500, plus 10% GST of $1,350 = $14,850. The amount excluding GST would be $13,500. Please confirm which figure is wanted for the register and whether it should be based on the starting rent or on reviewed rent.
- L02 landlord = `Collins Lane Nominees Pty Ltd as trustee for the Collins Lane Unit Trust`: check: Claude: The Landlord contracts as trustee for the Collins Lane Unit Trust; the trustee capacity has been included in the name. Confirm how the register should record trustee landlords.
- L02 annual_rent = `86400.0`: check: Claude: Rent is stated monthly ($7,200 per month plus GST); the annual figure of $86,400 was calculated as $7,200 x 12.
- L02 rent_review_type = `cpi`: check: Claude: CPI reviews apply on each anniversary during the initial term, with a no-decrease provision. A market review applies only at the start of any further term (clause 4.3), so the initial-term review type has been recorded as cpi.
- L02 break_clause = `True`: check: Claude: The Tenant's break right can only be used for a termination date after 15 March 2027 and requires a termination fee equal to 2 months' rent.
- L02 break_notice_months = `6`: check: Claude: The Tenant's break right can only be used for a termination date after 15 March 2027 and requires a termination fee equal to 2 months' rent.
- L03 term_months = `96`: check: Claude: The Deed of Variation dated 12 May 2025 changed the Schedule term from 7 years (expiry 30 June 2031) to 8 years (expiry 30 June 2032). The varied values are reported.
- L03 expiry_date = `2032-06-30`: check: Claude: The Deed of Variation dated 12 May 2025 changed the Schedule term from 7 years (expiry 30 June 2031) to 8 years (expiry 30 June 2032). The varied values are reported.
- L03 rent_review_type = `mixed`: check: Claude: Item 8 provides fixed 3.5% increases on each anniversary, with a market review on 1 July 2028 instead, so the review type is reported as mixed. The deed did not address reviews. The fixed 3.5% increases presumably apply to the added year (1 July 2031), but this should be confirmed.
- L03 fixed_review_percent = `3.5`: check: Claude: Item 8 provides fixed 3.5% increases on each anniversary, with a market review on 1 July 2028 instead, so the review type is reported as mixed. The deed did not address reviews. The fixed 3.5% increases presumably apply to the added year (1 July 2031), but this should be confirmed.
- L03 security_amount = `171600.0`: check: Claude: The bank guarantee of $171,600 equals 6 months' base rent ($156,000) plus GST. It was not adjusted by the Deed of Variation, and clause 6 requires it to be held until 3 months after the end of the lease. Check whether the guarantee needs extending to cover the new expiry date.
- L04 rent_review_type = `market`: check: Claude: The market reviews include a ratchet: rent cannot fall below the rent payable immediately before each review (clause 4).
- L04 security_type = `none`: check: Claude: No bond or bank guarantee is held; security is a personal guarantee from Thomas Okafor only (clause 6), recorded as none per the register rules.
- L04 security_amount = `None`: check: Claude: No bond or bank guarantee is held; security is a personal guarantee from Thomas Okafor only (clause 6), recorded as none per the register rules.
- L04 break_clause = `True`: check: Claude: The landlord's redevelopment termination right can only be exercised after 1 October 2030 and requires payment of the tenant's reasonable relocation costs. Check whether the Retail Leases Act 1993 (Vic) applies to this lease, as it may impose further requirements on demolition clauses.
- L04 break_notice_months = `6`: check: Claude: The landlord's redevelopment termination right can only be exercised after 1 October 2030 and requires payment of the tenant's reasonable relocation costs. Check whether the Retail Leases Act 1993 (Vic) applies to this lease, as it may impose further requirements on demolition clauses.
- L08 annual_rent = `66000.0`: check: Claude: Item 7 states Base Rent of $72,000 per annum plus GST, but Special Condition 1 (which prevails under clause 1) sets first-year Base Rent at $66,000 per annum plus GST, with the first 4% fixed review applying to $66,000. Recorded $66,000 as rent payable from commencement; note the $72,000 figure in Item 7 does not apply in year 1.; check: Claude: Bank guarantee of $19,800 equals 3 months of the Item 7 rent ($72,000) plus GST. At the reduced first-year rent of $66,000 the equivalent would be $18,150. The stated amount of $19,800 has been recorded; check whether the security was intended to be adjusted.
- L08 security_amount = `19800.0`: check: Claude: Bank guarantee of $19,800 equals 3 months of the Item 7 rent ($72,000) plus GST. At the reduced first-year rent of $66,000 the equivalent would be $18,150. The stated amount of $19,800 has been recorded; check whether the security was intended to be adjusted.

## Cost and speed

- $0.260 total, $0.032 per lease
- 11s per lease on average
- Models that answered: ['claude-opus-5-5']; fallbacks used: 0

Labels were written together with the fictional leases. Eight leases is a small sample, so treat percentages as indicative.
