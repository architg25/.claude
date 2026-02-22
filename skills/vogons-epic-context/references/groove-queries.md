# Groove MCP — Cached Schema & Query Reference

Use this file instead of calling `get-type-definition` or `get-available-queries`.
All types and queries needed for epic context gathering are here.

## Vogons Org UUID

```
6d0f330f-73ce-4128-866e-107a88d16b47
```

---

## Relevant Queries

```
epic(id: String) → Epic
epics(first: Int, after: String, filters: EpicFilter) → EpicRelayConnection
epicsCount(filters: EpicFilter) → Count
initiative(id: String) → Initiative
definitionOfDone(id: String) → DefinitionOfDone
organizationUnits(first: Int, filters: OrganizationUnitsFilter) → OrganizationUnitRelayConnection
search(searchText: String, limit: Int, workItemType: WorkItemType) → SearchResult
```

---

## Type Definitions

### Epic

```graphql
type Epic {
  id: String!
  title: String!
  description: String
  ownerEmail: String
  owner: User
  contributionRequestId: String
  contributionRequest: ContributionRequest
  definitionOfDoneId: String
  definitionOfDone: DefinitionOfDone
  status: EpicStatus! # BACKLOG | IN_PROGRESS | DONE | CANCELLED
  tags: [String!]
  jiraIssueKey: String
  orgId: String
  org: OrganizationUnit
  createdTime: DateTime!
  updatedTime: DateTime!
  deleted: Boolean
  startDate: Date
  dueDate: Date
  remoteLinks: [Link!]
  risks: [Risk!]
  openRisksCount: Int!
  milestones: [Milestone!]
  latestAnnotation: WorkItemAnnotation
  annotations: [WorkItemAnnotation!]
  tasks: [Task!]
  scopeChanges: [ScopeChange!]
}
```

### EpicFilter

```graphql
input EpicFilter {
  id: String
  title: String
  description: String
  status: [EpicStatus]
  tags: [String]
  org: [String] # UUIDs only
  indirectOrgs: [String] # UUIDs only — hierarchical lookup
  directOrgs: [String] # UUIDs only
  owner: [String] # deprecated, use owners
  owners: [String]
  parentInitiative: [String]
  parentInitiativeId: [String]
  parentDod: [String]
  parentDodId: [String]
  deleted: [Boolean]
  jiraIssueKey: String # plain string, not a list
  startDate: DateRange
  dueDate: DateRange
  annotationStatus: [WorkItemAnnotationStatus]
  periodIds: [String]
  priority: [PriorityState]
  dodPriority: [DefinitionOfDonePriority]
  definitionOfDoneIds: [String]
  contributionRequestIds: [String]
  riskCountFilter: RiskCountFilter
}
```

### DefinitionOfDone

```graphql
type DefinitionOfDone {
  id: String!
  title: String!
  description: String!
  ownerEmail: String!
  priority: DefinitionOfDonePriority! # NO_DOD_PRIORITY | must | could | should
  owner: User
  orgId: String!
  org: OrganizationUnit
  additionalOrgs: [OrganizationUnit!]
  initiative: Initiative!
  initiativeId: String!
  tags: [String!]
  externalLinks: [Link!]
  createdTime: DateTime!
  updatedTime: DateTime!
  deleted: Boolean
  epics(filters: EpicFilter): [Epic!]
  epicsStatus: StatusCounts
  contributionRequests: [ContributionRequest!]
  status: DefinitionOfDoneStatus! # IN_PLANNING | UNCOMMITTED | COMMITTED | IN_PROGRESS | CANCELLED | COMPLETED
  risks: [Risk!]
  openRisksCount: Int!
  startDate: Date
  dueDate: Date
  milestones: [Milestone!]
  latestAnnotation: WorkItemAnnotation
  annotations: [WorkItemAnnotation!]
  scopeChanges: [ScopeChange!]
}
```

### Initiative

```graphql
type Initiative {
  id: String!
  title: String!
  description: String!
  orgId: String!
  org: OrganizationUnit
  additionalOrgs: [OrganizationUnit!]
  priority: String!
  tags: [String!]
  externalLinks: [Link!]
  definitionsOfDone(filters: DefinitionOfDoneFilter): [DefinitionOfDone!]
  createdTime: DateTime!
  updatedTime: DateTime!
  deleted: Boolean
  ownerEmail: String!
  owner: User
  status: InitiativeStatus! # IN_PLANNING | READY_FOR_DELIVERY | IN_PROGRESS | CANCELLED | COMPLETED
  definitionsOfDoneStatus: StatusCounts
  epicsStatus: StatusCounts
  risks: [Risk!]
  openRisksCount: Int!
  startDate: Date
  dueDate: Date
  milestones: [Milestone!]
  latestAnnotation: WorkItemAnnotation
  annotations: [WorkItemAnnotation!]
  scopeChanges: [ScopeChange!]
}
```

### Supporting Types

