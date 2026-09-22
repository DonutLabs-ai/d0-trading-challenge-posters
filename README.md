# D0 Trading Challenge · posters

The five trading-challenge key visuals from
[Branding-white-Version](https://www.figma.com/design/NvQSCDtYClyN1TLhZ2UK6l/Branding-white-Version),
rebuilt as exact-size HTML. Every poster is a fixed pixel canvas, so what you see in the browser is
what comes out of the exporter — no responsive layout, no surprises.

Open `index.html` for the contact sheet.

| Poster | Size | Figma node |
| --- | --- | --- |
| [`posters/01-roadmap.html`](posters/01-roadmap.html) | 696 × 1237 | [445-377](https://www.figma.com/design/NvQSCDtYClyN1TLhZ2UK6l/Branding-white-Version?node-id=445-377) |
| [`posters/02-levels.html`](posters/02-levels.html) | 1200 × 675 | [445-394](https://www.figma.com/design/NvQSCDtYClyN1TLhZ2UK6l/Branding-white-Version?node-id=445-394) |
| [`posters/03-signup.html`](posters/03-signup.html) | 675 × 1200 | [445-438](https://www.figma.com/design/NvQSCDtYClyN1TLhZ2UK6l/Branding-white-Version?node-id=445-438) |
| [`posters/04-poster.html`](posters/04-poster.html) | 1024 × 1401 | [445-451](https://www.figma.com/design/NvQSCDtYClyN1TLhZ2UK6l/Branding-white-Version?node-id=445-451) |
| [`posters/05-rules.html`](posters/05-rules.html) | 1200 × 675 | [445-460](https://www.figma.com/design/NvQSCDtYClyN1TLhZ2UK6l/Branding-white-Version?node-id=445-460) |

Sizes are the Figma frames as drawn. `02` and `05` are already Twitter's 16:9 in-timeline size; `03` is
the 9:16 portrait; `01` and `04` are taller than Twitter crops to, so they post best as a single image
that opens full-size on tap.

## Exporting

```bash
npm install          # pulls Playwright
npx playwright install chromium
npm run export       # → export/01-roadmap.png … at the native size
npm run export:2x    # → export/01-roadmap@2x.png … retina masters
```

Export one poster: `npm run export -- --only 05`.

Chromium screenshots the `.poster` element, so the PNG is exactly the frame — nothing around it.

## Editing

Copy, dates and numbers are live text. Open a poster's HTML and edit it:

```html
<p class="t serif vc" style="left:471px; top:164px; width:258px; height:30px; ...">Starts Sep 20 9/20</p>
```

Every `left` / `top` / `width` is the number Figma shows for that layer, so a change in the design file
maps straight onto a number here. `class="vc"` means the Figma layer is set to
`textAlignVertical: CENTER`, and the element keeps the Figma box height so its lines centre in it.

Artwork lives in `assets/img/` — those are the Figma background layers exported at 2×, with their blurs
and noise baked in, so they cannot drift from the design. Everything drawn on top (type, the glass card
in `05`, the Donut lockup) is real HTML and SVG.

## Checking against Figma

`reference/` holds each frame as Figma renders it. Open [`tools/compare.html`](tools/compare.html) to see
the HTML, the Figma render and a `difference` blend of the two side by side — black means they agree.
(The blend needs a real browser; iframes come out empty in some embedded preview panes.)

Known gaps, all small:

- Type sits within about 1–4 px of the Figma render. Figma and CSS place the first line in a line box
  slightly differently, and the two disagree by a few px at 76–84 px display sizes.
- The glass card in `05` is CSS `backdrop-filter`, not Figma's Glass effect. Same read, slightly less
  refraction at the edges.
- `Instrument Serif` sets a little narrower here than in Figma — about 4 % on a long all-caps line.

## Fonts

Self-hosted in `assets/fonts/`, so an export is the same on any machine:
Instrument Serif 400, Geist 400 and 700. The Figma file also names Alan Sans on one layer, but every
character on it is overridden to Geist Bold, so nothing actually renders in Alan Sans.

## Refreshing from Figma

If a frame changes, re-pull its background plate and reference render:

```bash
export FIGMA_TOKEN=…            # a personal access token with file read
python3 tools/refresh.py 445:460
```

The script prints the layer tree with positions, fonts and colours next to what is in the HTML, so you
can see what moved.
