from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from context import csv_loader
from src.gigachat import gigachat

model = gigachat


async def call_model(state: MessagesState):
    """Async function to call the model with CSV context"""
    messages = state["messages"]

    # Get the last human message
    last_message = messages[-1].content if messages else ""

    # Prepare system prompt with CSV context
    system_prompt = f"""
    You are a helpful customer support assistant. Use this context to answer questions:
    
    {csv_loader.get_full_context()}
    
    Current conversation:
    """

    # Format the prompt with conversation history
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), *[(msg.type, msg.content) for msg in messages]]  # type: ignore
    )

    # Create chain with prompt and model
    chain = prompt | model
    response = await chain.ainvoke({"input": last_message})

    return {"messages": [*messages, AIMessage(content=response.content)]}


def create_graph():
    """Create and configure the LangGraph workflow with memory"""
    workflow = StateGraph(state_schema=MessagesState)

    # Add nodes and edges
    workflow.add_node("model", call_model)
    workflow.add_edge(START, "model")

    # Set up memory with automatic pruning
    memory = MemorySaver()

    # Configure the graph to maintain conversation history
    return workflow.compile(
        checkpointer=memory,
        # Keep last 6 messages (3 exchanges) to manage context length
        interrupt_before=["model"],
        # configurable={
        #     "thread_id": lambda: "default",  # Will be overridden by bot
        #     "recursion_limit": 50,  # Prevent infinite loops
        # },
    )


# Initialize graph
app = create_graph()