```graphql
type Task {
  id: String!
  title: String!
  description: String
  assigneeEmail: String
  assignee: User
  status: TaskStatus! # TODO | IN_PROGRESS | IN_REVIEW | DONE
  epicId: String
  createdTime: DateTime!
  updatedTime: DateTime!
  deleted: Boolean
}

type Milestone {
  id: String!
  title: String!
  description: String
  dueDate: Date!
  owner: User
  ownerEmail: String!
  tags: [String!]
  createdTime: DateTime!
  updatedTime: DateTime!
  deleted: Boolean
}

type Risk {
  id: String!
  description: String! # NOTE: no "title" field
  status: RiskStatus! # OPEN | CLOSED
  category: RiskCategory! # FYA | FYI | FYI_E_TEAM | FYA_E_TEAM
  responsibleOwnerEmail: String!
  responsibleOwner: User
  parentWorkItemId: String
  tags: [String!]
  priorityState: String
  resolution: String
  createdTime: DateTime!
  updatedTime: DateTime!
  deleted: Boolean
}

type WorkItemAnnotation {
  id: String!
  status: WorkItemAnnotationStatus! # UNSET | ON_TRACK | AT_RISK | OFF_TRACK
  description: String! # NOTE: not "comment"
  createdTime: DateTime! # NOTE: no "updatedTime"
  deletedTime: DateTime
  authorEmail: String!
  author: User
}

type Link {
  id: String
  name: String!
  link: String!
}

type StatusCounts {
  backlog: Int!
  inProgress: Int!
  done: Int!
}

type User {
  firstName: String!
  lastName: String!
  fullName: String!
  email: String!
  username: String!
  isActive: Boolean!
  title: String
  slackUserId: String
}

type OrganizationUnit {
  id: String!
  orgType: OrgType!
  parentOrgId: String
  parentOrg: OrganizationUnit
  name: String!
  description: String
  isArchived: Boolean!
  jiraProjectKey: String
  slackChannel: String
}
```

### Organization Search Filter

```graphql
input OrganizationUnitsFilter {
  name: SearchByTerm # { searchByTerm: "vogons" }
  types: [OrgType]
  includeArchived: Boolean
  indirectOrgs: [String]
}

input SearchByTerm {
  searchByTerm: String!
}
```

---

## Copy-Paste Query Templates

### Find Epic by Jira Key

```graphql
{
  epics(first: 5, filters: { jiraIssueKey: "CONACCESS-5", deleted: [false] }) {
    edges {
      node {
        id
        title
        description
        status
        ownerEmail
        owner {
          fullName
        }
        startDate
        dueDate
        jiraIssueKey
        definitionOfDoneId
      }
    }
  }
}
```

### Full Epic → DoD → Initiative Chain

```graphql
{
  epic(id: "EPIC-62187") {
    id
    title
    description
    status
    ownerEmail
    owner {
      fullName
    }
    startDate
    dueDate
    jiraIssueKey
    definitionOfDoneId
    definitionOfDone {
      id
      title
      description
      status
      priority
      owner {
        fullName
      }
      startDate
      dueDate
      tags
      initiative {
        id
        title
        description
        status
        owner {
          fullName
        }
        startDate
        dueDate
        tags
      }
      epics(
        filters: {
          indirectOrgs: ["6d0f330f-73ce-4128-866e-107a88d16b47"]
          deleted: [false]
        }
      ) {
        id
        title
        status
        owner {
          fullName
        }
        jiraIssueKey
      }
    }
    tasks {
      id
      title
      status
    }
    milestones {
      id
      title
      description
      dueDate
    }
    risks {
      id
      description
      status
      category
    }
    latestAnnotation {
      status
      description
      createdTime
      author {
        fullName
      }
    }
  }
}
```

### List Vogons Epics

```graphql
{
  epics(
    first: 50
    filters: {
      indirectOrgs: ["6d0f330f-73ce-4128-866e-107a88d16b47"]
      deleted: [false]
    }
  ) {
    edges {
      node {
        id
        title
        status
        ownerEmail
        owner {
          fullName
        }
        startDate
        dueDate
        jiraIssueKey
      }
    }
  }
}
```

---

## Common Pitfalls (DO NOT make these mistakes)

- `org` / `indirectOrgs` / `directOrgs` filters require **UUIDs**, never names
- `EpicFilter.jiraIssueKey` is a **plain String**, not a list
- `DefinitionOfDone` has **no `periods` field**
- `Milestone` has **no `status` field**
- `Risk` has **no `title` or `severity` field** — use `description` and `category`
- `WorkItemAnnotation` uses `description` (not `comment`) and `createdTime` (no `updatedTime`)
- `deleted` filter takes `[Boolean]` (a list), e.g. `deleted: [false]`

## Extracting Google Doc IDs from Descriptions

Groove/Jira descriptions contain doc links in two formats:

- Jira markup: `[link text|https://docs.google.com/document/d/DOC_ID/edit...]`
- Plain URLs: `https://docs.google.com/document/d/DOC_ID/edit...`

Extract DOC_ID = segment between `/d/` and the next `/`.
