# importing a necessary library
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph,MessagesState, START, END
from typing import Literal
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

class chatbot:
    def __init__(self):
        self.llm=ChatGroq(model="gemma2-9b-It")
        
    def call_tool(self):
        tool = TavilySearchResults(max_results=2)
        tools = [tool]
        self.tool_node = ToolNode(tools=[tool])
        self.llm_with_tool=self.llm.bind_tools(tools)
        
    def call_model(self,state: MessagesState):
        messages = state['messages']
        response = self.llm_with_tool.invoke(messages)
        return {"messages": [response]}
    
    def router_function(self,state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    
    
                
    def __call__(self):
        self.call_tool()
        memory = MemorySaver()
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools": "tools", END: END})
        workflow.add_edge("tools", 'agent')
        self.app = workflow.compile(checkpointer=memory)
        return self.app
        
if __name__=="__main__":
    mybot=chatbot()
    workflow=mybot()
    config = {"configurable" : {"thread_id" : "1"}}
    response=workflow.invoke({"messages": ["who is a current prime minister of USA?"]}, config=config)
    print(response['messages'][-1].content)