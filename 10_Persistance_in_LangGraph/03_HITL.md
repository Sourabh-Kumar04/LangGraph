# Human In The Loop (HITL)

**Human-in-the-Loop (HITL) in LangGraph** is all about pausing the graph execution so that a person can inspect, edit, or approve the intermediate state before continuing.

LangGraph makes this possible using **interrupts**.

---

## 🔑 Key Idea

* You mark nodes as *interruptible*.
* When execution reaches that node, LangGraph pauses and waits for human input.
* You then **resume** the graph with the provided feedback or decision.

---

## 🛠️ Example: HITL in LangGraph

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

# Define state
class State(TypedDict):
    question: str
    answer: str

# Node 1: LLM generates an answer
def generate_answer(state: State):
    return {"answer": f"AI thinks: {state['question']} → 42"}

# Node 2: Human-in-the-loop check
def human_check(state: State):
    # Pause for human input
    from langgraph.types import interrupt
    feedback = interrupt("Please validate or edit the AI’s answer:", state["answer"])
    return {"answer": feedback}

# Build workflow
workflow = StateGraph(State)
workflow.add_node("generate", generate_answer)
workflow.add_node("human_review", human_check)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "human_review")
workflow.add_edge("human_review", END)

# Save checkpoints
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

---

## 🚀 Running It

```python
config = {"configurable": {"thread_id": "hitl1"}}

# First run — it will stop at the interrupt
state = app.invoke({"question": "What is the meaning of life?"}, config)
```

👉 At this point, execution **pauses** waiting for human input.

---

## 📝 Resuming with Human Input

```python
# Resume after human input
app.stream(
    None,
    config,
    stream_mode="values",
    interrupt_before=["human_review"],  # wait here
)
# Later...
app.resume("Actually, the answer is 'Love and curiosity'", config)
```

So the flow is:

1. Graph runs until HITL node.
2. Execution pauses (`interrupt`).
3. Human gives input.
4. Graph resumes with that feedback.

---

✅ **Use Cases of HITL in LangGraph**

* Reviewing an AI draft before sending it to users.
* Approving/rejecting decisions in workflows (finance, HR, law).
* Injecting domain expertise (e.g., medical reports).

---

Perfect 🔥 Let’s build a **minimal working demo notebook** for Human-in-the-Loop (HITL) in LangGraph.

---

## 📓 Minimal HITL Notebook Demo

```python
# Install langgraph if not installed
# !pip install langgraph

from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

# 1. Define the state
class State(TypedDict):
    question: str
    answer: str

# 2. Node 1: AI generates an answer
def generate_answer(state: State):
    return {"answer": f"AI suggests: '{state['question']}' → 42"}

# 3. Node 2: Human-in-the-loop review
def human_review(state: State):
    # Pause execution here
    feedback = interrupt("Review the AI’s answer. Approve or change it:", state["answer"])
    return {"answer": feedback}

# 4. Build workflow
workflow = StateGraph(State)
workflow.add_node("generate", generate_answer)
workflow.add_node("review", human_review)

workflow.set_entry_point("generate")
workflow.add_edge("generate", "review")
workflow.add_edge("review", END)

# 5. Compile with memory checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

---

## ▶️ Step 1: Run Workflow Until Human Review

```python
config = {"configurable": {"thread_id": "hitl-demo"}}

# First run — execution stops at human_review
state = app.stream(
    {"question": "What is the meaning of life?"},
    config,
    stream_mode="values",
    interrupt_before=["review"],   # pause before human_review
)

for s in state:
    print(s)  # You’ll see AI’s initial suggestion
```

---

## ⏸️ Step 2: Provide Human Input and Resume

```python
# Resume with your feedback
app.resume("Actually, the answer is Love ❤️ and Curiosity 🧠", config)

# Fetch final state
final = app.get_state(config)
print(final.values)
```

---

### ✅ Output Flow

1. AI suggests an answer (`42`).
2. Graph **pauses** at `human_review`.
3. You (human) approve or change it.
4. Graph **resumes** with your input.

---
