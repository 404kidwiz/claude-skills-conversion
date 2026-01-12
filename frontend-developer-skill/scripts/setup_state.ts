import * as fs from 'fs';
import * as path from 'path';

interface StateConfig {
  name: string;
  type: 'redux' | 'zustand' | 'context' | 'jotai' | 'recoil';
  initialState: any;
  actions?: string[];
  asyncActions?: string[];
}

class StateManagerSetup {
  private config: StateConfig;

  constructor(config: StateConfig) {
    this.config = config;
  }

  setup(outputDir: string): void {
    const stateDir = path.join(outputDir, 'store');
    fs.mkdirSync(stateDir, { recursive: true });

    switch (this.config.type) {
      case 'redux':
        this.setupRedux(stateDir);
        break;
      case 'zustand':
        this.setupZustand(stateDir);
        break;
      case 'context':
        this.setupContext(stateDir);
        break;
      case 'jotai':
        this.setupJotai(stateDir);
        break;
      case 'recoil':
        this.setupRecoil(stateDir);
        break;
    }

    console.log(`✓ ${this.config.type.toUpperCase()} state management setup complete`);
  }

  private setupRedux(dir: string): void {
    // Create Redux Toolkit setup
    const sliceContent = `import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface ${this.capitalize(this.config.name)}State {
  ${this.config.name.toLowerCase()}: ${this.getInitialType()};
  loading: boolean;
  error: string | null;
}

const initialState: ${this.capitalize(this.config.name)}State = {
  ${this.config.name.toLowerCase()}: ${JSON.stringify(this.config.initialState)},
  loading: false,
  error: null,
};

// Async thunks
${this.generateAsyncThunks()}

const ${this.capitalize(this.config.name)}Slice = createSlice({
  name: '${this.config.name.toLowerCase()}',
  initialState,
  reducers: {
${this.generateReducers()}
  },
  extraReducers: (builder) => {
${this.generateExtraReducers()}
  },
});

export const { ${this.generateActionCreators()} } = ${this.capitalize(this.config.name)}Slice.actions;
export const ${this.generateSelectorName()} = (state: RootState) => state.${this.config.name.toLowerCase()}.${this.config.name.toLowerCase()};
export default ${this.capitalize(this.config.name)}Slice.reducer;
`;

    const storeContent = `import { configureStore } from '@reduxjs/toolkit';
import ${this.capitalize(this.config.name)}Reducer from './${this.capitalize(this.config.name)}Slice';

const store = configureStore({
  reducer: {
    ${this.config.name.toLowerCase()}: ${this.capitalize(this.config.name)}Reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
`;

    const hooksContent = `import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector = <T>(selector: (state: RootState) => T): T => {
  return useSelector(selector);
};
`;

    const typesContent = `export interface ${this.capitalize(this.config.name)} {
${this.generateTypeInterface()}
}
`;

    fs.writeFileSync(path.join(dir, `${this.capitalize(this.config.name)}Slice.ts`), sliceContent);
    fs.writeFileSync(path.join(dir, 'store.ts'), storeContent);
    fs.writeFileSync(path.join(dir, 'hooks.ts'), hooksContent);
    fs.writeFileSync(path.join(dir, 'types.ts'), typesContent);
    fs.writeFileSync(path.join(dir, 'index.ts'), this.generateIndex());
  }

  private setupZustand(dir: string): void {
    const storeContent = `import create from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface ${this.capitalize(this.config.name)}Store {
  ${this.config.name.toLowerCase()}: ${this.getInitialType()};
  loading: boolean;
  error: string | null;
${this.generateActions()}
}

export const use${this.capitalize(this.config.name)}Store = create<${this.capitalize(this.config.name)}Store>()(
  devtools(
    persist(
      (set) => ({
        ${this.config.name.toLowerCase()}: ${JSON.stringify(this.config.initialState)},
        loading: false,
        error: null,
${this.generateActionImplementations()}
      }),
      { name: '${this.config.name.toLowerCase()}-storage' }
    )
  )
);
`;

    fs.writeFileSync(path.join(dir, `${this.config.name}Store.ts`), storeContent);
    fs.writeFileSync(path.join(dir, 'index.ts'), `export { use${this.capitalize(this.config.name)}Store } from './${this.config.name}Store';`);
  }

