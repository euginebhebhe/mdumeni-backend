# MDUMENI Research Overview

**Project title:** MDUMENI: An Offline-First AI Agronomist for Smallholder Farmers in Zimbabwe's Semi-Arid Agro-Ecological Zones  
**Institution:** Department of Computer Science, University of Zimbabwe  
**Research group:** INTELLI-Farming  
**Principal investigator:** Eugine Bhebhe  
**Target conference:** AARSE 2026 (African Association of Remote Sensing of Environment)  
**Full paper deadline:** 31 August 2026  

---

## Abstract

Smallholder farming accounts for approximately 70% of agricultural production in Zimbabwe, yet fewer than one in ten smallholder farmers has reliable access to an agricultural extension officer. This gap in advisory services contributes to suboptimal input use, crop selection mismatch with local agro-ecological conditions, late pest detection, and systemic post-harvest losses.

MDUMENI is an open-source Android mobile application that deploys an AI-driven crop recommendation and agronomic advisory system capable of operating entirely offline on low-cost Android smartphones. The system integrates a six-factor weighted scoring engine across 60 crop varieties calibrated to Zimbabwe's five agro-ecological regions, a crop-specific farming calendar state machine, a symptom-based pest and disease diagnosis engine covering 74 organisms, and a natural language agricultural chatbot backed by a large language model (Llama 3.3 70B via Groq) when connected to the internet.

A pilot study involving 500 farmers across three districts in Zimbabwe's agro-ecological Regions II, III, and IV is planned for the 2026/2027 growing season. The pilot will evaluate whether AI-assisted crop selection and management recommendations lead to measurable yield improvements, input cost reductions, and changes in farmer decision-making behaviour compared to a control group receiving standard AGRITEX extension services.

---

## Background and Motivation

### Zimbabwe's smallholder agricultural context

Zimbabwe has approximately 1.8 million smallholder farming households, the majority of whom farm between 0.5 and 5 hectares in communal and resettlement areas. The agricultural sector directly supports approximately 70% of the population, yet average cereal yields in communal areas remain well below the potential of improved varieties — typically 0.8–1.2 t/ha maize in a good season compared to a physiological potential of 7–8 t/ha for hybrid varieties under appropriate management.

Key constraints identified in the literature and confirmed through community consultations include:

1. **Advisory service gap:** The AGRITEX extension service operates at approximately one extension officer per 1,000 farming households in communal areas — far below the recommended 1:400 ratio
2. **Inappropriate crop selection:** Farmers frequently plant varieties unsuited to their specific agro-ecological zone, soil conditions, or available input budget
3. **Late pest detection:** Fall Armyworm (Spodoptera frugiperda), maize stalk borer (Busseola fusca), and other pests cause 20–40% yield losses when not detected and managed at the appropriate growth stage
4. **Input inefficiency:** Without soil pH data, incorrect lime application rates and fertiliser choices are common
5. **Market disconnection:** Farmers often sell immediately post-harvest at trough prices, unaware of better market opportunities

### The role of mobile technology

Smartphone penetration in Zimbabwe reached approximately 55% in 2024, with Android devices dominant at the low end of the market. Mobile network coverage reaches approximately 85% of the populated area, though data costs (approximately $1–2 per GB on major networks) limit sustained online use among smallholder farmers.

This creates a specific technical requirement: agricultural advisory systems for this population must function reliably with minimal or no internet connectivity, while leveraging online capabilities when available.

---

## Technical Contribution

### Offline-first AI architecture

MDUMENI's primary technical contribution is the implementation of a complete AI agronomic advisory stack running on-device on standard Android hardware (tested on devices with 2GB RAM running Android 10+).

The on-device AI system consists of:

**Crop recommendation engine (cropEngine.js)**  
A weighted scoring model evaluating six factors: soil pH match (25%), soil moisture (20%), agro-ecological region suitability (20%), temperature optimality (15%), irrigation requirement match (10%), and budget compatibility (10%). The engine scores all 60 crop records in the dataset and returns a ranked list of viable options with variety-level recommendations and explanatory notes.

**Farming calendar engine (calendarEngine.js)**  
A phase-based state machine generating day-specific task lists for each of 60 crops. The calendar adapts to the farmer's planting date, current season progress, and sensor readings to surface actionable guidance — "apply 50kg/ha LAN today" rather than generic seasonal advice.

**Pest and disease engine (pestEngine.js)**  
A token-intersection symptom matcher across 74 pest and disease records. The engine accepts natural language symptom descriptions, tokenises and scores against all records, and returns ranked diagnoses with treatment recommendations graded by budget availability.

**Offline chat guide**  
486 pre-authored question-answer pairs covering soil management, crop establishment, pest management, fertiliser application, harvest, and storage. Answers are template-interpolated with the farmer's real farm data (region, crop, soil readings) to be contextually relevant.

### Backend architecture

The backend (FastAPI/Python on Railway) mirrors all AI engine logic in Python, serving as the authoritative version for online use. This dual implementation ensures consistent recommendations across online and offline modes while enabling Python-based testing and validation of the agronomic logic.

