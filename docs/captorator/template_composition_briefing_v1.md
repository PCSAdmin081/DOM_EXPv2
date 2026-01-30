# Captorator Briefing: Expanded Template Library + Composition Rules

## 1) Objective
Create a scalable caption system that:
- Produces strong, non-slop first lines (“hooks”) across many niches.
- Maintains Certified network tone and structure (region relevance + follow + micro-CTA + credit + hashtags).
- Reduces operator typing by using canonical dropdown fields + optional free-text details.
- Avoids grammar failures (duplicates, awkward phrasing) via deterministic assembly rules and a quality gate.

This briefing contains:
1) A full expanded template library (hook-first-line variants).
2) A recommended “slot + rule” composition model to assemble hooks from parts.
3) Logic rules for how user inputs map to templates and how the engine selects and assembles output.

---

## 2) Canonical Inputs and Vocabulary
To assemble hooks reliably, Captorator should treat user inputs as structured parts.

### 2.1 Fields (conceptual)
- **(b)** business handle/name (prefer @handle).
- **(r)** region/city (Orlando, St. Pete, South Florida).
- **(n)** neighborhood/area (optional).
- **(sub)** item/subject (burger, speakeasy, donut, latte, brunch, trail, market).
- **(adj)** adjective/vibe (hidden, new, underrated, iconic, cozy, late-night).
- **(event)** event name.
- **(time)** day/time window.
- **(season)** holiday/season (Halloween, Spring Break, this weekend).
- **(who)** community member (chef, artist, founder).

### 2.2 Derived/normalized fields (internal intent)
- **content_type**: food / things / event / viral / spotlight / generic
- **niche** (optional): dessert, coffee, brunch, sandwiches, pizza, tacos, seafood, nightlife, wellness, family, shopping, community
- **hook_family**: question / statement / hot_take / sign / gatekeep / alert / list / debate / viral
- **handle_mode**: inline handle vs separate handle line
- **region_mode**: inline “in (r)” vs separate “(r), FL 📍” line

---

## 3) Output Structure Standards (Network)
The hook library below represents **first line only**. A standard network caption block typically follows:

1. Hook (from library or assembled)
2. Region lock (optional depending on style rules)
3. Follow line (profile-driven)
4. Micro-CTA (profile/tone/content-driven)
5. Credit line (creator + platform)
6. Hashtags (tight, targeted set; cap enforced)

---

## 4) Full Template Library (Hook Line Variants)

**Legend**
- (adj) adjective/vibe
- (sub) subject/item
- (b) business
- (r) region/city
- (n) neighborhood/area (optional)
- (who) person/community member
- (event) event name
- (time) day/time window
- (season) holiday/season

### A) Food & Drink (general)
1. does (b) have the best (sub) in (r)?
2. (r) — who’s got better (sub) than (b)? 👀
3. the (sub) at (b) is actually crazy 🤤
4. you’re telling me this (sub) exists in (r)??
5. hot take: (b) might be top 3 in (r) for (sub)
6. if you like (sub), you need (b) on your list ✅
7. (adj) (sub) alert 🚨 (b) in (r)
8. (b) is dangerously good for (sub)
9. I’d drive across (r) for this (sub) 😭
10. (sub) check: (b) understood the assignment
11. don’t walk—run to (b) for (sub)
12. the way I’d eat this (sub) again immediately…

**“Rate it” variants**
13. rate (b)’s (sub) in (r) 1–10 👇
14. overrated or properly rated? (b)’s (sub)
15. is (b) the (sub) champ of (r)? 🏆

---

### B) Food Niches (drop-in)
#### Sandwiches / subs
16. (b) just made the sandwich of the week 🥪
17. best sub run in (r): start at (b)
18. if you’re craving a (sub), (b) is the answer

#### Pizza
19. (r) pizza debate starts here 🍕 (b)
20. thin crust or thick? either way, (b) wins
21. (b) pizza night = solved ✅

