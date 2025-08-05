from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from src.context import academic_loader
from src.gigachat import gigachat

model = gigachat

async def call_model(state: MessagesState, config: RunnableConfig):
    """Async function to call the model with context"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    system_prompt = f"""
    Ты — консультант по магистерским программам. Твоя задача — помогать абитуриентам выбирать между программами и планировать обучение.

    Доступные программы:
    {academic_loader.get_plan_context()}

    Правила работы:
    1. Отвечай ТОЛЬКО на вопросы, связанные с обучением
    2. При рекомендациях учитывай бэкграунд абитуриента
    3. Используй конкретные данные из учебных планов
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        *[(msg.type, msg.content) for msg in messages]
    ])

    chain = prompt | model
    response = await chain.ainvoke({"input": last_message})
    return {"messages": [*messages, AIMessage(content=response.content)]}

def create_graph():
    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_node("model", call_model)
    workflow.add_edge(START, "model")

    memory = MemorySaver()

    return workflow.compile(
        checkpointer=memory,
    )

workflow = create_graph()