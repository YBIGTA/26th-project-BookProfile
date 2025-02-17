import concurrent.futures
import json
from pathlib import Path
from typing import Any

from entities.document import Document
from helpers.log import get_logger
from tqdm import tqdm
from unstructured.partition.auto import partition

logger = get_logger(__name__)


class DirectoryLoader:
    """Load documents from a directory."""

    def __init__(
        self,
        path: Path,
        glob: str = "**/[!.]*",
        recursive: bool = False,
        show_progress: bool = False,
        use_multithreading: bool = False,
        max_concurrency: int = 4,
        **partition_kwargs: Any,
    ):
        """Initialize with a path to directory and how to glob over it.

        Args:
            path: Path to directory.
            glob: Glob pattern to use to find files. Defaults to "**/[!.]*"
               (all files except hidden).
            recursive: Whether to recursively search for files. Defaults to False.
            show_progress: Whether to show a progress bar. Defaults to False.
            use_multithreading: Whether to use multithreading. Defaults to False.
            max_concurrency: The maximum number of threads to use. Defaults to 4.
            partition_kwargs: Keyword arguments to pass to unstructured `partition` function.
        """
        self.path = path
        self.glob = glob
        self.recursive = recursive
        self.show_progress = show_progress
        self.use_multithreading = use_multithreading
        self.max_concurrency = max_concurrency
        self.partition_kwargs = partition_kwargs

    def load(self) -> list[Document]:
        """Load documents."""
        if not self.path.exists():
            raise FileNotFoundError(f"Directory not found: '{self.path}'")
        if not self.path.is_dir():
            raise ValueError(f"Expected directory, got file: '{self.path}'")

        docs: list[Document] = []
        items = list(self.path.rglob(self.glob) if self.recursive else self.path.glob(self.glob))

        pbar = None
        if self.show_progress:
            pbar = tqdm(total=len(items))

        if self.use_multithreading:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                executor.map(lambda item: self.load_file(item, docs, pbar), items)
        else:
            for i in items:
                self.load_file(i, docs, pbar)

        if pbar:
            pbar.close()

        return docs

    def load_file(self, doc_path: Path, docs: list[Document], pbar: Any | None) -> None:
        """
        Load document from the specified path.
    
        Args:
            doc_path (Path): The path to the document.
            docs: List of documents to append to.
            pbar: Progress bar. Defaults to None.
        """
        if doc_path.is_file():
            try:
                logger.debug(f"Processing file: {str(doc_path)}")
                text = ""
                if doc_path.suffix.lower() == ".json":
                    with open(doc_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    # 먼저 전체 파일을 한 번에 파싱을 시도합니다.
                    try:
                        data = json.loads(file_content)
                        text = json.dumps(data, indent=2, ensure_ascii=False)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Standard json.loads() failed for {doc_path}: {e}. Trying to decode multiple JSON objects.")
                        # 여러 JSON 객체가 연속되어 있을 경우, raw_decode()를 사용하여 파싱합니다.
                        decoder = json.JSONDecoder()
                        pos = 0
                        data_list = []
                        while pos < len(file_content):
                            try:
                                file_content = file_content.lstrip()  # 앞쪽 공백 제거
                                if not file_content:
                                    break
                                obj, idx = decoder.raw_decode(file_content)
                                data_list.append(obj)
                                file_content = file_content[idx:]
                            except json.JSONDecodeError as line_e:
                                logger.error(f"Error decoding JSON from {doc_path}: {line_e}")
                                break
                        text = json.dumps(data_list, indent=2, ensure_ascii=False)
                else:
                    # 기본적으로 unstructured.partition을 사용하여 문서 내용을 추출
                    elements = partition(filename=str(doc_path), **self.partition_kwargs)
                    text = "\n\n".join([str(el) for el in elements])
                docs.append(Document(page_content=text, metadata={"source": str(doc_path)}))
            except Exception as e:
                logger.error(f"Error processing file {doc_path}: {e}")
            finally:
                if pbar:
                    pbar.update(1)



if __name__ == "__main__":
    root_folder = Path(__file__).resolve().parent.parent.parent
    docs_path = root_folder / "docs"
    # glob 패턴을 "*.*"로 변경하면 모든 파일을 읽어오게 할 수도 있습니다.
    loader = DirectoryLoader(
        path=docs_path,
        glob="*.*",
        recursive=True,
        use_multithreading=True,
        show_progress=True,
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")
