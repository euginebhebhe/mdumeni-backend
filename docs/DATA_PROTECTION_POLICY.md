# MDUMENI Data Protection Policy

**Document type:** Internal policy  
**Applies to:** INTELLI-Farming research team, University of Zimbabwe  
**Version:** 1.0 — June 2026  
**Review date:** June 2027  

---

## 1. Purpose

This policy governs how INTELLI-Farming and the University of Zimbabwe collect, store, use, and protect personal data obtained through the MDUMENI application and the associated pilot research programme.

It is intended to support compliance with:
- The Access to Information and Protection of Privacy Act (AIPPA), Zimbabwe
- University of Zimbabwe Research Ethics guidelines
- Google Play Developer Policy (for app distribution)
- Good research practice principles for human subjects research

---

## 2. Data We Collect

### 2.1 App user data

| Data element | Classification | Legal basis | Retention |
|---|---|---|---|
| Phone number | Personal (contact) | Contractual (account creation) | Until account deleted |
| PIN (stored as bcrypt hash) | Credential | Contractual | Until account deleted |
| Province and district | Personal (location) | Consent + Contractual | Until account deleted |
| Farm size and characteristics | Personal (farm data) | Consent + Contractual | Until account deleted |
| Soil readings | Personal (farm data) | Consent | 90 days server-side; unlimited locally |
| Active crop and planting date | Personal (farm data) | Consent | Until changed/deleted |
| Season yield records | Personal (farm data) | Consent | Until account deleted |
| AI chat messages | Personal | Consent | Not stored server-side (in-memory only) |
| Marketplace listings | Personal (business) | Consent | 7 days (auto-deleted) |

### 2.2 Research pilot data

Data collected specifically for the pilot study is governed by an additional informed consent process (see Section 5).

| Data element | Classification | Purpose |
|---|---|---|
| Baseline survey responses | Research data | Pre-intervention benchmark |
| Midseason monitoring data | Research data | Intervention tracking |
| Actual yield measurements | Research data | Primary outcome measure |
| App engagement logs | Research data | Secondary outcome measure |
| End-of-season survey | Research data | Satisfaction and behaviour change |

---

## 3. Data Storage and Security

### 3.1 On-device storage

- SQLite database (`expo-sqlite`) stores: farm profile, crop history, local soil readings, and cached market data
- expo-secure-store (Android Keystore) stores: authentication JWT token, notification preference, marketplace draft queue
- No encryption of the SQLite database itself in v1.0 — to be addressed in v1.1

### 3.2 Server-side storage

- All farmer data is stored in Supabase (PostgreSQL), hosted in the United States on AWS infrastructure
- Data is encrypted at rest by Supabase
- All data in transit uses TLS 1.2 or higher
- Row Level Security is enabled at the application layer via JWT validation
- The Supabase service role key is stored only as a Render environment variable — it is never exposed in client-side code or committed to the repository

### 3.3 Third-party processors

| Processor | Data shared | Purpose | Country | DPA in place? |
|---|---|---|---|---|
| Supabase | All server-side farmer data | Database hosting | USA | Supabase Terms constitute a DPA |
| Groq Inc. | Question text + farm context summary | AI chat inference | USA | Groq Terms |
| Render | None (compute only, no data storage) | Backend hosting | USA | Render Terms |

### 3.4 Access controls

| Role | Data access |
|---|---|
| Farmer (app user) | Own data only (via JWT-authenticated API) |
| Backend API (service role) | All farmer data (via Supabase service key) |
| Research team | Anonymised aggregates only (no individual access to farmer data) |
| University ethics committee | Access to consent records and anonymised research data only |

---

## 4. Data Minimisation

The following data is intentionally NOT collected:
- GPS coordinates (province and district are sufficient for all features)
- Contact lists or SMS content
- Photographs (unless a farmer voluntarily uploads a marketplace photo)
- Device identifiers beyond the standard Expo device ID used for push notifications
- Financial account numbers, card numbers, or payment details
- Biometric data

---

## 5. Research Consent and Ethics

### 5.1 Informed consent for pilot participants

All 500 pilot farmers will provide written informed consent covering:
- The purpose of the research
- What data will be collected and how
- That participation is voluntary and can be withdrawn at any time
- That withdrawal does not affect their access to MDUMENI
- How data will be used (research and app improvement only)
- That data will be anonymised for any publications

Consent forms will be available in English, Shona, and Ndebele.

### 5.2 Ethics clearance

The pilot study will be registered with the University of Zimbabwe Research Ethics Committee before any data collection begins. Ethics application reference will be recorded here upon approval.

### 5.3 Control group rights

Farmers assigned to the control group will receive full access to MDUMENI at the conclusion of the 2026/2027 pilot season, regardless of whether the intervention showed positive results.

---

## 6. Data Breach Response

In the event of a suspected data breach:

1. The breach must be reported to the PI (Eugine Bhebhe) within 24 hours of discovery
2. Supabase will be notified if the breach involves server-side data
3. Affected farmers will be notified within 72 hours if there is a risk to their personal data
4. A written incident report will be filed with the University of Zimbabwe Research Ethics Committee
5. The breach will be documented in the project's data management log

Signs of a potential breach include:
- Unusual Supabase API traffic
- Unknown entries in the farmers table
- Reports from users of unauthorised access to their account

---

## 7. Data Retention and Deletion

| Data type | Retention period | Deletion process |
|---|---|---|
| Active user accounts | Until farmer requests deletion | Via email request — admin deletes from Supabase; farmer deletes local SQLite |
| Sensor readings (server) | 90 days rolling | Automated Supabase cron job |
| Marketplace listings | 7 days from posting | Automated expiry flag + manual sweep |
| Chat messages | Session only (in-memory) | Cleared on app close |
| Research pilot data | 5 years post-publication | Archived and anonymised |
| Anonymised research aggregates | Indefinite | N/A |

**Farmer deletion requests:** Actioned within 30 days of receipt. Contact: bhebheeugine@gmail.com.

---

## 8. International Data Transfers

Farmer data is stored on servers in the United States (Supabase/AWS). By registering for MDUMENI, farmers consent to this transfer.

For the research pilot specifically, anonymised data may be shared with international research collaborators (e.g. ICRISAT, CGIAR) in accordance with the approved ethics protocol.

---

## 9. Policy Governance

This policy is maintained by the INTELLI-Farming research group and reviewed annually.

Changes to this policy will be:
- Documented with a version number and date
- Reflected in the app's Privacy Policy where relevant
- Notified to pilot participants if they affect their data rights

**Policy owner:** Eugine Bhebhe, INTELLI-Farming, University of Zimbabwe  
**Contact:** bhebheeugine@gmail.com  
**Review date:** June 2027
