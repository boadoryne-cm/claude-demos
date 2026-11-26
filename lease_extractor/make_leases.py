"""Writes the fictional sample leases in leases/. All names, addresses and numbers are made up.

Two drafting styles are used on purpose (a schedule-based retail/commercial form and a
narrative-style lease), plus a deed of variation and a few deliberate traps:
  L03 deed of variation extends the term   L05 rent stated per week
  L02 rent stated per month                L06 rent-free incentive (base rent unchanged)
  L07 term and expiry contradict           L08 special condition overrides the schedule rent
"""
from pathlib import Path

OUT = Path(__file__).with_name("leases")
DISCLAIMER = "_Sample document for a software demonstration. All parties, addresses and figures are fictional._\n\n"


def schedule_form(no, title, items, special, extra=""):
    rows = "\n".join(f"| {i} | {k} | {v} |" for i, (k, v) in enumerate(items, 1))
    return f"""# {title}

{DISCLAIMER}## Schedule

| Item | Particular | Details |
|---|---|---|
{rows}

## Standard terms

**1. Interpretation.** Words defined in the Schedule have the same meaning in these terms. If there is any inconsistency between the Special Conditions and the Schedule or these standard terms, the Special Conditions prevail.

**2. Term.** The Landlord leases the Premises to the Tenant for the Term starting on the Commencement Date.

**3. Rent.** The Tenant must pay the Base Rent in Item 7 by equal monthly instalments in advance on the first day of each month, plus GST. Rent for any part month is apportioned daily.

**4. Rent review.** On each Review Date the Base Rent is reviewed in the way set out in Item 8.

**4.1 Fixed review.** Where Item 8 provides for a fixed review, the Base Rent from the Review Date is the Base Rent immediately before the Review Date increased by the percentage stated in Item 8.

**4.2 CPI review.** Where Item 8 provides for a CPI review, the Base Rent is adjusted by the percentage change in the Consumer Price Index (All Groups, weighted average of eight capital cities) over the previous 12 months, but the Base Rent will never decrease.

**4.3 Market review.** Where Item 8 provides for a market review, the Base Rent is the current market rent agreed by the parties or, failing agreement within 30 days, determined by a valuer appointed by the President of the Australian Property Institute (Victoria).

**5. Outgoings.** The Tenant must pay the Tenant's Proportion of Outgoings stated in Item 10 of the Landlord's reasonable outgoings for the Building, by monthly estimate with an annual adjustment.

**6. Security.** The Tenant must provide the Security described in Item 11 on or before the Commencement Date and keep it in place until 3 months after the end of the lease.

**7. Option to renew.** If Item 12 grants an option, the Tenant may renew the lease for each further term stated by giving the Landlord written notice not more than 6 months and not less than 3 months before the Expiry Date, provided the Tenant is not in breach.

**8. Use.** The Tenant must use the Premises only for the Permitted Use.

**9. Assignment.** The Tenant must not assign the lease or sublet the Premises without the Landlord's written consent, which must not be unreasonably withheld.

**10. Make good.** At the end of the lease the Tenant must remove its fittings and make good any damage, fair wear and tear excepted.

## Special Conditions

{special}
{extra}"""


def write(name, text):
    (OUT / name).write_text(text)


# ---------- L01 cafe, fixed review, security as a formula ----------
write("L01-two-spoons-cafe.md", schedule_form(1, "Retail Lease: Shop 3, 41 Pakington Street, Geelong West", [
    ("Landlord", "Bellarine Property Holdings Pty Ltd ACN 600 111 222"),
    ("Tenant", "Two Spoons Cafe Pty Ltd ACN 611 333 444"),
    ("Premises", "Shop 3, 41 Pakington Street, Geelong West VIC 3218"),
    ("Commencement Date", "1 February 2026"),
    ("Term", "5 years"),
    ("Expiry Date", "31 January 2031"),
    ("Base Rent", "$54,000 per annum plus GST"),
    ("Rent Review", "Fixed increase of 4% on each anniversary of the Commencement Date"),
    ("Permitted Use", "Cafe and takeaway food"),
    ("Tenant's Proportion of Outgoings", "12.5%"),
    ("Security", "Bank guarantee for an amount equal to 3 months' Base Rent plus GST"),
    ("Option to Renew", "One further term of 5 years"),
], "1. The Landlord will contribute up to $15,000 plus GST towards the Tenant's fit-out on receipt of tax invoices.\n\n2. The Tenant may trade from 6 am to 4 pm every day.\n"))

