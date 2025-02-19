from datasets import load_dataset
import math
from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, LoggingHandler, losses
from torch.utils.data import DataLoader
import logging

def parse_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    
    # Specific training setups (not used)
    parser.add_argument("--epoch", type=int, default=5, help="Upper limit on outer loop iterations")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for training")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO,
                        handlers=[LoggingHandler()])

    model_name = 'all-MiniLM-L6-v2'
    model = SentenceTransformer(model_name)

    data_file = load_dataset("bookcorpus", "plain_text", split="train")
    sentences = [example["text"] for example in data_file if example["text"].strip()]


    # 각 문장을 자기 자신과의 쌍으로 생성 (unsupervised 방식)
    train_examples = [InputExample(texts=[s, s]) for s in sentences]

    # SentencesDataset 및 DataLoader 생성
    train_dataset = SentencesDataset(train_examples, model)
    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=args.batch_size)

    # MultipleNegativesRankingLoss 사용 (unsupervised fine tuning에 자주 사용됨)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # 학습 파라미터 설정
    num_epochs = 5  # 필요에 따라 에폭 수 조정
    warmup_steps = math.ceil(len(train_dataloader) * num_epochs * 0.1)  # 전체 학습 데이터의 10%를 워밍업 단계로 사용

    # 모델 파인튜닝
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=num_epochs,
        warmup_steps=warmup_steps,
        output_path='./output/book_corpus_finetuned_model'
    )
