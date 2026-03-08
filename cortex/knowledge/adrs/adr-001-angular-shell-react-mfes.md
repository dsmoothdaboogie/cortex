# ADR-001 — Angular Shell with React Micro-Frontends

**Date:** 2026-03-08
**Status:** Accepted

---

## Context

The product is a multi-team enterprise application delivered as a suite of independent features. The platform team owns the shell — routing, authentication lifecycle, global navigation, and design system baseline. Feature teams (internal and third-party vendors) deliver self-contained modules.

Two constraints drove the framework decision:
1. The platform and most internal teams have deep Angular expertise. The existing shell, auth flow, interceptor chain, and routing infrastructure are all Angular.
2. Several feature MFEs are delivered by third-party vendors who build in React and cannot be asked to change framework.

Webpack Module Federation (via `@angular-architects/module-federation`) is available to federate these runtimes on a single page without iframes.

---

## Decision

**Angular owns the shell. React is used for individual MFEs.**

- The Angular shell is responsible for: application bootstrap, auth token acquisition and refresh, global routing (`app.routes.ts`), shell-level layout (nav, sidebar, header), and exposing the Module Federation host config.
- React is used for: new feature MFEs built by teams that prefer it, and all third-party-delivered MFEs. React MFEs are federated remotes exposed into the Angular shell.
- Angular MFEs remain an option for internal teams that prefer it — the shell can federate Angular remotes too. The decision is not "React only for MFEs", it is "React is the default for new MFEs unless a team has a strong reason to use Angular."

---

## Rationale

**Why Angular for the shell:**
- Angular's dependency injection, `HttpInterceptor` chain, and `CanActivateFn` guards are well-suited for cross-cutting shell concerns (auth, logging, error handling).
- `Router` with `withComponentInputBinding()` and `withViewTransitions()` gives the shell first-class control over navigation and transitions — React Router would introduce a second competing router.
- The existing team has built and maintained Angular infrastructure for several years. Replacing it introduces risk with no feature gain.

**Why React for MFEs:**
- Third-party vendors deliver React. Module Federation makes this workable without iframes.
- New internal feature teams have React experience and prefer it for component-heavy UI work.
- React's component model (hooks, context, simple composition) is faster for isolated feature UI with limited cross-system state.
- React MFEs boot independently — they can be developed and deployed by separate teams without touching the shell.

**Why not full Angular:**
Third-party vendors cannot be required to rewrite in Angular. The vendor MFE requirement is a hard constraint.

**Why not full React:**
Rewriting the existing Angular shell (auth, routing, interceptors, guards) in React carries high risk, high effort, and no functional improvement. The shell investment is preserved.

**Why not Vue or another framework for MFEs:**
No team expertise. Adds a third framework standard with no gain over React.

---

## Alternatives Considered

| Option | Reason rejected |
|--------|----------------|
| Full Angular (shell + all MFEs) | Vendor MFEs are React — cannot be changed |
| Full React (shell + all MFEs) | High-risk rewrite of working Angular shell with no feature benefit |
| Iframes for isolation | Poor UX (scroll, auth, theming), no shared DS token layer |
| Single-SPA instead of Module Federation | Module Federation is native to Webpack 5 and already in use |

---

## Consequences

**What becomes easier:**
- Vendor MFEs can be integrated without renegotiating technology contracts
- Feature teams choose React without needing shell access
- MFEs deploy independently — shell does not need to redeploy for a feature update

**What becomes harder:**
- Two framework standards must be maintained (`frontend-angular.md`, `frontend-react-mfe.md`)
- Shared dependencies (React, ReactDOM) must be declared as singletons in Module Federation config — version mismatches will cause runtime errors
- Design system tokens (Tailwind/DaisyUI) must be configured consistently in both runtimes
- Debugging across the Angular/React boundary requires understanding two component lifecycles
- Auth token availability must be explicitly contracted (see ADR-002)

**Non-negotiables that follow from this decision:**
- Module Federation shared deps config is owned by the platform team — MFE teams do not override it unilaterally
- React MFEs do not import Angular services or depend on Angular DI
- Angular shell does not render React component trees directly — only via Module Federation remote entry points
- Cross-MFE communication follows the contract defined in ADR-002
