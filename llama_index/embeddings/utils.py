"""Embedding utils for LlamaIndex."""
import os
from typing import List, Union

from llama_index.utils import get_cache_dir
from llama_index.bridge.langchain import Embeddings as LCEmbeddings
from llama_index.embeddings.base import BaseEmbedding
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

DEFAULT_HUGGINGFACE_EMBEDDING_MODEL = "BAAI/bge-small-en"


def save_embedding(embedding: List[float], file_path: str) -> None:
    """Save embedding to file."""
    with open(file_path, "w") as f:
        f.write(",".join([str(x) for x in embedding]))


def load_embedding(file_path: str) -> List[float]:
    """Load embedding from file. Will only return first embedding in file."""
    with open(file_path, "r") as f:
        for line in f:
            embedding = [float(x) for x in line.strip().split(",")]
            break
        return embedding


def resolve_embed_model(
    embed_model: Union[None, str, BaseEmbedding, LCEmbeddings]
) -> BaseEmbedding:
    """Resolve embed model."""
    if embed_model is None:
        try:
            return OpenAIEmbedding()
        except ValueError:
            embed_model = "local"
            print(
                "******\n"
                "Could not load OpenAIEmbedding. Using HuggingFaceBgeEmbeddings "
                f"with model_name={DEFAULT_HUGGINGFACE_EMBEDDING_MODEL}. "
                "Please check your API key if you intended to use OpenAI embeddings."
                "\n******"
            )

    if isinstance(embed_model, str):
        splits = embed_model.split(":", 1)
        is_local = splits[0]
        model_name = splits[1] if len(splits) > 1 else None
        if is_local != "local":
            raise ValueError(
                "embed_model must start with str 'local' or of type BaseEmbedding"
            )
        try:
            from langchain.embeddings import HuggingFaceBgeEmbeddings
        except ImportError as exc:
            raise ImportError(
                "Could not import sentence_transformers or langchain package. "
                "Please install with `pip install -U sentence-transformers langchain`."
            ) from exc

        cache_folder = os.path.join(get_cache_dir(), "models")

        embed_model = LangchainEmbedding(
            HuggingFaceBgeEmbeddings(
                model_name=model_name or DEFAULT_HUGGINGFACE_EMBEDDING_MODEL,
                cache_folder=cache_folder,
            )
        )

    if isinstance(embed_model, LCEmbeddings):
        embed_model = LangchainEmbedding(embed_model)

    return embed_model
