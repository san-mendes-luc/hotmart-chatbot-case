import os
import logging
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pymilvus import utility, connections

import pandas as pd
from pathlib import Path

# Configurações iniciais
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MILVUS_URI = os.getenv("MILVUS_URI", "http://milvus:19530")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "faq_collection")
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "PORTULAN/serafim-335m-portuguese-pt-sentence-encoder-ir"
)

# TODO: Mover para data lake
SOURCE_PATH = os.getenv("FAQ_CSV_PATH", "/src/core/milvus/source_documents/hotmart_faq_dag_documents.csv")
if not Path(SOURCE_PATH).exists():
    raise FileNotFoundError(f"{SOURCE_PATH} not found. Please set FAQ_CSV_PATH correctly.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=25
)

class MilvusClient:
    def __init__(self):
        self.encoder =  HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs={"device": "cpu", "trust_remote_code": True}
        )

        # 2. Verificar existência
        connections.connect(uri=MILVUS_URI)
        if not utility.has_collection(COLLECTION_NAME):
            print(f"Coleção '{COLLECTION_NAME}' não existe. Criando e inserindo documentos...")

            raw_documents = [Document(page_content=row[2], metadata={'article_name': row[0], 'article_url': row[1]})
                            for row in pd.read_csv(SOURCE_PATH).values]
            # Split documents into chunks
            documents = []
            for doc in raw_documents:
                for chunk in text_splitter.split_text(doc.page_content):
                    documents.append(Document(page_content=chunk, metadata=doc.metadata))
            self.client = Milvus.from_documents(
                documents=documents,
                embedding=self.encoder,
                collection_name=COLLECTION_NAME,
                connection_args={"uri": MILVUS_URI},
                drop_old=True
            )
        else:
            print(f"Coleção '{COLLECTION_NAME}' já existe. Conectando sem dropar...")
            
            self.client = Milvus(
                embedding_function=self.encoder,
                collection_name=COLLECTION_NAME,
                connection_args={"uri": MILVUS_URI},
                drop_old=False
            )

        logger.info("MilvusIngestor inicializado com %s", MODEL_NAME)


    def ingest_batch(self, docs: List[Document]):
        total = len(docs)
        logger.info("Iniciando ingestão em lote de %d documentos", total)
        try:
            # Split each document before ingesting
            split_docs = []
            for doc in docs:
                for chunk in text_splitter.split_text(doc.page_content):
                    split_docs.append(Document(page_content=chunk, metadata=doc.metadata))
            self.client.add_documents(split_docs)
        except Exception as e:
            logger.exception("Erro na ingestão em lote: %s", e)
            raise

    def ingest_single(self, doc: Document):
        logger.info("Ingestão de documento único: %s", doc.metadata.get("id"))
        try:
            split_docs = [Document(page_content=chunk, metadata=doc.metadata) for chunk in text_splitter.split_text(doc.page_content)]
            self.client.add_documents(split_docs)
        except Exception as e:
            logger.exception("Falha ao adicionar documento %s: %s", doc.metadata.get("id"), e)
            raise

    def semantic_search(self, query: str, k: int = 5) -> List[Document]:
        logger.info("Buscando top %d para: %s", k, query)
        try:
            results = self.client.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.exception("Erro na busca semântica: %s", e)
            raise
