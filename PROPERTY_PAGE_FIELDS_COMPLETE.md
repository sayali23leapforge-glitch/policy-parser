# Property Insurance Page - Complete Fields List

## PROPERTY PAGE SECTIONS & INPUTS CHECKLIST

### CARD 1: CLIENT DETAILS (HOMEOWNERS & TENANTS)
**Scope:** `customer`

#### Customer Information
- [x] `name` - Customer Name (text)
- [x] `dob` - Date of Birth (date MM-DD-YYYY)
- [x] `phone` - Home Phone (phone format)
- [x] `address` - Street Address (text)
- [x] `city` - City (text)
- [x] `postal` - Postal Code (A1A 1A1 format)
- [x] `consent` - Type of Consent (radio: Verbal/Written/None)
- [x] `quoteType` - Quote Type (New Business / Renewal - HIDDEN, NOT IN FORM)

---

### CARD 2: APPLICANTS & HISTORY (HOMEOWNERS ONLY)
**Scope:** `property`

#### Insured Information
- [x] `insDob` - Insured DOB (date MM-DD-YYYY)
- [x] `insGender` - Insured Gender (dropdown: Male/Female)
- [x] `insuredPropertySince` - Property Insured Since (date MM-DD-YYYY) [HIDDEN in Tenants]

#### Occupation
- [x] `occupation` - Occupation Title (text) [HIDDEN in Tenants]
- [x] `empStatus` - Employment Status (dropdown: Full Time/Retired) [HIDDEN in Tenants]

#### Co-Insured Information [HIDDEN in Tenants]
- [x] `coDob` - Co-Insured DOB (date MM-DD-YYYY)
- [x] `coGender` - Co-Insured Gender (dropdown: Male/Female)

#### Insurance History
- [x] `insuredSince` - Continuously Insured Since (date MM-DD-YYYY) [HIDDEN in Tenants]
- [x] `insuredBrokerageSince` - With Brokerage Since (date MM-DD-YYYY) [HIDDEN in Tenants]

---

### CARD 3: COVERAGE & MORTGAGE
**Scope:** `property`

#### Mortgage Information
- [x] `mortgageCount` - Number of Mortgages (stepper 0-∞) [HIDDEN in Tenants]
- [x] `firstTimeBuyer` - First Time Buyer (radio: Yes/No) [HIDDEN in Tenants]

#### Smoke Free
- [x] `smokeFree` - Property Smoke Free (radio: Yes/No)

#### Coverage Details
- [x] `coverageType` - Coverage Type (dropdown: All Risks/All Risks, All Risks/Named Perils, Named Perils/Named Perils)
- [x] `gbrc` - GBRC (radio: Yes/No) [HIDDEN in Tenants]
- [x] `singleLimit` - Single Limit (radio: Yes/No) [HIDDEN in Tenants]

#### Deductible & Liability
- [x] `deductible` - Deductible (dropdown: 2500/5000/etc)
- [x] `liability` - Liability (dropdown: 2M/3M/etc)

---

### CARD 4: PROPERTY DETAILS
**Scope:** `property`

#### Policy Type & Structure
- [x] `policyType` - Policy Type (radio: Homeowners/Tenants)
- [x] `structure` - Structure Type (dropdown: Detached, Semi-Detached, Townhouse, Condo, Row House, Mobile Home)

#### Building & Occupancy
- [x] `yearBuilt` - Year Built (YYYY)
- [x] `occupiedSince` - Occupied Since (MM-YYYY)
- [x] `storeys` - Number of Stories (stepper)
- [x] `units` - Number of Units (stepper) [HIDDEN in Tenants]
- [x] `families` - Number of Families (stepper) [HIDDEN in Tenants]
- [x] `ownerOcc` - Owner Occupied (radio: Yes/No) [HIDDEN in Tenants]
- [x] `livingArea` - Total Living Area (sq ft)

#### Interior & Basement
- [x] `fullBaths` - Full Bathrooms (text/stepper)
- [x] `halfBaths` - Half Bathrooms (text/stepper)
- [x] `bsmtArea` - Basement Sq Ft (text)
- [x] `bsmtFin` - Basement Finished Type (dropdown)
- [x] `bsmtFinBool` - Basement Finished (radio: Yes/No)
- [x] `sepEntrance` - Separate Entrance (radio: Yes/No)
- [x] `bsmtRented` - Basement Rented (radio: Yes/No) [HIDDEN in Tenants]

#### System Updates (Year)
- [x] `heatYear` - Heating Year (YYYY)
- [x] `elecYear` - Electric Year (YYYY)
- [x] `plumbYear` - Plumbing Year (YYYY)
- [x] `roofYear` - Roofing Year (YYYY)
- [x] `tankYear` - HWT (Hot Water Tank) Year (YYYY)
- [x] `tankType` - Tank Type (dropdown: Tank/Tankless) [HIDDEN in Tenants]

#### Safety & Alarms
- [x] `burglar` - Monitored Burglar (radio: Yes/No)
- [x] `fire` - Monitored Fire (radio: Yes/No)
- [x] `sprinkler` - Sprinkler System (radio: Yes/No)
- [x] `sumpPump` - Sump Pit (radio: Yes/No)
- [x] `fireExt` - Fire Extinguishers (stepper)
- [x] `smokeDet` - Smoke Detectors (stepper)

---

### CARD 5: ADDITIONAL DETAILS
**Scope:** `property`

#### Additional Notes
- [x] `additionalNotes` - Additional Notes / Remarks (textarea)

---

## DATABASE SCHEMA VERIFICATION

The following fields **MUST** exist in the `properties_data` table:

### CUSTOMER Fields
```
name, dob, phone, address, city, postal, consent, quoteType, email
```

### PROPERTY Fields
```
id, policyType, structure, 
deductible, liability, mortgageCount, smokeFree, firstTimeBuyer, 
coverageType, gbrc, singleLimit,
yearBuilt, occupiedSince, storeys, units, families, ownerOcc, livingArea,
insDob, insGender, insuredPropertySince, occupation, empStatus, 
coDob, coGender, insuredSince, insuredBrokerageSince,
fullBaths, halfBaths, bsmtArea, bsmtFin, bsmtFinBool, sepEntrance, bsmtRented,
heatYear, elecYear, plumbYear, roofYear, tankYear, tankType,
burglar, fire, sprinkler, sumpPump, fireExt, smokeDet,
additionalNotes
```

### TOP-LEVEL Fields
```
email, customer (JSONB), properties (JSONB array), created_at, updated_at, lead_id, viewMode
```

---

## HOMEOWNERS SPECIFIC (Hidden in Tenants)
- mortgageCount
- firstTimeBuyer
- gbrc
- singleLimit
- occupation
- empStatus
- insuredPropertySince
- insuredSince
- insuredBrokerageSince
- units
- families
- ownerOcc
- tankType
- bsmtRented
- co-insured-col (entire section)

## TENANTS SPECIFIC (Hidden in Homeowners)
- None exclusively, but some fields are hidden

---

## SAVE FUNCTION STATUS
✅ All fields listed above are being saved to the database
✅ Homeowners mode data saving
✅ Tenants mode data saving  
✅ viewMode is saved to identify which form was last used
✅ All form inputs are properly mapped to data keys

## LOAD FUNCTION STATUS
✅ viewMode restoration working
✅ Switching to Tenants mode when loading Tenants data
✅ All fields being loaded back to form inputs
