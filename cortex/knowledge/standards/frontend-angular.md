# Frontend Standard — Angular

**Tag:** standards
**Scope:** All Angular applications
**Level:** Principal UI Engineer
**Design System:** Tailwind CSS + DaisyUI (ICG Design System not yet documented — update this file when DS docs are added to `knowledge/design-system/`)

---

## 1. Project Structure

### Folder Layout

```
src/
  app/
    core/               # Singleton services, interceptors, guards, app-level providers
    shared/             # Reusable components, directives, pipes, utilities — no business logic
    features/           # One folder per feature domain
      auth/
        components/     # Dumb/presentational components scoped to this feature
        containers/     # Smart components that wire data
        services/       # Feature-scoped services
        store/          # NgRx feature store (actions, reducers, selectors, effects)
        auth.routes.ts
    layout/             # Shell, nav, sidebar — structural components only
  environments/
  assets/
  styles/               # Global Tailwind config, base layers, custom utilities
```

### Rules
- Features are lazy-loaded via `loadComponent` or `loadChildren`. No feature module is eagerly imported.
- `core/` is imported once in `app.config.ts`. Never import core services in feature modules.
- `shared/` contains zero business logic. If a component needs a service, it belongs in a feature.
- Barrel files (`index.ts`) at the feature level only — not inside subfolders. Deep barrel files cause circular dependency issues.

---

## 2. Component Architecture

### Smart vs. Dumb Components

| Type | Where | Responsibilities |
|------|-------|-----------------|
| Container (smart) | `features/*/containers/` | Data fetching, store dispatch, passes data down via `@Input` |
| Presentational (dumb) | `features/*/components/`, `shared/` | Renders UI, emits events up via `@Output`, no service injection |

- Dumb components accept data via `input()` signals — never inject store or HTTP services directly.
- Containers own side effects. Presentational components own layout and interaction.

### Signals-First (Angular 17+)

```typescript
// Prefer signals over class fields for reactive state
count = signal(0);
doubled = computed(() => this.count() * 2);

// Effect for side effects that depend on signal state
effect(() => {
  console.log('count changed:', this.count());
});

// @Input as signal
value = input.required<string>();
label = input('default label');

// @Output as output()
clicked = output<void>();
selected = output<Item>();
```

- Use `input()` / `output()` in new components. Decorator-based `@Input()` / `@Output()` is acceptable in existing code — do not rewrite on sight.
- `model()` for two-way bindable inputs (replaces `@Input` + `@Output` pairs).
- Avoid `Subject` + `BehaviorSubject` in component class for local state — use `signal` instead.

### Change Detection

- All new components use `changeDetection: ChangeDetectionStrategy.OnPush`.
- Signal-based components with `input()` automatically propagate changes without manual `markForCheck()`.
- Never call `detectChanges()` in component logic. If you feel you need to, the data flow is wrong.

### Component File Conventions

```typescript
@Component({
  selector: 'app-user-card',
  standalone: true,
  imports: [CommonModule, RouterModule],  // only what this component uses
  templateUrl: './user-card.component.html',
  styleUrl: './user-card.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserCardComponent {
  // 1. Injected services (inject() preferred over constructor injection)
  private userService = inject(UserService);

  // 2. Inputs / outputs
  user = input.required<User>();
  deleted = output<string>();

  // 3. Computed / derived state
  displayName = computed(() => `${this.user().firstName} ${this.user().lastName}`);

  // 4. Methods (event handlers named onXxx)
  onDelete() {
    this.deleted.emit(this.user().id);
  }
}
```

- Use `inject()` over constructor injection for all new code.
- Order within class: injections → inputs/outputs → signals/computed → lifecycle → methods.
- Selector prefix matches the app or feature prefix defined in `.eslintrc` (e.g. `app-`, `feat-`).

---

## 3. State Management

### Decision Tree

```
Local UI state only (toggle, form step)?
  → signal() in component

Shared within a feature, no persistence?
  → Feature service with signals or small NgRx feature store

Cross-feature or persisted (auth, cart, preferences)?
  → NgRx global store
```

### NgRx Conventions

