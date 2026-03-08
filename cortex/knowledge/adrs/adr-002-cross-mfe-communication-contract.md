# ADR-002 — Cross-MFE Communication Contract

**Date:** 2026-03-08
**Status:** Accepted
**Depends on:** ADR-001

---

## Context

With Angular shell and React MFEs running as separate JavaScript runtimes on the same page, there is no shared module scope for direct imports. MFEs need to:
- Receive auth tokens to make authenticated API calls
- Respond to shell-level events (user logged out, theme changed, navigation triggered)
- Optionally communicate with each other (e.g. a notification MFE broadcasting an unread count)
- Apply consistent theming without shipping duplicate CSS

Without an explicit contract, teams will invent ad-hoc solutions (direct `window` property mutations, undocumented `localStorage` keys, DOM events with no schema) that become invisible coupling.

---

## Decision

### Auth Token Delivery

<!-- TODO: confirm with team — choose one and delete the others -->

**Option A — Shell injects via Module Federation props:**
The shell passes the current access token as a prop when mounting the MFE remote component. The MFE uses this token for the lifetime of that render. On token refresh, the shell re-renders the remote with the new token.

**Option B — Shared localStorage key:**
The shell writes the current access token to `localStorage` under the key `__cortex_auth_token`. React MFEs read this key before making API calls. The shell is responsible for keeping this key current on refresh. MFEs never write to this key.

**Option C — Custom event on token refresh:**
The shell dispatches `window.dispatchEvent(new CustomEvent('auth:token-refreshed', { detail: { token } }))` on every refresh. MFEs listen and update their internal token state.

> **Current implementation:** <!-- TODO: fill in which option is live -->

### Shell → MFE Broadcasts

The shell dispatches typed custom events on `window` for platform-level state changes:

```typescript
// Shell dispatches
window.dispatchEvent(new CustomEvent('platform:theme-changed', { detail: { theme: 'dark' } }));
window.dispatchEvent(new CustomEvent('platform:user-logout', {}));
window.dispatchEvent(new CustomEvent('platform:navigate', { detail: { path: '/dashboard' } }));
```

MFEs listen with `window.addEventListener` and clean up on unmount. MFEs never dispatch `platform:*` events — only the shell does.

**Agreed event schema** (extend this list via PR):

| Event name | Payload | Who dispatches |
|-----------|---------|---------------|
| `platform:theme-changed` | `{ theme: 'light' \| 'dark' }` | Shell only |
| `platform:user-logout` | `{}` | Shell only |
| `platform:navigate` | `{ path: string }` | Shell only |

### MFE → Shell Communication

MFEs dispatch typed `mfe:*` events for actions that require shell involvement:

```typescript
// MFE dispatches
window.dispatchEvent(new CustomEvent('mfe:navigate-requested', { detail: { path: '/settings' } }));
window.dispatchEvent(new CustomEvent('mfe:notification', { detail: { message: string, type: 'success' | 'error' } }));
```

The shell listens for `mfe:*` events and acts on them. MFEs never call `window.history.pushState` directly — all navigation goes through `mfe:navigate-requested`.

**Agreed MFE event schema:**

| Event name | Payload | Who dispatches |
|-----------|---------|---------------|
| `mfe:navigate-requested` | `{ path: string }` | Any MFE |
| `mfe:notification` | `{ message: string, type: 'success' \| 'error' \| 'info' }` | Any MFE |

### MFE → MFE Communication

Direct MFE-to-MFE communication is **not permitted**. If two MFEs need to share state:
1. The state lives in the shell (shell owns it, passes it down via props or events)
2. Or the state is persisted in a documented `localStorage` key with a schema owned by the platform team

MFEs do not import from each other's remote entry points.

### Persistent Shared State (localStorage)

All `localStorage` keys shared between shell and MFEs use the prefix `__cx_`. The schema for each key is documented here:

| Key | Owner | Schema | Consumers |
|-----|-------|--------|----------|
| `__cx_auth_token` | Shell | `string` (JWT) | All MFEs |
| `__cx_theme` | Shell | `'light' \| 'dark'` | All MFEs |
| `__cx_user_prefs` | Shell | `{ locale: string, timezone: string }` | <!-- TODO: list MFEs --> |

MFEs read these keys but **never write them** unless explicitly documented here as owner.

### Style Isolation

<!-- TODO: confirm with team -->

Each MFE is responsible for scoping its own styles. Options (choose one):

- **CSS Modules** — React MFEs use CSS Modules; class names are locally scoped by build tooling. No global class leakage.
- **Tailwind + DaisyUI with a scoped prefix** — MFEs apply a wrapper class (`[data-mfe="feature-name"]`) and scope all Tailwind utilities under it.
- **Shadow DOM** — MFE root is a Web Component with a shadow root. Full style isolation, but complicates DaisyUI theming.

The shell guarantees:
- `data-theme` attribute is set on `<html>` and reflects the current DaisyUI theme
- Tailwind config and DaisyUI plugin version are aligned across shell and MFEs (platform team owns this)
- MFEs inherit DaisyUI semantic tokens (`primary`, `base-100`, etc.) automatically if they share the same Tailwind config

---

## What Is Explicitly Not Allowed

- Direct DOM queries across MFE boundaries (`document.querySelector` targeting another MFE's elements)
- Importing Angular services, Angular DI tokens, or Angular modules into React MFEs
- Importing React components from a React MFE directly into Angular (use Module Federation remote entry only)
- Writing to `localStorage` keys prefixed `__cx_` from an MFE unless that MFE is the documented owner
- Dispatching `platform:*` events from an MFE (shell-only namespace)
- Using `window.__angularPlatform__` or similar internal Angular globals from an MFE
- Shared mutable global state via `window.myGlobalState = ...`

---

## Consequences

**What becomes easier:**
- Any team can reason about what crosses the MFE boundary by reading this ADR
- New MFEs know exactly what to listen for and what to dispatch without asking the shell team
- Style bugs are isolated — one MFE's CSS cannot bleed into another's

**What becomes harder:**
- Event schemas must be kept in sync with this document — stale schemas cause silent failures
- Debugging cross-MFE issues requires inspecting `window` event listeners in both runtimes
- Token refresh race conditions need explicit handling in each MFE's auth header logic

**Review trigger:** Any new cross-MFE data need that doesn't fit the existing event schema requires a PR updating this ADR before implementation.
