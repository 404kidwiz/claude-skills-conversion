import * as fs from 'fs';
import * as path from 'path';

class UtilsGenerator {
  generate(outputDir: string): void {
    const utilsDir = path.join(outputDir, 'utils');
    fs.mkdirSync(utilsDir, { recursive: true });

    this.createFormatters(utilsDir);
    this.createValidators(utilsDir);
    this.createFormatters(utilsDir);
    this.createLocalStorage(utilsDir);
    this.createDateUtils(utilsDir);
    this.createNumberUtils(utilsDir);
    this.createStringUtils(utilsDir);
    this.createIndex(utilsDir);

    console.log('✓ Utility functions generated');
  }

  private createValidators(dir: string): void {
    const content = `// Email validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Password validation (at least 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special)
export const isValidPassword = (password: string): boolean => {
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  return passwordRegex.test(password);
};

// URL validation
export const isValidURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Phone number validation (simple)
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s-()]+$/;
  return phoneRegex.test(phone);
};
`;

    fs.writeFileSync(path.join(dir, 'validators.ts'), content);
  }

  private createLocalStorage(dir: string): void {
    const content = `// Local storage helpers
export const storage = {
  get<T>(key: string, defaultValue?: T): T | null {
    if (typeof window === 'undefined') return defaultValue || null;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error(\`Error reading from localStorage: \${error}\`);
      return defaultValue || null;
    }
  },

  set<T>(key: string, value: T): void {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(\`Error writing to localStorage: \${error}\`);
    }
  },

  remove(key: string): void {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.error(\`Error removing from localStorage: \${error}\`);
    }
  },

  clear(): void {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.clear();
    } catch (error) {
      console.error(\`Error clearing localStorage: \${error}\`);
    }
  },
};

// Session storage helpers
export const sessionStorage = {
  get<T>(key: string, defaultValue?: T): T | null {
    if (typeof window === 'undefined') return defaultValue || null;
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error(\`Error reading from sessionStorage: \${error}\`);
      return defaultValue || null;
    }
  },

  set<T>(key: string, value: T): void {
    if (typeof window === 'undefined') return;
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(\`Error writing to sessionStorage: \${error}\`);
    }
  },

  remove(key: string): void {
    if (typeof window === 'undefined') return;
    try {
      window.sessionStorage.removeItem(key);
    } catch (error) {
      console.error(\`Error removing from sessionStorage: \${error}\`);
    }
  },
};
`;

    fs.writeFileSync(path.join(dir, 'storage.ts'), content);
  }

  private createDateUtils(dir: string): void {
    const content = `// Format date to locale string
export const formatDate = (date: Date | string, locale = 'en-US'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

// Format date and time
export const formatDateTime = (date: Date | string, locale = 'en-US'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Format relative time (e.g., "2 hours ago")
export const formatRelativeTime = (date: Date | string, locale = 'en-US'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

  if (diffInSeconds < 60) {
    return rtf.format(-diffInSeconds, 'second');
  } else if (diffInSeconds < 3600) {
    return rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
  } else if (diffInSeconds < 86400) {
    return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
  } else if (diffInSeconds < 604800) {
    return rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
  } else {
    return formatDate(d, locale);
  }
};

// Get time ago
export const timeAgo = (date: Date | string): string => {
  return formatRelativeTime(date);
};
`;

    fs.writeFileSync(path.join(dir, 'date.ts'), content);
  }

  private createNumberUtils(dir: string): void {
    const content = `// Format number with commas
export const formatNumber = (num: number, locale = 'en-US'): string => {
  return num.toLocaleString(locale);
};

// Format currency
export const formatCurrency = (
  amount: number,
  currency = 'USD',
  locale = 'en-US'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount);
};

// Format percentage
export const formatPercentage = (
  value: number,
  decimals = 2,
  locale = 'en-US'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
};

// Format bytes
export const formatBytes = (bytes: number, decimals = 2): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

// Clamp number between min and max
export const clamp = (num: number, min: number, max: number): number => {
  return Math.min(Math.max(num, min), max);
};

// Generate random number between min and max
export const randomBetween = (min: number, max: number): number => {
  return Math.random() * (max - min) + min;
};

// Generate random integer between min and max (inclusive)
export const randomIntBetween = (min: number, max: number): number => {
  return Math.floor(randomBetween(min, max + 1));
};
`;

    fs.writeFileSync(path.join(dir, 'number.ts'), content);
  }

  private createStringUtils(dir: string): void {
    const content = `// Capitalize first letter
export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Convert to title case
export const toTitleCase = (str: string): string => {
  return str
    .toLowerCase()
    .split(' ')
    .map((word) => capitalize(word))
    .join(' ');
};

// Truncate string with ellipsis
export const truncate = (str: string, length: number): string => {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
};

// Generate slug from string
export const slugify = (str: string): string => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

// Generate initials from name
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

// Check if string is empty or whitespace
export const isEmpty = (str: string | null | undefined): boolean => {
  return !str || str.trim().length === 0;
};

// Remove accents from string
export const removeAccents = (str: string): string => {
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
};
`;

    fs.writeFileSync(path.join(dir, 'string.ts'), content);
  }

  private createFormatters(dir: string): void {
    const content = `// Truncate with word boundary
export const truncateWords = (text: string, maxWords: number): string => {
  const words = text.split(' ');
  if (words.length <= maxWords) return text;
  return words.slice(0, maxWords).join(' ') + '...';
};

// Pluralize word
export const pluralize = (count: number, word: string, pluralForm?: string): string => {
  if (count === 1) return \`1 \${word}\`;
  return \`\${count} \${pluralForm || word + 's'}\`;
};

// Mask sensitive data (e.g., email, credit card)
export const maskEmail = (email: string): string => {
  const [username, domain] = email.split('@');
  const maskedUsername = username.slice(0, 2) + '***';
  return \`\${maskedUsername}@\${domain}\`;
};

export const maskCreditCard = (cardNumber: string): string => {
  return '**** **** **** ' + cardNumber.slice(-4);
};

export const maskPhoneNumber = (phone: string): string => {
  return phone.replace(/(\d{3})\d{3}(\d{4})/, '\$1***\$2');
};
`;

    fs.writeFileSync(path.join(dir, 'formatters.ts'), content);
  }

  private createIndex(dir: string): void {
    const content = `export * from './validators';
export * from './storage';
export * from './date';
export * from './number';
export * from './string';
export * from './formatters';
`;

    fs.writeFileSync(path.join(dir, 'index.ts'), content);
  }
}

const generator = new UtilsGenerator();
generator.generate('./src');