- Use NgRx Signals Store (`@ngrx/signals`) for new feature stores. Classic `@ngrx/store` is maintained but not extended.
- One store file per feature: `feature.store.ts` using `signalStore()`.
- Actions in classic store follow `[Feature] Event` naming. Effects are named `loadXxx$`, `saveXxx$`.
- Selectors are the only way to read store state in components — never inject `Store` and call `select()` inline in a template.

```typescript
// NgRx Signals Store pattern
export const UserStore = signalStore(
  { providedIn: 'root' },
  withState<UserState>({ users: [], loading: false, error: null }),
  withComputed(({ users }) => ({
    activeUsers: computed(() => users().filter(u => u.active)),
  })),
  withMethods((store, userService = inject(UserService)) => ({
    async loadUsers() {
      patchState(store, { loading: true });
      const users = await firstValueFrom(userService.getAll());
      patchState(store, { users, loading: false });
    },
  })),
);
```

---

## 4. Routing

- All routes are lazy-loaded. No component is imported directly in the root route config unless it is the shell.
- Route guards use the functional form (`CanActivateFn`, `CanMatchFn`).
- Resolvers use the functional form (`ResolveFn<T>`).
- `withComponentInputBinding()` is enabled in `provideRouter()` — route params and query params are bound directly to component inputs.

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'users',
    loadComponent: () => import('./features/users/containers/user-list.component').then(m => m.UserListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'users/:id',
    loadComponent: () => import('./features/users/containers/user-detail.component').then(m => m.UserDetailComponent),
    resolve: { user: userResolver },
  },
];

