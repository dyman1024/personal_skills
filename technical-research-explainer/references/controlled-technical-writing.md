# Controlled Technical Research and Explanation

This guide adapts principles from ASD-STE100 Simplified Technical English for technical research and explanation. It does not claim formal ASD-STE100 compliance. Preserve technical meaning; do not mechanically apply the STE controlled dictionary, English-specific parts-of-speech rules, or fixed word limits to Chinese text, code, formulas, and domain terminology.

## Optimize for reader understanding

- Make the subject accurate, unambiguous, verifiable, and easy to follow.
- Adapt terminology and depth to the target reader without hiding material complexity.
- Preserve conditions, actors, boundaries, exceptions, risks, and limitations.
- Do not simplify by deleting information that changes the technical meaning.

## Separate information classes

Keep these classes distinct:

- **Sourced fact:** Directly supported by a cited source or inspected implementation.
- **Source claim:** Asserted by a source but not independently established.
- **Inference:** Derived from identified evidence.
- **Recommendation:** A judgment about what to choose or do.
- **Assumption:** Accepted temporarily because required information is missing.
- **Unknown:** Not established by available evidence.

Do not present an inference, recommendation, convention, desired outcome, or target design as an implemented fact.

## Control terminology

- Use one preferred term for one concept. Do not switch synonyms only to avoid repetition.
- Use each term with one meaning within the same deliverable.
- Define an abbreviation at first use. Introduce it only if it appears again.
- Preserve official names from standards, papers, interfaces, source code, and authoritative documentation.
- Define domain-specific terms when the target reader might not know their meaning or boundary.
- Avoid ambiguous references such as “it,” “this component,” “the related system,” or “the service” when more than one referent is possible. Name the object directly.
- Replace vague terms such as “appropriate,” “fast,” “high,” “normally,” “when necessary,” and “as much as possible” with a threshold, condition, time range, measurement, or explicit uncertainty.

## Control sentences and paragraphs

- Put one principal fact, claim, inference, decision, action, or causal relationship in each sentence.
- Prefer short sentences. Split sentences with multiple actions, conditions, branches, or nested qualifications. Do not enforce a mechanical word or character limit.
- Prefer active voice and identify the actor. Use passive voice only when the actor is unknown, irrelevant, or intentionally undisclosed.
- Put a condition before the action or result that depends on it.
- Do not omit a subject, action, object, unit, version, or precondition that the reader needs.
- Cover one topic in each paragraph. Use a vertical list or table for complex alternatives, branches, constraints, and comparisons.
- Use strong causal words such as “therefore,” “causes,” “guarantees,” and “solves” only when evidence supports the causal relationship.
- Remove generic openings, empty transitions, repeated summaries, and sentences that add no technical information.

## Explain before evaluating

- State what the subject is, what problem it addresses, and how its main parts relate.
- Explain mechanisms in dependency order. Introduce prerequisites before dependent behavior.
- Separate the normal path from errors, retries, timeouts, fallback behavior, and recovery.
- Separate documented intent, implemented behavior, measured outcomes, and your evaluation.
- Reconstruct a design rationale only when evidence supports it. Otherwise, label the rationale as unknown or inferred.
- Do not silently transform an explanation into a redesign proposal.

## Compare consistently

- State the decision context and relevant constraints before comparing options.
- Apply the same criteria to all options.
- Separate intrinsic properties from environment-dependent outcomes.
- Explain the evidence behind each material difference.
- Give conditional conclusions instead of declaring a universal winner when the result depends on context.

## Keep artifacts consistent

- Use the same terms in diagrams, tables, code references, interfaces, states, and prose.
- Label important relationships with the action, protocol, state change, or data they represent.
- Make each diagram answer one primary question and keep it at one abstraction level.
- After a diagram, state the conclusions and constraints that the diagram cannot show. Do not narrate every edge.
- Never present illustrative values as verified production data.

## Handle uncertainty and sources

- Do not invent behavior, interfaces, data, links, owners, schedules, rationale, test results, or production outcomes.
- Cite evidence near the claim it supports.
- Record material version and date boundaries.
- State the evidence behind an inference.
- If sources disagree, describe the disagreement and its effect on the conclusion.
- State what is unknown and what evidence would resolve it.

## Review before delivery

Review in this order:

1. **Meaning:** Preserve the complete technical meaning and relevant boundaries.
2. **Evidence:** Ensure each material conclusion has appropriate support.
3. **Information class:** Separate facts, claims, inferences, recommendations, assumptions, and unknowns.
4. **Terminology:** Remove undefined abbreviations, synonym drift, overloaded terms, and ambiguous references.
5. **Sentences:** Keep one principal information unit per sentence and put conditions before dependent actions.
6. **Structure:** Put the mental model and conclusion before low-level detail.
7. **Consistency:** Align diagrams, tables, code references, interfaces, versions, and prose.
8. **Proportionality:** Do not claim more certainty, generality, or causality than the evidence supports.

Fix detected problems before delivery. Do not merely list them. Do not expose private chain-of-thought. Provide conclusions, evidence, explicit reasoning summaries, assumptions, limitations, and open questions.
