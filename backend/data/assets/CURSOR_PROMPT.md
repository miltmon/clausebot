# Foundation Track - Cursor Implementation Prompt

**Copy-paste this prompt into Cursor for immediate scaffolding:**

---

Build Foundation Track pages in Next.js + Supabase using the schema from our canvas doc.

## Pages to Create:
- `/foundation-track` (overview)
- `/foundation-track/module/[slug]` (module outline)
- `/foundation-track/lesson/[id]` (lesson/quest/quiz renderer)

## Core Requirements:
1. **Enrollment Gating**: Check `public.enrollments` for `product='foundation_track'` AND `status='active'`
2. **Content Rendering**:
   - Lesson markdown → HTML
   - Quest JSON → Triad format (Interpret→Navigate→Apply)
   - Quiz → QuizEngine with score + rationale
3. **Progress Tracking**: Write to `public.progress` and mirror XP to `xp_events`
4. **Mobile-First**: Tailwind tokens, responsive at 375px
5. **Components**: Keep minimal, reusable

## Database Schema:
```sql
-- Use the foundation_track_schema.sql file provided
-- Tables: courses, modules, lessons, quiz_questions, enrollments, progress, xp_events
```

## Key Features:
- **You-Are-Here Map**: Visual progress indicator
- **QuizEngine**: 25min timer, 80% pass threshold, detailed explanations
- **Quest Triad**: Step-by-step scenario-based learning
- **XP System**: Reward completion, track leaderboard
- **Checkout Integration**: Link to `/api/checkout/session`

## Environment Variables Needed:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE=your_service_role_key
```

## Acceptance Criteria:
- ✅ Module pages render with lesson list
- ✅ Enrollment gate shows pricing tiers ($197/$297)
- ✅ Quiz engine: timer, scoring, explanations with "(verify)" anchors
- ✅ Quest renderer: 3-step Triad format
- ✅ Progress writes to Supabase on completion
- ✅ Mobile responsive (375px breakpoint)
- ✅ No code quotes in content - use "(verify)" anchors only

## Component Files Provided:
- `foundation_track_pages.tsx` - Main overview page
- `quiz_engine.tsx` - Complete quiz implementation
- `quest_renderer.tsx` - Triad quest format
- `foundation_track_schema.sql` - Database setup

## Next Steps:
1. Run SQL schema in Supabase
2. Set environment variables
3. Import components into your Next.js app
4. Create API routes for checkout integration
5. Test enrollment flow end-to-end

**Goal**: Ship playable Modules 1-2 with gated enrollment in 48 hours.
