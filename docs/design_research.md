# Design research — actionable findings (Streamlit data-app polish)

Cited synthesis from the deep-research pass. Sorted by *safe-to-ship-today* vs *post-deadline*.

## ✅ Already in the app (validated by the research)
- **vis-network for the interactive causal DAG** — node-link graph as a JS component embedded via `st.components.v1.html`. (We ship this in Track ②.)
- **Native `config.toml [theme]`** — `primaryColor` (accent for hover/focus/selected), `backgroundColor`, `secondaryBackgroundColor`, `textColor`, `base`. (Shipped.) Source: docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders
- **Scoped CSS via `data-testid` selectors + `st.markdown(unsafe_allow_html=True)`** for what the theme can't reach. (Shipped — instrument type system, hero, meters.)
- **Honest uncertainty encoding** — our confidence meter + grade chip follows the "show caution under uncertainty" principle (VSUP / value-suppressing palette intent).

## ⚠️ High value but deferred (dependency/version risk on deadline day)
- **Newer theme keys** `baseRadius`, `showWidgetBorder`, `borderColor`, `[theme.sidebar]` — clean rounding/borders with no CSS, BUT an older deployed Streamlit can refuse to start on an unknown `[theme]` key. We already round/border via CSS, so skip until after submission.
- **`st.plotly_chart(..., on_select="rerun", selection_mode="points")`** — turns charts into cross-filter inputs (click a capability bar → filter the table/map). Real wow, but adds rerun complexity; add carefully post-deadline. (Streamlit ≥1.35.)
- **`@st.fragment`** — isolate the Copilot/Genie reruns so the page doesn't fully rerun (snappier). (Streamlit ≥1.37.)
- **Component libraries** — `streamlit-shadcn-ui` (30+ Tailwind/Radix components), `streamlit-extras` (metric cards, badges, grids). Premium look fast, but new deps in `requirements.txt` = deploy risk today.

## Visualizing uncertainty without misleading (the trust core)
- **VSUPs** (Value-Suppressing Uncertainty Palettes): collapse high-uncertainty values toward a single root color → empirically pushes viewers to caution.
- **HOPs** (Hypothetical Outcome Plots): animate random draws so users *count frequencies* instead of reading an opaque band.
- **`go.Indicator` gauges** with colored confidence-band steps for single-number trust scores.
- **IBM Carbon color rules**: categorical palette applied in strict order; sequential = lightness ramp; avoid gradients for meaningful progression.

## Principles (Tufte / analytics-product UX)
- Maximize data-ink; kill chrome that doesn't encode information.
- Microcopy for trust: name controls by what the user does; never present weak evidence as fact; empty/error states give direction.

> The strongest, most authoritative evidence was for native theming, Plotly selection events, and the uncertainty-viz research. Weakest/unverified: pydeck `on_select` and `streamlit-agraph` selection — we avoid relying on those.
