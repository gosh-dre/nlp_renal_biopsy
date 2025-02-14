from llama_cpp import Llama
import ollama
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def use_llm_to_compare(
    entity1: str, entity2: str, model: str = "gemma2:2b", provider: str = "ollama"
) -> bool:
    """Compare two medical entities using specified LLM."""

    default_false_phrases = ["none", "None", "null", "Null", "nan", "NaN"]
    # TODO: safe option would be to go to default value for entity if any of these seen
    if entity1 in default_false_phrases:
        entity1 = "0"
    if entity2 in default_false_phrases:
        entity2 = "0"

    entity1 = entity1.lower()
    entity2 = entity2.lower()

    if entity1 == entity2:
        return True
    if (entity1 == "0" and entity2 != "0") or (entity2 == "0" and entity1 != "0"):
        return False

    query = f"""
    You are a renal biopsy expert.
    Are the phrases "{entity1}" and "{entity2}" describing equivalent or
    similar concepts? Only answer True or False.
    Answer based on the nouns, adjectives, or numbers.
    """

    if provider == "ollama":
        response = ollama.generate(
            model=model,
            prompt=query,
            options={"temperature": 0, "num_predict": 2, "num_ctx": 1024},
        )
        return "True" in response["response"]

    elif provider == "llama-cpp":
        messages = [{"role": "user", "content": query}]
        llm = Llama(
            model_path="models/Phi-3.5-mini-instruct-Q5_K_M.gguf",
            chat_format="chatml",
            verbose=False,
            n_ctx=250,
        )
        answer = llm.create_chat_completion(
            messages=messages,
            max_tokens=2,
            temperature=0,
        )
        return "True" in answer["choices"][0]["message"]["content"]

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def use_bert_to_compare(entity1, entity2, threshold=0.8):
    model = SentenceTransformer("bert-base-nli-mean-tokens")
    embeddings = model.encode([entity1, entity2])
    similarity = cosine_similarity(
        embeddings[0].reshape(1, -1),
        embeddings[1].reshape(1, -1),
    )[0][0]
    print(f"{entity1}, {entity2}: {similarity}")
    return similarity >= threshold
