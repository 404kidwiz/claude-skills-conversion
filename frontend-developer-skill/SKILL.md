# Frontend Developer Skill

## Overview

The Frontend Developer skill provides comprehensive tools and references for building modern, performant web applications with React and other frameworks.

## Scripts

### React Component Scaffolding
```bash
ts-node scripts/scaffold_component.tsx <ComponentName> [OPTIONS]

# Options:
# --hooks=<hooks>: Include hooks (useState,useEffect,useCallback)
# --props=<json>: Component props as JSON
# --styles=<type>: CSS type (css, styled-components, emotion, module)
# --no-test: Skip test file generation

# Example: Create component with hooks
ts-node scripts/scaffold_component.tsx UserProfile --hooks=useState,useEffect

# Example: Create component with props
ts-node scripts/scaffold_component.tsx Button --props='[{"name":"label","type":"string","required":true}]'

# Example: Create component with styled-components
ts-node scripts/scaffold_component.tsx Card --styles=styled-components
```

### State Management Setup
```bash
ts-node scripts/setup_state.ts <stateName> <type>

# Types: redux, zustand, context, jotai, recoil

# Example: Setup Redux store
ts-node scripts/setup_state.ts User redux

# Example: Setup Zustand store
ts-node scripts/setup_state.ts Cart zustand

# Example: Setup Context API
ts-node scripts/setup_state.ts Auth context
```

### API Client Generation
```bash
ts-node scripts/create_api_client.ts <clientType>

# Client types: axios, fetch

# Example: Generate Axios client
ts-node scripts/create_api_client.ts axios

# Example: Generate Fetch client
ts-node scripts/create_api_client.ts fetch
```

### Utility Functions Generation
```bash
ts-node scripts/create_utils.ts

# Generates:
# - Validators (email, password, URL, phone)
# - Storage helpers (localStorage, sessionStorage)
# - Date utilities
# - Number utilities
# - String utilities
# - Formatters

# Example: Generate all utilities
ts-node scripts/create_utils.ts
```

### Linting Setup
```bash
ts-node scripts/setup_linting.ts

# Generates:
# - ESLint configuration
# - Prettier configuration
# - Ignore files
# - Package.json scripts

# Example: Setup linting
ts-node scripts/setup_linting.ts
```

### Testing Setup
```bash
ts-node scripts/setup_testing.ts <framework>

# Frameworks: jest, vitest, playwright

# Example: Setup Jest
ts-node scripts/setup_testing.ts jest

# Example: Setup Vitest
ts-node scripts/setup_testing.ts vitest

# Example: Setup Playwright (E2E)
ts-node scripts/setup_testing.ts playwright
```

### Build Optimization
```bash
ts-node scripts/optimize_build.ts <bundler>

# Bundlers: vite, webpack

# Example: Optimize Vite build
ts-node scripts/optimize_build.ts vite

# Example: Optimize Webpack build
ts-node scripts/optimize_build.ts webpack
```

### Deployment Script
```bash
./scripts/deploy.sh [OPTIONS]

# Options:
# --skip-tests: Skip test execution
# --skip-quality: Skip linting/formatting
# --platform <vercel|netlify|s3|github>: Deployment platform

# Example: Deploy to Vercel
./scripts/deploy.sh --platform vercel

# Example: Deploy to Netlify
./scripts/deploy.sh --platform netlify

# Example: Deploy to AWS S3
./scripts/deploy.sh --platform s3
```

## References

### React Patterns (`references/react_patterns.md`)
- Functional components with hooks
- Container/Presentational pattern
- Higher-Order Components (HOC)
- Custom hooks
- State management patterns
- Performance optimization
- Testing patterns
- Error handling (Error Boundaries)
- Form handling
- Accessibility

### State Management (`references/state_management.md`)
- Redux Toolkit
- Zustand
- Context API
- Jotai
- Recoil
- Comparison table
- When to use what
- Best practices
- Code examples

### Performance Guide (`references/performance_guide.md`)
- Core Web Vitals (LCP, FID, CLS)
- Code splitting (route-based, component-based)
- Tree shaking
- Bundle optimization
- Memory management
- Image optimization
- Font optimization
- Rendering optimization (virtualization, memoization)
- Network optimization
- Performance monitoring

## Quick Start

### Create a New Project

