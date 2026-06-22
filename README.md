# Interview Practice Suggester - LangGraph Interview Coach

A simple LangGraph-based assistant that generates a personalized interview practice pack when a user provides a job role. The graph runs multiple specialist nodes in parallel, decides whether the user needs a beginner or advanced practice pack, and returns a concise practice plan plus an execution log.

```text
[User Job Role]
      |
      v
understand_role
      |
      +--> generate_technical_questions ----+
      +--> generate_behavioral_questions ---+--> pick_interview_pack
      +--> generate_role_specific_questions-+          |
                                                conditional
                                             /              \
                                     beginner_pack       advanced_pack
                                            |                    |
                                           END                  END
```

## What This Project Does
A user starts the CLI by running interview_coach.py and enters a job role (for example, "Senior Backend Engineer"). The graph then:

- Parses and acknowledges the role in the understand_role node.
- Runs three specialist nodes in parallel to produce question groups:
- generate_technical_questions — technical prompts tailored to the role.
- generate_behavioral_questions — STAR-style behavioral prompts.
- generate_role_specific_questions — domain- or role-specific questions.
- Fan-in: the three question groups are aggregated and passed to pick_interview_pack.
- Decision node pick_interview_pack chooses whether to return a beginner_interview_pack (short/high-level) or an advanced_interview_pack (deeper multi-question plan), and routes conditionally.
- The final node formats and returns the selected pack along with an execution message log to the CLI.

## Key behaviors:

- Parallel execution: the three question-generator nodes run concurrently after understand_role.
- Conditional routing: pick_interview_pack selects the next node at runtime (beginner vs advanced).
- Message accumulation: node outputs and trace messages are collected in state so the final output includes an execution log.