  private setupContext(dir: string): void {
    const contextContent = `import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

interface ${this.capitalize(this.config.name)}ContextType {
  ${this.config.name.toLowerCase()}: ${this.getInitialType()};
  loading: boolean;
  error: string | null;
${this.generateActionSignatures()}
}

interface ${this.capitalize(this.config.name)}ProviderProps {
  children: ReactNode;
}

const ${this.capitalize(this.config.name)}Context = createContext<${this.capitalize(this.config.name)}ContextType | undefined>(undefined);

export const use${this.capitalize(this.config.name)} = () => {
  const context = useContext(${this.capitalize(this.config.name)}Context);
  if (!context) {
    throw new Error('use${this.capitalize(this.config.name)} must be used within a ${this.capitalize(this.config.name)}Provider');
  }
  return context;
};

export const ${this.capitalize(this.config.name)}Provider: React.FC<${this.capitalize(this.config.name)}ProviderProps> = ({ children }) => {
  const [${this.config.name.toLowerCase()}, set${this.capitalize(this.config.name)}] = useState<${this.getInitialType()}>(\${JSON.stringify(this.config.initialState)});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

${this.generateContextActions()}

  return (
    <${this.capitalize(this.config.name)}Context.Provider
      value={{
        ${this.config.name.toLowerCase()},
        loading,
        error,
${this.generateProviderValues()}
      }}
    >
      {children}
    </${this.capitalize(this.config.name)}Context.Provider>
  );
};
`;

    fs.writeFileSync(path.join(dir, `${this.config.name}Context.tsx`), contextContent);
    fs.writeFileSync(path.join(dir, 'index.ts'), `export { use${this.capitalize(this.config.name)}, ${this.capitalize(this.config.name)}Provider } from './${this.config.name}Context';`);
  }

  private setupJotai(dir: string): void {
    const atomsContent = `import { atom, useAtom, useSetAtom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

// Base atom
export const ${this.config.name.toLowerCase()}Atom = atomWithStorage(
  '${this.config.name.toLowerCase()}',
  ${JSON.stringify(this.config.initialState)}
);

// Derived atoms
export const ${this.config.name.toLowerCase()}Selector = atom((get) => get(${this.config.name.toLowerCase()}Atom));

// Action atoms
${this.generateActionAtoms()}
`;

    const hooksContent = `import { ${this.config.name.toLowerCase()}Atom, ${this.generateActionAtomNames()} } from './atoms';

// Read/write hooks
export const use${this.capitalize(this.config.name)} = () => {
  return useAtom(${this.config.name.toLowerCase()}Atom);
};

// Read-only hooks
export const use${this.capitalize(this.config.name)}Value = () => {
  return useAtom(${this.config.name.toLowerCase()}Selector)[0];
};

// Action hooks
${this.generateActionHooks()}
`;

    fs.writeFileSync(path.join(dir, 'atoms.ts'), atomsContent);
    fs.writeFileSync(path.join(dir, 'hooks.ts'), hooksContent);
    fs.writeFileSync(path.join(dir, 'index.ts'), `export * from './atoms';\nexport * from './hooks';`);
  }

  private setupRecoil(dir: string): void {
    const atomsContent = `import { atom, selector, useRecoilState, useRecoilValue, useSetRecoilState } from 'recoil';

// State atoms
export const ${this.config.name.toLowerCase()}State = atom<${this.getInitialType()}>({
  key: '${this.config.name.toLowerCase()}State',
  default: ${JSON.stringify(this.config.initialState)},
});

// Derived selectors
${this.generateSelectors()}
`;

    const hooksContent = `import {
  ${this.config.name.toLowerCase()}State,
  ${this.generateSelectorExports()}
} from './atoms';

export const use${this.capitalize(this.config.name)} = () => useRecoilState(${this.config.name.toLowerCase()}State);
export const use${this.capitalize(this.config.name)}Value = () => useRecoilValue(${this.config.name.toLowerCase()}State);
export const useSet${this.capitalize(this.config.name)} = () => useSetRecoilState(${this.config.name.toLowerCase()}State);
`;

    fs.writeFileSync(path.join(dir, 'atoms.ts'), atomsContent);
    fs.writeFileSync(path.join(dir, 'hooks.ts'), hooksContent);
    fs.writeFileSync(path.join(dir, 'index.ts'), `export * from './atoms';\nexport * from './hooks';`);
  }

