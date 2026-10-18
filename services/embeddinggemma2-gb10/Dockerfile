FROM local-inference/comfyui:gb10-20261012
USER root
RUN python3 -m pip install --break-system-packages --no-cache-dir sentence-transformers==6.1.0 transformers==5.20.1
WORKDIR /opt/embeddinggemma2
COPY server.py .
ENV HF_HOME=/models/huggingface
CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8011", "--no-access-log"]
