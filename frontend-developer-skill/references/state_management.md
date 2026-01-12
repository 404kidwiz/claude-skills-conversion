# State Management Guide

## Overview

Choosing the right state management solution depends on your application's complexity, team size, and specific use cases. This guide covers the most popular options.

## Redux Toolkit

### Quick Start

```typescript
// store/userSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
  users: User[];
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  users: [],
  loading: false,
  error: null,
};

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async () => {
    const response = await fetch('/api/users');
    return response.json();
  }
);

const userSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    addUser: (state, action: PayloadAction<User>) => {
      state.users.push(action.payload);
    },
    updateUser: (state, action: PayloadAction<User>) => {
      const index = state.users.findIndex(u => u.id === action.payload.id);
      if (index !== -1) {
        state.users[index] = action.payload;
      }
    },
    deleteUser: (state, action: PayloadAction<number>) => {
      state.users = state.users.filter(u => u.id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch users';
      });
  },
});

export const { addUser, updateUser, deleteUser } = userSlice.actions;
export default userSlice.reducer;

// store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';

export const store = configureStore({
  reducer: {
    users: userReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// store/hooks.ts
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector = <T>(selector: (state: RootState) => T): T => {
  return useSelector(selector);
};
```

### Usage in Components

```typescript
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchUsers, addUser } from '../store/userSlice';

export const UserList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { users, loading, error } = useAppSelector(state => state.users);

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  const handleAddUser = (user: User) => {
    dispatch(addUser(user));
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
};
```

## Zustand

### Basic Usage

```typescript
// store/userStore.ts
import create from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface UserStore {
  users: User[];
  loading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
  addUser: (user: User) => void;
  removeUser: (id: number) => void;
}

export const useUserStore = create<UserStore>()(
  devtools(
    persist(
      (set) => ({
        users: [],
        loading: false,
        error: null,
        fetchUsers: async () => {
          set({ loading: true, error: null });
          try {
            const response = await fetch('/api/users');
            const data = await response.json();
            set({ users: data, loading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch',
              loading: false,
            });
          }
        },
        addUser: (user) => set((state) => ({ users: [...state.users, user] })),
        removeUser: (id) =>
          set((state) => ({ users: state.users.filter((u) => u.id !== id) })),
      }),
      { name: 'user-storage' }
    )
  )
);
```

### Usage in Components

```typescript
import { useUserStore } from '../store/userStore';

export const UserList: React.FC = () => {
  const { users, loading, error, fetchUsers, addUser } = useUserStore();

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
};
```

## Context API

### Setup

```typescript
// context/AuthContext.tsx
import React, { createContext, useContext, useState, useCallback } from 'react';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    setUser(data.user);
    localStorage.setItem('token', data.token);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('token');
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Usage

```typescript
import { useAuth } from '../context/AuthContext';

export const UserProfile: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
};
```

## Jotai

### Setup

```typescript
// atoms.ts
import { atom, useAtom, useSetAtom, useAtomValue } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

// Primitive atom
export const countAtom = atom(0);

// Derived atom
export const doubleCountAtom = atom((get) => get(countAtom) * 2);

// Async atom
export const usersAtom = atom(async () => {
  const response = await fetch('/api/users');
  return response.json();
});

// Storage atom
export const themeAtom = atomWithStorage('theme', 'light');
```

### Usage

```typescript
import { useAtom, useAtomValue, useSetAtom } from 'jotai';
import { countAtom, doubleCountAtom, usersAtom, themeAtom } from '../atoms';

export const Counter: React.FC = () => {
  const [count, setCount] = useAtom(countAtom);
  const doubleCount = useAtomValue(doubleCountAtom);
  const setTheme = useSetAtom(themeAtom);

  return (
    <div>
      <p>Count: {count}</p>
      <p>Double: {doubleCount}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
      <button onClick={() => setTheme('dark')}>Dark Mode</button>
    </div>
  );
};
```

## Recoil

### Setup

```typescript
// atoms.ts
import { atom, selector, useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';

// State atom
export const countState = atom({
  key: 'countState',
  default: 0,
});

// Selector (derived state)
export const doubleCountState = selector({
  key: 'doubleCountState',
  get: ({ get }) => {
    const count = get(countState);
    return count * 2;
  },
});

// Async selector
export const usersState = selector({
  key: 'usersState',
  get: async () => {
    const response = await fetch('/api/users');
    return response.json();
  },
});
```

### Usage

```typescript
import { useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';
import { countState, doubleCountState } from '../atoms';

export const Counter: React.FC = () => {
  const [count, setCount] = useRecoilState(countState);
  const doubleCount = useRecoilValue(doubleCountState);

  return (
    <div>
      <p>Count: {count}</p>
      <p>Double: {doubleCount}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  );
};
```

## Comparison

| Feature | Redux | Zustand | Context | Jotai | Recoil |
|---------|--------|---------|---------|-------|--------|
| Bundle Size | Large | Tiny | Built-in | Tiny | Medium |
| Learning Curve | Medium | Low | Low | Low | Medium |
| DevTools | Excellent | Good | Basic | Good | Good |
| TypeScript Support | Excellent | Excellent | Good | Excellent | Excellent |
| Persistence | Yes | Yes | Manual | Yes | Yes |
| Async Actions | Built-in | Manual | Manual | Built-in | Built-in |
| Best For | Large Apps | Any App | Small Apps | Any App | Large Apps |

## When to Use What

### Redux Toolkit
- Large, complex applications
- Need for advanced debugging
- Team experienced with Redux
- Require time-travel debugging

### Zustand
- Any size application
- Prefer simplicity over advanced features
- Need for minimal boilerplate
- Want TypeScript-first API

### Context API
- Small to medium applications
- Simple state needs
- Want to avoid external dependencies
- Theme, authentication, user preferences

### Jotai
- Any size application
- Prefer atomic state management
- Want minimal boilerplate
- Need for flexible composition

### Recoil
- Large applications
- Need for advanced features
- Want Facebook's battle-tested solution
- Require complex derived state

## Best Practices

### Keep State Minimal
```typescript
// BAD - Store everything
const state = {
  users: [],
  userProfiles: [],
  userSettings: [],
  userPosts: [],
};

// GOOD - Store only what's needed
const state = {
  users: [],
  currentUserId: null,
};
```

### Normalize Data
```typescript
// BAD - Nested structures
const state = {
  users: [
    { id: 1, name: 'John', posts: [{ id: 1, title: 'Post 1' }] },
  ],
};

// GOOD - Normalized
const state = {
  users: { 1: { id: 1, name: 'John', posts: [1] } },
  posts: { 1: { id: 1, title: 'Post 1', userId: 1 } },
};
```

### Use Selectors
```typescript
// BAD - Select in component
const users = useSelector(state => state.users);
const activeUsers = users.filter(u => u.isActive);

// GOOD - Create selector
const selectActiveUsers = createSelector(
  [state => state.users],
  users => users.filter(u => u.isActive)
);
```
