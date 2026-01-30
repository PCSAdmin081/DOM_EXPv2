# Captorator Dev Log

## v1.2.2 — 2026-01-XX (Startup Performance Fix)

### Performance Optimization

**Startup Time Improvement**
- Moved large `UI_HTML` string (~1,100 lines) from `captorator/api.py` to external file `captorator/ui.html`
- Implemented lazy loading with caching via `_get_ui_html()` function
- Reduced `api.py` from ~1,272 lines to 218 lines (~82% reduction)
- HTML is now loaded on first request and cached for subsequent requests
- **Impact**: Significantly faster module import time since Python no longer needs to parse the large HTML string literal at startup

**Files Changed:**
- `captorator/api.py`: Removed inline HTML string, added lazy-loading function
- `captorator/ui.html` (NEW): Extracted HTML content (1,054 lines)

## v2.0.0 — 2026-01-XX (Decision-Constrained Content Engine)

### Major Architectural Change: Decision-Constrained Content Engine

Implemented foundational constraint systems that transform Captorator from a simple caption generator into a decision-constrained content engine. This enables delegation, preserves brand integrity, and scales across industries.

### PHASE 1 — CORE CONTROL AND SAFETY (REQUIRED)

**1. Decision Lock Layer** (`captorator/constraints.py`)
- Implemented input categorization: Fixed (cannot override), Semi-fixed (requires override flag), Dynamic (freely selectable)
- Fixed inputs: experience_depth, primary_value_driver, risk_sensitivity, operator_type
- Semi-fixed inputs: allowed_urgency_modes, allowed_offer_focus, maximum_cta_strength
- Dynamic inputs: channel, photo_context, buyer_intent
- Enforcement: Fixed values cannot be overridden; semi-fixed require explicit override flags
- Purpose: Prevent tone drift, make outputs predictable across operators

**2. Prohibited Constructs Engine** (`captorator/constraints.py`)
- Rule system blocks disallowed language and structures
- Defines: Forbidden words, sentence types, claim categories, emotional triggers
- Enforcement: Filters vocabulary pools before generation; scans final output and fails if violations detected
- Purpose: Protect brand integrity, prevent compliance and trust violations

**3. Copy Lane Isolation** (`captorator/constraints.py`)
- Enforces single copy lane selection: brand_positioning, trust_reinforcement, feature_focus, event_or_moment, conversion
- Enforcement: Zero or multiple lanes cause generation failure; each lane maps to its own templates
- Purpose: Eliminate muddled or unfocused copy

### PHASE 2 — INTELLIGENCE AND CONSISTENCY

**4. Experience Depth Engine** (`captorator/constraints.py`)
- Global experience depth axis: Experiential, Guided, Productized, Transactional
- Controls: Allowed detail level, claim strength, urgency tolerance, CTA strength
- Enforcement: All vocabulary, templates, urgency logic, and CTAs filtered through depth rules
- Purpose: Prevent mismatched tone across business types

**5. Urgency Governor** (`captorator/constraints.py`)
- Urgency modes: None, Environmental, Time-bound, Capacity-based, Incentive-driven
- Enforcement: Incentive-driven forbidden for experiential/guided; time-bound forbidden in high-risk categories
- Purpose: Prevent urgency misuse and brand erosion

**6. Offer Focus Controller** (`captorator/constraints.py`)
- Offer focus types: Brand only, Core offering, Limited feature, Event/moment, Promotional incentive
- Enforcement: Promotional incentives only for productized/transactional; must align with urgency rules
- Purpose: Prevent promotions from degrading premium or trust-based brands

### PHASE 3 — QUALITY, SCALE, AND DELEGATION

**7. Confidence Gradient** (`captorator/constraints.py`)
- Confidence levels: Implicit, Assured, Declarative
- Controls: Verb certainty, sentence closure, claim framing
- Purpose: Allow authority without arrogance, reassurance without weakness

**8. Variation Budget** (`captorator/constraints.py`)
- Variation dimensions: Lexical, Structural, Conceptual
- Enforcement: Only one dimension may vary meaningfully per output; tracks recent usage
- Purpose: Prevent staleness without introducing drift

