# Changelog

## 1.1.0 - Post‑Launch Enhancements and Fixes

- Added multi-parser RSS ingestion (RSS → Atom → JSONFeed) with graceful fallback.
- Added concurrency-limited parallel fetching to improve run speed.
- Implemented per-feed and per-strategy timeouts to prevent long hangs.
- Added tolerant parsing for malformed or partial feeds.
- Expanded and updated `feeds.json` with full statewide, regional, and vertical feed coverage.
- Added automatic inclusion of `omg.florida` to all feeds.
- Implemented `isOmgFloridaCandidate` for strict OMG/"Florida Man" filtering.
- Added noise-blocking heuristics to eliminate Reddit Q&A and non-news content.
- Added fallback selection logic ensuring every page always receives headlines.
- Added timestamped output filenames for all Markdown and JSON run reports.
- Expanded regional keyword sets for improved place detection.
- Fixed TypeScript errors (implicit any, missing properties, summary/description fallbacks).
- Improved error handling to safely skip malfunctioning feeds.
- Added summary/description/contentSnippet fallback extraction for scoring.
- General stability, correctness, and filtering improvements throughout the pipeline.

## 1.2.0 - Multi-tier fallback and robustness pass

- Added multi-tier candidate selection (primary/secondary/tertiary) so that every page can fall back to:
  - Fresh, unseen articles within the main recency window.
  - Recently seen-but-still-relevant articles from this run.
  - Older articles from the same run when a page is still under-filled.
- Introduced per-page configuration hooks (`maxRecencyHours`, `seenWindowDays`, `fallbackFrom`) to tune recency and repeat windows without changing code.
- Relaxed global hard filters by treating older or previously seen headlines as lower-scoring fallback tiers instead of dropping them entirely.
- Updated selection logic for `omg.florida` so strict "Florida Man/Woman" filtering is used when available, but gracefully falls back to other Florida stories instead of going empty.
- Wired `omg.florida` to all feeds at runtime in `loadConfig`, removing the need for manual config rewrite scripts.
- Normalized all feed and scraped links to absolute HTTP(S) URLs and filtered out non-article links (e.g. `mailto:`, `javascript:`, anchors) to reduce broken URLs.
- Tightened HTML scraping to only emit items with valid, normalized URLs.
- Added title cleanup in normalization to strip common site/brand suffixes (e.g. " - Site Name", " | Station Name") while preserving strong, descriptive headlines.
- Preserved existing scoring and Markdown/JSON output formats so existing consumers can upgrade without breaking changes.

## 1.2.1 - Stability and Operational Refinements

- Verified multi‑tier fallback logic across multiple runs with consistent page coverage.
- Resolved TypeScript type mismatch in `run.ts` by converting the per‑page candidate record into a `Map` for `writeOutputs`.
- Ensured `omg.florida` relaxed filtering logic remained backward‑compatible while preventing empty-page scenarios.
- Confirmed proper URL normalization and rejection of non-HTTP(S) links across all HTML‑scraped feeds.
- Verified title‑cleanup behavior for site-suffix removal without damaging meaningful headline context.
- Validated feed expansion logic and fallback recency windows operate consistently under real workloads.

## 1.2.2 - New Niches, Keyword Expansion, and Stability Fixes

- Added new vertical/niche categories (gaming, marketing, and additional topical sets) across ingestion, selection, and tagging layers.
- Expanded `keywords.json` with full keyword coverage for the new niches and updated normalization rules.
- Patched `selection.ts` multiple times to resolve primitive‑value scoring errors and ensure consistent tier handling for newly added categories.
- Patched `run.ts` and `cli/run.ts` to eliminate primitive‑value writeOutput crashes, correct candidate‑set construction, and ensure valid JSON/Markdown emission after niche expansion.
- Updated `tagging.ts` to prevent undefined primitive reads during tag assignment for the new verticals.
- Verified full integration after patches, including multi‑parser ingestion, scoring, and output stability with all newly added niches.

## 1.2.3 - Reporting Enhancements and Recency Note Restoration

- Added recursive note extraction to `cli/run.ts` to restore display of recency annotations and per‑article notes in run output.
- Implemented `collectNotes` helper to safely traverse nested report objects for `note` and `notes` fields.
- Added run‑report parsing block to print all collected notes without altering the existing output or run pipeline.
- Ensured full backward compatibility by avoiding modification of core run or scoring logic.
- Verified restored note visibility across multiple runs, including recency windows and fallback‑tier annotations.
