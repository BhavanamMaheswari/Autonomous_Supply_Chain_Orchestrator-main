import sys
try:
    import pinecone
    print(f"Pinecone module: {pinecone}")
    print(f"Content: {dir(pinecone)}")
except ImportError as e:
    print(f"Import pinecone failed: {e}")

try:
    from pinecone import Pinecone
    print("SUCCESS: from pinecone import Pinecone works.")
except ImportError as e:
    print(f"FAILURE: from pinecone import Pinecone failed: {e}")