#### Tacos / Mexican
22. taco spot check 🌮 (b) in (r)
23. (b) understood taco Tuesday
24. margs + tacos at (b)?? say less

#### Asian (Chinese/Japanese/Korean/Vietnamese/Thai)
25. (adj) (sub) in (r)… (b) did that
26. comfort food check: (b) for (sub)
27. if you’re craving (sub), don’t skip (b)

#### Italian
28. (r) — is (b) the move for Italian?
29. pasta night at (b) >>>>
30. (b) might be your new Italian go-to

#### Seafood
31. seafood cravings = (b) 🐟
32. (r) seafood run: (b) is a must
33. if it’s seafood in (r), I’m checking (b) first

#### Dessert / ice cream / bakery
34. sweet tooth alert 🍦 (b) in (r)
35. the dessert from (b) is a problem 😭
36. if you’re in (r) and need something sweet: (b)
37. (b) might have the best (sub) in (r) 🧁
38. this is your sign to get ice cream at (b)

#### Coffee / cafes
39. coffee + vibes at (b) ☕✨
40. (r) — add (b) to your cafe rotation
41. if you need a cute study/work spot: (b)
42. morning reset: (b) for (sub)

---

### C) Things to Do / Hidden Spots
43. did you know this exists in (r)? 😳
44. (r) locals: are we gatekeeping (b) or what?
45. save this for the weekend ✅ (b)
46. (adj) spot in (r) you need to check out
47. if you’re bored in (r), go to (b)
48. date idea in (r): (b)
49. group plans in (r)? send this 👇 (b)
50. this is your sign to try (b) in (r)

---

### D) Events
51. who’s going to (event) in (r)?
52. (event) this (time) in (r) 👀
53. weekend plans: (event) in (r) ✅
54. save this: (event) • (r) • (time)
55. tag your +1 👇 (event) in (r)
56. if you’re free this (time), pull up to (event)

---

### E) Local Business / Community Spotlight
57. local spot we’re loving: (b) in (r)
58. put some respect on (b) 👏 (r)
59. if you haven’t been to (b) yet… this is your sign
60. support local in (r): (b)
61. (r) — do you know about (b)?
62. shoutout (b) for doing it right ✅

**Community member spotlight**
63. (r) has talent — meet (who) 👏
64. support your local creators: (who) in (r)
65. (who) is putting on for (r) 🔥
66. (r) people: show (who) some love

---

### F) Nightlife / Bars / Speakeasies
67. need a date night spot in (r)? (b)
68. if you’re doing cocktails in (r) → (b)
69. (adj) speakeasy vibes in (r)… (b)
70. nightlife check: (b) understood the assignment 🥂
71. start the night at (b), thank me later
72. late-night plans in (r): (b)

---

### G) Wellness / Fitness / Reset Day
73. (r) wellness check: (b)
74. recovery day in (r) → (b)
75. if you need a reset in (r), start at (b)
76. (b) is a whole reset button 🧘
77. this is your sign to book (sub) in (r)
78. healthy spot in (r) you should know: (b)

---

### H) Family-Friendly / Kids / Group Activities
79. family plans in (r)? (b) ✅
80. take the kids to (b) in (r)
81. group activity in (r) that never misses: (b)
82. rainy day plan in (r): (b)
83. tag your friend who’d love this 👇 (b)

---

### I) Seasonal / Holiday
84. (season) plans in (r)? start at (b)
85. save this for (season) weekend ✅ (b)
86. (r) is doing (season) right… (b)
87. last-minute (season) idea in (r): (b)
88. bring your out-of-town friends to (b) this (season)

---

### J) Viral / OMG Florida Energy
89. FLORIDA. IS. UNDEFEATED. 😭
90. only in (r)…
91. what would you do?? 👇 (r)
92. this happened in (r) and I’m losing it 💀
93. caption this right now 👇

---

### K) Ultra-Short (minimal 1-line)
94. (b) in (r) >>>>
95. (adj) (sub) at (b)
96. (r) — don’t sleep on (b)
97. add (b) to your list ✅
98. tell me you’ve tried (b) 👀

