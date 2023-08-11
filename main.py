import os

from langchain import LLMChain
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate

from embedding.embedding import EmbeddingLocalBackend
from prompt.prompt_template import developer_prompt_template
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT


def create_ui(query):
    llm = ChatOpenAI()
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
    eb = EmbeddingLocalBackend(path="chroma")
    messages_combine = [SystemMessagePromptTemplate.from_template(developer_prompt_template)]
    p_chat_combine = ChatPromptTemplate.from_messages(messages_combine)

    doc_chain = load_qa_chain(llm, chain_type="map_reduce", combine_prompt=p_chat_combine)
    chain = ConversationalRetrievalChain(
        retriever=eb.vectordb.as_retriever(),
        question_generator=question_generator,
        combine_docs_chain=doc_chain,
    )
    chat_history = []
    result = chain.run({"question": query, "chat_history": chat_history})
    return result


if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = "xxxxx"
    command = "create a button with a label hello"
    print(create_ui(command))
