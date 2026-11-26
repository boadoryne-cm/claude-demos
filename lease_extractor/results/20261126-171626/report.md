# Lease extraction results

Run at 2026-11-26 17:16. Model: claude-opus-5-5 (effort high). 8 leases, 17 fields each.

**Fields correct: 136/136 (100%)**

- Wrong values flagged for review by the checks: 0/0
- Wrong values that slipped through unflagged: 0
- Correct values flagged anyway (extra review work): 21
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
| L05-priyas-threads.md | 17/17 | 3 |
| L06-coastline-digital.md | 17/17 | 0 |
| L07-ironbark-strength.md | 17/17 | 4 |
| L08-saltwater-board-co.md | 17/17 | 3 |

## Correct values that were flagged

- L01 security_amount = `14850.0`: check: amount was calculated, not stated; check the maths; check: Claude: Security amount is calculated, not stated: 3 months' Base Rent = $54,000 / 12 x 3 = $13,500, plus GST at 10% = $14,850. Confirm the calculation and that GST is to be included in the guarantee amount (excluding GST it would be $13,500).
- L02 landlord = `Collins Lane Nominees Pty Ltd as trustee for the Collins Lane Unit Trust`: check: Claude: The Landlord contracts as trustee for the Collins Lane Unit Trust; trustee capacity included in the name. Check how the register should record trustee landlords.
- L02 annual_rent = `86400.0`: check: Claude: Rent is stated monthly ($7,200 per month plus GST); annual figure of $86,400 calculated as 7,200 x 12.
- L02 rent_review_type = `cpi`: check: Claude: CPI reviews apply annually during the initial term (rent cannot decrease); market review applies at the start of each further term. Initial-term review recorded as cpi.
- L02 break_clause = `True`: check: Claude: Tenant break right is exercisable only for an end date after 15 March 2027, and the Tenant must pay a termination fee equal to 2 months' rent on exercise.
- L02 break_notice_months = `6`: check: Claude: Tenant break right is exercisable only for an end date after 15 March 2027, and the Tenant must pay a termination fee equal to 2 months' rent on exercise.
- L03 term_months = `96`: check: Claude: The Deed of Variation dated 12 May 2025 replaced the original 7-year term (expiry 30 June 2031) with 8 years (expiry 30 June 2032). The values reflect the deed. The option exercise window in clause 7 (3 to 6 months before the Expiry Date) now runs against the new 2032 expiry date.
- L03 expiry_date = `2032-06-30`: check: Claude: The Deed of Variation dated 12 May 2025 replaced the original 7-year term (expiry 30 June 2031) with 8 years (expiry 30 June 2032). The values reflect the deed. The option exercise window in clause 7 (3 to 6 months before the Expiry Date) now runs against the new 2032 expiry date.
- L03 rent_review_type = `mixed`: check: Claude: Rent review is mixed: fixed 3.5% on each anniversary, except a market review on 1 July 2028. The deed extended the term but did not address reviews. Presumably the fixed 3.5% review also applies on the added anniversary (1 July 2031). Please confirm.
- L03 fixed_review_percent = `3.5`: check: Claude: Rent review is mixed: fixed 3.5% on each anniversary, except a market review on 1 July 2028. The deed extended the term but did not address reviews. Presumably the fixed 3.5% review also applies on the added anniversary (1 July 2031). Please confirm.
- L03 security_amount = `171600.0`: check: Claude: The bank guarantee of $171,600 equals 6 months of Base Rent including GST ($312,000 x 1.1 / 2). The deed did not change the security. Check whether the guarantee needs extending to cover the new expiry date plus 3 months under clause 6.
- L04 rent_review_type = `market`: check: Claude: Market reviews are subject to a ratchet: rent cannot fall below the rent payable immediately before the review.
- L04 security_type = `none`: check: Claude: No bond or bank guarantee; security is a personal guarantee from Thomas Okafor only, recorded as none per register rules.
- L04 security_amount = `None`: check: Claude: No bond or bank guarantee; security is a personal guarantee from Thomas Okafor only, recorded as none per register rules.
- L04 break_clause = `True`: check: Claude: Landlord redevelopment termination right is exercisable only after 1 October 2030 and requires the Landlord to pay the Tenant's reasonable relocation costs. Check whether retail leases legislation applies and affects enforceability of this clause.
- L04 break_notice_months = `6`: check: Claude: Landlord redevelopment termination right is exercisable only after 1 October 2030 and requires the Landlord to pay the Tenant's reasonable relocation costs. Check whether retail leases legislation applies and affects enforceability of this clause.
- L05 term_months = `36`: check: Claude: Term of 3 years is less than the 5-year minimum under the Retail Leases Act 2003 (Vic); Special Condition 1 states a section 21 certificate was obtained. Confirm the certificate is on file.
- L05 annual_rent = `59800.0`: check: Claude: Base Rent is stated weekly ($1,150); converted at 52 weeks = $59,800, which matches the annual figure stated in Item 7. Note that clause 3 requires payment by equal monthly instalments.
- L05 outgoings_percent = `0.0`: check: Claude: Item 10 states nil outgoings with the Base Rent inclusive of outgoings (gross lease); clause 5 refers to paying outgoings by monthly estimate, but the proportion is nil, so recorded as 0.
- L08 annual_rent = `66000.0`: check: Claude: Item 7 states Base Rent of $72,000 per annum plus GST, but Special Condition 1 (which prevails under clause 1) sets first-year Base Rent at $66,000 per annum plus GST, with the first 4% fixed review applying to that amount (i.e. $68,640 from year 2). $66,000 recorded as rent payable from commencement; Item 7's $72,000 figure should not be used for the register.; check: Claude: The bank guarantee of $19,800 equals 3 months' rent plus GST calculated on the Item 7 rent of $72,000, not the reduced first-year rent of $66,000 under Special Condition 1. The amount is stated as a fixed figure so $19,800 is recorded, but check whether the parties intended it to reflect the reduced rent.
- L08 security_amount = `19800.0`: check: Claude: The bank guarantee of $19,800 equals 3 months' rent plus GST calculated on the Item 7 rent of $72,000, not the reduced first-year rent of $66,000 under Special Condition 1. The amount is stated as a fixed figure so $19,800 is recorded, but check whether the parties intended it to reflect the reduced rent.

## Cost and speed

- $0.296 total, $0.037 per lease
- 11s per lease on average
- Models that answered: ['claude-opus-5-5']; fallbacks used: 0

Labels were written together with the fictional leases. Eight leases is a small sample, so treat percentages as indicative.
