# MDUMENI Privacy Policy

**Effective date:** 1 June 2026  
**Last updated:** 1 June 2026  
**Application:** MDUMENI — AI Agronomist  
**Developer:** INTELLI-Farming, University of Zimbabwe  
**Contact:** bhebheeugine@gmail.com  

---

## 1. Introduction

MDUMENI ("we", "our", "the app") is a mobile application that helps Zimbabwean farmers make better agricultural decisions. This Privacy Policy explains what personal information we collect, how we use it, and your rights regarding that information.

We take your privacy seriously. MDUMENI is built for smallholder farmers — many of whom are first-time smartphone users — and we are committed to collecting only what is necessary to provide agronomic advice, and nothing more.

---

## 2. Information We Collect

### 2.1 Information You Provide Directly

When you register and use MDUMENI, you provide:

| Information | Purpose | Required? |
|---|---|---|
| Phone number | Account identification and login | Yes |
| 4-digit PIN | Secure account access | Yes |
| Province and district | Regional crop recommendations and nearby services | Yes |
| Agro-ecological region | Calibrate AI recommendations to your farming area | Yes |
| Farm size (hectares) | Yield estimates and fertiliser calculations | Yes |
| Irrigation access | Crop suitability filtering | Yes |
| Budget level (low/medium/high) | Variety and input recommendations | Yes |

### 2.2 Information Generated Through Use

| Information | Purpose |
|---|---|
| Active crop and planting date | Farming calendar and daily task generation |
| Yield records and season history | Performance tracking and future planning |
| AI chat messages | Agronomic question answering (see Section 4) |
| Market listings (if you post one) | Buyer/seller matching in ZimAgroMarket |

### 2.3 Sensor Data (Optional)

If you connect an MDUMENI ESP32 soil sensor, the app receives:
- Soil pH readings
- Soil moisture percentage
- Soil temperature (°C)

This data is stored locally on your device and, with your consent, on our secure servers to improve your recommendations.

### 2.4 Information We Do NOT Collect

We do not collect:
- Your exact GPS coordinates (we use only province and district)
- Financial account numbers or payment information
- Photos from your device camera or gallery
- Contacts, call logs, or SMS messages
- Browsing history or data from other apps
- Advertising identifiers
- Biometric data

---

## 3. How We Use Your Information

We use your information exclusively to:

1. **Provide agronomic recommendations** — your farm profile (region, soil data, crop, budget) is used solely to generate personalised crop recommendations, farming calendars, and pest management advice.

2. **Enable account access** — your phone number and PIN allow you to log in securely. We store your PIN as a secure hash — we cannot read your PIN.

3. **Show you nearby services** — your province and district are used to display relevant AGRITEX offices, agro dealers, GMB depots, and markets near you.

4. **Enable marketplace listings** — if you choose to post a produce listing, your name, district, and phone number are visible to other app users as the seller contact.

5. **Research and improvement** — anonymised, aggregated farming data (e.g. "how many farmers in Region III planted maize in October") may be used to improve the app and for academic research at the University of Zimbabwe. No individual farmer is identifiable in this research data.

---

## 4. AI Chat and Data Processing

When you send a message in the AI Chat feature and you are connected to the internet, your question and your farm profile summary (region, active crop, soil readings) are sent to:

- **Our server** (hosted on Railway) for processing
- **Groq Inc.** (United States) — the AI inference provider

Groq processes your message to generate an agricultural response. We send only the agronomic context necessary to answer your question. We do not send your name, phone number, or any personally identifying information to Groq.

When you are offline, all chat responses are generated entirely on your device and no data leaves your phone.

**Groq's Privacy Policy:** https://groq.com/privacy-policy/

---

## 5. Data Storage

