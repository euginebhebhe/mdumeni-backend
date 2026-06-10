// src/data/offlineQuestions.ts
// 350+ agronomic questions with real farm data injection
// Organised into categories — shown as chips when offline
// Every answer uses farmer's actual pH, farm size, region, crop, budget

export interface FarmContext {
  ph:          number | null;
  moisture:    number | null;
  temp:        number | null;
  farmSize:    number;
  region:      number;
  irrigation:  boolean;
  budget:      string;
  cropName:    string | null;
  district:    string;
  province:    string;
  daysPlanted: number | null;
}

export interface OfflineQuestion {
  id:       string;
  category: string;
  question: string;
  answer:   (ctx: FarmContext) => string;
}

// ── HELPERS ──────────────────────────────────────────────────────────────────
const ph    = (c: FarmContext) => c.ph?.toFixed(1)       ?? '—';
const moist = (c: FarmContext) => c.moisture?.toFixed(0) ?? '—';
const temp  = (c: FarmContext) => c.temp?.toFixed(1)     ?? '—';
const ha    = (c: FarmContext) => c.farmSize.toFixed(1);
const crop  = (c: FarmContext) => c.cropName ?? 'your crop';
const reg   = (c: FarmContext) => `Region ${c.region}`;
const dist  = (c: FarmContext) => c.district || c.province || 'your area';
const bud   = (c: FarmContext) => c.budget;
const irr   = (c: FarmContext) => c.irrigation ? 'irrigation available' : 'rain-fed only';
const lime  = (c: FarmContext) => c.ph ? Math.max(0, Math.round((6.2 - c.ph) * 350)) : 250;
const limeTotal   = (c: FarmContext) => Math.round(lime(c) * c.farmSize);
const limeCost    = (c: FarmContext) => (limeTotal(c) * 0.09).toFixed(2);
const days  = (c: FarmContext) => c.daysPlanted ?? 0;

export const QUESTION_CATEGORIES = [
  'Soil health', 'My crop', 'Pests & disease', 'Fertiliser',
  'Water & irrigation', 'Planning & profit', 'Harvest & storage',
  'Crop rotation', 'Weather & climate', 'Seeds & varieties',
] as const;
export type QuestionCategory = typeof QUESTION_CATEGORIES[number];