---

### L) Expanded versions of your originals
99. does (b) have the best (sub) in (r)?
100. the (sub) from (b) 👀🤤
101. (b)’s (sub) = must try?? 😳
102. bet you can’t find better (sub) in (r) than (b) 😎
103. this weekend’s plans: (sub) at (b) 🥰 only in (r)
104. treat yourself: (sub) from (b)
105. (r)’s finest 🥰 (b)
106. we can’t get enough of (b)’s (sub) 🤤
107. if you know, you know… (b) in (r)
108. underrated (sub) spot in (r): (b)

---

## 5) Why “Slot + Rule” Assembly Is Better Than Storing 500 Full Hooks
A slot model:
- Normalizes user inputs into canonical noun phrases.
- Applies rules to avoid duplicates and awkward combos.
- Allows safe combinatoric variety from a small controlled library.

---

## 6) Hook Composition Model (Parts + Families)

### 6.1 Hook parts
- **Starter** (tone-coded): “does”, “hot take:”, “this is your sign…”, “(r) locals:”
- **Frame** (intent-coded): “have the best”, “might be top 3”, “put (b) on your list”
- **Noun phrase**: assembled from item/category_detail/place_type
- **Mentions**: business and region can be inline or separate lines
- **Finishers**: controlled punctuation and emojis

### 6.2 Hook families (recommended set)
1) **Question**
- “does (b) have the best (noun) in (r)?”
- “(r) — who’s got better (noun) than (b)? 👀”

2) **Claim / Statement**
- “(b) might be the move in (r).”
- “(r) — put (b) on your list.”

3) **Hot take**
- “hot take: (b) might be top 3 in (r) for (noun)”

4) **Sign / Recommendation**
- “this is your sign to try (b) in (r)”
- “if you like (noun), you need (b) on your list ✅”

5) **Gatekeep**
- “(b) is one of those (r) spots people gatekeep.”

6) **Alert**
- “(adj) (noun) alert 🚨 (b) in (r)”

7) **Plan / Weekend**
- “this weekend’s plans: (noun) at (b) 🥰”
- “save this for the weekend ✅ (b)”

8) **Viral (OMG)**
- “FLORIDA. IS. UNDEFEATED.”
- “only in (r)…”
- “caption this 👇”

---

## 7) Rules for Template Selection (Decision Logic)

### 7.1 Inputs that determine hook selection
- **content_type** drives which families are allowed.
- **tone** drives which starters and punctuation are allowed.
- **niche detector** (nightlife/wellness/dessert/etc.) overrides the generic family set.
- **handle_mode** decides whether business is included in hook or placed on its own line.

### 7.2 Recommended “Allowed Families” map
- **food**
  - allowed: question, claim, hot_take, sign, alert, plan
  - avoid: viral (unless OMG)

- **things**
  - allowed: sign, gatekeep, plan, claim
  - avoid: rating by default

- **event**
  - allowed: plan, question (“who’s going”), claim
  - must include: event name somewhere in first two lines

- **spotlight (local business/community)**
  - allowed: claim, sign, gatekeep, plan
  - avoid: rating by default

- **viral**
  - allowed: viral-only set

### 7.3 Niche override rules
- **Nightlife**: prefer plan/claim/alert; avoid “best ____?” when item is missing.
- **Wellness**: prefer reset framing; avoid “rate it 1–10” and “local gem:” style openers.
- **Dessert**: prefer alert/sign; ensure no duplicated “shop” language.

---

## 8) Noun Phrase Builder Rules (Critical for Grammar)

### 8.1 Canonical components
- **item**: “ice cream”, “matcha”, “brunch”, “sauna session”
- **place_type** (optional): “shop”, “cafe”, “spot”, “bar”, “speakeasy”
- **category_detail** (optional): “Italian”, “Korean BBQ”, “smash burger”, “late-night”
- **adjective** (optional): “hidden”, “new”, “underrated”