# ---------- L02 office, narrative style, monthly rent, CPI, break clause ----------
write("L02-northgate-accounting.md", f"""# Lease of Level 4, 210 Collins Street, Melbourne

{DISCLAIMER}This lease is made between **Collins Lane Nominees Pty Ltd ACN 622 555 666 as trustee for the Collins Lane Unit Trust** (the Landlord) and **Northgate Accounting Pty Ltd ACN 633 777 888** (the Tenant).

## 1. Premises
The Landlord leases to the Tenant the whole of Level 4, 210 Collins Street, Melbourne VIC 3000, with an agreed lettable area of 180 square metres (the Premises).

## 2. Term
The lease starts on 15 March 2025 and is for a term of three (3) years, ending on 14 March 2028.

## 3. Use
The Premises may be used for professional offices only.

## 4. Rent
4.1 The Tenant must pay rent of $7,200 per month plus GST, in advance on the 15th day of each month.

4.2 On each anniversary of the start date during the initial term, the rent is increased by the percentage change in the Consumer Price Index (All Groups, Melbourne) for the previous 12 months. The rent will not decrease.

4.3 At the start of any further term, the rent will be reviewed to current market rent.

## 5. Outgoings
The Tenant must pay 8% of the Landlord's outgoings for the building, being the Premises' share of the building's lettable area.

## 6. Security deposit
On signing, the Tenant must pay the Landlord a cash security deposit of $21,600. The Landlord will hold the deposit in a separate trust account and return it within 30 days after the lease ends, less any amount owing.

## 7. Further terms
If the Tenant has complied with this lease, it may extend the lease for two further terms of three (3) years each, by giving written notice at least 3 months before the end of the current term.

## 8. Early termination by the Tenant
The Tenant may end this lease on any date after 15 March 2027 by giving the Landlord at least six (6) months' written notice. If the Tenant does so, it must pay the Landlord an amount equal to 2 months' rent as a termination fee.

## 9. Assignment and subletting
The Tenant may not assign or sublet without the Landlord's consent, which will not be unreasonably withheld.

## 10. End of lease
At the end of the lease the Tenant must return the Premises in the condition they were in at the start date, fair wear and tear excepted.
""")

# ---------- L03 warehouse, mixed review, deed of variation extends term ----------
write("L03-freshroute-logistics.md", schedule_form(3, "Industrial Lease: 18 Abbotts Road, Dandenong South", [
    ("Landlord", "Kessler Industrial Pty Ltd ACN 644 999 000"),
    ("Tenant", "FreshRoute Logistics Pty Ltd ACN 655 121 314"),
    ("Premises", "Warehouse and office, 18 Abbotts Road, Dandenong South VIC 3175"),
    ("Commencement Date", "1 July 2024"),
    ("Term", "7 years"),
    ("Expiry Date", "30 June 2031"),
    ("Base Rent", "$312,000 per annum plus GST"),
    ("Rent Review", "Fixed increase of 3.5% on each anniversary of the Commencement Date, except a market review on 1 July 2028"),
    ("Permitted Use", "Warehousing, cold storage and distribution"),
    ("Tenant's Proportion of Outgoings", "100%"),
    ("Security", "Bank guarantee for $171,600"),
    ("Option to Renew", "One further term of 7 years"),
], "1. The Tenant may operate 24 hours a day, 7 days a week.\n\n2. The Landlord must maintain the roof and structure of the building.\n",
extra="""
---

# Deed of Variation of Lease

Dated 12 May 2025

**Parties:** Kessler Industrial Pty Ltd ACN 644 999 000 (Landlord) and FreshRoute Logistics Pty Ltd ACN 655 121 314 (Tenant).

**Background:** The parties are parties to the lease of 18 Abbotts Road, Dandenong South commencing on 1 July 2024 (the Lease). The Tenant has installed additional cold storage and has asked for a longer term.

**Operative part:**

1. With effect from the date of this deed, the Term in Item 5 of the Schedule is deleted and replaced with "8 years".

2. The Expiry Date in Item 6 of the Schedule is deleted and replaced with "30 June 2032".

3. All other terms of the Lease continue unchanged.
"""))