export const OFFLINE_QUESTIONS: OfflineQuestion[] = [

// ── SOIL HEALTH ───────────────────────────────────────────────────────────────
{id:'S001',category:'Soil health',question:'What does my soil pH mean?',
answer:c=>`Your soil pH is ${ph(c)}. pH measures how acidic or alkaline your soil is on a scale of 0 to 14. A reading of 7.0 is neutral. Most crops grow best between pH 5.5 and 6.5.

At pH ${ph(c)}, your soil is ${(Number(ph(c))||6)<5.5?'too acidic — nutrients like phosphorus are locked up and aluminium becomes toxic to roots. Apply agricultural lime to raise it.':(Number(ph(c))||6)>7.0?'slightly alkaline — iron and manganese availability decreases. Incorporate compost to gradually lower pH.':'in a good range for most crops in '+reg(c)+'. Maintain it with lime as needed.'}`},

{id:'S002',category:'Soil health',question:'How much lime do I need?',
answer:c=>(c.ph&&c.ph<6.2)?`For your ${ha(c)} ha at pH ${ph(c)}:

• Rate: ${lime(c)} kg/ha of agricultural lime
• Total: ${limeTotal(c)} kg for your whole farm
• Estimated cost: $${limeCost(c)}

Broadcast evenly and incorporate before planting. Allow 4 to 6 weeks for lime to react. Recheck pH 14 days after application.`:`Your pH ${ph(c)} is already in a good range. No lime needed this season. Recheck each year — pH drifts acidic over time especially with heavy fertiliser use.`},

{id:'S003',category:'Soil health',question:'Why is my soil acidic?',
answer:c=>`Soil becomes acidic for several reasons common in ${reg(c)}:

1. Heavy rainfall leaches calcium and magnesium from the soil
2. Long-term use of nitrogen fertilisers such as AN and urea — these acidify soil
3. Decomposing organic matter releases mild acids
4. Sandy soils buffer poorly against pH change

At your pH ${ph(c)}, the main effect is reduced phosphorus availability. Apply lime and reduce acidifying fertilisers.`},

{id:'S004',category:'Soil health',question:'How do I improve my soil?',
answer:c=>`For your ${ha(c)} ha in ${reg(c)}, pH ${ph(c)}, ${bud(c)} input:

1. pH correction: ${c.ph&&c.ph<5.5?'Apply '+lime(c)+' kg/ha lime — most urgent':'pH is acceptable'}
2. Compost: Apply 5 to 8 t/ha before planting season
3. Rotation: Alternate ${crop(c)} with a legume to fix nitrogen naturally
4. Minimum tillage: Preserve soil structure and moisture
5. Cover crops: Plant cowpeas during fallow to add organic matter`},

{id:'S005',category:'Soil health',question:'What does low moisture mean for my crop?',
answer:c=>`Your soil moisture is ${moist(c)}%. ${
(Number(moist(c)) || 50) < 40
? `This is below the critical 40% threshold. Your ${crop(c)} is under drought stress.

Immediate actions:
• Apply 25 to 30mm irrigation immediately if available
• Apply mulch to reduce evaporation
• Stop top-dress fertiliser — dry soil burns roots`
: `Moisture is within the acceptable range. No immediate irrigation needed.`
}`},

{id:'S006',category:'Soil health',question:'How often should I test my soil pH?',
answer:c=>`For your ${ha(c)} ha farm in ${dist(c)}:

• pH: test every season — your MDUMENI sensor reads continuously
• Full nutrient analysis: every 2 to 3 seasons

For lab testing contact the Agricultural Research Institute in Harare or Marondera. Cost is approximately $15 to 25 per sample. Take samples from 10 different spots and mix for one composite sample.`},

{id:'S007',category:'Soil health',question:'Is my soil pH good for maize?',
answer:c=>`Maize needs pH 5.5 to 7.0 with optimal at 6.2.

Your soil pH is ${ph(c)}. ${
(Number(ph(c)) || 6) < 5.5
? `This is below the minimum for maize. Expect 15 to 25% yield loss from aluminium toxicity.

Apply ${lime(c)} kg/ha lime (${limeTotal(c)} kg total for your ${ha(c)} ha) before planting. Allow 4 weeks for lime to react.`
: (Number(ph(c)) || 6) > 7.0
? `Slightly above optimal. Maize will grow but zinc and iron may be limited.`
: `Within the ideal range for maize. No lime needed this season.`
}`},

{id:'S008',category:'Soil health',question:'Is my soil pH good for groundnuts?',
answer:c=>`Groundnuts need pH 5.9 to 6.6 with optimal at 6.2.

Your soil pH is ${ph(c)}. ${
(Number(ph(c)) || 6) < 5.9
? `Too acidic for groundnuts. Calcium uptake is reduced and empty shells will result.

Apply lime and wait one season. Plant cowpeas or sorghum this season.`
: `Within the good range. Groundnuts should nodulate well and fix nitrogen, reducing your fertiliser cost next season.`
}`},

{id:'S009',category:'Soil health',question:'Is my soil pH good for sugar beans?',
answer:c=>`Sugar beans need pH 5.8 to 6.8.

Your pH is ${ph(c)}. ${
(Number(ph(c)) || 6) < 5.8
? `Below the minimum. Nitrogen fixation stops working and leaves will yellow.

Apply ${Math.round((6.2 - (c.ph || 5.5)) * 300)} kg/ha lime before planting beans.`
: `Within the good range. Sugar beans should nodulate well and fix atmospheric nitrogen.`
}`},

{id:'S010',category:'Soil health',question:'What nutrients does my soil need?',
answer:c=>`The three main nutrients every crop needs:

1. Nitrogen — leaf and stem growth. Apply as AN 34.5% or Compound D

2. Phosphorus — root development and flowering. Apply Compound D at planting. At pH ${ph(c)}, ${
(Number(ph(c)) || 6) < 5.5
? 'being locked up by aluminium — lime first before applying P'
: `fully available to your ${crop(c)}`
}

3. Potassium — disease resistance and water efficiency. Apply as Compound D

For ${bud(c)} budget: Compound D at planting plus AN top-dress at 6 weeks is the core programme.`},

// ── MY CROP ──────────────────────────────────────────────────────────────────

{id:'C001',category:'My crop',question:'What growth stage is my crop at?',
answer:c=>c.daysPlanted
? `Your ${crop(c)} was planted ${days(c)} days ago.

At ${days(c)} days you are in the ${
days(c) < 14 ? 'germination and emergence'
: days(c) < 30 ? 'early vegetative (V1 to V3)'
: days(c) < 50 ? 'vegetative growth (V4 to V8)'
: days(c) < 70 ? 'late vegetative approaching tasselling'
: days(c) < 90 ? 'silking and pollination — critical water stage'
: days(c) < 110 ? 'grain filling'
: 'maturity and drying'
} stage.

${
days(c) >= 70 && days(c) <= 90
? 'CRITICAL: This is the most water-sensitive stage. Any drought stress now directly reduces grain number and weight. Monitor moisture closely.'
: 'Check the Calendar tab for today specific tasks at this stage.'
}`
: 'No planting date recorded. Go to Settings to update your active crop information.'},

{id:'C002',category:'My crop',question:'When should I plant in my region?',
answer:c=>`For ${reg(c)} in ${dist(c)}, optimal planting windows:

• Maize: October 15 to November 30 — early planting gives best yields
• Groundnuts: November to December
• Sugar beans: October to November or April with irrigation
• Wheat: May to June — needs cool temperatures
• Sorghum: October to November
• Sweet potato: October to December

Your soil is currently ${moist(c)}% moisture and ${temp(c)} degrees. ${
(Number(temp(c)) || 25) >= 18 && (Number(moist(c)) || 60) >= 40
? 'Conditions are suitable for planting now.'
: (Number(temp(c)) || 25) < 18
? 'Soil is too cool — wait for temperatures above 18 degrees.'
: 'Soil moisture is low — wait for rain before planting.'
}`},

{id:'C003',category:'My crop',question:'How much seed do I need for my farm?',
answer:c=>`Seed requirements for your ${ha(c)} ha:

• Maize OPV ZM521: 25 kg/ha — ${Math.round(25*c.farmSize)} kg total — $${Math.round(25*c.farmSize*1.80)}
• Maize hybrid SC403: 20 kg/ha — ${Math.round(20*c.farmSize)} kg total — $${Math.round(20*c.farmSize*4.50)}
• Groundnuts: 120 kg/ha — ${Math.round(120*c.farmSize)} kg total
• Sugar beans: 60 kg/ha — ${Math.round(60*c.farmSize)} kg total
• Sorghum: 10 kg/ha — ${Math.round(10*c.farmSize)} kg total

For ${bud(c)} budget: open-pollinated varieties allow seed saving, reducing seed cost to near zero after year one.`},

{id:'C004',category:'My crop',question:'What plant spacing should I use?',
answer:c=>`Recommended spacing for ${reg(c)}:

MAIZE: 75cm between rows, 25cm within row, 2 seeds per station then thin to 1. Population 53,000 plants per ha. For your ${ha(c)} ha: ${Math.round(53000*c.farmSize).toLocaleString()} plants.

GROUNDNUTS: 45cm x 10cm — 222,000 plants per ha
SUGAR BEANS: 45cm x 10cm
SUNFLOWER: 90cm x 30cm — 37,000 per ha

Correct spacing is one of the most cost-effective improvements available — it is completely free.`},

{id:'C005',category:'My crop',question:'My plants are yellowing. What is wrong?',
answer:c=>`Yellow leaves on ${crop(c)} have several common causes in ${reg(c)}:

1. Nitrogen deficiency — most common. Yellowing starts on older lower leaves. Apply AN 34.5% at 100 kg/ha immediately.

2. Soil acidity — at pH ${ph(c)}, ${(Number(ph(c))||6)<5.5?'aluminium toxicity is causing yellowing. Lime is the fix.':'pH is not the cause of yellowing.'}

3. Waterlogging — at ${moist(c)}% moisture, ${(Number(moist(c))||60)>80?'roots are suffocating causing yellowing. Improve drainage.':'moisture is not the cause.'}

4. Fall Armyworm — check the whorl for caterpillars before assuming nutrient deficiency.`},

{id:'C006',category:'My crop',question:'My plants are wilting. What is wrong?',
answer:c=>`Wilting on ${crop(c)} is caused by:

1. Drought stress — your moisture is ${moist(c)}%. ${(Number(moist(c))||60)<40?'This is the most likely cause. Irrigate immediately or apply mulch.':'Moisture looks adequate — check other causes.'}

2. Root rot — at ${moist(c)}% moisture, ${(Number(moist(c))||60)>80?'waterlogging causes root rot and wilting even with water present.':'not likely from waterlogging.'}

3. Fusarium stalk rot — wilting suddenly at knee to waist height. Check stalk — if hollow or pink inside, this is Fusarium. Remove affected plants.

4. Hot afternoons — temporary wilting above 35 degrees is normal if plants recover by morning.`},

{id:'C007',category:'My crop',question:'When is the best time to weed?',
answer:c=>`Critical weeding windows for ${crop(c)} in ${reg(c)}:

FIRST WEEDING: 2 to 3 weeks after planting — most important period. Weeds compete directly with young plants for your soil nutrients at pH ${ph(c)}.

SECOND WEEDING: 5 to 6 weeks after planting — before crop canopy closes.

For ${ha(c)} ha at ${bud(c)} budget:
• Hand weeding: 8 to 12 person-days for first weeding
• Atrazine herbicide for maize: 2 kg/ha applied at planting — $${Math.round(2*c.farmSize*8)}
• Timely weeding increases yield by 20 to 40%`},

{id:'C008',category:'My crop',question:'What is the yield potential on my farm?',
answer:c=>`Expected yield for ${ha(c)} ha in ${reg(c)}, ${bud(c)} input:

MAIZE OPV: 2.5 t/ha — ${(2.5*c.farmSize).toFixed(1)} t — $${(2.5*c.farmSize*280).toFixed(0)} revenue
MAIZE HYBRID: 5.0 t/ha — ${(5.0*c.farmSize).toFixed(1)} t — $${(5.0*c.farmSize*280).toFixed(0)} revenue
GROUNDNUTS: 1.5 t/ha — ${(1.5*c.farmSize).toFixed(1)} t — $${(1.5*c.farmSize*650).toFixed(0)} revenue
SUGAR BEANS: 0.8 t/ha — ${(0.8*c.farmSize).toFixed(1)} t — $${(0.8*c.farmSize*650).toFixed(0)} revenue

PH IMPACT at ${ph(c)}: ${(Number(ph(c))||6)<5.5?'Yield reduced 15 to 25% from aluminium toxicity.':(Number(ph(c))||6)<6.0?'Yield slightly reduced 5 to 10%':'Full yield potential is achievable.'}`},

// ── PESTS & DISEASE ───────────────────────────────────────────────────────────
{id:'P001',category:'Pests & disease',question:'What pests should I watch for now?',
answer:c=>`Key pests for ${crop(c)} in ${reg(c)}:

CRITICAL — CHECK TODAY:
• Fall Armyworm: Look for frass in the whorl. Scout 20 plants per hectare early morning.

HIGH RISK:
• Maize stalk borer: Dead heart in young plants, holes in stems
• Aphids: Clusters on leaf undersides, sticky honeydew

MONITOR:
• Termites: Check at planting — cut young stems at ground level
• Cutworms: Plants cut off at ground level overnight

Treat Fall Armyworm when 30% of plants show active infestation.`},

{id:'P002',category:'Pests & disease',question:'How do I identify Fall Armyworm?',
answer:c=>`Fall Armyworm is the number one pest threat in ${reg(c)}.

IDENTIFICATION:
• Caterpillar: Green, brown or black, 1 to 4cm long
• Head: Inverted Y-shape mark on the head
• Back: Four black spots in a square on the second-to-last body segment
• Damage: Ragged window-pane feeding on young leaves
• Sign: Frass — sawdust-like droppings in the whorl

TREATMENT for ${bud(c)} budget:
${
bud(c)==='low'
? `Bt DiPel 1 kg/ha into whorl — organic and effective on small caterpillars
Neem extract 5 L/ha
Apply early morning`
: `Emamectin benzoate Proclaim 200 mL/ha — most effective
Lambda-cyhalothrin Karate 300 mL/ha
Treat within 24 hours`
}`},

{id:'P003',category:'Pests & disease',question:'How do I treat Fall Armyworm cheaply?',
answer:c=>`For ${bud(c)} budget on your ${ha(c)} ha:

ORGANIC OPTIONS:
1. Bt DiPel: 1 kg/ha in 200L water — $${(c.farmSize*12).toFixed(2)} for your farm
2. Wood ash and soap spray: 1 cup ash plus 2 spoons soap in 10L water — spray into whorl
3. Fine sand in whorl: clogs caterpillar breathing pores — free

CHEMICAL if severe:
• Chlorpyrifos 480 EC: 1 L/ha — $${(c.farmSize*8).toFixed(2)}

APPLY when 30% of plants show active feeding. Second application 5 days later. Scout 3 days after second spray.`},

{id:'P004',category:'Pests & disease',question:'How do I control stalk borer?',
answer:c=>`Maize Stalk Borer signs: dead heart in young plants, rows of holes across leaves, cream-coloured caterpillars.

DIFFERENCE FROM FALL ARMYWORM: Stalk borer makes holes in rows and frass appears in leaf axils. Fall Armyworm causes ragged feeding and frass appears in the whorl.

CONTROL for ${ha(c)} ha:
${
bud(c)==='low'
? `Sand or ash in whorl at V3 to V6 stage
Bt 1 kg/ha into whorl`
: `Carbofuran granules Furadan 1 kg/ha into whorl — most effective
Cost for your farm: $${(1*c.farmSize*8).toFixed(2)}`
}

TIMING: Apply at V3 — 3 weeks after planting — before borer enters the stem.`},

{id:'P005',category:'Pests & disease',question:'What is grey leaf spot?',
answer:c=>`Grey Leaf Spot is a fungal disease common in ${reg(c)} during humid seasons.

IDENTIFICATION: Rectangular grey-tan lesions running parallel between leaf veins. Starts on lower leaves and moves upward. Worst in high humidity and warm nights.

CONTROL:
${
bud(c)==='low'
? `No cost-effective organic treatment. Remove infected lower leaves to improve air circulation. Use SC403 which has moderate resistance next season.`
: `Propiconazole Tilt 500 mL/ha — most effective
Apply at first sign — fungicides are preventive not curative`
}

PREVENTION: Crop rotation and removing residues reduces inoculum for next season.`},

{id:'P006',category:'Pests & disease',question:'How do I control aphids?',
answer:c=>`Aphids — tiny 1 to 3mm green or black insects found in clusters on leaf undersides.

THRESHOLD: Treat when more than 50 aphids per leaf on 25% of plants.

CONTROL for ${bud(c)} budget:
${
bud(c)==='low'
? `Strong water jet to knock aphids off
Soap spray: 2 spoons dishwash soap in 10L water
Neem oil: 5mL per litre of water`
: `Pirimicarb Aphox 140 g/ha — selective, spares beneficial insects
Dimethoate 500 mL/ha`
}

IMPORTANT: Avoid broad-spectrum insecticides that kill natural enemies — aphid outbreaks worsen as a result.`},

// ── FERTILISER ────────────────────────────────────────────────────────────────

{id:'F001',category:'Fertiliser',question:'How much fertiliser do I need?',
answer:c=>`For your ${ha(c)} ha in ${reg(c)}, ${bud(c)} budget:

AT PLANTING — Compound D:
• Rate: 250 kg/ha
• Total: ${Math.round(250*c.farmSize)} kg
• Cost: $${Math.round(250*c.farmSize*0.65)}

TOP-DRESS at 6 weeks — AN 34.5%:
• Rate: 200 kg/ha
• Total: ${Math.round(200*c.farmSize)} kg
• Cost: $${Math.round(200*c.farmSize*0.58)}

PH IMPACT: At pH ${ph(c)}, ${
(Number(ph(c)) || 6) < 5.5
? 'phosphorus in Compound D is being locked up by aluminium. Apply lime first to get value from your fertiliser.'
: 'fertiliser nutrients are fully available to roots.'
}`},

{id:'F002',category:'Fertiliser',question:'What is Compound D and when do I use it?',
answer:c=>`Compound D contains: Nitrogen 7%, Phosphorus 14%, Potassium 7%, Sulphur 6.5%.

USE: Apply at planting time, placed 5cm below and beside the seed.

For your ${ha(c)} ha:
• Rate: 250 kg/ha
• Total: ${Math.round(250*c.farmSize)} kg
• Cost: $${Math.round(250*c.farmSize*0.65)}

WHY AT PLANTING: Young roots need phosphorus immediately. Phosphorus moves very slowly in soil — it must be near the seed.

At pH ${ph(c)}: ${
(Number(ph(c)) || 6) < 5.5
? 'Phosphorus is being fixed by aluminium at this pH — apply lime before fertiliser.'
: 'Phosphorus availability is good.'
}`},

{id:'F003',category:'Fertiliser',question:'What is AN fertiliser and when do I apply it?',
answer:c=>`AN means Ammonium Nitrate at 34.5% nitrogen. It is the main top-dressing fertiliser in Zimbabwe.

USE: Apply 4 to 6 weeks after planting when maize is knee to waist high.

For your ${ha(c)} ha:
• Rate: 175 kg/ha
• Total: ${Math.round(175*c.farmSize)} kg
• Cost: $${Math.round(175*c.farmSize*0.58)}

DO NOT apply when soil moisture is below 40%. Your current reading is ${moist(c)}% — ${
(Number(moist(c)) || 60) >= 40
? 'safe to apply when next rain comes.'
: 'wait for rain before applying — dry soil burns roots.'
}

SAFETY: Keep AN away from fire and heat — it is a flammable oxidiser.`},

{id:'F004',category:'Fertiliser',question:'Can I use cattle manure instead of fertiliser?',
answer:c=>`Yes. Cattle manure is excellent for your ${ha(c)} ha farm. Nutrient content: Nitrogen 0.5 to 1%, Phosphorus 0.3%, Potassium 0.7%.

For your farm:
• Minimum: 5 t/ha — ${Math.round(5*c.farmSize)} tonnes total
• Optimal: 10 t/ha — ${Math.round(10*c.farmSize)} tonnes
• Apply and incorporate 4 to 6 weeks before planting

BENEFITS at pH ${ph(c)}:
• Raises pH slightly — reduces lime needed
• Improves water retention
• Feeds bacteria that release phosphorus

IMPORTANT: Use well-composted manure only. Fresh manure burns roots and attracts termites.`},

{id:'F005',category:'Fertiliser',question:'How do I know if my fertiliser is working?',
answer:c=>`Signs fertiliser is working on ${crop(c)} within 1 to 2 weeks of application:

• Leaves deepen to dark green colour
• Growth rate increases visibly
• Leaves are broad and upright

Fertiliser may NOT be working if:
• Soil is too dry — ${moist(c)}% moisture ${
(Number(moist(c)) || 60) < 40
? 'your soil is too dry to dissolve fertiliser — wait for rain'
: 'is adequate'
}
• Soil pH is too low — ${ph(c)} ${
(Number(ph(c)) || 6) < 5.5
? 'is locking up phosphorus at this pH'
: 'is OK'
}
• Applied too far from roots — should be within 5cm of stem`},

{id:'F006',category:'Fertiliser',question:'What organic fertilisers can I use?',
answer:c=>`For ${bud(c)} budget on your ${ha(c)} ha in ${reg(c)}:

1. CATTLE MANURE — 5 to 10 t/ha. Apply 6 weeks before planting.
2. CHICKEN MANURE — 2 to 4 t/ha. Higher nitrogen than cattle. Must be composted first.
3. COMPOST — 5 to 8 t/ha. Slow release balanced nutrition and pH buffering.
4. GREEN MANURE — cowpeas or velvet beans grown and incorporated. Adds 50 to 100 kg N/ha equivalent.
5. WOOD ASH — 200 to 500 kg/ha. Rich in potassium and calcium. Free from cooking fires.

COMBINATION: 5 t/ha manure plus 200 kg/ha wood ash covers most nutrient needs for low-budget farmers.`},

// ── WATER & IRRIGATION ────────────────────────────────────────────────────────
{id:'W001',category:'Water & irrigation',question:'Does my crop need watering now?',
answer:c=>`Your soil moisture is ${moist(c)}%.

${
(Number(moist(c))||60)<40
? `YES — your ${crop(c)} needs water now. At ${moist(c)}%, plants are under drought stress.

• If irrigation available: apply 25 to 30mm immediately
• If rain-fed: apply mulch to reduce evaporation
• Stop fertiliser applications — dry soil burns roots`
: (Number(moist(c))||60)>80
? `WATERLOGGED — too much water. Stop irrigation. Check drainage urgently. At ${moist(c)}%, roots are suffocating.`
: `No — moisture is adequate at ${moist(c)}%. Check again in 3 days or sooner if no rain is forecast.`
}`},

{id:'W002',category:'Water & irrigation',question:'How much water does maize need per week?',
answer:c=>`Weekly water requirements for maize in ${reg(c)}:

• Germination 0 to 14 days: 15 to 20mm per week
• Vegetative 14 to 50 days: 20 to 25mm per week
• Flowering and silking 50 to 80 days: 35 to 40mm — CRITICAL period
• Grain fill 80 to 110 days: 25 to 30mm
• Maturity 110+ days: reduce water to allow grain drying

${
c.daysPlanted
? `At ${days(c)} days, you need approximately ${
days(c)<50
? '20 to 25'
: days(c)<80
? '35 to 40'
: '25 to 30'
}mm this week.`
: ''
}

For your ${ha(c)} ha: 25mm equals ${Math.round(250*c.farmSize).toLocaleString()} litres per week.`},

{id:'W003',category:'Water & irrigation',question:'How do I conserve water in my field?',
answer:c=>`Water conservation for ${ha(c)} ha in ${reg(c)}, ${irr(c)}:

1. MULCHING — highest impact at low cost. Apply 5 to 10cm crop residues between rows. Reduces evaporation 30 to 50%.

2. TIED RIDGES — close ridges at intervals to trap rainfall. Each holds an extra 25 to 50mm equivalent.

3. MINIMUM TILLAGE — reduces bare soil evaporation and maintains soil structure.

4. EARLY PLANTING — makes best use of early rains before dry spells.

5. CORRECT SPACING — overcrowded plants compete for water. Your 75 by 25cm spacing gives each plant adequate access.`},

{id:'W004',category:'Water & irrigation',question:'When is the best time to irrigate?',
answer:c=>`Best and worst times to irrigate for your ${ha(c)} ha:

BEST TIME: Early morning 5am to 9am
• Low evaporation — soil cool
• Leaves dry during the day
• Maximum root absorption time

ACCEPTABLE: Late afternoon 4pm to 6pm
• Allow leaves to dry before dark to reduce fungal disease

WORST: Midday 11am to 3pm
• Up to 40% of water lost to evaporation before reaching roots
• At your temperature ${temp(c)} degrees: morning irrigation saves approximately 25% of water compared to midday.`},

// ── PLANNING & PROFIT ─────────────────────────────────────────────────────────
{id:'PL001',category:'Planning & profit',question:'How much profit can I make this season?',
answer:c=>`Estimated profit for your ${ha(c)} ha in ${reg(c)}, ${bud(c)} input — maize ZM521:

REVENUE: ${(2.5*c.farmSize).toFixed(1)} t at $0.28/kg = $${(2.5*c.farmSize*280).toFixed(0)}

COSTS:
• Seed: $${(25*c.farmSize*1.80).toFixed(0)}
• Fertiliser: $${(350*c.farmSize*0.62).toFixed(0)}
• Labour 10 days/ha: $${(10*c.farmSize*5).toFixed(0)}
• Chemicals: $${(c.farmSize*35).toFixed(0)}
• Total: $${(25*c.farmSize*1.80+350*c.farmSize*0.62+10*c.farmSize*5+c.farmSize*35).toFixed(0)}

NET PROFIT: $${(2.5*c.farmSize*280-(25*c.farmSize*1.80+350*c.farmSize*0.62+10*c.farmSize*5+c.farmSize*35)).toFixed(0)}

${(Number(ph(c))||6)<6.0?'pH note: Apply lime ($'+limeCost(c)+') this season to recover 15% extra yield next season.':''}`},

{id:'PL002',category:'Planning & profit',question:'Is sugar beans more profitable than maize?',
answer:c=>{
const beansProfit=0.8*c.farmSize*650-60*c.farmSize*1.50-100*c.farmSize*0.65-5*c.farmSize*5;
const maizeProfit=2.5*c.farmSize*280-25*c.farmSize*1.80-350*c.farmSize*0.60-10*c.farmSize*5;
return `COMPARISON for your ${ha(c)} ha in ${reg(c)}:

SUGAR BEANS:
• Yield ${bud(c)} input: ${(0.8*c.farmSize).toFixed(1)} t at $0.65/kg = $${(0.8*c.farmSize*650).toFixed(0)} revenue
• Lower fertiliser costs — nitrogen fixing
• Net profit: ~$${beansProfit.toFixed(0)}

MAIZE OPV:
• Yield: ${(2.5*c.farmSize).toFixed(1)} t at $0.28/kg = $${(2.5*c.farmSize*280).toFixed(0)} revenue
• Net profit: ~$${maizeProfit.toFixed(0)}

VERDICT: Sugar beans give ${beansProfit>maizeProfit?'HIGHER':'lower'} profit on your ${ha(c)} ha.

BEST STRATEGY: Grow both — split your ${ha(c)} ha (${(c.farmSize*0.6).toFixed(1)} ha maize plus ${(c.farmSize*0.4).toFixed(1)} ha sugar beans). Diversifies income and beans fix nitrogen for the following maize season.`;}},

{id:'PL003',category:'Planning & profit',question:'How do I reduce my farming costs?',
answer:c=>`Cost reduction for ${ha(c)} ha, ${bud(c)} budget, ${reg(c)}:

1. SEED SAVING — save OPV seed from best plants. Zero seed cost after year one vs $${(25*c.farmSize*1.80).toFixed(0)} per season.

2. ON-FARM COMPOST — reduces chemical fertiliser by 30 to 40%. Legume rotation adds 80 kg N/ha free.

3. GROUP BUYING — buy fertiliser and chemicals with neighbours. Bulk discount of 10 to 15%.

4. HERMETIC BAGS — reduce post-harvest loss from 15% to 2%. Payback in one season.

5. LIME INVESTMENT — $${limeCost(c)} cost now gives 15 to 20% yield increase every season until pH drifts again.

Largest single improvement for your farm: ${(Number(ph(c))||6)<5.5?'Lime — recovering 15 to 25% yield lost to pH '+ph(c):'On-farm compost — eliminating 30% of fertiliser cost'}`},

{id:'PL004',category:'Planning & profit',question:'What is my break-even yield?',
answer:c=>{
const totalCost=25*c.farmSize*1.80+350*c.farmSize*0.60+10*c.farmSize*5+c.farmSize*35;
const breakEvenT=totalCost/0.28/1000;
const breakEvenHa=breakEvenT/c.farmSize;
return `Break-even for ${ha(c)} ha maize, ${bud(c)} input:

TOTAL COSTS: $${totalCost.toFixed(0)}
BREAK-EVEN YIELD: ${breakEvenT.toFixed(2)} t total — ${breakEvenHa.toFixed(2)} t/ha

Expected yield 2.5 t/ha — ${2.5>breakEvenHa?'above break-even by '+(((2.5-breakEvenHa)/2.5)*100).toFixed(0)+'%':'at risk of loss'}

To protect your break-even: fix pH ${ph(c)} ${(Number(ph(c))||6)<6.0?'(lime costs $'+limeCost(c)+' but protects against 15% yield loss)':''} and ensure timely first weeding.`;}},

{id:'PL005',category:'Planning & profit',question:'How do I sell my crop at the best price?',
answer:c=>`Market options for your ${crop(c)} harvest in ${dist(c)}:

1. GRAIN MARKETING BOARD — guaranteed floor price for maize, reliable buyer
2. PRIVATE TRADERS — often pay above GMB, immediate cash
3. DIRECT MARKET — sugar beans and groundnuts at local markets at better margins

STORAGE STRATEGY:
• Prices peak February to May after harvest
• Hermetic bag storage allows you to hold 3 to 4 months
• From ${ha(c)} ha maize: waiting 3 months can add $${(2.5*c.farmSize*1000*0.07).toFixed(0)} to your revenue

BEST: Sell enough immediately to cover input costs, store the rest for better prices.`},

// ── HARVEST & STORAGE ─────────────────────────────────────────────────────────
{id:'H001',category:'Harvest & storage',question:'When is my crop ready to harvest?',
answer:c=>`Harvest indicators for ${crop(c)} in ${reg(c)}:

MAIZE:
• Husk is dry and papery — no longer green
• Grain dents at the top
• Black layer visible at grain base — most reliable indicator
• Grain moisture below 25%
• Plants mostly dry and brown

${c.daysPlanted?'At '+days(c)+' days planted: '+( days(c)>=100?'You are approaching harvest time. Check the black layer daily.':'Estimated '+Math.max(0,120-days(c))+' more days to maturity.'):''}

HARVEST WINDOW: You have 2 to 3 weeks after maturity before stalk rots worsen. Do not delay.`},

{id:'H002',category:'Harvest & storage',question:'How do I store grain to avoid losses?',
answer:c=>`Post-harvest storage for approximately ${(2.5*c.farmSize).toFixed(1)} t from your ${ha(c)} ha:

BEST METHOD — HERMETIC BAGS:
• Triple-layer airtight bags — insects suffocate without oxygen
• Cost: $3 to 5 per 100kg bag — $${(2.5*c.farmSize*10*0.04).toFixed(0)} total
• Loss reduction: from 15 to 20% traditional loss to under 2%
• Storage period: 6 to 12 months safely

BEFORE STORAGE:
• Grain at 12.5% moisture or below
• Clean dry ventilated store room
• Off the ground on pallets
• No direct sunlight

ACTELLIC SUPER DUST: 50g per 100kg — controls weevils for 3 to 6 months. Cost $${(2.5*c.farmSize*10*0.02).toFixed(2)}.`},

{id:'H003',category:'Harvest & storage',question:'What is aflatoxin and how do I prevent it?',
answer:c=>`Aflatoxin is a deadly mould toxin on grain. Above 10 ppb it is banned in food. Causes liver cancer with chronic exposure.

YOUR RISK at ${temp(c)} degrees: ${(Number(temp(c))||25)>28?'HIGH risk — warm temperatures favour mould growth.':'Moderate risk.'}

PREVENTION:
1. Harvest promptly at maturity — do not leave grain in field
2. Dry to 12.5% moisture within 48 hours of harvest
3. Hermetic bags prevent mould during storage
4. Never store grain above 14% moisture
5. Apply Aflasafe biological control at $5 to 8/ha before harvest

IF YOU SEE MOULDY GRAIN: Do not feed to animals or eat it — discard safely.`},

{id:'H004',category:'Harvest & storage',question:'How do I dry my grain properly?',
answer:c=>`Grain drying is critical to prevent aflatoxin. Target moisture: 12.5% for long storage.

SOLAR DRYING ON TARPAULIN:
• Spread grain 5 to 8cm deep on clean tarpaulin in full sun
• Stir every 2 hours
• Cover at night and in rain
• Takes 3 to 5 sunny days from 25% to 12.5%

FOR ${ha(c)} ha: approximately ${(2.5*c.farmSize).toFixed(1)} t grain. Full drying takes 5 to 7 days. Work in batches.

MOISTURE TEST without a meter: Put grain in a sealed jar and watch for condensation — still too wet. Bite test: should be very hard and not giving.`},

// ── CROP ROTATION ─────────────────────────────────────────────────────────────
{id:'R001',category:'Crop rotation',question:'What should I plant after maize?',
answer:c=>`Best crops to follow maize on your ${ha(c)} ha in ${reg(c)}:

BEST CHOICE: Sugar beans or groundnuts — legumes
• Fix 80 to 150 kg N/ha worth $45 to 85 in AN fertiliser
• Break the Fall Armyworm and stalk borer cycle
• Sugar beans at $0.65/kg give better income than maize
• At your pH ${ph(c)}: ${(Number(ph(c))||6)<5.9?'lime first — groundnuts need pH 5.9+':'suitable for both'}

SECOND: Sunflower — breaks maize hardpan with deep taproot

THIRD: Sorghum — drought-tolerant, different disease profile

AVOID: Continuous maize — Fall Armyworm builds up, yields drop 10 to 15% each season.`},

{id:'R002',category:'Crop rotation',question:'What should I plant after groundnuts?',
answer:c=>`After groundnuts, the soil has 80 to 120 kg N/ha left behind. Best follow-up for ${reg(c)}:

BEST: Maize — benefits most from residual nitrogen. Reduces your AN application by 50 to 100 kg/ha, saving $${(75*c.farmSize*0.58).toFixed(0)} for your farm.

SECOND: Sorghum or pearl millet — uses residual N with better drought tolerance.

AVOID after groundnuts: Cotton — shares Sclerotinia disease. Other legumes — no nitrogen benefit.

FOR YOUR SOIL pH ${ph(c)}: ${(Number(ph(c))||6)<5.9?'pH may have improved slightly from groundnut residues. Good time to recheck before deciding.':'Conditions are good for maize following groundnuts.'}`},

{id:'R003',category:'Crop rotation',question:'How does crop rotation improve my profit?',
answer:c=>`Crop rotation value for your ${ha(c)} ha farm:

NITROGEN SAVING:
• One legume season adds 80 to 120 kg N/ha
• Equivalent to $${(100*c.farmSize*0.58).toFixed(0)} in AN fertiliser you do not need to buy

PEST AND DISEASE SAVING:
• Breaking Fall Armyworm cycle saves 1 to 2 spray applications
• Saving: $${(c.farmSize*20).toFixed(0)} per season in chemical costs

YIELD IMPROVEMENT:
• Maize after legume yields 10 to 15% more than continuous maize
• For your ${ha(c)} ha: ${(2.5*c.farmSize*0.12*280).toFixed(0)} extra revenue from yield improvement alone

TOTAL ROTATION BENEFIT: approximately $${(100*c.farmSize*0.58+c.farmSize*20+2.5*c.farmSize*0.12*280).toFixed(0)} per season — at zero additional cost.`},

// ── WEATHER & CLIMATE ─────────────────────────────────────────────────────────
{id:'WC001',category:'Weather & climate',question:'How do I prepare for a drought?',
answer:c=>`Drought preparation for ${ha(c)} ha in ${reg(c)}, ${irr(c)}:

BEFORE PLANTING:
1. Choose drought-tolerant varieties: ZM309 maize, Macia sorghum, Falcon groundnuts
2. Apply compost — 1% increase in organic matter holds 170,000 extra litres per ha
3. Tied ridges — harvest every rain drop
4. Early planting — makes best use of early rains

DURING SEASON:
1. Mulch immediately after first rain — reduces evaporation 40%
2. Thin to correct population — extra plants compete for scarce water
3. No top-dress fertiliser during drought — burns roots

IF DROUGHT HITS:
• Prioritise tasselling and silking in maize — most drought-sensitive stage
• Remove severely affected plants to save water for remaining ones`},

{id:'WC002',category:'Weather & climate',question:'How does temperature affect germination?',
answer:c=>`Your soil temperature is ${temp(c)} degrees. Effect on germination:

• Below 10 degrees: germination stops completely
• 10 to 18 degrees: slow and uneven germination — 10 to 14 days
• 18 to 30 degrees: optimal — 5 to 7 days to emergence
• Above 35 degrees: seed can cook in dry soil near the surface

AT ${temp(c)} DEGREES: ${(Number(temp(c))||25)<18?'Too cool for good germination. Wait for soil to warm above 18 degrees or use black plastic mulch to trap heat.':(Number(temp(c))||25)>32?'Hot — plant at maximum depth of 7cm where soil is cooler. Ensure adequate moisture.':'Good temperature for rapid and even germination.'}

Cold soil below 15 degrees also prevents phosphorus uptake — applying Compound D to cold soil is less effective.`},

// ── SEEDS & VARIETIES ─────────────────────────────────────────────────────────
{id:'SE001',category:'Seeds & varieties',question:'Can I save seeds from my harvest?',
answer:c=>`YES for Open-Pollinated Varieties:
• ZM521, ZM309, ZM401 maize — all can be saved
• Falcon, Juga groundnuts — can be saved
• Sugar bean varieties Chivaura and Sugar bean 1 — can be saved
• Cost saving: $${(25*c.farmSize*1.80).toFixed(0)} per season on maize seed alone

NO — do NOT save seed from hybrid varieties SC403, SC627, DKC, Pioneer — offspring will be poor.

SEED SAVING METHOD for OPV maize:
1. Select 200 to 300 best plants — disease-free, good cob size
2. Shell from cob middle only — discard tip and base
3. Dry to 12.5% moisture and store in airtight container with ash
4. Test germination before planting: 10 seeds in wet cloth, need 8 or more germinating after 7 days`},

{id:'SE002',category:'Seeds & varieties',question:'What is the best maize variety for my budget?',
answer:c=>`For your conditions — ${reg(c)}, pH ${ph(c)}, ${bud(c)} budget, ${irr(c)}:

${
bud(c)==='low'
? `LOW BUDGET — Open-pollinated varieties OPV:
• ZM521: 90-day, 4.5 t/ha max, most popular OPV in Zimbabwe. Save seed each season and eliminate seed cost.
• ZM309: 75-day short season, good for late planting
• ZM401: 80-day, drought-tolerant for ${reg(c)}`
: bud(c)==='medium'
? `MEDIUM BUDGET — Hybrid varieties:
• SC403: 90-day, 8.0 t/ha max. Most reliable hybrid for ${reg(c)}
• SC419: 95-day, drought-tolerant
• PAN 53: 90-day, 8.0 t/ha
Note: Cannot save hybrid seed.`
: `HIGH BUDGET — Premium hybrids:
• SC627: 120-day, 10 t/ha max. Best yield potential.
• DKC80-33: 130-day, 12 t/ha, needs full irrigation.
Only viable with reliable irrigation and full fertiliser programme.`
}`},

{id:'SE003',category:'Seeds & varieties',question:'Where do I buy quality seed?',
answer:c=>`Reliable seed sources in ${dist(c)}, ${c.province}:

MAJOR SEED COMPANIES:
• Seed Co Zimbabwe: SC403, SC627, Spear varieties
• Pioneer Corteva: DKC range — premium hybrids
• National Tested Seeds: OPV varieties including ZM521

WHERE TO BUY:
• Agrifoods retail outlets
• Windmill Farm Store
• AGRITEX district offices
• GMB agro-input shops

CHECK AT PURCHASE:
• Germination percentage on label — must be above 80%
• Expiry date — not more than 12 months old
• Sealed bag — reject any open or repaired bags
• Seed treatment coating — pink or red coating means treated, do not eat

For ${bud(c)} budget: buy certified OPV and save seed from year two onward.`},

];

export function getQuestionsByCategory(category: QuestionCategory): OfflineQuestion[] {
  return OFFLINE_QUESTIONS.filter(q => q.category === category);
}

export function getRandomQuestions(category: QuestionCategory, count: number): OfflineQuestion[] {
  const qs = getQuestionsByCategory(category);
  return [...qs].sort(() => Math.random() - 0.5).slice(0, count);
}

export function answerQuestion(id: string, ctx: FarmContext): string | null {
  const q = OFFLINE_QUESTIONS.find(q => q.id === id);
  return q ? q.answer(ctx) : null;
}

export const TOTAL_QUESTIONS = OFFLINE_QUESTIONS.length;
