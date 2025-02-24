import argparse
import sys
import os 
from pathlib import Path

from bot.memory.embedder import Embedder
from bot.memory.vector_database.chroma import Chroma
from document_loader.format import Format
from document_loader.loader import DirectoryLoader
from document_loader.text_splitter import create_recursive_text_splitter
from entities.document import Document
from helpers.log import get_logger

logger = get_logger(__name__)



def load_documents(docs_path: Path) -> list[Document]:
    """
    Loads Markdown documents from the specified path.

    Args:
        docs_path (Path): The path to the documents.

    Returns:
        List[Document]: A list of loaded documents.
    """
    loader = DirectoryLoader(
        path=docs_path,
        glob="**/*.*",  # 기존 "**/*.md" 대신 모든 파일을 대상으로 합니다.
        show_progress=True,
    )
    return loader.load()


def split_chunks(sources: list, chunk_size: int = 512, chunk_overlap: int = 25) -> list:
    """
    Splits a list of sources into smaller chunks.

    Args:
        sources (List): The list of sources to be split into chunks.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 512.
        chunk_overlap (int, optional): The amount of overlap between consecutive chunks. Defaults to 0.

    Returns:
        List: A list of smaller chunks obtained from the input sources.
    """
    chunks = []
    for source in sources:
        # 기본 형식은 markdown, metadata의 source 필드로 판단 (예: "file.md", "file.json")
        file_source = source.metadata.get("source", "").lower() if source.metadata else ""
        if file_source.endswith(".json"):
            file_format = Format.JSON.value
        else:
            file_format = Format.MARKDOWN.value

        # 각 문서별로 적절한 형식의 splitter를 생성합니다.
        splitter = create_recursive_text_splitter(
            format=file_format, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        # 각 문서를 분리하고 결과를 추가합니다.
        chunks.extend(splitter.split_documents([source]))
    return chunks

def build_memory_index(docs_path: Path, vector_store_path: str, chunk_size: int, chunk_overlap: int, doft: bool) -> None:
    logger.info(f"Loading documents from: {docs_path}")
    sources = load_documents(docs_path)
    logger.info(f"Number of loaded documents: {len(sources)}")

    logger.info("Chunking documents...")
    chunks = split_chunks(sources, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    logger.info(f"Number of generated chunks: {len(chunks)}")

    logger.info("Creating memory index...")
    embedding = Embedder(doft=doft)
    vector_database = Chroma(persist_directory=str(vector_store_path), embedding=embedding)
    vector_database.from_chunks(chunks)
    logger.info("Memory Index has been created successfully!")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Memory Builder")
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="The maximum size of each chunk. Defaults to 512.",
        required=False,
        default=512,
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        help="The amount of overlap between consecutive chunks. Defaults to 25.",
        required=False,
        default=25,
    )
    parser.add_argument(
        "--epoch",
        type=int,
        help="Upper limit on outer loop iterations",
        default=5,
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        help="Batch size for training",
        default=32,
    )
    parser.add_argument(
        "--doft",
        type=bool,
        help="Learning rate for training",
        default=False, 
    )

    return parser.parse_args()

def run_train_emb(parameters):
    if parameters.doft:
        train_cmd = f"python3 chatbot/bot/memory/train_sentencetransformer.py --epoch {parameters.epoch} --batch_size {parameters.batch_size}"
        os.system(train_cmd)

def main(parameters):
    root_folder = Path(__file__).resolve().parent.parent
    doc_path = root_folder / "docs"
    vector_store_path = root_folder / "vector_store" / "docs_index"
    
    run_train_emb(parameters)

    build_memory_index(
        doc_path,
        str(vector_store_path),
        parameters.chunk_size,
        parameters.chunk_overlap,
        parameters.doft,
    )


if __name__ == "__main__":
    try:
        args = get_args()
        main(args)
    except Exception as error:
        logger.error(f"An error occurred: {str(error)}", exc_info=True, stack_info=True)
        sys.exit(1)
