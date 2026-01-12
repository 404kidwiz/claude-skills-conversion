# Extended Subagent Skills Catalog

This document catalogs the 300+ additional subagents identified for potential conversion to Agent Skills format, organized by category and priority.

## Overview

**Currently Converted:** 9 core subagents
**Remaining to Convert:** 300+ subagents across multiple collections

## Conversion Priority Matrix

### Priority 1: Core Utility (High Value)

These agents provide foundational capabilities used across most development workflows.

| Agent | Description | Tools | Rationale |
|-------|-------------|-------|------------|
| **code-reviewer** | Quality-focused code review with security focus | Read, Grep, Glob | Critical for all development |
| **debugger** | Advanced debugging and root cause analysis | Read, Grep, Glob | Common bottleneck in workflows |
| **refactoring-specialist** | Code refactoring and design patterns | Read, Write, Edit, Bash, Glob, Grep | Improves codebase quality |
| **dependency-manager** | Package management and supply chain security | Read, Write, Edit, Bash, Glob, Grep | Critical for modern projects |

### Priority 2: Language Specialists (High Frequency)

23 language-specific agents covering major frameworks and technologies.

#### JavaScript/TypeScript Ecosystem
| Agent | Expertise | Use Cases |
|-------|-----------|------------|
| **javascript-pro** | Modern ES2023+, Node.js, Bun, async patterns | Vanilla JS, Node.js backends |
| **typescript-pro** | TypeScript 5+ patterns, generics, utility types | Type-safe JS projects |
| **react-specialist** | React 18+, Next.js, Zustand, TanStack Query | React apps and libraries |
| **nextjs-developer** | Next.js 14+, App Router, Server Actions | Full-stack React apps |
| **vue-expert** | Vue 3 Composition API, Pinia, Nuxt | Vue.js applications |

#### Backend Languages
| Agent | Expertise | Use Cases |
|-------|-----------|------------|
| **python-pro** | Python 3.11+, type hints, async, FastAPI | Python backends, data science |
| **golang-pro** | Go 1.21+, goroutines, channels, stdlib | High-performance services |
| **java-architect** | Java 21, Spring Boot 3, Jakarta EE | Enterprise Java applications |
| **spring-boot-engineer** | Spring Boot 3+, Spring Cloud, Kubernetes | Spring-based microservices |
| **dotnet-core-expert** | .NET 8 cross-platform, MAUI, EF Core | C#/.NET applications |
| **rust-engineer** | Rust async, ownership, FFI, WebAssembly | Systems programming, WASM |

#### Mobile & Specialized
| Agent | Expertise | Use Cases |
|-------|-----------|------------|
| **flutter-expert** | Flutter 3+, Dart, Firebase, platform channels | Cross-platform mobile |
| **kotlin-specialist** | Kotlin 2.0, KMP, Coroutines, Ktor | Android development |
| **swift-expert** | iOS/macOS, SwiftUI, Combine, concurrency | Apple platforms |

#### Other Languages
- **cpp-pro** - C++20, modern features, performance optimization
- **csharp-developer** - .NET 8, C# 12, ASP.NET Core, EF Core
- **php-pro** - PHP 8.2+, modern patterns, Composer
- **ruby-on-rails** - Ruby on Rails, Hotwire, Turbo, Stimulus
- **laravel-specialist** - Laravel 10+, PHP 8.2, Eloquent, Livewire

### Priority 3: Infrastructure & DevOps (Critical Foundation)

11 agents covering cloud, databases, and operations.

| Agent | Focus | Tools | Rationale |
|-------|-------|-------|------------|
| **cloud-architect** | AWS/Azure/GCP, multi-cloud, cost optimization | Read, Write, Edit, Bash, Glob, Grep | Cloud deployment strategy |
| **kubernetes-specialist** | K8s orchestration, Helm, operators | Read, Write, Edit, Bash, Glob, Grep | Container orchestration |
| **deployment-engineer** | CI/CD, Docker, Kubernetes, GitOps | Read, Write, Edit, Bash, Glob, Grep | Deployment automation |
| **database-administrator** | PostgreSQL/MySQL, HA, backup, monitoring | Read, Write, Edit, Bash, Glob, Grep | Database management |
| **sre-engineer** | Site reliability, SLOs, error budgets | Read, Write, Edit, Bash, Glob, Grep | Production reliability |
| **devops-engineer** | CI/CD automation, IaC, monitoring, SRE | Read, Write, Edit, Bash, Glob, Grep | DevOps workflows |

### Priority 4: Quality & Security (Compliance Critical)

13 agents focused on code quality, security, and compliance.

