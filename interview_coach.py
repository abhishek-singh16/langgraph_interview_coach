# Interview Coach Graph

# **Use Case:** A user provides a job role. The graph prepares interview practice.

# **Specialist Node 1 - `generate_technical_questions`**
# - Generate technical questions.

# **Specialist Node 2 - `generate_behavioral_questions`**
# - Generate behavioral questions.

# **Specialist Node 3 - `generate_role_specific_questions`**
# - Generate questions specific to the role.

# **Decision Node:** Decide whether the candidate needs beginner or advanced prep.

# **Final Nodes:** `beginner_interview_pack` and `advanced_interview_pack`.

import sys
import operator
import json
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

class InterviewPreparation(BaseModel):
    job_role: str = ""
    technical_questions: str = ""
    behavioral_questions: str = ""
    role_specific_questions: str = ""
    needs_advanced_pack: bool = False
    final_suggestion: str = ""
    messages: Annotated[list, operator.add] = []


llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.6)


def understand_role(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are an expert interview assistant. "
        f"A user is applying to the following role: '{state.job_role}'. "
        f"Acknowledge their role in 1-2 sentences. "
    )
    return {
        "messages": [f"[understand_role] {response.content}"]
    }


def generate_technical_questions(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are a technical interview specialist. "
        f"The user is applying for the role of: '{state.job_role}'. "
        f"Generate 3-5 technical questions that are relevant to this role. "
        f"Keep each question concise and focused on key skills or knowledge areas."
    )
    return {
        "technical_questions": response.content,
        "messages": [f"[generate_technical_questions] Done"]
    }


def generate_behavioral_questions(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are a behavioral interview specialist. "
        f"The user is applying for the role of: '{state.job_role}'. "
        f"Generate 3-5 behavioral questions that are relevant to this role. "
        f"Keep each question concise and focused on key skills or knowledge areas."
    )
    return {
        "behavioral_questions": response.content,
        "messages": [f"[generate_behavioral_questions] Done"]
    }


def generate_role_specific_questions(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are a role-specific interview specialist. "
        f"The user is applying for the role of: '{state.job_role}'. "
        f"Generate 3-5 role-specific questions that are relevant to this role. "
        f"Keep each question concise and focused on key skills or knowledge areas."
    )
    return {
        "role_specific_questions": response.content,
        "messages": [f"[generate_role_specific_questions] Done"]
    }

def pick_interview_pack(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are an interview preparation decision system. The user is applying for the role of: '{state.job_role}'.\n\n"
        f"Here are three question groups from specialists:\n\n"
        f"TECHNICAL QUESTIONS:\n{state.technical_questions}\n\n"
        f"BEHAVIOURAL QUESTIONS:\n{state.behavioral_questions}\n\n"
        f"ROLE-SPECIFIC QUESTIONS:\n{state.role_specific_questions}\n\n"
        f"Decide: does this person need a BEGINNER pack (for foundational practice and near time interview preparation) "
        f"or an ADVANCED pack (for deeper expertise and enough time for the interview preparation)?\n\n"
        f"Reply STRICTLY in this JSON format (no other text):\n"
        f'{{"needs_advanced_pack": true/false, "reason": "one sentence explanation"}}'
    )
    try:
        result = json.loads(response.content)
        needs_advanced = result["needs_advanced_pack"]
        reason = result["reason"]
    except (json.JSONDecodeError, KeyError):
        needs_advanced = False
        reason = "Could not parse decision, defaulting to beginner practice."

    return {
        "needs_advanced_pack": needs_advanced,
        "practice_reason": reason,
        "messages": [f"[pick_best_practice] advanced_pack={needs_advanced}"]
    }

def beginner_interview_pack(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are a expert interview coach. The user is applying for the role of: '{state.job_role}'.\n\n"
        f"Based on these specialist suggestions, create a SHORT practice question bank (under 30 minutes) "
        f"that combines the best elements:\n\n"
        f"TECHNICAL QUESTIONS: {state.technical_questions}\n"
        f"BEHAVIORAL QUESTIONS: {state.behavioral_questions}\n"
        f"ROLE-SPECIFIC QUESTIONS: {state.role_specific_questions}\n\n"
        f"Structure it as a simple practice list. Focus on the most essential questions that will give the user quick wins in their interview preparation. "
        f"Format it as a simple numbered list of questions. "
        f"Keep it to the point and encouraging. End with an encouraging closing line."
    )
    return {
        "final_suggestion": f"BEGINNER INTERVIEW PACK (under 30 min)\n{'='*45}\n{response.content}",
        "messages": [f"[beginner_interview_pack] Generated beginner pack"]
    }


