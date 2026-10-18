import os
import secrets
import threading
from pathlib import Path
from typing import Literal

import torch
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

MODEL_ID = 'google/embeddinggemma-2'
REVISION = os.environ['MODEL_REVISION']
KEY = Path('/run/secrets/api_key').read_text().strip()
if not KEY:
    raise RuntimeError('API key is empty')
model = SentenceTransformer(MODEL_ID, revision=REVISION, device='cuda',
                            config_kwargs={'vision_config': None, 'audio_config': None},
                            model_kwargs={'torch_dtype': torch.bfloat16})
model.max_seq_length = 8192
lock = threading.Lock()


def authorize(authorization: str | None = Header(default=None)):
    if not secrets.compare_digest(authorization or '', 'Bearer ' + KEY):
        raise HTTPException(401, 'API key required')


app = FastAPI(dependencies=[Depends(authorize)])


class Request(BaseModel):
    input: str | list[str]
    model: Literal['google/embeddinggemma-2'] = MODEL_ID
    input_type: Literal['document', 'query'] = 'document'
    dimensions: Literal[128, 256, 512, 768] = 768
    encoding_format: Literal['float'] = 'float'


@app.get('/health')
def health():
    return {'status': 'ready', 'model': MODEL_ID, 'revision': REVISION,
            'device': str(model.device), 'text_only': True,
            'cuda_allocated_bytes': torch.cuda.memory_allocated(),
            'cuda_reserved_bytes': torch.cuda.memory_reserved()}


@app.get('/v1/models')
def models():
    return {'object': 'list', 'data': [{'id': MODEL_ID, 'object': 'model', 'owned_by': 'google'}]}


@app.post('/v1/embeddings')
def embeddings(request: Request):
    texts = [request.input] if isinstance(request.input, str) else request.input
    if not 1 <= len(texts) <= 16 or any(not t.strip() for t in texts):
        raise HTTPException(400, 'Provide 1-16 nonempty text inputs')
    prefix = model.prompts[request.input_type]
    counts = [len(model.tokenizer.encode(prefix + text, add_special_tokens=True, truncation=False)) for text in texts]
    if max(counts) > model.max_seq_length:
        raise HTTPException(400, f'Input exceeds {model.max_seq_length} tokens including task prefix')
    with lock, torch.inference_mode():
        vectors = model.encode(texts, prompt_name=request.input_type, batch_size=8,
                               normalize_embeddings=True, show_progress_bar=False)
        vectors = vectors[:, :request.dimensions]
        vectors /= (vectors ** 2).sum(axis=1, keepdims=True) ** 0.5
    return {'object': 'list', 'model': MODEL_ID,
            'data': [{'object': 'embedding', 'index': i, 'embedding': v.tolist()}
                     for i, v in enumerate(vectors)],
            'usage': {'prompt_tokens': sum(counts), 'total_tokens': sum(counts)}}
