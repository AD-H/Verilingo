from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the AI model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Two sentences
sentence1 = "The RBI will discontinue UPI."
sentence2 = "UPI will be banned by the RBI."

# Convert sentences into embeddings
embedding1 = model.encode([sentence1])
embedding2 = model.encode([sentence2])

# Calculate similarity
similarity = cosine_similarity(embedding1, embedding2)

print("Sentence 1:", sentence1)
print("Sentence 2:", sentence2)
print("Similarity Score:", similarity[0][0])