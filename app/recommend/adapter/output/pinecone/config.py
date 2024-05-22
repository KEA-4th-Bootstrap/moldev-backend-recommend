from pinecone import Pinecone

from config import config

pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index("user-item")