### 8.2 Composition rules
1. If `item` already includes place type (“ice cream shop”), do not append place_type.
2. If `category_detail` overlaps with `item`, keep the more specific phrase and do not concatenate both.
3. If `category_detail` is a modifier (“Italian”), apply it to the item (“Italian subs”).
4. If `category_detail` is a second concept, push it to a later texture line.
5. Collapse adjacent duplicates (“ice cream shop ice cream shop” → “ice cream shop”).
6. Cap hook noun phrase length; overflow goes to texture.

---

## 9) Handle and Region Placement Rules

### 9.1 Handle placement
- **Inline**: best when hook is short and handle is central.
- **Standalone handle line**: best when you want a clean hook or the handle is long.

### 9.2 Region lock placement
- **Inline region**: “in (r)” inside hook.
- **Separate region line**: “(r), FL 📍” line 2.

Rule: avoid repeating region twice unless intentional.

---

## 10) Tone Rules (Wording + Emoji Discipline)
Tone affects starters, punctuation, emoji allowance, and CTA aggressiveness:
- **highlight**: clean, confident, minimal emoji
- **curious**: question-led
- **hot_take**: debate phrasing
- **utility**: practical framing (save/list)
- **vibe_check**: vibe/date-night language
- **viral**: short caps, chaos

---

## 11) Micro-CTA and Follow Logic (Behavior Rules)

### 11.1 Micro-CTA defaults
- **food**: rate 1–10 (unless wellness/spotlight rules apply)
- **things**: save / weekend
- **event**: tag +1 / save
- **spotlight**: tag friend / save / show love
- **viral**: caption this / what would you do

### 11.2 Certified “anti-slop” mode
For Certified profiles in highlight tone:
- prefer softer micro-CTAs: “Let us know👇”, “Would you try this?”, “What are you ordering?”
- follow line remains the primary CTA

---

## 12) Quality Gate Rules (Post-Assembly Validation)
After assembling a hook:
- Must pass: no duplicates, no “the the”, no repeated handle, acceptable length, meets mention requirements.
- Soft checks: avoid banned weak openers; avoid rating prompts for wellness/community spotlight.
- Safe fallbacks: “(r) — put (b) on your list.” / “this is your sign to try (b) in (r).” / “save this for the weekend ✅ (b)”

---

## 13) Operator Guidance
- Keep (sub) as the core item, not the place: “ice cream” > “ice cream shop”.
- Use category_detail for modifiers: “Italian”, “matcha”, “smash burger”.
- Use key details for texture lines, not hook stuffing.
- Use content_type by intent: wellness → things/spotlight; markets/festivals → event; chaos → viral.

---

## 14) Implementation Summary (Behavioral Requirements)
1. Store hooks as families (patterns) + curated banks, not only full strings.
2. Normalize inputs into canonical slots.
3. Select hook families based on content_type + tone + niche.
4. Assemble hook with strict slot rules.
5. Apply quality gate with rerolls and fallbacks.
6. Keep network caption order stable.

---

## 15) Quick Examples
### Ice cream (no duplication)
- (b)=@someicecream, (r)=Orlando, (sub)=ice cream, category_detail=soft serve
- Hook options: “sweet tooth alert 🍦 @someicecream in Orlando” / “does @someicecream have the best ice cream in Orlando?”

### Wellness cafe + sauna
- (b)=@balance_house, (r)=St. Pete, content_type=spotlight, niche=wellness
- Hook options: “St. Pete wellness check: @balance_house.” / “if you need a reset in St. Pete, start at @balance_house”

---

## 16) Recommended Next Expansion (Library Roadmap)
Add niche starter sets in batches:
- sandwiches, pizza, sushi, ramen, Korean BBQ, Chinese, Thai, Vietnamese
- brunch/breakfast, coffee, desserts
- rooftop, speakeasy, late-night
- beaches, parks, trails, springs
- markets, festivals, art walks
- small business/community member spotlight
- major holidays + seasonal weekends

A slot system ensures additions scale cleanly without grammar regressions.
