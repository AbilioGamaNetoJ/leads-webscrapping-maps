# {PROJECT_NAME} — Code Conventions

<!-- Canonical source of code conventions for AI agents. -->

| Field | Value |
|---|---|
| **Response language** | {PT/EN} |
| **Code language** | {EN} |
| **Last updated** | {DATE} |

## Naming

| Element | Convention | Example |
|---|---|---|
| Files (components) | kebab-case | `product-card.tsx` |
| Files (utils) | kebab-case | `format-price.ts` |
| Components | PascalCase | `ProductCard` |
| Functions | camelCase | `calculateTotal()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| DB tables | snake_case | `order_items` |
| DB columns | snake_case | `created_at` |
| Environment variables | UPPER_SNAKE | `DATABASE_URL` |
| Git branches | kebab-case | `feat/user-auth` |
| Commits | conventional | `feat(scope): description` |

## Imports

```{LANGUAGE}
// ✅ CORRECT: Path aliases
import { Button } from "@/components/ui/button";

// ❌ WRONG: Long relative paths
import { Button } from "../../../components/ui/button";
```

## Typing

```{LANGUAGE}
// ✅ CORRECT: Strong typing
interface User {
  id: string;
  name: string;
  email: string;
  role: "admin" | "user";
}

// ❌ WRONG: Weak typing
const user: any = { ... };
```

## Error Handling

```{LANGUAGE}
// ✅ CORRECT: Consistent API error handling
try {
  // ... logic
  return Response.json({ data });
} catch (error) {
  console.error("[CONTEXT]", error);
  return Response.json(
    { error: "Error description" },
    { status: 500 }
  );
}
```

## Environment Variables

```{LANGUAGE}
// ✅ CORRECT: Server-side only
const apiKey = process.env.SECRET_KEY;

// ✅ CORRECT: Client-side (public)
const appUrl = process.env.NEXT_PUBLIC_APP_URL;

// ❌ WRONG: Expose secret to client
const secret = process.env.NEXT_PUBLIC_SECRET_KEY;
```

## Commits

```
type(scope): short description

feat(auth): add magic link login
fix(cart): fix race condition on quantity update
refactor(api): extract validation into middleware
```

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change without feat/fix |
| `docs` | Documentation only |
| `style` | Formatting |
| `test` | Add/update tests |
| `chore` | Build, deps, tooling |

---

> **Note for AIs:** These conventions apply to ALL generated code. Follow them strictly.
