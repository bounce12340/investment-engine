# Task: Stress Test of Investment-Engine on NVDA

## Objective
Perform a full end-to-end stress test of the Investment-Engine pipeline using NVDA as the target ticker. The goal is to identify logical gaps, ensure structural stability, and validate the mathematical soundness of the valuation module.

## Team Structure (ClawTeam)
- **CEO**: Orchestrates the engine flow (Narrative -> Tree -> Valuation), ensuring a seamless transition between modules.
- **Reviewer**: Critiques the logical rigor, ensures MECE compliance in the hypothesis tree, and verifies the alignment between the core bet and the final valuation.
- **QA**: Actively seeks hallucinations, identifies logical gaps, tests edge cases in the probability calculations, and validates the SKILL.md orchestration.

## Execution Plan

### Step 1: Narrative Detection (Stress Test)
- **Action**: Execute `investment-narrative-detector` for NVDA.
- **Stress Points**: 
    - Can it distinguish between "AI Hype" (Consensus) and "Sustainable Moat/Software Transition" (Variant)?
    - Is the "Primary Risk" specific enough to be falsifiable, or is it a generic "AI demand drops" statement?
- **Deliverable**: Narrative Map.

### Step 2: Hypothesis Tree Construction (Stress Test)
- **Action**: Execute `investment-hypothesis-tree` using the Narrative Map.
- **Stress Points**:
    - **MECE Check**: Do the L1 pillars overlap? Is anything critical missing (e.g., geopolitical risk in Taiwan)?
    - **Kill Switch Validity**: Are the falsification conditions binary and data-driven, or vague?
    - **Linkage**: Does every leaf lead back to the root investment question?
- **Deliverable**: Detailed Hypothesis Tree.

### Step 3: Scenario Valuation (Stress Test)
- **Action**: Execute `investment-scenario-valuation` using the Hypothesis Tree.
- **Stress Points**:
    - **Math Audit**: Validate the implied probability formula $P = \sum (Prob_i \times Value_i)$. 
    - **Actionability**: Is the difference between Agent Probability and Implied Probability sufficient to justify a trade?
    - **Sensitivity**: Does a 10% change in a key driver move the needle significantly?
- **Deliverable**: Valuation Table and Final Verdict.

### Step 4: Systemic Review (Orchestration)
- **Action**: Audit the transition between files.
- **Stress Points**: 
    - Check for breaking errors in `investment-engine.md`.
    - Ensure the context from Phase 1 is actually preserved and used in Phase 3.

## Success Criteria
1. Completion of a full Investment Memo for NVDA.
2. Identification of at least 2-3 logical gaps or "friction points" in the current skill set.
3. Verification that the probability-weighted valuation is mathematically consistent.
