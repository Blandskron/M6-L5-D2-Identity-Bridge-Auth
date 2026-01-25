#!/bin/bash

KEY_NAME="jwt"
KEY_SIZE=2048

FASTAPI_KEYS_DIR="./fastapi-gateway/app/keys"

mkdir -p $FASTAPI_KEYS_DIR

# =========================
# FastAPI: clave privada
# =========================
openssl genpkey \
  -algorithm RSA \
  -out $FASTAPI_KEYS_DIR/${KEY_NAME}_private.pem \
  -pkeyopt rsa_keygen_bits:${KEY_SIZE}

# =========================
# FastAPI: clave pública
# =========================
openssl rsa \
  -pubout \
  -in $FASTAPI_KEYS_DIR/${KEY_NAME}_private.pem \
  -out $FASTAPI_KEYS_DIR/${KEY_NAME}_public.pem

# =========================
# Permisos seguros
# =========================
chmod 600 $FASTAPI_KEYS_DIR/${KEY_NAME}_private.pem
chmod 644 $FASTAPI_KEYS_DIR/${KEY_NAME}_public.pem

echo "✅ Claves JWT generadas correctamente"
echo "🔐 FastAPI privada: $FASTAPI_KEYS_DIR/${KEY_NAME}_private.pem"
echo "🔓 FastAPI pública: $FASTAPI_KEYS_DIR/${KEY_NAME}_public.pem"
