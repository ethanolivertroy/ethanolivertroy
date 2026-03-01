# Profile README Redesign

**Date:** 2026-03-01
**Status:** Approved

## Goal

Refresh the `ethanolivertroy` GitHub profile README to better reflect actual interests (offensive AI, Kubernetes, infra/hardware) rather than leading with GRC. Add Spotify Now Playing card.

## Changes

### 1. Spotify Now Playing Card
- Deploy `novatorem/novatorem` to Vercel
- Place card below the social badges (YouTube, Website, Buy Me a Coffee), above the fold
- Requires: Spotify Developer app credentials + Vercel deployment

### 2. Replace "what I'm currently interested & focused on" with "currently hacking on"

New content:
```
- **offensive AI security** — red teaming LLMs, adversarial ML, AI workload attack surfaces
- **Kubernetes security** — hardening AI workloads in K8s, runtime security, supply chain
- **infrastructure & hardware** — going deeper on infra fundamentals and hardware security
- **GRC engineering** — compliance automation, FedRAMP tooling, OSCAL (the day job)
```

### 3. Reorder project sections

**New order:**
1. Intro + philosophy + social badges
2. Spotify Now Playing (new)
3. Currently hacking on (renamed + new content)
4. My content out there
5. Personal + technical blog posts
6. --- divider ---
7. AI ← moved up
8. Developer tools
9. Go terminal UIs
10. Intentionally vulnerable projects
11. Package distribution
12. --- divider ---
13. GRC engineering & compliance tools ← moved down
14. Trainings I've made
15. Contributions to other projects
16. Notable past projects
17. Other stuff
18. --- divider ---
19. Badges I got for clicking buttons

## Spotify Setup Steps (user action required)

1. Go to https://developer.spotify.com/dashboard and create a new app
2. Set Redirect URI to `https://novatorem.vercel.app/callback` (or your Vercel URL once deployed)
3. Note Client ID and Client Secret
4. Fork `novatorem/novatorem` on GitHub
5. Deploy fork to Vercel with env vars: `CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`
6. Get refresh token via the novatorem auth flow at `<vercel-url>/login`
7. Update README with `<vercel-url>/api/spotify`