| Data | Where stored | How long |
|---|---|---|
| Account information | Supabase (PostgreSQL), hosted in United States | Until you delete your account |
| Farming records | Your device (SQLite) + Supabase | Until you delete them or your account |
| Sensor readings | Your device (SQLite) + Supabase | Last 90 days on server; unlimited locally |
| Season history | Your device (SQLite) + Supabase | Until you delete your account |
| AI chat messages | Your device only (in-memory) | Cleared when you close the app |
| Market listings | Supabase | Active for 7 days; deleted automatically |

**Supabase Privacy Policy:** https://supabase.com/privacy

All server-side data is stored in the United States. By using MDUMENI, you consent to this transfer.

---

## 6. Data Sharing

We do not sell your personal data. We do not share your data with advertisers.

We share data only in these limited circumstances:

| Recipient | What we share | Why |
|---|---|---|
| Groq Inc. | Your farming question + crop/region context | AI chat responses |
| Other MDUMENI users | Your name, district, phone (marketplace listings only) | So buyers can contact you |
| University of Zimbabwe researchers | Anonymised, aggregated statistics only | Academic research |
| Law enforcement | As required by Zimbabwean law | Legal compliance only |

---

## 7. Security

We protect your data using:

- **Encrypted transmission** — all data between the app and our server uses HTTPS/TLS encryption
- **Hashed PINs** — your 4-digit PIN is stored as a cryptographic hash (bcrypt); it cannot be read or recovered by anyone, including us
- **JWT authentication** — account access tokens expire and must be renewed
- **Supabase Row Level Security** — database policies ensure each farmer can only access their own data
- **Secure device storage** — your authentication token is stored in expo-secure-store (Android Keystore / iOS Keychain)

If you believe your account has been compromised, contact us immediately at bhebheeugine@gmail.com.

---

## 8. Your Rights

You have the right to:

**Access your data** — request a copy of all data we hold about you.

**Correct your data** — update your farm profile at any time through the Settings screen.

**Delete your data** — delete your account and all associated data by contacting us at bhebheeugine@gmail.com. We will action deletion requests within 30 days.

**Withdraw consent** — stop using the app at any time. You may also disable specific features (e.g. marketplace listings) without deleting your account.

**Data portability** — request your farming data in a machine-readable format (JSON or CSV).

To exercise any of these rights, contact us at **bhebheeugine@gmail.com** with the subject line "Privacy Request".

---

## 9. Children's Privacy

MDUMENI is not directed at children under the age of 13. We do not knowingly collect personal information from children under 13. If you believe a child under 13 has provided us with information, please contact us and we will delete it promptly.

---

## 10. Offline Use

A core principle of MDUMENI is that your farming data never has to leave your phone. When you use the app offline:

- All AI crop recommendations are generated entirely on your device
- All farming calendar guidance is generated on your device
- All pest and disease diagnosis is performed on your device
- No data is transmitted to any server

You can use MDUMENI fully offline indefinitely. Internet connectivity is required only for: AI chat (Groq), live market prices, account registration/login, and marketplace listings.

---

## 11. Third-Party Services

MDUMENI integrates with the following third-party services:

| Service | Purpose | Their Privacy Policy |
|---|---|---|
| Supabase | Database and authentication | https://supabase.com/privacy |
| Groq Inc. | AI language model inference | https://groq.com/privacy-policy/ |
| Railway | Backend server hosting | https://railway.com/privacy |

---

## 12. Changes to This Policy

We may update this Privacy Policy as the app evolves. When we make material changes, we will notify you through an in-app notification. The effective date at the top of this page will always reflect the most recent update.

Continued use of MDUMENI after changes are posted constitutes your acceptance of the revised policy.

---

## 13. Contact Us

If you have any questions about this Privacy Policy or how we handle your data:

**Eugine Bhebhe**  
INTELLI-Farming · University of Zimbabwe  
📧 bhebheeugine@gmail.com  
📱 +263 78 461 7009  

For formal data protection enquiries, please write to us at the above email with the subject line "Data Protection".

---

*This Privacy Policy applies to MDUMENI version 1.0.0 and above.*  
*© 2026 INTELLI-Farming, University of Zimbabwe. All rights reserved.*
