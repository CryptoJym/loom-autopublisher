# Product Requirements Document – Loom→Everywhere Local Auto‑Publisher

**Version:** v1.0  |  **Owner:** Argonot  |  **First builder:** o3 agent running in Windsurf

---

## 1. Purpose

Automate the journey from a single Loom recording → multi‑channel content blast **with zero clicks after you paste the Loom URL**.  Output assets:

1. **Walk‑through web page** pushed to your existing static‑site repo (Netlify auto‑deploy).
   *Format:* raw **HTML (or MDX)** with front‑matter; no Markdown lesson outline.  AI must read existing site codebase (components, CSS) and produce branded HTML that matches.
2. **Full tutorial video** uploaded to YouTube with AI‑generated title, description & custom thumbnail.
3. **15‑second HeyGen avatar intro** uploaded to YouTube *Shorts* **and** queued via Buffer to TikTok, Instagram Reels, X, LinkedIn.
4. **Teaser social post** (caption + link to the new walkthrough page) blasted via Buffer to the same social profiles.
5. **(Optional) Email** notification via SendGrid using the same walkthrough URL + thumbnail.

User control: only URLs pasted into the desktop UI are published.  No hidden folder polling.

---

## 2. Success Criteria (MVP)

| KPI                                    | Target                         |
| -------------------------------------- | ------------------------------ |
| Paste‑to‑publish latency               | < 6 min for a 5‑min Loom video |
| Manual effort after paste              | 0 clicks                       |
| Failure rate per asset type            | < 2 %                          |
| Build start‑to‑green tests in Windsurf | ≤ 2 hrs agent time             |

---

## 3. Functional Requirements

### 3.1 Desktop UI

* Streamlit one‑page app (`app.py`).
* Input: single Loom **share URL** text field + “Publish” button.
* Output: live log pane → final links (Walkthrough, YouTube, Short).

### 3.2 Assets Extraction

* From the share URL, derive `VIDEO_ID`.
* Fetch assets via hard URLs:

  * `https://cdn.loom.com/sessions/transcoded/{ID}/720.mp4`
  * `https://cdn.loom.com/sessions/transcripts/{ID}.json` (plain JSON captions)
  * `https://cdn.loom.com/sessions/thumbnails/{ID}-with-play.jpg`

### 3.3 AI Content Generation

* Single GPT‑4o call returns JSON structure:

  ```jsonc
  {
    "title": "<60c",
    "description": "<150w",
    "teaser": "<110c",
    "slug": "kebab-case",
    "walkthrough_html": "<raw HTML ready for site layout>"
  }
  ```
* Prompt must reference **brand palette + typography** by reading `/styles/variables.css` in the repo.

### 3.4 Publishing Steps

1. **YouTube**: upload MP4, set custom thumbnail. Return `yt_url`.
2. **HeyGen**: POST 35‑word script → poll → download 15 s MP4.

   * Upload this MP4 as a YouTube Short (`shorts=true`). Return `short_url`.
3. **Site push**:

   * Write `content/walkthroughs/{slug}.html` with front‑matter `{ title, date, yt: yt_url }`.
   * `git add`, `commit -m "feat(walk): {slug}"`, `push`.
4. **Buffer blast**: one call with `text = teaser + ' ▶ ' + netlify_url` plus `remote_video_url = short_url`.
5. **Email (optional)**: send to `RECIPIENTS` if `SENDGRID_KEY` present.

### 3.5 Error Handling

* Any failed external call logs to Streamlit pane and retries once after 2 min.
* If a step fails after retry, mark run as ❌ and stop subsequent steps.

---

## 4. Non‑Functional Requirements

* Written in **Python 3.11**; run in Windsurf Dev Container.
* One dependency file (`requirements.txt`).
* Secrets pulled from `.env` (template provided).
* All long‑running I/O done with **asyncio + httpx**.
* Unit tests covering:

  * Transcript fetch parses >90 % of words.
  * GPT JSON conforms to schema.
  * Dummy upload mocks succeed.

---

## 5. Delivery Milestones (for o3)

| Day | Deliverable                                                         |
| --- | ------------------------------------------------------------------- |
| ‑0  | Repo scaffold + `.env.example`                                      |
| 1   | `loom.py`, tests pass with sample URL                               |
| 2   | `generator.py`, unit test snapshot approved                         |
| 3   | `youtube.py` + thumbnail set (mock creds)                           |
| 4   | `site.py` commits local repo & pushes to origin in Windsurf sandbox |
| 5   | `heygen.py` & `buffer.py` integrated                                |
| 6   | Streamlit UI live; end‑to‑end dry‑run with test keys                |
| 7   | README + Dockerfile, handoff to human                               |

---

## 6. Open Questions (Resolved)

1. Walkthrough HTML embeds the full YouTube iframe.
2. HeyGen quota exceeded: abort the pipeline (no fallback).
3. Thumbnails will be committed into the repo.

---

*End of PRD.*