def advanced_interview_pack(state: InterviewPreparation) -> dict:
    response = llm.invoke(
        f"You are a expert interview coach. The user is applying for the role of: '{state.job_role}'.\n\n"
        f"Based on these specialist suggestions, create an ADVANCED practice question bank (1 hour to 2 hours) "
        f"that thoughtfully combines all three question groups:\n\n"
        f"TECHNICAL QUESTIONS: {state.technical_questions}\n"
        f"BEHAVIORAL QUESTIONS: {state.behavioral_questions}\n"
        f"ROLE-SPECIFIC QUESTIONS: {state.role_specific_questions}\n\n"
        f"Structure it in a deep practice format that encourages the user to reflect on their answers. For each question, provide a brief explanation of why it's important and what the interviewer might be looking for in a strong answer. "
        f"Keep it to the point and encouraging. End with an encouraging closing line"
    )
    return {
        "final_suggestion": f"ADVANCED INTERVIEW SESSION (1-2 hours)\n{'='*45}\n{response.content}",
        "messages": [f"[advanced_interview_pack] Generated advanced session"]
    }


def route_after_decision(state: InterviewPreparation) -> str:
    if state.needs_advanced_pack:
        return "advanced"
    else:
        return "beginner"


graph = StateGraph(InterviewPreparation)

graph.add_node("understand_role", understand_role)
graph.add_node("generate_technical_questions", generate_technical_questions)
graph.add_node("generate_behavioral_questions", generate_behavioral_questions)
graph.add_node("generate_role_specific_questions", generate_role_specific_questions)
graph.add_node("pick_interview_pack", pick_interview_pack)
graph.add_node("beginner_interview_pack", beginner_interview_pack)
graph.add_node("advanced_interview_pack", advanced_interview_pack)

graph.add_edge(START, "understand_role")

graph.add_edge("understand_role", "generate_technical_questions")
graph.add_edge("understand_role", "generate_behavioral_questions")
graph.add_edge("understand_role", "generate_role_specific_questions")

graph.add_edge("generate_technical_questions", "pick_interview_pack")
graph.add_edge("generate_behavioral_questions", "pick_interview_pack")
graph.add_edge("generate_role_specific_questions", "pick_interview_pack")

graph.add_conditional_edges(
    "pick_interview_pack",
    route_after_decision,
    {
        "beginner": "beginner_interview_pack",
        "advanced": "advanced_interview_pack",
    }
)

graph.add_edge("beginner_interview_pack", END)
graph.add_edge("advanced_interview_pack", END)

agent = graph.compile()


def run_interview_check(job_role: str):
    print("=" * 55)
    print("  INTERVIEW PRACTICE SUGGESTER")
    print(f"  You are applying for this role: \"{job_role}\"")
    print("=" * 55)

    result = agent.invoke({
        "job_role": job_role,
        "messages": [],
    })

    print("\n" + "=" * 55)
    print("  YOUR PERSONALIZED PRACTICE")
    print("=" * 55)
    print(f"\n{result['final_suggestion']}")

    print("\n" + "-" * 55)
    print("  MESSAGE LOG")
    print("-" * 55)
    for msg in result["messages"]:
        print(f"  {msg}")

    return result


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  INTERVIEW PRACTICE SUGGESTER")
    print("=" * 55)
    print("\n  Tell me about the role you're applying for and I'll suggest a")
    print("  personalized interview practice just for you.")
    print("  Type 'quit' to exit.\n")

    while True:
        job_role = input("  What is the role you're applying for? > ").strip()

        if job_role.lower() in ("quit", "exit", "q"):
            print("\n  Good luck with your interview preparation. Goodbye!\n")
            break

        if not job_role:
            continue

        run_interview_check(job_role)
        print("\n")