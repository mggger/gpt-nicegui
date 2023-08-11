from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


class EmbeddingLocalBackend(object):
    def __init__(self, path='db'):
        self.path = path
        self.vectordb = Chroma(persist_directory=self.path, embedding_function=OpenAIEmbeddings())

    def add_markdown_embedding(self, data, auto_commit=True):
        text_splitter = CharacterTextSplitter(
            separator="*" * 40,
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        documents = text_splitter.create_documents([data])
        self.vectordb.add_documents(documents)

        if auto_commit:
            self._commit()

    def _commit(self):
        self.vectordb.persist()

    def query(self, query):
        embedding_vector = OpenAIEmbeddings().embed_query(query)
        docs = self.vectordb.similarity_search_by_vector(embedding_vector)
        return docs