# ---------- L04 medical suite, narrative, market review, landlord demolition break, no option ----------
write("L04-lakeside-physio.md", f"""# Lease: Suite 2, 15 Wendouree Parade, Lake Wendouree

{DISCLAIMER}**Landlord:** Margaret Anne Liu and David Chen Liu
**Tenant:** Lakeside Physio Group Pty Ltd ACN 666 222 333
**Guarantor:** Thomas Okafor

## 1. Grant of lease
The Landlord leases Suite 2, 15 Wendouree Parade, Lake Wendouree VIC 3350 to the Tenant for ten (10) years starting on 1 October 2025. The lease ends on 30 September 2035.

## 2. Use
The Tenant may use the suite as a physiotherapy and allied health clinic.

## 3. Rent
The Tenant must pay rent of $48,500 per annum plus GST by monthly instalments in advance.

## 4. Rent reviews
The rent will be reviewed to market rent on 1 October 2028, 1 October 2031 and 1 October 2034. The rent will not be less than the rent payable immediately before the review.

## 5. Outgoings
The Tenant must pay 5.2% of the outgoings for the building.

## 6. Security
No bond or bank guarantee is required. The Guarantor guarantees the Tenant's obligations under this lease.

## 7. Renewal
There is no option to renew this lease.

## 8. Redevelopment
After 1 October 2030, the Landlord may end this lease by giving the Tenant at least six (6) months' written notice if the Landlord intends to demolish or substantially redevelop the building. The Landlord must pay the Tenant's reasonable relocation costs.

## 9. Fit-out
The Tenant may install treatment rooms and a hydrotherapy pool subject to the Landlord's approval of plans.
""")

# ---------- L05 kiosk, weekly rent, gross lease, cash bond ----------
write("L05-priyas-threads.md", schedule_form(5, "Retail Lease: Kiosk K12, Corio Village Shopping Centre", [
    ("Landlord", "Corio Village Shopping Centre Pty Ltd ACN 677 444 555"),
    ("Tenant", "Priya Natarajan trading as Priya's Threads"),
    ("Premises", "Kiosk K12, Corio Village Shopping Centre, 2 Purnell Road, Corio VIC 3214"),
    ("Commencement Date", "1 December 2025"),
    ("Term", "3 years"),
    ("Expiry Date", "30 November 2028"),
    ("Base Rent", "$1,150 per week plus GST (being $59,800 per annum plus GST)"),
    ("Rent Review", "Fixed increase of 5% on each anniversary of the Commencement Date"),
    ("Permitted Use", "Alterations and tailoring"),
    ("Tenant's Proportion of Outgoings", "Nil. The Base Rent is inclusive of outgoings."),
    ("Security", "Cash bond of $4,600"),
    ("Option to Renew", "None"),
], "1. The Tenant has obtained a certificate under section 21 of the Retail Leases Act 2003 (Vic) and agrees to a term of less than 5 years.\n\n2. The Tenant must trade during the Centre's core trading hours.\n"))

