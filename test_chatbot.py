from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)

from rag_utils_manatee import create_chat_engine

chat_engine = create_chat_engine()
prepend = "I am going to give you a query to generate a lesson plan. Here are some general guidelines, but if the query says something contradicting this, go with the query. The lessons are taught in only English. Make sure that every new topic has a question posed alongside it. Questions are insightful and appropriate. Make sure the lesson has appropriate icebreakers at the beginning and asks students about their day, lessons maintain a friendly atmosphere. Generate 3 or more specific sets of practice problems. Create a brief introduction to the topic. The lesson plan should contain 5 or more specific examples. The lesson plan should have the following sections: Objective, Warm-up, Introduction, Explanation, Examples, Practice Problems, Interactive Activity, and Conclusion. Based on these guidelines, generate a lesson plan given the following topic: "

while True:
    incoming_message = input("Enter a query: ")
    rag_response = chat_engine.chat(prepend + incoming_message)
    print(str(rag_response))