| Agent | Specialty | Tools | Rationale |
|-------|-----------|-------|------------|
| **security-auditor** | Security vulnerabilities, OWASP | Read, Grep, Glob | Security review |
| **accessibility-tester** | WCAG 2.1 AA compliance, A11y audits | Read, Grep, Glob | Accessibility compliance |
| **penetration-tester** | Ethical hacking, vulnerability assessment | Read, Grep, Glob | Security testing |
| **performance-engineer** | Performance optimization, profiling | Read, Grep, Glob | Performance review |
| **compliance-auditor** | SOC2, HIPAA, GDPR compliance | Read, Grep, Glob | Regulatory compliance |
| **code-reviewer** | Code quality, security, best practices | Read, Grep, Glob | Quality gate |

### Priority 5: Architecture & Design (Strategic)

Multiple agents focused on system architecture and API design.

| Agent | Focus | Tools | Rationale |
|-------|-------|-------|------------|
| **api-designer** | REST/GraphQL API architect with OpenAPI 3.1 | Read, Write, Edit, Bash, Glob, Grep | API design |
| **microservices-architect** | Distributed systems, service decomposition | Read, Write, Edit, Bash, Glob, Grep | Microservices |
| **backend-developer** | Scalable APIs, database design, auth | Read, Write, Edit, Bash, Glob, Grep | Backend architecture |
| **frontend-developer** | React/Vue/Angular UI/UX, accessibility | Read, Write, Edit, Bash, Glob, Grep | Frontend architecture |
| **ui-designer** | Visual design, design systems, interaction patterns | Read, Write, Edit, Bash, Glob, Grep | UI/UX design |

### Priority 6: Data & AI (Emerging Importance)

13 agents covering data engineering, ML, and AI systems.

| Agent | Focus | Tools | Rationale |
|-------|-------|-------|------------|
| **data-engineer** | ETL/ELT, data lakes, streaming (Spark, Kafka) | Read, Write, Edit, Bash, Glob, Grep | Data pipelines |
| **machine-learning-engineer** | ML systems, TensorFlow, PyTorch | Read, Write, Edit, Bash, Glob, Grep | ML infrastructure |
| **mlops-engineer** | MLOps, model deployment, monitoring | Read, Write, Edit, Bash, Glob, Grep | ML operations |
| **llm-architect** | LLM architecture, RAG, fine-tuning | Read, Write, Edit, Bash, Glob, Grep | LLM integration |
| **data-scientist** | Analytics, ML models, statistical analysis | Read, Write, Edit, Bash, Glob, Grep | Data analysis |
| **database-optimizer** | Query optimization, indexing, performance | Read, Write, Edit, Bash, Glob, Grep | DB performance |

### Priority 7: Developer Experience (Productivity)

9 agents improving developer workflows and tooling.

| Agent | Specialty | Tools | Rationale |
|-------|-----------|-------|------------|
| **git-workflow-manager** | Git workflows, branching strategies | Read, Write, Edit, Bash, Glob, Grep | Git processes |
| **tooling-engineer** | Developer tooling, plugins, extensions | Read, Write, Edit, Bash, Glob, Grep | Custom tools |
| **cli-developer** | CLI tools, click, argparse, UX | Read, Write, Edit, Bash, Glob, Grep | CLI development |
| **legacy-modernizer** | Legacy code modernization, refactoring | Read, Write, Edit, Bash, Glob, Grep | Tech debt reduction |

### Priority 8: Business & Product (Cross-Domain)

10 agents for product management, business analysis, and documentation.

| Agent | Focus | Tools | Rationale |
|-------|-------|-------|------------|
| **product-manager** | Product strategy, roadmap, prioritization | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch | Product planning |
| **business-analyst** | Requirements, business analysis | Read, Write, Edit, Glob, Grep | Requirements gathering |
| **project-manager** | Project management, delivery | Read, Write, Edit, Glob, Grep | Project coordination |
| **technical-writer** | Technical writing, docs | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch | Documentation |
| **ux-researcher** | UX research, user testing | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch | UX validation |

### Priority 9: Specialized Domains (Niche but Critical)

10 domain-specific agents for specialized requirements.

