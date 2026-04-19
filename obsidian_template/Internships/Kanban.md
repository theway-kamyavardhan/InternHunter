---
kanban-plugin: basic
---

## To Apply
**Query**: `TABLE without id file.link AS "Company - Role", confidence_score AS "Score" FROM "Internships/Applications" WHERE status = "To Apply"`

## Applied
**Query**: `TABLE without id file.link AS "Company - Role", date_applied AS "Date" FROM "Internships/Applications" WHERE status = "Applied"`

## Follow-up
**Query**: `TABLE without id file.link AS "Company - Role", date_applied AS "Date Applied" FROM "Internships/Applications" WHERE status = "Follow-up"`

## Interview
**Query**: `TABLE without id file.link AS "Company - Role" FROM "Internships/Applications" WHERE status = "Interview"`

## Offer
**Query**: `TABLE without id file.link AS "Company - Role" FROM "Internships/Applications" WHERE status = "Offer"`

## Rejected / Ghosted
**Query**: `TABLE without id file.link AS "Company - Role" FROM "Internships/Applications" WHERE status = "Rejected / Ghosted"`

***

## 📊 Analytics & Health

### Pipeline Health
```dataview
TABLE length(rows) AS "Count"
FROM "Internships/Applications"
GROUP BY status
```

### Win-Rate % (Interviews / Total Applied)
*(Requires DataviewJS for exact % calculation, simple table fallback below)*
```dataview
TABLE length(rows) AS "Total Applications", 
      length(filter(rows, (r) => r.status = "Interview" or r.status = "Offer")) AS "Positive Replies"
FROM "Internships/Applications"
GROUP BY "Overview"
```
