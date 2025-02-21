from datasets import load_dataset
import math
from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, LoggingHandler, losses
from torch.utils.data import DataLoader
import logging
import random
import argparse

def parse_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    
    # Specific training setups (not used)
    parser.add_argument("--epoch", type=int, default=5, help="Upper limit on outer loop iterations")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--rag", type=bool, default=False, help="Learning rate for training")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO,
                        handlers=[LoggingHandler()])

    model_name = 'all-MiniLM-L6-v2'
    model = SentenceTransformer(model_name)
    
    # Positive & Negative Pair 데이터
    positive_pairs = [
        ("나는 책을 좋아해.", "독서는 내 취미야."),
        ("그녀는 피아노를 잘 친다.", "그녀는 음악을 좋아해."),
        ("서울은 한국의 수도다.", "서울에는 많은 사람들이 산다."),
    ]

    negative_pairs = [
        ("나는 책을 좋아해.", "오늘 날씨가 참 좋네."),
        ("그녀는 피아노를 잘 친다.", "나는 아침에 운동을 한다."),
        ("서울은 한국의 수도다.", "나는 축구 경기를 좋아해."),
    ]

    # InputExample 형식으로 변환
    train_examples = []

    for sent1, sent2 in positive_pairs:
        train_examples.append(InputExample(texts=[sent1, sent2], label=1.0))  # 유사한 문장은 1

    for sent1, sent2 in negative_pairs:
        train_examples.append(InputExample(texts=[sent1, sent2], label=0.0))  # 다른 문장은 0

    # 데이터 확인
    for example in train_examples:
        print(example.texts, example.label)
        
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # DataLoader 생성
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=32)

    # Contrastive Loss 적용
    train_loss = losses.ContrastiveLoss(model)

    # 모델 학습
    model.fit(train_objectives=[(train_dataloader, train_loss)],
            epochs=5,
            warmup_steps=100,
            output_path='./output/contrastive_model')
    

    # data_file = load_dataset("bookcorpus", "plain_text", split="train",trust_remote_code=True)
    # sentences = [example["text"] for example in data_file if example["text"].strip()]


    # # 각 문장을 자기 자신과의 쌍으로 생성 (unsupervised 방식)
    # train_examples = [InputExample(texts=[s, s]) for s in sentences]

    # # SentencesDataset 및 DataLoader 생성
    # train_dataset = SentencesDataset(train_examples, model)
    # train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=args.batch_size)

    # # MultipleNegativesRankingLoss 사용 (unsupervised fine tuning에 자주 사용됨)
    # train_loss = losses.MultipleNegativesRankingLoss(model)

    # # 학습 파라미터 설정
    # num_epochs = 5  # 필요에 따라 에폭 수 조정
    # warmup_steps = math.ceil(len(train_dataloader) * num_epochs * 0.1)  # 전체 학습 데이터의 10%를 워밍업 단계로 사용

    # # 모델 파인튜닝
    # model.fit(
    #     train_objectives=[(train_dataloader, train_loss)],
    #     epochs=num_epochs,
    #     warmup_steps=warmup_steps,
    #     output_path='./output/book_corpus_finetuned_model'
    # )
    