# ---------- L06 office, rent-free incentive ----------
write("L06-coastline-digital.md", schedule_form(6, "Commercial Lease: Suite 5.02, 80 Moorabool Street, Geelong", [
    ("Landlord", "Moorabool Street Investments Pty Ltd ACN 688 666 777"),
    ("Tenant", "Coastline Digital Pty Ltd ACN 699 888 999"),
    ("Premises", "Suite 5.02, Level 5, 80 Moorabool Street, Geelong VIC 3220"),
    ("Commencement Date", "1 May 2026"),
    ("Term", "4 years"),
    ("Expiry Date", "30 April 2030"),
    ("Base Rent", "$62,000 per annum plus GST"),
    ("Rent Review", "Fixed increase of 3% on each anniversary of the Commencement Date"),
    ("Permitted Use", "Offices"),
    ("Tenant's Proportion of Outgoings", "6.75%"),
    ("Security", "Bank guarantee for $17,050"),
    ("Option to Renew", "One further term of 4 years"),
], "1. **Rent-free period.** As a lease incentive, the Tenant is not required to pay Base Rent for the first 3 months of the Term. The Base Rent in Item 7 is not otherwise affected, and the Tenant must pay Outgoings during the rent-free period.\n\n2. If the Tenant breaches this lease and the lease is terminated in the first 2 years, the Tenant must repay a proportion of the rent-free incentive.\n"))

# ---------- L07 gym, term and expiry contradict ----------
write("L07-ironbark-strength.md", f"""# Lease of 7 Hollis Court, North Geelong

{DISCLAIMER}This lease is between **Hollis Family Pty Ltd ACN 700 123 456** (Landlord) and **Ironbark Strength Pty Ltd ACN 711 234 567** (Tenant).

## 1. Premises and term
1.1 The Landlord leases the building and land at 7 Hollis Court, North Geelong VIC 3215 (the Premises) to the Tenant.

1.2 The term of this lease is five (5) years starting on 1 August 2025 and ending on 31 July 2029.

## 2. Permitted use
Gymnasium and strength training facility.

## 3. Rent
The Tenant must pay annual rent of $96,000 plus GST, by monthly instalments of $8,000 plus GST in advance.

## 4. Review
The rent is increased on each anniversary of the start date by the percentage increase in the Consumer Price Index (All Groups, Melbourne) over the previous 12 months.

## 5. Outgoings
As the Tenant occupies the whole of the Premises, the Tenant must pay all outgoings for the Premises.

## 6. Bank guarantee
The Tenant must give the Landlord an unconditional bank guarantee for $26,400 before taking possession.

## 7. Option
The Tenant has one option to renew this lease for a further five (5) years, exercisable by written notice given at least 3 months before the end of the term.

## 8. Noise
The Tenant must not drop weights on the floor between 10 pm and 6 am and must install rubber flooring in all training areas.
""")

# ---------- L08 surf shop, special condition overrides schedule rent ----------
write("L08-saltwater-board-co.md", schedule_form(8, "Retail Lease: Shop 6, Torquay Surf Plaza", [
    ("Landlord", "Torquay Surf Plaza Pty Ltd ACN 722 345 678"),
    ("Tenant", "Saltwater Board Co Pty Ltd ACN 733 456 789"),
    ("Premises", "Shop 6, Torquay Surf Plaza, 15 Gilbert Street, Torquay VIC 3228"),
    ("Commencement Date", "1 September 2026"),
    ("Term", "5 years"),
    ("Expiry Date", "31 August 2031"),
    ("Base Rent", "$72,000 per annum plus GST"),
    ("Rent Review", "Fixed increase of 4% on each anniversary of the Commencement Date"),
    ("Permitted Use", "Retail sale and hire of surfboards, wetsuits and accessories"),
    ("Tenant's Proportion of Outgoings", "9%"),
    ("Security", "Bank guarantee for $19,800"),
    ("Option to Renew", "Two further terms of 5 years each"),
], "1. **First year rent.** Despite Item 7, the Base Rent for the first year of the Term is $66,000 per annum plus GST. The first fixed review under Item 8 applies to that amount.\n\n2. The Tenant may display surfboards on the footpath directly outside the Premises during trading hours.\n"))

print(sorted(p.name for p in OUT.glob("*.md")))
