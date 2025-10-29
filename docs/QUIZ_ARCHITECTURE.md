# Quiz Architecture v2.0

## Overview

Native React-based quiz system replacing external script injection. Focuses on compliance learning with adaptive difficulty and comprehensive telemetry.

## Components

### Frontend (`/frontend/src/features/quiz/`)

```
quiz/
├── QuizModal.tsx           # Main modal component
├── QuizProvider.tsx        # Context provider for quiz state
├── hooks/
│   ├── useQuiz.ts         # Quiz logic hook
│   ├── useQuizTelemetry.ts # Analytics & tracking
│   └── useAdaptiveDifficulty.ts # Difficulty adjustment
├── types/
│   └── quiz.types.ts      # TypeScript definitions
└── components/
    ├── QuizQuestion.tsx   # Individual question display
    ├── QuizProgress.tsx   # Progress indicator
    └── QuizResults.tsx    # Results summary
```

### Backend (`/backend/clausebot_api/routes/`)

```
quiz.py                    # Quiz endpoint (/v1/quiz)
├── QuizResponseItem       # Response model
├── get_quiz()            # Main quiz handler
└── QuizTelemetryItem     # Telemetry model (future)
```

## Data Flow

```mermaid
graph TD
    A[User clicks "Start Quiz"] --> B[QuizModal opens]
    B --> C[Fetch /v1/quiz?count=5]
    C --> D[Display first question]
    D --> E[User selects answer]
    E --> F[Record telemetry]
    F --> G[Show explanation]
    G --> H{More questions?}
    H -->|Yes| I[Next question] --> D
    H -->|No| J[Show results]
    J --> K[Submit completion telemetry]
```

## Types

```typescript
interface QuizItem {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;  // "A", "B", "C", "D"
  category: string;
  clause_ref: string;
  explanation: string;
  source: string;
}

interface QuizSession {
  sessionId: string;
  startTime: number;
  questions: QuizItem[];
  answers: QuizAnswer[];
  score: number;
  difficulty: number;
}

interface QuizTelemetry {
  event: 'quiz_start' | 'quiz_answer' | 'quiz_hint' | 'quiz_complete';
  sessionId: string;
  questionId?: string;
  dwellTime?: number;
  isCorrect?: boolean;
  hintUsed?: boolean;
  reasonCode?: string;
}
```

## Features

### Phase 1 (Week 1) ✅
- [x] Native React modal
- [x] Basic question display
- [x] Answer selection
- [x] Progress tracking
- [x] GA4 integration

### Phase 2 (Week 2)
- [ ] Adaptive difficulty
- [ ] Advanced telemetry
- [ ] Clause citations
- [ ] Wrong-answer taxonomy
- [ ] Performance optimization

### Phase 3 (Weeks 3-4)
- [ ] ClauseGraph integration
- [ ] Clause lookup in explanations
- [ ] Cross-references
- [ ] Verification status

## Adaptive Difficulty Algorithm

```typescript
// Simple rule-based adjustment
const adjustDifficulty = (session: QuizSession) => {
  const recentAnswers = session.answers.slice(-3);
  const correctCount = recentAnswers.filter(a => a.isCorrect).length;
  
  if (correctCount >= 3) {
    session.difficulty = Math.min(session.difficulty + 1, 5);
  } else if (correctCount <= 1) {
    session.difficulty = Math.max(session.difficulty - 1, 1);
  }
};
```

## Telemetry Events

### quiz_start
```json
{
  "event": "quiz_start",
  "sessionId": "uuid",
  "category": "Structural Welding",
  "questionCount": 5,
  "difficulty": 2
}
```

### quiz_answer
```json
{
  "event": "quiz_answer",
  "sessionId": "uuid", 
  "questionId": "rec123",
  "selected": "B",
  "correct": "C",
  "isCorrect": false,
  "dwellTime": 15000,
  "hintUsed": true,
  "reasonCode": "misread_options"
}
```

### quiz_complete
```json
{
  "event": "quiz_complete",
  "sessionId": "uuid",
  "score": 4,
  "total": 5,
  "duration": 180000,
  "difficulty": 3
}
```

## Security

- **CSP**: Strict content security policy prevents script injection
- **Input Validation**: All user inputs sanitized
- **Rate Limiting**: Quiz API rate limited per session
- **Data Privacy**: No PII in telemetry events

## Performance Targets

- **P95 Render**: < 3s on mobile
- **API Response**: < 500ms for /v1/quiz
- **Bundle Size**: Quiz modal < 50KB gzipped
- **Memory Usage**: < 10MB during quiz session

## Monitoring

- **Completion Rate**: Target 70%+ (baseline TBD)
- **Second Attempt Accuracy**: Target +10% improvement
- **Error Rate**: < 1% quiz load failures
- **CSP Violations**: 0 (strict enforcement)

## Rollback Plan

1. **Feature Flag**: `ENABLE_NATIVE_QUIZ` (default: true)
2. **Gradual Rollout**: 10% → 50% → 100% over 3 days
3. **Revert Trigger**: Completion rate drops >20% or error rate >5%
4. **Emergency**: Toggle flag off, investigate, fix, re-enable

## Future Enhancements

- **Offline Mode**: Cache questions for offline use
- **Spaced Repetition**: Resurface missed questions
- **Collaborative**: Team quiz sessions
- **Voice Interface**: Audio questions for accessibility
- **AR Integration**: Visual welding scenarios

---

**Last Updated**: October 25, 2025  
**Status**: Phase 1 Complete, Phase 2 In Progress  
**Owner**: Development Team
