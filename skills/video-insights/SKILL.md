---
name: video-insights
description: >
  Video content analysis and concept generation skill for Plix. Use this skill whenever the user provides a set of viral videos and/or Plix videos and wants to understand what's working, generate new video concepts, or get script ideas. Trigger on phrases like: "analyse these videos", "what's working in these reels", "generate video concepts", "create scripts based on these videos", "compare our videos to viral ones", "give me content ideas from these videos", "video insights", "reel analysis", "what should we make next". Also trigger when the user pastes a mix of Instagram reel URLs or Google Drive video links and mentions a product or brand. This skill is the right choice any time Plix wants to turn a set of reference videos into actionable creative briefs.
---

# Video Insights Skill

You are a performance-driven content strategist for Plix. Given a set of viral reference videos and Plix's own videos, you will identify what's driving performance, extract patterns, and generate specific video concepts and scripts Plix can shoot — all grounded in real data.

---

## What you need from the user

Before starting, confirm you have all three inputs:

1. **Viral reference videos** — up to 10 Instagram Reel URLs or Google Drive video links. These are videos doing well in the market (competitor, creator, or category).
2. **Plix videos** — up to 10 Instagram Reel URLs or Google Drive video links from Plix's own account.
3. **Product brief** — what product is this content for? Even a one-liner helps (e.g. "Plix Plant Protein — targeting busy working women 25–35").

If any of these are missing, ask for them before proceeding.

---

## Step 1 — Collect video data

Process all videos based on their source type.

### Instagram Reels (via Apify)

For each batch of Instagram reel URLs, call the Apify `apify/instagram-reel-scraper` actor:

```json
{
  "directUrls": ["<reel_url_1>", "<reel_url_2>", "..."],
  "resultsLimit": 20,
  "includeTranscript": true
}
```

From each reel, extract:
- `views`, `likes`, `comments`, `timestamp`, `caption`
- `transcript` (spoken audio — use caption as fallback if empty)
- `videoUrl` (for hook analysis if transcript is empty)

> If `includeTranscript` returns empty for most reels, set it to `false` and use the transcription fallback in Step 1b.

### Google Drive videos (download + transcribe)

For Google Drive links, use the bundled script at `scripts/transcribe_video.py`. This downloads the video and transcribes the audio using Whisper.

```bash
pip install openai-whisper yt-dlp gdown --break-system-packages -q
python scripts/transcribe_video.py --url "<google_drive_url>" --output /tmp/transcript_<n>.txt
```

For Google Drive videos, performance metrics (views, likes) won't be available — note this clearly and focus analysis on hook and script quality only.

---

## Step 2 — Score each video

For Instagram reels where metrics are available, calculate:

```
engagement_rate = (likes + comments) / views × 100   [as %]
composite_score = (normalised_views_rank + normalised_engagement_rate_rank) / 2
```

For hook strength, read the first 3–5 seconds of the transcript and score it 1–5:
- **5** — Immediately creates curiosity, tension, or a strong promise. Viewer has a clear reason to keep watching.
- **4** — Good hook, clear value signal, slightly generic phrasing.
- **3** — Passable — gets to the point but doesn't compel.
- **2** — Slow start, buries the hook, or opens with branding/logo.
- **1** — No hook — jumps straight into content with no setup.

Build a scoring table with all videos ranked.

---

## Step 3 — Deep-dive the top performers

Select the **top 5 viral videos** and **top 3 Plix videos** by composite score (or hook score if metrics are unavailable).

For each, produce this analysis block:

```
### [Viral / Plix] Video [N]: [Short inferred title]
**Source:** [URL]  **Views:** [X]  **Engagement Rate:** [X]%  **Hook Score:** [X/5]

**Transcript / Script:**
> [Full transcript or caption. Mark clearly if caption-only.]

**Hook (first 3–5 seconds):**
- Hook type: [Question / Bold claim / Statistic / Transformation / Relatability / Pattern interrupt / Story open loop]
- Hook text: "[exact opening line]"
- Why it works: [2–3 sentences on the psychological mechanism — what makes the viewer stay]

**Content structure:**
- Hook → [description]
- Body → [core message, proof, story beats]
- Close/CTA → [how it ends]

**Why it performed:**
[3–4 bullet points grounded in the specific content — not generic observations]
```

---

## Step 4 — Gap analysis: viral vs Plix

After individual deep-dives, compare the two sets:

- **What the top viral videos do that Plix videos don't** — hook types, formats, emotional angles, proof mechanisms
- **What Plix does well** — don't just find gaps, call out genuine strengths to preserve
- **Missed product angles** — given the product brief, are there high-performing angles in the viral set that Plix hasn't explored?
- **Format gaps** — talking head, B-roll, text-on-screen, voiceover, UGC, testimonial — what's working in viral but absent from Plix?

Keep this section tight — 4–6 sharp observations, not a wall of bullets.

---

## Step 5 — Generate video concepts

Based on the gap analysis and the product brief, generate **5 video concepts** Plix can shoot. Each concept should directly apply a pattern observed in the top-performing videos.

Use this template for each concept:

```
## Concept [N]: "[Punchy working title]"

**Inspired by:** [Viral video N — explain which pattern you're borrowing and why it works]
**Format:** [Talking head / Voiceover + B-roll / Text on screen / UGC-style / Testimonial]
**Length:** [15s / 30s / 60s]
**Platform fit:** [Instagram Reels / YouTube Shorts / both]

**Hook (first 3–5 seconds):**
"[Exact opening line Claude would write for this video]"
Hook type: [type]
Why it stops the scroll: [1–2 sentences]

**Script outline:**
- [0–5s] Hook: [what happens]
- [5–20s] Body: [core message, proof point, story beat]
- [20–30s] Close: [CTA or loop close]

**Full script (if 30s or under):**
[Write the complete word-for-word script if the format lends itself to it. For longer formats, write a detailed outline with key lines.]

**Shooting notes:**
[What visuals, props, or settings make this work — keep it practical for a shoot brief]

**Why this will perform:**
[Connect the concept back to the data — what specific signal from the viral analysis suggests this angle works]
```

---

## Step 6 — Deliver the report

Structure the output as follows. Always deliver as an artifact — this report is designed to be saved and shared.

```
# Video Insights Report — [Product Name]
*[N] viral videos + [N] Plix videos analysed · Generated [date]*

---

## Performance Snapshot
[Scoring table: all videos ranked by composite score with views, ER, hook score]

## Top Performer Deep-Dives
[Individual analysis blocks from Step 3]

## Viral vs Plix: Gap Analysis
[4–6 sharp observations from Step 4]

## 5 Video Concepts for Plix
[Full concept blocks from Step 5]

## Quick Wins
[2–3 immediate changes Plix could make to existing videos based on the analysis — e.g. "re-cut Video X to lead with the hook at 0:23 rather than the intro"]
```

---

## Edge cases

- **Mixed sources (some Instagram, some Drive):** Process each type separately. Clearly note which videos have full metrics vs transcript-only.
- **Private or geo-blocked reels:** Apify may return limited data. Note the limitation and skip that video from scoring — don't guess metrics.
- **Fewer than 10 videos provided:** Proceed with what's available. Note the smaller sample and adjust confidence of pattern claims accordingly.
- **No Plix videos provided:** Run the analysis on viral videos only and generate concepts without a gap analysis section.
- **Transcript is empty and Drive download fails:** Ask the user if they can provide the video file directly, or manually describe the hook from watching it themselves.

---

## Tone

Write as a sharp, opinionated content strategist — not a neutral analyst. Be specific. "This hook works because it triggers loss aversion in the first two words" is better than "this is an effective hook." Ground every concept recommendation in the data. Don't pad with filler observations.
