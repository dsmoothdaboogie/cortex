# Frontend Standard — React MFE

**Tag:** standards
**Scope:** All React Micro-Frontend remotes
**Level:** Principal UI Engineer
**Design System:** Tailwind CSS + DaisyUI (shared config from shell — see section 7)
**Architectural context:** ADR-001 (why React for MFEs), ADR-002 (cross-MFE communication contract)

---

## 1. Project Structure

### Folder Layout

```
src/
  components/       # Presentational components — no direct API calls, no store
  hooks/            # Custom hooks — data fetching, business logic, event listeners
  store/            # Local MFE state (Zustand slice or React Context)
  types/            # TypeScript interfaces and types scoped to this MFE
  utils/            # Pure functions — no side effects, no hooks
  __tests__/        # Co-located tests or a mirror of src/ structure
  bootstrap.tsx     # Module Federation async boundary (imports ./App)
  App.tsx           # Root component — receives shell props, sets up providers
  index.ts          # Module Federation remote entry — exposes App or named components
```

### Rules
- `bootstrap.tsx` exists solely to create the async boundary required by Module Federation shared singleton deps. It imports `./App` dynamically. Do not add logic here.
- `index.ts` only exposes what the shell contract requires — do not expose internal components.
- `components/` has zero business logic. If a component needs to fetch or dispatch, it belongs in `hooks/` + `components/` wired together.
- No barrel files (`index.ts`) inside subfolders — they create circular dependency issues with Module Federation.

---

## 2. Component Architecture

### Functional Components Only

No class components. Every component is a function.

```tsx
// ✓ Correct
export function UserCard({ user, onDelete }: UserCardProps) {
  return (
    <div className="card card-body">
      <span>{user.name}</span>
      <button className="btn btn-error btn-sm" onClick={() => onDelete(user.id)}>
        Delete
      </button>
    </div>
  );
}

// ✗ Wrong
class UserCard extends React.Component { ... }
```

### Prop Drilling Limit

- 1–2 levels: pass props directly.
- 3+ levels: introduce a Context or move state to the Zustand store.
- Never drill the same prop through more than 3 component levels.

### Composition Over Configuration

Prefer composing small focused components over a single component with many conditional branches.

```tsx
// ✓ Compose
<Card>
  <CardHeader title="Users" />
  <CardBody>{isLoading ? <Spinner /> : <UserList users={users} />}</CardBody>
</Card>

// ✗ One mega-component with flags
<UserSection showHeader loading={isLoading} variant="list" />
```

---

## 3. State Management

### Decision Tree

```
Server state (API data, caching, background refetch)?
  → React Query (TanStack Query)

Local UI state (toggle, modal open, form step)?
  → useState / useReducer in component

Shared within this MFE across multiple components?
  → Zustand slice scoped to this MFE

State that must cross the MFE boundary?
  → ADR-002 event contract — do NOT use React state or Zustand for this
```

### React Query Conventions

```tsx
// Query keys are typed arrays — colocate with the hook
const userKeys = {
  all: ['users'] as const,
  detail: (id: string) => ['users', id] as const,
};

export function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => fetchUser(id),
    staleTime: 5 * 60 * 1000, // 5 min — adjust per resource
  });
}
```

- Every data-fetching hook uses React Query. No raw `useEffect` + `useState` for fetching.
- Mutations use `useMutation` with `onSuccess` invalidating related queries.
- Error states are handled at the hook level — components receive typed `error` objects, not raw `unknown`.

### Zustand Conventions

```tsx
// store/user.store.ts
interface UserStore {
  selectedId: string | null;
  setSelected: (id: string | null) => void;
}

export const useUserStore = create<UserStore>((set) => ({
  selectedId: null,
  setSelected: (id) => set({ selectedId: id }),
}));
```

- One Zustand store file per concern — not one global store for the entire MFE.
- Store state is serialisable. No functions, class instances, or DOM refs in Zustand.
- Zustand is for this MFE only — never accessed from another MFE (see ADR-002).