  private generateAsyncThunks(): string {
    if (!this.config.asyncActions) return '';

    return this.config.asyncActions.map(action => {
      return `export const ${action} = createAsyncThunk(
  '${this.config.name.toLowerCase()}/${action}',
  async (payload: any, { rejectWithValue }) => {
    try {
      // Async logic here
      const response = await fetch('/api/endpoint');
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);`;
    }).join('\n\n');
  }

  private generateReducers(): string {
    if (!this.config.actions) return '';

    return this.config.actions.map(action => {
      return `    ${action}(state, action: PayloadAction<any>) {
      // Reducer logic here
    },`;
    }).join('\n');
  }

  private generateExtraReducers(): string {
    if (!this.config.asyncActions) return '';

    return this.config.asyncActions.map(action => {
      return `    builder
      .addCase(${action}.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(${action}.fulfilled, (state, action) => {
        state.loading = false;
        state.${this.config.name.toLowerCase()} = action.payload;
      })
      .addCase(${action}.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })`;
    }).join('\n    ');
  }

  private generateActionCreators(): string {
    if (!this.config.actions) return '';

    return this.config.actions.join(', ');
  }

  private generateActionSignatures(): string {
    return this.config.actions?.map(action => {
      return `  ${action}: (payload: any) => void;`;
    }).join('\n') || '';
  }

  private generateActions(): string {
    return this.config.actions?.map(action => {
      return `  ${action}: (payload: any) => void;`;
    }).join('\n') || '';
  }

  private generateActionImplementations(): string {
    return this.config.actions?.map(action => {
      return `    ${action}: (payload) => set((state) => ({ ${this.config.name.toLowerCase()}: payload })),`;
    }).join('\n') || '';
  }

  private generateContextActions(): string {
    return this.config.actions?.map(action => {
      return `  const ${action} = useCallback((payload: any) => {
    set${this.capitalize(this.config.name)}(payload);
  }, []);`;
    }).join('\n\n') || '';
  }

  private generateProviderValues(): string {
    return this.config.actions?.join(',\n        ') || '';
  }

  private capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  private getInitialType(): string {
    if (typeof this.config.initialState === 'string') return 'string';
    if (typeof this.config.initialState === 'number') return 'number';
    if (typeof this.config.initialState === 'boolean') return 'boolean';
    if (Array.isArray(this.config.initialState)) return 'any[]';
    return 'any';
  }

  private generateIndex(): string {
    return `export { default as ${this.capitalize(this.config.name)}Reducer } from './${this.capitalize(this.config.name)}Slice';
export { useAppDispatch, useAppSelector } from './hooks';
export type { RootState, AppDispatch } from './store';
`;
  }

  private generateTypeInterface(): string {
    return this.config.initialState
      ? Object.keys(this.config.initialState).map(key => {
          const value = (this.config.initialState as any)[key];
          return `  ${key}: ${typeof value};`;
        }).join('\n')
      : '';
  }

  private generateActionAtoms(): string {
    return this.config.actions?.map(action => {
      return `export const ${action}Atom = atom(
  null,
  (get, set, payload) => {
    set(${this.config.name.toLowerCase()}Atom, payload);
  }
);`;
    }).join('\n\n') || '';
  }

  private generateActionAtomNames(): string {
    return this.config.actions?.join(', ') || '';
  }

  private generateActionHooks(): string {
    return this.config.actions?.map(action => {
      return `export const use${this.capitalize(action)} = () => useSetRecoilState(${action}Atom);`;
    }).join('\n') || '';
  }

  private generateSelectors(): string {
    return `export const ${this.config.name.toLowerCase()}ValueSelector = selector({
  key: '${this.config.name.toLowerCase()}ValueSelector',
  get: ({ get }) => get(${this.config.name.toLowerCase()}State),
});`;
  }

  private generateSelectorExports(): string {
    return `${this.config.name.toLowerCase()}ValueSelector`;
  }
}

// CLI
const args = process.argv.slice(2);
const name = args[0];
const type = args[1] || 'redux';

if (!name) {
  console.error('State name is required');
  process.exit(1);
}

const config: StateConfig = {
  name,
  type: type as any,
  initialState: {},
  actions: [],
  asyncActions: []
};

const setup = new StateManagerSetup(config);
setup.setup('./src/store');