| Agent | Domain | Tools | Rationale |
|-------|---------|-------|------------|
| **api-documenter** | API documentation (OpenAPI, Swagger) | Read, Write, Edit, Glob, Grep | API docs |
| **blockchain-developer** | Web3, smart contracts, DeFi | Read, Write, Edit, Bash, Glob, Grep | Web3/blockchain |
| **embedded-systems** | Embedded, real-time, RTOS | Read, Write, Edit, Bash, Glob, Grep | Embedded/IoT |
| **fintech-engineer** | Financial tech, trading, compliance | Read, Write, Edit, Bash, Glob, Grep | FinTech |
| **game-developer** | Game development, Unity, Unreal | Read, Write, Edit, Bash, Glob, Grep | Game development |
| **iot-engineer** | IoT, edge computing, sensors | Read, Write, Edit, Bash, Glob, Grep | IoT solutions |
| **payment-integration** | Payment systems (Stripe, PayPal) | Read, Write, Edit, Bash, Glob, Grep | Payment processing |
| **quant-analyst** | Quantitative analysis, finance | Read, Write, Edit, Bash, Glob, Grep | Quant finance |
| **risk-manager** | Risk assessment, management | Read, Write, Edit, Bash, Glob, Grep | Risk analysis |
| **seo-specialist** | SEO, optimization, analytics | Read, Write, Edit, Bash, Glob, Grep | SEO/optimization |

### Priority 10: Meta & Orchestration (Workflow)

8 agents for coordinating work and managing agents.

| Agent | Purpose | Tools | Rationale |
|-------|---------|-------|------------|
| **agent-organizer** | Multi-agent coordinator, team assembly | Read, Write, Edit, Glob, Grep | Agent coordination |
| **workflow-orchestrator** | Complex workflow automation | Read, Write, Edit, Glob, Grep | Workflow automation |
| **task-distributor** | Task allocation, load balancing | Read, Write, Edit, Glob, Grep | Task distribution |
| **knowledge-synthesizer** | Knowledge aggregation, synthesis | Read, Write, Edit, Glob, Grep | Knowledge management |

### Priority 11: Research & Analysis (Information)

6 agents for comprehensive research and analysis.

| Agent | Specialty | Tools | Rationale |
|-------|-----------|-------|------------|
| **research-analyst** | Comprehensive research, synthesis | Read, Grep, Glob, WebFetch, WebSearch | Deep research |
| **search-specialist** | Advanced information retrieval | Read, Grep, Glob, WebFetch, WebSearch | Research queries |
| **trend-analyst** | Trend analysis, forecasting | Read, Grep, Glob, WebFetch, WebSearch | Market trends |
| **competitive-analyst** | Competitive intelligence | Read, Grep, Glob, WebFetch, WebSearch | Competitive analysis |
| **market-researcher** | Market analysis, consumer insights | Read, Grep, Glob, WebFetch, WebSearch | Market research |
| **data-researcher** | Data discovery, analysis | Read, Grep, Glob, WebFetch, WebSearch | Data research |

## Systematic Conversion Strategy

### Phase 1: High-Impact Agents (Immediate)

Convert 20 highest-impact agents first:

**Core Utilities** (4 agents):
- code-reviewer
- debugger
- refactoring-specialist
- dependency-manager

**Top Language Specialists** (8 agents):
- javascript-pro
- typescript-pro
- react-specialist
- python-pro
- golang-pro
- java-architect
- nextjs-developer
- vue-expert

**Critical Infrastructure** (8 agents):
- cloud-architect
- kubernetes-specialist
- deployment-engineer
- database-administrator
- sre-engineer
- devops-engineer
- security-auditor
- performance-engineer

### Phase 2: Language Coverage (Short Term)

Convert remaining language specialists (15 agents):

- Backend languages: spring-boot-engineer, dotnet-core-expert, rust-engineer, cpp-pro
- Mobile: flutter-expert, kotlin-specialist, swift-expert
- Web frameworks: angular-architect, vue-expert, laravel-specialist
- Other: php-pro, rails-expert

### Phase 3: Domain Specialists (Medium Term)

Convert domain-specific agents by priority:

**Quality & Security** (8 agents):
- accessibility-tester
- penetration-tester
- compliance-auditor
- code-reviewer
- qa-expert
- test-automator
- error-detective
- terraform-engineer

**Data & AI** (10 agents):
- data-engineer
- machine-learning-engineer
- mlops-engineer
- llm-architect
- data-scientist
- database-optimizer
- nlp-engineer
- ai-engineer
- ml-engineer
- prompt-engineer

**Architecture & Design** (4 agents):
- api-designer
- microservices-architect
- graphql-architect
- fullstack-developer

### Phase 4: Business & Specialized (Long Term)

Convert business and specialized agents:

**Business & Product** (8 agents):
- product-manager
- business-analyst
- project-manager
- technical-writer
- ux-researcher
- scrum-master
- customer-success-manager
- sales-engineer

**Specialized Domains** (8 agents):
- api-documenter
- blockchain-developer
- embedded-systems
- fintech-engineer
- game-developer
- iot-engineer
- payment-integration
- seo-specialist