---

## 4. Routing

React MFEs do not own top-level routing. The Angular shell owns the URL. Within a mounted MFE:

- If the MFE has internal sub-views, use React Router scoped to a base path provided by the shell.
- The MFE receives its `basePath` as a prop from the shell mount point.
- Never call `window.history.pushState` directly — dispatch `mfe:navigate-requested` per ADR-002.

```tsx
// App.tsx
export function App({ basePath = '/feature' }: AppProps) {
  return (
    <BrowserRouter basename={basePath}>
      <Routes>
        <Route path="/" element={<FeatureList />} />
        <Route path="/:id" element={<FeatureDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 5. Design System — Tailwind CSS + DaisyUI

The shell owns the Tailwind config. MFEs consume the same config to ensure token alignment.

<!-- TODO: confirm with platform team — shared config approach vs. separate install with aligned versions -->

### Component Usage Rules

Same table as `frontend-angular.md` — DaisyUI component names are identical in React:

| Need | Use |
|------|-----|
| Button | `<button className="btn btn-primary">` |
| Input | `<input className="input input-bordered" />` inside `<label className="form-control">` |
| Select | `<select className="select select-bordered">` |
| Modal | DaisyUI `modal` + `modal-box` — not a custom modal or `<dialog>` |
| Table | DaisyUI `table` with `table-zebra` |
| Alert | DaisyUI `alert alert-success / alert-error` |
| Badge | DaisyUI `badge` variants |
| Loading | DaisyUI `loading loading-spinner` |
| Card | DaisyUI `card card-body` |
| Dropdown | DaisyUI `dropdown` — not custom-built |

- Never build a custom component for anything DaisyUI provides.
- Use DaisyUI semantic tokens (`text-primary`, `bg-base-100`) — not raw Tailwind colours (`text-blue-500`).
- Dark mode is controlled by the shell via `data-theme` on `<html>`. MFEs do not toggle themes.
- Do not apply arbitrary Tailwind values (`w-[347px]`). Use the scale.

### Theme Inheritance

The shell sets `data-theme` on `<html>`. DaisyUI tokens cascade into MFE DOM nodes automatically as long as MFEs are not in Shadow DOM. MFEs do not need to listen for theme changes to rerender — CSS variables update automatically.

---

## 6. TypeScript Standards

- `strict: true` in `tsconfig.json`. No `any`, no `// @ts-ignore` without a comment.
- `unknown` over `any` for truly unknown types — narrow with type guards before use.
- Interfaces for object shapes; `type` for unions, intersections, mapped types.
- Event handler types are always explicit — never `(e: any) => void`.
- Props interfaces are named `{ComponentName}Props` and exported.
- Return types are explicit on all custom hooks and utility functions.

```tsx
interface UserCardProps {
  user: User;
  onDelete: (id: string) => void;
}

export function useUserSelection(): { selectedId: string | null; select: (id: string) => void } {
  // ...
}
```

---

## 7. HTTP and Data Access

- HTTP calls live in functions in `hooks/` — never inline in components.
- All HTTP is done via React Query (`useQuery`, `useMutation`). No raw `fetch` + `useState`.
- Auth token is retrieved per ADR-002 (from the agreed source — localStorage key or prop).
- Never hardcode base URLs — use an injection point (env var or prop from shell).

```tsx
// hooks/api.ts — centralise base URL and auth header attachment
const apiClient = {
  get: <T>(path: string): Promise<T> =>
    fetch(`${import.meta.env.VITE_API_BASE}${path}`, {
      headers: { Authorization: `Bearer ${getAuthToken()}` }, // ADR-002 token source
    }).then(res => {
      if (!res.ok) throw new ApiError(res.status, res.statusText);
      return res.json() as Promise<T>;
    }),
};
```

---

## 8. Testing

### Unit / Component Tests (React Testing Library)