```bash
# 1. Create component with hooks
ts-node scripts/scaffold_component.tsx UserProfile --hooks=useState,useEffect --styles=module

# 2. Setup state management
ts-node scripts/setup_state.ts User redux

# 3. Generate API client
ts-node scripts/create_api_client.ts axios

# 4. Generate utilities
ts-node scripts/create_utils.ts

# 5. Setup testing
ts-node scripts/setup_testing.ts vitest

# 6. Setup linting
ts-node scripts/setup_linting.ts
```

### Deploy to Production

```bash
# Run quality checks
npm run lint-and-format

# Deploy to platform
./scripts/deploy.sh --platform vercel
```

## Component Library

### Available Components

- UserCard
- UserProfile
- Button
- Form
- Modal
- Table
- Chart
- Map
- Editor

### Usage

```typescript
import UserProfile from './UserProfile';

const App = () => {
  return (
    <UserProfile userId={1} onUpdate={handleUpdate} />
  );
};
```

## State Management

### Redux Toolkit

```typescript
// Generate store
ts-node scripts/setup_state.ts User redux

// Use in component
import { useAppDispatch, useAppSelector } from './store/hooks';
import { fetchUsers } from './store/userSlice';

const UserList = () => {
  const dispatch = useAppDispatch();
  const users = useAppSelector(state => state.users.users);

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  return <div>{/* ... */}</div>;
};
```

### Zustand

```typescript
// Generate store
ts-node scripts/setup_state.ts Cart zustand

// Use in component
import { useCartStore } from './store/cartStore';

const ShoppingCart = () => {
  const { items, addItem } = useCartStore();

  return <div>{/* ... */}</div>;
};
```

## Testing

### Unit Testing

```typescript
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('renders user information', () => {
    render(<UserProfile userId={1} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### E2E Testing

```typescript
import { test, expect } from '@playwright/test';

test('user login flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=Login');
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button:has-text("Login")');
  
  await expect(page).toHaveURL(/dashboard/);
});
```

## Performance

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));

const App = () => {
  return (
    <Suspense fallback={<Loading />}>
      <Dashboard />
    </Suspense>
  );
};
```

### Memoization

```typescript
import { memo, useMemo, useCallback } from 'react';

const ExpensiveComponent = memo(({ data }: { data: Data }) => {
  const processedData = useMemo(() => {
    return heavyComputation(data);
  }, [data]);

  return <div>{processedData}</div>;
});
```

## Best Practices

1. **Use functional components** - Modern React pattern
2. **Leverage hooks** - Avoid class components when possible
3. **Memoize expensive operations** - Use useMemo, useCallback
4. **Lazy load components** - Reduce initial bundle size
5. **Type everything** - Leverage TypeScript
6. **Test thoroughly** - Unit, integration, and E2E tests
7. **Optimize images** - Use modern formats and lazy loading
8. **Implement error boundaries** - Catch errors gracefully
9. **Make it accessible** - ARIA labels, keyboard navigation
10. **Monitor performance** - Track Core Web Vitals

## Common Patterns

### Custom Hooks

```typescript
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
}
```

### Container/Presentational

```typescript
// Presentational (dumb)
const UserList = ({ users, onUserClick }: UserListProps) => (
  <ul>
    {users.map(user => (
      <li key={user.id} onClick={() => onUserClick(user.id)}>
        {user.name}
      </li>
    ))}
  </ul>
);

// Container (smart)
const UserListContainer = () => {
  const { users, fetchUsers } = useUsers();

  useEffect(() => fetchUsers(), [fetchUsers]);

  return <UserList users={users} onUserClick={handleClick} />;
};
```

## Troubleshooting

### Common Issues

**State not updating**
- Check if using correct setter
- Verify dependency arrays in useEffect
- Ensure components are re-rendering

**Component not re-rendering**
- Check for unnecessary re-renders
- Verify memoization is working
- Review prop changes

**Performance issues**
- Profile with React DevTools
- Check for large bundle sizes
- Review unnecessary re-renders
- Implement code splitting

**Tests failing**
- Verify test setup
- Check mock implementations
- Review async handling
- Ensure proper cleanup

## Resources

- [React Documentation](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Vite](https://vitejs.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright](https://playwright.dev/)
- [Web Vitals](https://web.dev/vitals/)
