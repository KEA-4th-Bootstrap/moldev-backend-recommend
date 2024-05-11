from pinecone import Pinecone

pc = Pinecone(api_key="bbfb4eb0-776f-4efc-ad13-b44bb07d8755")
index = pc.Index("user-item")