- Every custom hook has a unit test using `renderHook`.
- Every component has at minimum a render test + one interaction test per user action.
- Use `screen.getByRole` and `screen.getByLabelText` — not `getByTestId` unless no semantic alternative exists.
- Mock HTTP with `msw` (Mock Service Worker) — not by mocking `fetch` directly.
- Do not test implementation details (internal state, hook internals). Test what the user sees.

### Coverage Targets

| Layer | Target |
|-------|--------|
| Custom hooks (business logic) | 90% branch coverage |
| Container-equivalent components | 80% |
| Presentational components | 70% (render + key interactions) |
| Utilities / pure functions | 100% |

### E2E (Playwright)

- Critical user journeys within the MFE have Playwright specs.
- Selectors use `data-testid` at feature boundaries — not CSS classes.
- Cross-MFE E2E tests are owned by the shell team, not individual MFE teams.

---

## 9. Performance

- MFE bundle size target: < 120 KB gzipped for initial render (excluding React/ReactDOM — these are shared via Module Federation).
- Lazy-load heavy components within the MFE using `React.lazy` + `Suspense`.
- Use `React.memo` for list item components that receive stable props.
- Virtualise lists > 100 items with `react-virtual` or `@tanstack/virtual`.
- Avoid inline object/function creation in JSX props for frequently re-rendered components.

```tsx
// ✓ Stable ref
const handleDelete = useCallback((id: string) => { ... }, []);

// ✗ New function on every render
<UserCard onDelete={(id) => handleDelete(id)} />
```

---

## 10. Accessibility

- Every interactive element is keyboard-navigable.
- DaisyUI components are ARIA-annotated — do not strip or override `role` / `aria-*` attributes.
- Colour contrast: minimum 4.5:1 for body text (DaisyUI themes meet this — verify custom theme additions).
- Focus management on modal open/close: trap focus inside the modal using `focus-trap-react` or DaisyUI's built-in behaviour.
- Form error messages are associated with their input via `aria-describedby`.
- Run `axe-core` in Playwright E2E on MFE entry routes.

---

## 11. Cross-MFE Communication

All cross-boundary communication follows ADR-002. Summary for React MFE authors:

```tsx
// Listen for shell events (in useEffect, clean up on unmount)
useEffect(() => {
  const handler = (e: Event) => {
    const { theme } = (e as CustomEvent).detail;
    // react to theme change
  };
  window.addEventListener('platform:theme-changed', handler);
  return () => window.removeEventListener('platform:theme-changed', handler);
}, []);

// Request shell navigation (never use window.history directly)
const navigateTo = (path: string) => {
  window.dispatchEvent(new CustomEvent('mfe:navigate-requested', { detail: { path } }));
};
```

Never dispatch `platform:*` events — that namespace belongs to the shell.

---

## 12. Common Mistakes to Avoid

| Mistake | Correct approach |
|---------|-----------------|
| `useEffect` to derive state from props | `useMemo` or compute inline |
| Missing dependency array on `useEffect` | Always declare all deps; use the eslint-plugin-react-hooks lint rule |
| Raw `fetch` + `useState` + `useEffect` for data | React Query (`useQuery`) |
| `any` for event handler types | `React.ChangeEvent<HTMLInputElement>`, `React.MouseEvent`, etc. |
| Prop drilling past 3 levels | Zustand slice or Context |
| `window.history.pushState` for navigation | `mfe:navigate-requested` custom event (ADR-002) |
| Accessing `localStorage.__cx_*` keys as owner | Read-only unless documented in ADR-002 as this MFE's key |
| Raw Tailwind colour classes (`text-blue-500`) | DaisyUI semantic tokens (`text-primary`) |
| Building a custom modal/dropdown/tooltip | DaisyUI component + Tailwind utilities |
| Class components | Functional components only |
| `index.ts` barrel files inside subfolders | Flat imports or feature-level barrel only |