**9. Preflight Failure Detection** (`captorator/constraints.py`)
- Checks for: Multiple CTAs, conflicting urgency/depth, claim strength exceeding risk tolerance, multiple copy lanes
- Enforcement: Any violation causes hard failure; requires manual override to proceed
- Purpose: Catch bad copy before publication

**10. Soft Memory (Non-Learning)** (`captorator/constraints.py`)
- Tracks usage frequency: Copy lanes, urgency modes, offer focus types
- Enforcement: Warns when patterns are overused; never auto-optimizes or changes behavior
- Purpose: Maintain strategic balance over time

### Implementation Status

- ✅ All 10 constraint systems implemented as foundational modules in `captorator/constraints.py`
- ⚠️ **Note**: This is a foundational implementation. Integration with the existing caption generation pipeline (`captorator/core.py`) is pending.
- ⚠️ **Note**: These systems are designed for a decision-constrained content engine architecture. Full integration will require:
  - Mapping existing caption inputs to new constraint system parameters
  - Integrating validation checks into the generation pipeline
  - Creating configuration files/profiles for constraint settings
  - Updating API/CLI interfaces to support new parameters
  - Implementing template pools for copy lanes
  - Adding UI controls for constraint system parameters

### Files Changed
- `captorator/constraints.py` (NEW): Complete constraint system implementation with all 10 phases

## v1.2.1 — 2026-01-11

### What changed
- Implemented the **network-standard repost caption format** (the 90% default):
  - Hook (line 1)
  - Region lock: `City, FL 📍` (line 2) with optional neighborhood / event info
  - Follow line (line 3) using **your page handle** (not just a hashtag)
  - Micro-CTA (line 4): Rate / Save / Tag / Caption this
  - Creator credit (line 5): `🎥: @creator (via TikTok/IG)`
  - Tight hashtag set (line 6) — defaults to ~10 max
- Added `caption_format` switch:
  - `network` (new default)
  - `legacy` (keeps the prior Certified/OMG separator-based blocks)
- Added `content_type` to drive better defaults for hooks + CTAs:
  - `food | things | event | spotlight | viral | generic`
- Added `micro_cta` override (or leave blank for auto) and a `disclosure` field that is forced to the **top line** when provided.
- Added optional context fields used in network formatting:
  - `neighborhood`, `event_name`, `event_time`, `region_state`
- Updated follow-line logic in network format:
  - Certified profiles now render like **“Follow @yourpage for more #Region”**
  - OMG/viral defaults to **“Follow @omg.florida for daily Florida chaos”**
- Expanded credit platform options to include `ig` (Instagram).

### UI + API
- UI adds dropdowns/fields for: `caption_format`, `content_type`, `micro_cta`, `disclosure`, plus optional neighborhood/event inputs.
- UI state persistence upgraded (more fields saved) and includes the **Creator = business** checkbox.
- `/meta` now returns `caption_formats`, `content_types`, and `micro_ctas` for UI dropdown population.

## v1.2.0 — 2026-01-11

### What changed
- Added additional **account profiles** so the UI/Profile dropdown supports the full network scope:
  - `stpetecertified`
  - `jaxvillecertified`
  - `gvillecertified`
  - `tallycertified`
  - `swflcertified`
- Added per-profile `brand_handle` so the UI can auto-fill the correct brand handle and avoid cross-profile leakage (e.g., Orlando handle showing while SWFL profile is selected).
- Set `swflcertified` default behavior to **include texture line** (`include_texture_line_default=True`) to better fit nightlife/cocktail/lounge content.

### UI + API
- Added a local **web UI** served from `GET /` (FastAPI) so caption generation does not require terminal typing.
- Added `GET /meta` to supply UI dropdown options and now includes `profile_map` (profile defaults + metadata) for client-side autofill.
- UI enhancements:
  - Profile change now auto-fills `brand_handle` and creator credit defaults (credit prefix/platform) from `profile_map`.
  - Added `Creator = business` checkbox to mirror the business handle into the creator field and reduce repetitive typing.
  - Added local persistence via `localStorage` so inputs persist across page refresh.
  - Fixed initial UI HTML escaping issues that prevented dropdown population (removed backslash-escaped quotes; corrected textarea placeholder newlines).
