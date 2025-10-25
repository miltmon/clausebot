# Contributing to ClauseBot.Ai

Thank you for your interest in contributing to ClauseBot.Ai! This guide will help you get started with development, understand our standards, and successfully contribute to the project.

## 🎯 Ways to Contribute

- 🐛 **Report bugs** - Help us identify issues
- 💡 **Suggest features** - Share ideas for improvements
- 📝 **Improve documentation** - Help others understand the project
- 🎨 **Design improvements** - Enhance UI/UX
- 💻 **Code contributions** - Fix bugs and add features
- 🧪 **Testing** - Help ensure quality
- 🌐 **Translations** - Make ClauseBot.Ai multilingual (future)

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **npm** 9+ (comes with Node.js)
- **Git** ([Download](https://git-scm.com/))
- **Code Editor** (VS Code recommended)

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Click "Fork" button on GitHub
   # Then clone your fork
   git clone https://github.com/YOUR-USERNAME/clausebot-ai.git
   cd clausebot-ai
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Set Up Environment Variables**
   ```bash
   # Copy example env file
   cp .env.example .env.local
   
   # Edit .env.local with your values
   VITE_API_BASE_URL=https://clausebot-api.onrender.com
   VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   ```

5. **Open Browser**
   ```
   http://localhost:5173
   ```

### Project Structure

```
clausebot-ai/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── ui/         # shadcn/ui components
│   │   └── ...         # Feature components
│   ├── pages/          # Route pages
│   ├── hooks/          # Custom hooks
│   ├── services/       # API services
│   ├── lib/            # Utilities
│   └── types/          # TypeScript types
├── docs/               # Documentation
└── ...config files
```

## 💻 Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/doc-name` - Documentation updates

### Creating a Feature Branch

```bash
# Update your local main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write Code**
   - Follow code standards (see below)
   - Write clean, readable code
   - Add comments where necessary
   - Update types as needed

2. **Test Locally**
   ```bash
   # Run dev server
   npm run dev
   
   # Build for production
   npm run build
   
   # Preview production build
   npm run preview
   ```

3. **Commit Changes**
   ```bash
   # Stage changes
   git add .
   
   # Commit with descriptive message
   git commit -m "feat: add user authentication"
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
feat(auth): add user login functionality
fix(api): resolve timeout issue with answer verification
docs(readme): update installation instructions
style(button): improve hover state styling
refactor(hooks): simplify useOfflineCapability logic
```

### Pushing Changes

```bash
# Push to your fork
git push origin feature/your-feature-name
```

### Creating a Pull Request

1. Go to GitHub repository
2. Click "Pull Requests" → "New Pull Request"
3. Select your branch
4. Fill in PR template:
   - **Title**: Clear, descriptive title
   - **Description**: What and why
   - **Screenshots**: For UI changes
   - **Testing**: How you tested
   - **Checklist**: Complete checklist

5. Submit PR

## 📋 Code Standards

### TypeScript

```typescript
// ✅ Good
interface User {
  id: string;
  name: string;
  email: string;
}

function getUser(id: string): Promise<User> {
  return fetch(`/api/users/${id}`).then(r => r.json());
}

// ❌ Bad
function getUser(id: any): any {
  return fetch(`/api/users/${id}`).then(r => r.json());
}
```

### React Components

```typescript
// ✅ Good - Functional component with TypeScript
import { useState } from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function Button({ label, onClick, disabled = false }: ButtonProps) {
  return (
    <button 
      onClick={onClick} 
      disabled={disabled}
      className="px-4 py-2 bg-primary text-white rounded"
    >
      {label}
    </button>
  );
}

// ❌ Bad - No types, inline styles
export function Button(props) {
  return (
    <button 
      onClick={props.onClick}
      style={{ padding: '8px 16px', background: '#1976D2' }}
    >
      {props.label}
    </button>
  );
}
```

### Styling with Tailwind

```typescript
// ✅ Good - Use Tailwind classes, semantic tokens
<div className="bg-background text-foreground p-6 rounded-lg">
  <h2 className="text-2xl font-bold text-primary">Title</h2>
  <Button variant="default">Click Me</Button>
</div>

// ❌ Bad - Inline styles, hardcoded colors
<div style={{ backgroundColor: '#fff', color: '#000', padding: '24px' }}>
  <h2 style={{ fontSize: '24px', color: '#1976D2' }}>Title</h2>
  <button style={{ background: '#1976D2' }}>Click Me</button>
</div>
```

### File Organization

```typescript
// ✅ Good - Organized imports
// 1. External libraries
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Internal components
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// 3. Hooks and utilities
import { useClausebotApi } from '@/hooks/useClauesbotApi';
import { cn } from '@/lib/utils';

// 4. Types
import type { Answer } from '@/services/clausebotApi';

// ❌ Bad - Mixed order, no grouping
import { cn } from '@/lib/utils';
import { useState } from 'react';
import type { Answer } from '@/services/clausebotApi';
import { Button } from '@/components/ui/button';
```

### Error Handling

```typescript
// ✅ Good - Proper error handling
async function fetchAnswer(question: string) {
  try {
    const response = await clausebotApi.verifyAnswer({
      question,
      intent: 'clause_lookup',
      mode: 'audit'
    });
    return response;
  } catch (error) {
    console.error('Failed to fetch answer:', error);
    toast.error('Failed to get answer. Please try again.');
    return null;
  }
}

// ❌ Bad - No error handling
async function fetchAnswer(question: string) {
  const response = await clausebotApi.verifyAnswer({
    question,
    intent: 'clause_lookup',
    mode: 'audit'
  });
  return response;
}
```

## 🧪 Testing

### Manual Testing

1. **Feature Testing**
   - Test all new functionality
   - Test edge cases
   - Test error states
   - Test loading states

2. **Browser Testing**
   - Chrome (latest)
   - Firefox (latest)
   - Safari (latest)
   - Edge (latest)

3. **Device Testing**
   - Desktop (1920x1080, 1366x768)
   - Tablet (768x1024)
   - Mobile (375x667, 414x896)

4. **PWA Testing**
   - Install as PWA
   - Test offline mode
   - Test service worker
   - Test cache

### Unit Tests (Future)

```typescript
// Example test structure
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct label', () => {
    render(<Button label="Click Me" onClick={() => {}} />);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button label="Click" onClick={handleClick} />);
    screen.getByText('Click').click();
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

## 📝 Documentation

### Code Comments

```typescript
/**
 * Verifies an answer to a welding code question with citations
 * 
 * @param request - The verification request containing question and parameters
 * @returns Promise resolving to Answer with verdict and citations
 * @throws Error if API request fails
 * 
 * @example
 * ```typescript
 * const answer = await verifyAnswer({
 *   question: "What is the undercut limit?",
 *   intent: "clause_lookup",
 *   mode: "audit"
 * });
 * ```
 */
async function verifyAnswer(request: VerifyAnswerRequest): Promise<Answer> {
  // Implementation
}
```

### Component Documentation

```typescript
/**
 * Button Component
 * 
 * A reusable button component with multiple variants and states
 * 
 * @component
 * @example
 * ```tsx
 * <Button 
 *   variant="default" 
 *   size="lg"
 *   onClick={() => console.log('clicked')}
 * >
 *   Click Me
 * </Button>
 * ```
 */
export function Button({ variant, size, children, ...props }: ButtonProps) {
  // Implementation
}
```

## 🎨 UI/UX Guidelines

### Design Principles

1. **Consistency** - Use design system tokens
2. **Accessibility** - WCAG 2.1 AA compliance
3. **Responsiveness** - Mobile-first approach
4. **Performance** - Optimize for speed
5. **Clarity** - Clear visual hierarchy

### Accessibility

```typescript
// ✅ Good - Accessible
<button
  aria-label="Close dialog"
  onClick={onClose}
  className="..."
>
  <X className="h-4 w-4" />
</button>

// ❌ Bad - Not accessible
<div onClick={onClose}>
  <X />
</div>
```

### Responsive Design

```typescript
// ✅ Good - Mobile-first responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>

// ❌ Bad - Desktop-only
<div className="grid grid-cols-3 gap-4">
  {/* Content */}
</div>
```

## 🔍 Code Review Process

### What We Look For

1. **Functionality** - Does it work as intended?
2. **Code Quality** - Is it clean and maintainable?
3. **Performance** - Is it optimized?
4. **Security** - Are there vulnerabilities?
5. **Testing** - Is it properly tested?
6. **Documentation** - Is it well-documented?

### Review Timeline

- **Initial Review**: Within 2-3 business days
- **Follow-up**: Within 1-2 business days
- **Final Approval**: After all feedback addressed

## 🐛 Reporting Issues

### Bug Reports

Use the bug report template and include:

1. **Description** - Clear description of the bug
2. **Steps to Reproduce** - Detailed steps
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Screenshots** - Visual evidence
6. **Environment** - Browser, OS, device
7. **Console Logs** - Any error messages

### Feature Requests

Use the feature request template and include:

1. **Problem Statement** - What problem does this solve?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other solutions considered
4. **Additional Context** - Screenshots, mockups

## 📞 Getting Help

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and discussions
- **Discord** - Real-time chat (coming soon)
- **Email** - team@clausebot.ai

### Response Times

- **Critical Bugs**: Within 24 hours
- **Bug Reports**: Within 2-3 days
- **Feature Requests**: Within 1 week
- **General Questions**: Within 3-5 days

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Invited to private beta features
- Considered for team positions

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to ClauseBot.Ai!** 🙏

Your contributions help welding professionals worldwide work more efficiently and safely.

---

**Last Updated**: 2025-01-18  
**Maintained By**: ClauseBot.Ai Team
