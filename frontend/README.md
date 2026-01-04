# Frontend (Vite + React + Tailwind)

This frontend uses React + TypeScript with Tailwind for styling and a light Google-brand theme overlay.

## UI Theme and Design Tokens

Theme tokens are defined in `frontend/tailwind.config.js` and applied across components.

- Colors (prefix `google-*`):
  - `bg-google-blue`, `text-google-blue`
  - `bg-google-green`, `bg-google-yellow`, `text-google-red`
  - Neutral: `bg-slate-25` base background, standard Slate text/borders
- Shadows:
  - `shadow-card` for elevated cards

Components using tokens:

- `Button` variants (`src/components/ui/Button.tsx`)
  - `primary`: blue filled (uses `bg-google-blue`)
  - `secondary`: dark slate filled
  - `outline`: white with slate border
  - `danger`: red outline (uses `text-google-red`)
  - All variants use focus ring `focus-visible:ring-google-blue/30`

- `Card` (`src/components/ui/Card.tsx`): rounded with `shadow-card`

- `NavBar` active state: `text-google-blue`

Form controls (inputs/selects/textareas) adopt branded focus styles:

```html
class="border border-slate-300 rounded p-2 focus:outline-none focus:ring-1 focus:ring-google-blue focus:border-google-blue bg-white"
```

### StatusMeter component

Reusable segmented progress meter used on the Runs dashboard.

File: `src/components/ui/StatusMeter.tsx`

Usage:

```tsx
<StatusMeter
  segments={[
    { label: 'Queued', value: 10, color: 'yellow' },
    { label: 'Running', value: 60, color: 'blue' },
    { label: 'Done', value: 30, color: 'green' },
  ]}
  showLegend
/>
```

Colors map to the theme’s google palette: `blue | green | yellow | red`.

### Run Control menus

The Runs dashboard exposes selectable Pause/Abort menus via a small inline Menu primitive. For testing or wiring external handlers, `RunDashboardPage` accepts optional callbacks:

```tsx
<RunDashboardPage
  onRunAction={(action) => {/* 'pause' | 'resume' */}}
  onAbortAction={(action) => {/* 'abort' | 'abort_delete' */}}
/>
```

## Dev notes

- After editing `tailwind.config.js`, restart the dev server so Tailwind rebuilds classes.
- If a custom class doesn’t appear, ensure the class name is present as a literal string in the source so Tailwind includes it.

## Scripts

- `npm run dev` — start dev server
- `npm test` — run unit tests (Vitest + Testing Library)

## Linting (optional)

You can extend ESLint configs per your needs. See React/TypeScript ESLint guidance for type-aware rules if desired.