The backend additionally provides: Groq-powered natural language chat with full conversation continuity; live market price intelligence; ZimAgroMarket (peer-to-peer produce marketplace); and GPS-accurate agricultural services lookup via province-structured JSON data covering 247 agricultural service locations across all 10 Zimbabwe provinces.

### Agro-ecological calibration

The crop recommendation engine is calibrated to Zimbabwe's five agro-ecological regions (Zones I–V) as defined by the Department of Research and Specialist Services (DRSS). Variety-level recommendations within each crop are drawn from the current Seed Co Zimbabwe, Pannar, and DRSS variety trial catalogues, validated against AGRITEX production guidelines.

The dataset covers crops spanning traditional food security crops (finger millet/Zviyo, bambara groundnut/Nyimo, pigeon peas/Nhunguru, cowpeas), commercial crops (maize, tobacco, cotton, soybeans), high-value export crops (coffee, tea, macadamia, green beans), and nutrition-security crops (moringa, amaranth/Mowa).

---

## Research Design

### Pilot study overview

**Duration:** October 2026 – May 2027 (full 2026/2027 season)  
**Sample size:** 500 farmers (target)  
**Districts:** One each in Regions II, III, and IV (specific districts TBD based on AGRITEX partnership)  
**Design:** Quasi-experimental with treatment and control groups

**Treatment group (250 farmers):**  
Receive MDUMENI smartphone with the app pre-installed and trained. App-guided crop selection, calendar-driven management, and pest alerts throughout the season.

**Control group (250 farmers):**  
Continue with standard AGRITEX extension services (no app intervention).

### Primary outcome measures

1. **Yield:** Actual kg/ha for the primary crop, measured at harvest by trained enumerators
2. **Input efficiency:** Input cost per kg of output (USD/kg)
3. **Crop selection appropriateness:** Whether planted variety matches the optimal for the farmer's conditions (based on post-season soil test data)
4. **Pest detection speed:** Days from infestation onset to farmer action (treatment group: alert trigger date; control: farmer-reported detection date)

### Secondary outcome measures

1. App engagement: session frequency, features used, chat questions asked
2. Farmer confidence: pre/post-season survey on confidence in crop management decisions
3. Market outcomes: sale price achieved vs seasonal average
4. Technology adoption: willingness to continue using app after pilot

### Data collection

- Baseline survey: farmer profile, previous season yields, current soil test
- Midseason check: crop establishment, pest/disease incidence, management actions taken
- End-of-season: final yield measurement, income statement, satisfaction survey
- Sensor data: weekly soil pH, moisture, temperature for treatment group (where sensor hardware available)

---

## Ethical Considerations

- Written informed consent will be obtained from all pilot participants
- Farmers in the control group will receive full app access after the pilot season concludes
- Data will be anonymised for any publications — no individual farmer will be identifiable
- The study will be registered with the University of Zimbabwe Research Ethics Committee
- All recommendations in the app include explicit guidance to consult AGRITEX officers for major decisions

---

## Expected Outcomes and Impact

### For the pilot study

We hypothesise that treatment group farmers will achieve 15–25% higher yields than control group farmers through improved variety selection and better-timed management interventions. This estimate is conservative relative to the literature on mobile advisory services in sub-Saharan Africa.

### Longer-term impact pathway

1. If pilot results are positive, MDUMENI will be submitted for adoption by the Zimbabwe Ministry of Agriculture as an official extension support tool
2. Collaboration with AGRITEX to pre-load the app on government farmer support tablets
3. Integration with the Zimbabwe Agriculture Investment Plan's digital agriculture component
4. Potential adaptation for Zambia, Malawi, and other SADC countries with similar agro-ecological zones (dataset is regionalisable)

### Open-source multiplier

By releasing MDUMENI as open-source (MIT licence), the technical architecture — particularly the offline-first AI engine design — can be adapted for other smallholder farming contexts globally. The province-structured agricultural services data model is particularly transferable to other country contexts.

---

## Publications and Presentations

**AARSE 2026 full paper:**  
*MDUMENI: Offline-First AI-Assisted Agronomy for Smallholder Farmers in Zimbabwe's Semi-Arid Zones*  
Target submission: 31 August 2026

**UZ Research Week:**  
Exhibition and poster presentation, May/June 2026

**Conference targets (2027, pending pilot results):**  
- IEEE AFRICON 2027
- ICT4D Conference 2027
- Zimbabwe Agricultural Society annual conference

---

## Project Team

**Eugine Bhebhe** — Lead Developer and Principal Investigator  
Department of Computer Science, University of Zimbabwe  
bhebheeugine@gmail.com · +263 78 461 7009

**INTELLI-Farming Research Group**  
University of Zimbabwe

---

## Funding and Acknowledgements

MDUMENI has been developed as an unfunded academic research project. Computing resources and API costs have been met by the research team.

We acknowledge:
- AGRITEX Zimbabwe for agronomic validation discussions
- Seed Co Zimbabwe and Pannar Seed for variety trial data
- ICRISAT for semi-arid crop research data
- Groq Inc. for research API access

*Funding applications are pending with: Seedstars Africa (June 2026 deadline), MIT Solve Food Security Challenge (September 2026), CGIAR Digital Innovation initiative.*