- Added server-side handle normalization in `POST /generate` so handles are automatically prefixed with `@` if omitted.

### Caption generation (core)
- Improved `highlight` tone hook wording to avoid clunky templates (replaced the “Need a ___ spot?” phrasing).
- Added **nightlife-aware** caption logic for categories/details containing: `cocktail(s)`, `bar(s)`, `speakeasy`, `lounge`, `nightlife`:
  - Uses dedicated nightlife hook templates (unless `tone=viral`).
  - Uses dedicated nightlife texture templates and avoids label-style lines like `Notable:`.
  - Uses a more natural details combo format (`" / "` join) and randomly selects from key details to reduce repetition.
- Reduced separator clutter by converting double dash separators to single dash separators for cleaner caption blocks.

### Hashtag coverage
- Expanded city hashtag packs to improve regional tagging:
  - Added/expanded: `gainesville`, `naples`, `fortmyers`, `sarasota`.
- Expanded nightlife category hashtags (e.g., `bars` now includes cocktail/speakeasy/lounges related tags).

### Notes
- After updating code, restart the API (`Ctrl+C` then `python3 run_api.py`) and hard refresh the UI (`Cmd+Shift+R`) to ensure the latest UI + meta changes load.

## v1.1.0 — 2026-01-11

### What changed
- Added **account profiles** to match your existing caption formatting (follow line placement, creator credit style, OMG feature tag line):
  - `orlandocertified`
  - `soflocertified`
  - `omg.florida`
- Added tone packs:
  - `highlight` (recommendation-style; closer to your Certified posts)
  - `viral` (punchier, OMG-style)
- Added switches to turn off “extra” lines when you want a single-line main caption:
  - `include_texture_line`
  - `include_prompt_line`
- Added creator credit controls:
  - `credit_prefix=camera` renders `🎥: @creator on tt`

### Current spec summary
- Required: `handle`, `city`, `category`, `creator`
- Optional profile: `profile` (applies follow/credit/hashtag defaults)
- Tone: `curious | hot_take | utility | vibe_check | bracket | highlight | viral`
- Formatting options: `include_follow_line`, `include_texture_line`, `include_prompt_line` (set to `null` to use profile defaults)
- Added optional `standalone_handle_line` to match posts where the featured handle is on its own line.
- Credit options: `credit_platform`, `credit_prefix`

---

## v1.0.0 — 2026-01-11

### What this version does
- Generates a full Instagram caption *block* from structured inputs:
  - Hook (tone-pack based)
  - Texture line (1 detail line)
  - Optional community prompt (omitted ~35% to reduce CTA fatigue)
  - Optional soft follow line (only if `brand_handle` + `include_follow_line`)
  - Credit line: `credit: @creator`
  - Hashtag line pack (city + category + brand + extras), deduped, capped

### Inputs (current spec)
- Required: `handle`, `city`, `category`, `creator`
- Recommended: `details` (1–3 short bullets)
- Tone: `curious | hot_take | utility | vibe_check | bracket`
- Optional: `brand_handle`, `include_follow_line`, `emoji_level`, `seed`, hashtag overrides

### Interfaces
- CLI:
  - `python3 run_cli.py --handle ... --city ... --category ... --creator ... --details ...`
- FastAPI:
  - `GET /health`
  - `POST /generate` (JSON → caption string)

### Guardrails (anti-slop)
- One hook + one texture line.
- At most one community prompt.
- No “fact invention”: output uses only user-provided detail strings plus templates.
- Hashtags are capped and deduped.

### Known limitations / next candidates
- No per-account “style profiles” yet (e.g., omg.florida vs Certified city accounts).
- No persistence layer (no saved presets, no history).
- Hashtag packs are basic and require manual expansion.
- No UI (API/CLI only).

---
Append new entries above this line for each version.
