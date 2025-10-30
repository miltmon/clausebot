# 🧠 Beads Agent Memory Endpoints

Quick reference for frontend/dashboard integration with copy-paste examples.

## Core Endpoints

### Get Ready Work
```bash
GET /v1/agent/memory/ready?limit=10&sort=hybrid&category=Structural%20Welding
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "task": {
        "id": "cb-1",
        "title": "Update AWS D1.1:2025 references in Module 1",
        "priority": 1,
        "task_type": "aws_update",
        "status": "pending",
        "category": "Structural Welding"
      },
      "priority_score": 10.5,
      "age_hours": 2.3
    }
  ],
  "message": "Found 1 ready work items"
}
```

### Create Task
```bash
POST /v1/agent/memory/task
Content-Type: application/json

{
  "title": "Fix missing explanation in question Q042",
  "description": "Question Q042 lacks proper explanation for AWS clause reference",
  "priority": 2,
  "task_type": "content_review",
  "category": "Structural Welding",
  "labels": ["content", "explanation"]
}
```

### Get Statistics
```bash
GET /v1/agent/memory/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_tasks": 15,
    "ready_tasks": 8,
    "blocked_tasks": 3,
    "dependencies": 5
  }
}
```

### Batch Create Tasks
```bash
POST /v1/agent/memory/tasks/batch
Content-Type: application/json

{
  "tasks": [
    {
      "title": "Validate question difficulty for Q043",
      "task_type": "question_validation",
      "priority": 2,
      "category": "Structural Welding"
    }
  ],
  "source": "agent_discovery",
  "session_id": "session-001"
}
```

## Quiz Integration

### Get Quiz Ready Work
```bash
GET /v1/quiz/ready?format=json&limit=5
```

### Batch Validate Questions
```bash
POST /v1/quiz/batch-validate
Content-Type: application/json

{
  "question_ids": ["Q001", "Q002", "Q003"],
  "category": "Structural Welding",
  "session_id": "validation-session-001"
}
```

**Response:**
```json
{
  "total_validated": 3,
  "valid_count": 2,
  "invalid_count": 1,
  "tasks_created": ["cb-4"]
}
```

## Dashboard Widget Examples

### Ready Work Widget
```javascript
// Fetch ready work for dashboard
const response = await fetch('/v1/agent/memory/ready?limit=5&sort=hybrid');
const { data: readyItems } = await response.json();

// Display in UI
readyItems.forEach(item => {
  console.log(`${item.task.title} (Score: ${item.priority_score})`);
});
```

### Stats Widget
```javascript
// Get memory statistics
const statsResponse = await fetch('/v1/agent/memory/stats');
const { data: stats } = await statsResponse.json();

// Update dashboard counters
document.getElementById('ready-count').textContent = stats.ready_tasks;
document.getElementById('blocked-count').textContent = stats.blocked_tasks;
```

### Task Creation Form
```javascript
// Create task from form
const taskData = {
  title: document.getElementById('task-title').value,
  description: document.getElementById('task-description').value,
  priority: parseInt(document.getElementById('priority').value),
  task_type: document.getElementById('task-type').value,
  category: document.getElementById('category').value
};

const response = await fetch('/v1/agent/memory/task', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(taskData)
});

const result = await response.json();
if (result.success) {
  console.log('Task created:', result.data.id);
}
```

## Error Handling

All endpoints return consistent error format:
```json
{
  "success": false,
  "data": null,
  "message": "Error description"
}
```

## Feature Flag

All agent memory functionality is controlled by `AGENT_MEMORY_ENABLED` environment variable:
- `true`: Full functionality enabled
- `false`: Endpoints return empty/disabled responses

Check feature status:
```javascript
const statsResponse = await fetch('/v1/agent/memory/stats');
if (statsResponse.status === 200) {
  // Agent memory is enabled
} else {
  // Feature disabled or error
}
```
