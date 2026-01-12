# Frontend Performance Guide

## Core Web Vitals

### Largest Contentful Paint (LCP)

**Target:** < 2.5 seconds

LCP measures the loading performance of the largest content element visible in the viewport.

```typescript
// Optimize LCP
// 1. Remove render-blocking resources
<link rel="preload" href="critical.css" as="style">
<link rel="preconnect" href="https://fonts.googleapis.com">

// 2. Lazy load images
<img 
  loading="lazy" 
  src="image.jpg" 
  alt="Description"
/>

// 3. Use modern image formats
<picture>
  <source type="image/webp" srcset="image.webp">
  <source type="image/jpeg" srcset="image.jpg">
  <img src="image.jpg" alt="Description">
</picture>
```

### First Input Delay (FID)

**Target:** < 100 milliseconds

FID measures the time from when a user first interacts with your page to the time when the browser responds.

```typescript
// Minimize JavaScript execution
// 1. Code split by routes
const Dashboard = lazy(() => import('./Dashboard'));

// 2. Reduce main thread work
// Avoid long-running synchronous operations
const heavyTask = () => {
  // BAD: Blocks main thread
  for (let i = 0; i < 1000000; i++) {
    processItem(i);
  }
};

// GOOD: Use Web Workers or break into chunks
const chunkedTask = async () => {
  for (let i = 0; i < 100; i++) {
    await new Promise(resolve => requestAnimationFrame(resolve));
    processItem(i);
  }
};

// 3. Debounce event handlers
const debounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const handleInput = debounce((value: string) => {
  // Expensive operation
}, 300);
```

### Cumulative Layout Shift (CLS)

**Target:** < 0.1

CLS measures the stability of a page layout as it loads.

```typescript
// Reserve space for dynamic content
// BAD
<div>
  <img src="image.jpg" alt="" />
</div>

// GOOD
<div style={{ width: '300px', height: '200px' }}>
  <img src="image.jpg" alt="" />
</div>

// Use skeleton loading
<SkeletonLoader width="100%" height="200px" />

// Avoid injecting content above existing content
// BAD
setTimeout(() => {
  document.body.insertBefore(newElement, existingElement);
}, 1000);

// GOOD
const container = useRef<HTMLDivElement>(null);
useEffect(() => {
  if (container.current) {
    container.current.appendChild(newElement);
  }
}, []);
```

## Code Splitting

### Route-based Splitting

```typescript
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load routes
const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// Add loading fallback
function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

### Component-based Splitting

```typescript
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./HeavyChart'));

export const Dashboard: React.FC = () => {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>
      {showChart && (
        <Suspense fallback={<LoadingSpinner />}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
};
```

## Tree Shaking

### Proper Imports

```javascript
// BAD - Imports entire library
import _ from 'lodash';

// GOOD - Import only what's needed
import { debounce, throttle } from 'lodash';

// EVEN BETTER - Use tree-shakeable libraries
import { debounce } from 'lodash-es';
```

### Dynamic Imports

```typescript
// Load heavy libraries only when needed
const loadChart = async () => {
  const { Chart } = await import('chart.js');
  // Use Chart
};
```

## Bundle Optimization

### Webpack Configuration

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    },
    runtimeChunk: 'single',
  },
};
```

### Vite Configuration

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@mui/material', '@mui/icons-material'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
});
```

## Memory Management

### Cleanup Effects

```typescript
useEffect(() => {
  const timer = setInterval(() => {
    console.log('Tick');
  }, 1000);

  const abortController = new AbortController();

  fetch('/api/data', { signal: abortController.signal });

  // Cleanup
  return () => {
    clearInterval(timer);
    abortController.abort();
  };
}, []);
```

### Avoid Memory Leaks

```typescript
// BAD - Accumulating data in state
export const List: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Keeps adding items without cleanup
      setItems(prev => [...prev, newItem]);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <>{/* ... */}</>;
};

// GOOD - Limit data size
export const List: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const MAX_ITEMS = 100;

  useEffect(() => {
    const interval = setInterval(() => {
      setItems(prev => {
        const newItems = [...prev, newItem];
        return newItems.length > MAX_ITEMS
          ? newItems.slice(-MAX_ITEMS)
          : newItems;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <>{/* ... */}</>;
};
```

## Image Optimization

### Responsive Images

```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero Image"
  width={1920}
  height={1080}
  priority
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

### Lazy Loading

```typescript
<img
  loading="lazy"
  src="image.jpg"
  alt="Description"
  width="800"
  height="600"
/>
```

### Modern Formats

```typescript
<picture>
  <source type="image/avif" srcset="image.avif">
  <source type="image/webp" srcset="image.webp">
  <img src="image.jpg" alt="Description">
</picture>
```

## Font Optimization

### Font Loading

```html
<!-- Preconnect to font domain -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Preload critical fonts -->
<link rel="preload" 
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" 
      as="style">

<!-- Async load non-critical fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" 
      rel="stylesheet">
```

### Font Display

```css
@font-face {
  font-family: 'Inter';
  src: url('inter.woff2') format('woff2');
  font-display: swap;
}
```

## Rendering Optimization

### Virtualization

```typescript
import { FixedSizeList } from 'react-window';

export const VirtualList: React.FC<{ items: any[] }> = ({ items }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

### Memoization

```typescript
// React.memo for components
export const ExpensiveComponent = React.memo(({ data }: { data: Data }) => {
  // Expensive rendering
  return <div>{/* ... */}</div>;
}, (prevProps, nextProps) => {
  return prevProps.data.id === nextProps.data.id;
});

// useMemo for expensive computations
const filteredData = useMemo(() => {
  return data.filter(item => item.isActive);
}, [data]);

// useCallback for stable function references
const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);
```

## Network Optimization

### Request Batching

```typescript
// BAD - Individual requests
const fetchData = async () => {
  const user1 = await fetch('/api/users/1');
  const user2 = await fetch('/api/users/2');
  const user3 = await fetch('/api/users/3');
};

// GOOD - Batched request
const fetchData = async () => {
  const response = await fetch('/api/users?ids=1,2,3');
  return response.json();
};
```

### Request Debouncing

```typescript
const debounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const handleSearch = debounce((query: string) => {
  fetch(`/api/search?q=${query}`);
}, 300);
```

## Performance Monitoring

### Web Vitals Measurement

```typescript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export const reportWebVitals = (metric: any) => {
  // Send to analytics
  console.log(metric);
  
  // Send to monitoring service
  // analytics.track('Web Vitals', metric);
};

getCLS(reportWebVitals);
getFID(reportWebVitals);
getFCP(reportWebVitals);
getLCP(reportWebVitals);
getTTFB(reportWebVitals);
```

## Tools and Resources

- **Lighthouse**: Chrome DevTools for performance auditing
- **WebPageTest**: Web performance testing tool
- **Chrome DevTools**: Built-in browser performance tools
- **Bundle Analyzer**: Analyze bundle size and composition
- **React DevTools**: Profiler for React components

## Checklists

### Before Deploying
- [ ] Run Lighthouse audit
- [ ] Check bundle sizes
- [ ] Test on slow connections
- [ ] Verify lazy loading works
- [ ] Test on mobile devices
- [ ] Check Core Web Vitals
- [ ] Optimize images
- [ ] Minimize JavaScript

### Continuous Monitoring
- [ ] Track Core Web Vitals
- [ ] Monitor error rates
- [ ] Track user engagement metrics
- [ ] Monitor API performance
- [ ] Track bundle size changes
