# -*- coding: utf-8 -*-
"""NLP MINI PROJECT.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fcPdkkZsigzZBT51nB2LIg_6mZN7cEpI
"""

!pip install uvicorn

!pip install fastapi
!pip install pyngrok

from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained(
    'bert-base-uncased', output_hidden_states=True)


def get_embeddings(text, token_length):
    tokens = tokenizer(text, max_length=token_length,
                       padding='max_length', truncation=True)
    output = model(torch.tensor(tokens.input_ids).unsqueeze(0),
                   attention_mask=torch.tensor(tokens.attention_mask).unsqueeze(0)).hidden_states[-1]
    return torch.mean(output, axis=1).detach().numpy()


def calculate_similarity(text1, text2, token_length=20):
    out1 = get_embeddings(text1, token_length=token_length)
    out2 = get_embeddings(text2, token_length=token_length)
    sim = cosine_similarity(out1, out2)[0][0]
    print(sim)
    return sim


app = FastAPI(title="Similarity Score")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
class UserInput(BaseModel):
    user_input: float


@app.get('/calculate/')
async def sentences(sen1: str, sen2: str):
    print(sen1, sen2, sep="\n")

    similarity = calculate_similarity(sen1, sen2)

    return {"calculate": float(similarity)}

import nest_asyncio
from pyngrok import ngrok

ngrok.set_auth_token("2gMYvDSwH5X6wn1DPt5LKCa49YK_7b4EkR6KXZQPp4DvqYe4s")
ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)