// Functional guard
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isAuthenticated() ? true : inject(Router).createUrlTree(['/login']);
};
```

---

## 5. HTTP and Data Access

### Service Layer

- HTTP calls live in services (`features/*/services/` or `core/` for cross-cutting).
- Services return `Observable<T>`. Components that need a one-shot value use `toSignal()` or `firstValueFrom()`.
- Never subscribe in a service — return the observable and let the consumer decide.
- Use `HttpContext` for request-scoped metadata (e.g. skip auth interceptor).

```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private baseUrl = inject(API_BASE_URL);  // injection token, not environment direct

  getAll(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users`);
  }

  getById(id: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/${id}`);
  }
}
```

### Interceptors

- Auth token attachment: one interceptor in `core/interceptors/auth.interceptor.ts`.
- Error normalisation: one interceptor maps HTTP errors to a typed `AppError`.
- Interceptors are functional (`HttpInterceptorFn`).

### Signals Integration

```typescript
// In a container component
private userStore = inject(UserStore);
users = this.userStore.activeUsers;  // computed signal — no subscribe, no async pipe

// One-shot HTTP to signal
private userService = inject(UserService);
user = toSignal(this.userService.getById(this.userId()), { initialValue: null });
```

- Prefer `toSignal()` over `async` pipe for new components. `async` pipe is acceptable in existing templates.
- Always provide `initialValue` or `requireSync: true` in `toSignal()` to avoid undefined type widening.

---

## 6. Forms

### Reactive Forms Only

- Template-driven forms are not used in new code. All forms are reactive (`FormGroup`, `FormControl`).
- Use typed reactive forms (`FormControl<string>`, `FormGroup<{ email: FormControl<string> }>`).
- Form groups are built in the component or a dedicated form builder service for complex forms.

```typescript
form = new FormGroup({
  email: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.email] }),
  password: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.minLength(8)] }),
});

onSubmit() {
  if (this.form.invalid) return;
  const { email, password } = this.form.getRawValue();
  // ...
}
```

### Validation

- Custom validators are pure functions (`ValidatorFn`) — no class validators.
- Cross-field validators go on the `FormGroup`, not individual controls.
- Async validators are debounced (minimum 300 ms) to prevent excessive API calls.
- Error messages are driven by a shared `FormErrorPipe` or `FormErrorComponent` — no inline error string logic in templates.

---

## 7. Design System — Tailwind CSS + DaisyUI

> No ICG Design System documentation exists in `knowledge/design-system/` at time of writing.
> When ICG DS docs are added, update this section and the design system usage rules below.
> Run `python3 cortex.py add knowledge/standards/frontend-angular.md --tag standards` after updating.

### Setup

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{html,ts}'],
  plugins: [require('daisyui')],
  daisyui: {
    themes: ['light', 'dark'],  // add brand theme here
    logs: false,
  },
};
```

### Component Usage Rules

| Need | Use |
|------|-----|
| Button | `<button class="btn btn-primary">` — DaisyUI `btn` variants |
| Input | `<input class="input input-bordered">` inside `<label class="form-control">` |
| Select | `<select class="select select-bordered">` |
| Modal | DaisyUI `modal` + `modal-box` — do not use native `<dialog>` directly |
| Table | DaisyUI `table` with `table-zebra` or `table-pin-rows` |
| Alert/Toast | DaisyUI `alert` with `alert-success / alert-error / alert-warning` |
| Badge | DaisyUI `badge` variants |
| Loading | DaisyUI `loading loading-spinner` |
| Card | DaisyUI `card` + `card-body` |
| Tabs | DaisyUI `tabs` + `tab` |
| Dropdown | DaisyUI `dropdown` — not custom-built |
| Avatar | DaisyUI `avatar` |
| Tooltip | DaisyUI `tooltip` + `data-tip` attribute |

- Never build a custom component for anything DaisyUI provides. Extend with Tailwind utilities, not replacement markup.
- Do not use arbitrary Tailwind values (`w-[347px]`) — use the scale. If the scale doesn't fit, raise the design token gap.
- Layout is Flexbox or Grid via Tailwind utilities. No custom CSS layout classes.
- Dark mode is toggled via DaisyUI `data-theme` on `<html>` — not via Tailwind's `dark:` prefix class toggle.

### Theming

- Colours reference DaisyUI semantic tokens (`primary`, `secondary`, `accent`, `base-100`, etc.), not raw Tailwind colour names (`blue-500`).
- Spacing, font-size, and border-radius use the Tailwind scale unless a brand token overrides it in `tailwind.config.js`.

### Angular Integration

- Apply Tailwind classes in the component template. No `styleUrl` for layout — use the template.
- `styleUrl` is only for component-specific animations or pseudo-element tricks not achievable with utilities.
- Use Angular CDK (`@angular/cdk`) for overlay/focus-trap behaviour behind DaisyUI modal — do not re-implement accessibility primitives.

---

## 8. TypeScript Standards

- `strict: true` enabled in `tsconfig.json`. No `any`, no `// @ts-ignore` without a comment explaining why.
- Use `unknown` over `any` for truly unknown types, then narrow with type guards.
- Interfaces for data shapes; types for unions, intersections, and utility types.
- Enums are avoided — use `as const` objects with a derived type:
  ```typescript
  const Role = { Admin: 'admin', Viewer: 'viewer' } as const;
  type Role = typeof Role[keyof typeof Role];
  ```
- Return types are explicit on all public service methods and store methods. Inferred on private helpers and callbacks.
- Non-null assertion (`!`) requires a comment. Prefer optional chaining + nullish coalescing.

---

## 9. RxJS Conventions

- Import operators from `rxjs/operators` (tree-shakable). Never import from `rxjs/Rx`.
- Avoid nested subscribes. Compose with `switchMap`, `concatMap`, `mergeMap`, `exhaustMap` based on cancellation semantics:
  - `switchMap` — cancel previous (search, navigation)
  - `exhaustMap` — ignore new while active (form submit)
  - `concatMap` — queue (ordered saves)
  - `mergeMap` — parallel (fire and forget)
- Unsubscription: use `takeUntilDestroyed(this.destroyRef)` in new code. `AsyncPipe` and `toSignal()` handle unsubscription automatically.
- Error handling: catch at the effect/service boundary with `catchError`. Do not let errors propagate uncaught into the component.

---

## 10. Testing

### Unit Tests (Jest or Karma/Jasmine — match project config)

- Every service has a unit test. Every component has at minimum a render test + one interaction test per output.
- Use Angular Testing Library (`@testing-library/angular`) for component tests — prefer `screen.getByRole` over direct DOM queries.
- Do not test implementation details (private methods, internal signals). Test observable behaviour.
- Mock HTTP with `HttpClientTestingModule` + `HttpTestingController`. Never hit real APIs in unit tests.
- Store tests use `signalStore` directly with mocked services.

### Coverage Targets

| Layer | Target |
|-------|--------|
| Services (business logic) | 90 % branch coverage |
| Containers (smart components) | 80 % |
| Presentational components | 70 % (render + key interactions) |
| Utilities / pipes | 100 % |

### E2E (Playwright)

- Critical user journeys have Playwright specs in `e2e/`.
- Selectors use `data-testid` attributes — not CSS classes or text content (brittle under copy changes).
- Add `data-testid` at the feature boundary, not on every element.

---

## 11. Performance

- Lazy load all feature routes. Bundle size goal: initial chunk < 150 KB gzipped.
- `@defer` blocks for below-the-fold content and heavy third-party widgets.
- Images: `NgOptimizedImage` directive (`[ngSrc]`) for all static and CMS images — never raw `<img src>` for LCP candidates.
- Virtual scrolling (`CdkVirtualScrollViewport`) for lists > 100 items.
- `trackBy` (or `track` in `@for`) on every `*ngFor` / `@for` that renders a list of objects.
- Avoid `Object.keys()` / `.length` calls directly in templates — derive via `computed()`.

---

## 12. Accessibility

- Every interactive element is keyboard-navigable and has an ARIA label or visible text.
- DaisyUI components are ARIA-annotated by default — do not strip or override `role` / `aria-*` attributes without a documented reason.
- Colour contrast: minimum 4.5:1 for body text, 3:1 for large text (DaisyUI themes generally meet this — verify custom theme colours).
- Focus management on modal open/close uses Angular CDK `FocusTrap`.
- Error messages are associated with their input via `aria-describedby` — use the shared `FormErrorComponent`.
- Run `axe-core` in Playwright E2E on all page routes as part of CI.

---

## 13. Security

- Never bind `[innerHTML]` without sanitisation via Angular's `DomSanitizer.bypassSecurityTrustHtml()` — and that function requires a code review comment explaining the trust decision.
- No `eval()`, `Function()`, or `setTimeout(string)` anywhere.
- Route guards enforce auth on every protected route. Do not rely on UI hiding as a security control.
- Sensitive data (tokens, PII) is not stored in `localStorage`. Use `sessionStorage` or in-memory only.
- CSP headers are set at the infrastructure layer — Angular's SSR config must not disable them.
- Input sanitisation for user-generated content: validate on the API, never trust the client.

---

## 14. Code Quality Gates

- ESLint with `@angular-eslint` — zero warnings in CI.
- Prettier — formatting enforced pre-commit via Husky + lint-staged.
- Import order: Angular core → Angular packages → third-party → internal (`@app/*`) → relative.
- No unused imports, no unused variables (TypeScript `noUnusedLocals`, `noUnusedParameters`).
- PRs with console.log statements outside of development guards are rejected.
- Commit messages follow Conventional Commits: `feat(users): add avatar upload`, `fix(auth): handle token expiry`.

---

## 15. Common Mistakes to Avoid

| Mistake | Correct approach |
|---------|-----------------|
| Subscribing in a service, storing result in a field | Return `Observable<T>`, let consumer decide lifecycle |
| Using `any` to silence TypeScript | Define the type or use `unknown` + type guard |
| Injecting `Store` directly in a dumb component | Pass data via `input()` from the container |
| `new BehaviorSubject()` for component local state | `signal()` |
| Direct DOM manipulation (`document.querySelector`) | Angular renderer or CDK |
| Importing a feature service into another feature | Extract to `core/` or communicate via store |
| Raw Tailwind colour classes (`text-blue-500`) | DaisyUI semantic tokens (`text-primary`) |
| `*ngIf` / `*ngFor` with `NgIf` / `NgFor` module imports | `@if` / `@for` control flow (Angular 17+) |
| `async` pipe with no initial value guard | `toSignal()` with `initialValue` |
| Skipping `trackBy` / `track` on lists | Always provide a stable identity function |