**Developer Experience** (5 agents):
- git-workflow-manager
- tooling-engineer
- cli-developer
- legacy-modernizer
- dx-optimizer

### Phase 5: Meta & Orchestration (Long Term)

Convert coordination and research agents:

**Meta & Orchestration** (5 agents):
- agent-organizer
- workflow-orchestrator
- task-distributor
- knowledge-synthesizer
- performance-monitor

**Research & Analysis** (6 agents):
- research-analyst
- search-specialist
- trend-analyst
- competitive-analyst
- market-researcher
- data-researcher

## Conversion Templates

### Language Specialist Template

For converting language-specific agents, use this structure:

```markdown
---
name: [language]-development
description: Expert [language] developer with mastery of [version features], [frameworks], and [ecosystem patterns]. Use when developing [language] applications, working with [common libraries], or needing [language]-specific guidance.
---

# [Language] Development Skill

You are an expert [language] developer with deep knowledge of [version] features, modern patterns, and the [language] ecosystem.

## Core Expertise

### Language Features
- [version] capabilities and syntax
- Type system features
- Standard library usage
- Performance characteristics

### Frameworks & Libraries
- [framework1] - when to use
- [framework2] - use cases
- [library patterns] - common libraries
- Ecosystem best practices

### Development Patterns
- Code organization
- Error handling
- Testing approaches
- Performance optimization
```

### Infrastructure Specialist Template

For converting infrastructure/DevOps agents:

```markdown
---
name: [domain]-infrastructure
description: [domain] specialist with expertise in [cloud platforms], [technologies], and [operational patterns]. Use when designing [domain] architecture, deploying to [platforms], or managing [domain] operations.
---

# [Domain] Infrastructure Skill

You are an expert [domain] engineer with comprehensive knowledge of [platforms], [tools], and operational excellence.

## Core Capabilities

### Platform Expertise
- AWS/Azure/GCP services
- Multi-cloud strategies
- Cost optimization
- Security best practices

### Technologies
- [tool1] patterns and best practices
- [tool2] integration strategies
- [tool3] optimization techniques

### Operational Excellence
- Monitoring and observability
- Incident response
- Capacity planning
- Reliability engineering
```

## Estimations

### Effort Required

- **Phase 1** (20 agents): ~4 hours
- **Phase 2** (15 agents): ~3 hours
- **Phase 3** (22 agents): ~4.5 hours
- **Phase 4** (21 agents): ~4.5 hours
- **Phase 5** (11 agents): ~2.5 hours

**Total Estimated**: ~18.5 hours for 89 high-priority agents

### Full Catalog Conversion

Converting all 300+ agents would require approximately:
- **Time**: ~60+ hours
- **Skill Files**: 300+ SKILL.md files
- **Validation**: Extensive testing across all skills
- **Documentation**: Supporting guides and templates

## Recommendations

### Option 1: Targeted Conversion (Recommended)

Convert 50-100 highest-impact agents first:
- Focus on most commonly used capabilities
- Prioritize infrastructure, security, and language specialists
- Defer niche/specialized agents to later phases
- **Time Investment**: 20-25 hours
- **Coverage**: 80-90% of common use cases

### Option 2: Full Systematic Conversion

Convert all agents using established templates:
- Create agent-specific templates for each category
- Use batch processing for similar agents
- Implement progressive disclosure for complex skills
- **Time Investment**: 60+ hours
- **Coverage**: 100% of documented agents

### Option 3: On-Demand Conversion

Convert agents as needed based on user requests:
- Start with highest-priority agents
- Convert specific agents when users request them
- **Time Investment**: Variable, minimal upfront
- **Coverage**: Expands organically based on needs

## Next Steps

1. **Choose Approach**: Decide between targeted, full, or on-demand conversion
2. **Define Priorities**: Select which agents/categories to convert first
3. **Create Templates**: Develop templates for each agent category
4. **Execute Conversion**: Systematically convert selected agents
5. **Validate Thoroughly**: Test each skill before finalizing
6. **Document Process**: Update conversion guide with learnings

## Resources

All skills should reference:
- Official Anthropic skill documentation
- anthropics/skills repository examples
- Best practices guide in SKILL-VALIDATION-GUIDE.md
- Conversion process in CONVERSION-GUIDE.md

## Summary

- **9 skills completed**: Core utilities (explore, oracle, librarian, etc.)
- **300+ skills remaining**: Organized by priority and category
- **Clear conversion strategy**: 5 phases with time estimates
- **Templates provided**: For language, infrastructure, and specialist agents
- **Multiple options**: Targeted (25h), full (60h), or on-demand conversion

Ready to proceed with systematic conversion based on your priorities and time constraints.
