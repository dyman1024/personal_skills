---
name: technical-research-explainer
description: 调研、梳理、比较或解释技术主题、现有架构、既有技术方案、RFC、标准、论文与行业实践，使用可追溯证据、受控术语、事实与推断分离、机制与流程说明、同维度比较和明确的不确定性产出技术调研或解读。用户要求“技术调研”“方案调研”“技术选型比较”“解释或介绍现有技术方案、架构、RFC、论文”时使用；要求创建、重构、评审改进或落地新技术方案时改用 write-technical-solution，简单概念问答或纯代码修改时不要使用。
---

# Technical Research and Explanation

## Core boundary

- Research and explain before recommending. Preserve the source design and its original intent.
- Do not silently turn an explanation of an existing design into a new design proposal.
- Use `write-technical-solution` when the requested outcome is a new design, a substantial redesign, an implementation RFC, or a rollout plan. If a request contains both research and design, complete the evidence-based research first and use its findings as design inputs.
- Scale the work to the request. Do not force a full report onto a simple explanation.
- Write in the user's language unless the target document requires another language.

## Required writing guidance

Before drafting the deliverable, read [references/controlled-technical-writing.md](references/controlled-technical-writing.md) completely and apply it. Use it as a controlled-language guide, not as a claim of formal ASD-STE100 compliance.

## Workflow

### 1. Define the research contract

Identify:

- the target readers and what they need to understand or decide;
- the primary question and explicitly excluded questions;
- the required depth, output format, and time horizon;
- whether the task is research, explanation, comparison, or a combination;
- whether current information, direct quotations, or source citations are required.

Ask only when a missing answer would materially change the research direction. Otherwise, use the smallest reasonable assumption and label it.

### 2. Build the evidence base

Use the sources appropriate to the task:

1. Read user-provided artifacts first.
2. For repository-backed explanations, inspect applicable instructions, documentation, code, tests, configuration, schemas, and history. Distinguish implemented behavior from documented intent.
3. Browse when the user requests current information or citations, when facts are time-sensitive, or when the topic is niche enough that memory is unreliable.
4. Prefer primary evidence: official documentation, standards, RFCs, research papers, source code, release notes, and maintainers' statements. Use secondary sources to understand terminology or the broader landscape.
5. Use Wikipedia for orientation and terminology discovery, not as the sole authority for material technical claims when primary sources are available.

For each material conclusion, know whether it is:

- a sourced fact;
- an inference from one or more sources;
- a recommendation;
- an assumption;
- unknown or disputed.

Record the relevant version, release, publication date, or “as of” date when it affects the result. Cite sources near the claims they support. Do not provide an undifferentiated source dump.

### 3. Establish terminology and a mental model

- Define the small set of terms needed to understand the topic.
- Use one preferred term for each concept and preserve names from authoritative sources, code, interfaces, and diagrams.
- Start with a concise mental model: what the subject is, what problem it addresses, and how its main parts relate.
- Introduce detail in dependency order. Explain prerequisites before dependent mechanisms.
- Use a diagram only when relationships, sequence, state, or comparison are materially clearer visually.

### 4. Select an output mode

#### Technical research

Use this default structure and remove sections that do not add information:

```markdown
# <Research topic>

## Conclusion summary
## Research questions and scope
## Terminology and mental model
## Current landscape or background
## Core mechanisms
## Approaches and trade-offs
## Findings and implications
## Limitations, disputes, and open questions
```

Describe what is established before presenting an interpretation. Explain why approaches differ and under which constraints each approach is appropriate.

#### Existing design or architecture explanation

Explain in this order when applicable:

1. purpose, context, and boundary;
2. overall architecture and primary responsibility split;
3. core runtime or data flow;
4. important modules, interfaces, states, and persisted data;
5. original decisions and their trade-offs;
6. reliability, security, performance, and observability characteristics;
7. limitations, risks, and unresolved questions.

Separate “what the design does” from “how well it works.” If evidence is insufficient to reconstruct a design decision, mark the rationale as unknown instead of inventing one.

#### Technical comparison

- State the decision context before listing options.
- Compare all options with the same criteria.
- Separate observed properties from environment-dependent judgments.
- Give a conditional conclusion: which option fits which constraints and why.
- Do not convert popularity into technical superiority.

Suggested comparison dimensions include correctness, compatibility, maturity, operational complexity, performance, security, ecosystem, cost, migration effort, and reversibility. Use only dimensions relevant to the question.

### 5. Explain mechanisms and flows

- Trace inputs, transformations, state changes, outputs, and failure paths.
- Name the actor for each important action.
- Put conditions before the actions or results that depend on them.
- Separate the normal path from exceptions, retries, timeouts, degradation, and recovery.
- When explaining code, link claims to concrete files and line locations. Do not infer runtime behavior from names alone.
- When explaining an external standard or paper, separate the source's claims from later implementations and your interpretation.

### 6. Conclude without overreaching

- Lead with the answer to the user's primary question.
- State what the evidence establishes, what remains uncertain, and what would resolve the uncertainty.
- Include implications or next questions when useful, but do not add an unsolicited implementation plan.
- If the evidence supports a design recommendation and the user wants a new proposal, hand the findings to `write-technical-solution` rather than extending this workflow into a design document.

## Quality gate

Before delivery, verify:

- [ ] The output answers a defined research or explanation question.
- [ ] Material current or niche claims use appropriate primary evidence.
- [ ] Facts, source claims, inferences, recommendations, assumptions, and unknowns are distinguishable.
- [ ] The explanation preserves the existing design instead of silently redesigning it.
- [ ] Terminology is defined, stable, and consistent with sources and implementation.
- [ ] The mental model appears before low-level detail.
- [ ] Mechanisms and flows identify actors, conditions, state changes, outputs, and material failure paths.
- [ ] Comparisons use the same relevant criteria for every option.
- [ ] Diagrams, tables, code references, and prose agree.
- [ ] Citations or local file links directly support the claims beside them.
- [ ] Limitations, version boundaries, disputes, and open questions are explicit.
- [ ] The conclusion is proportional to the evidence and does not claim certainty that the sources do not support.
