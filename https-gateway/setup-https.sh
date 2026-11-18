#!/bin/bash
set -eo pipefail
DIR="$(dirname "$(readlink -f "$0")")"

# envsubst
command -v envsubst >/dev/null 2>&1 || { echo "Asennetaan gettext-base..."; sudo apt-get update -qq && sudo apt-get install -y gettext-base; }

# Syötteet + validointi
read -p "Let's Encrypt email: " EMAIL
read -p "Public domain (esim. 195.148.21.146.sslip.io): " DOMAIN
if [ -z "$EMAIL" ] || [ -z "$DOMAIN" ]; then
  echo "Virhe: email ja domain ovat pakollisia."; exit 1
fi

read -p "Issuer: [1] staging (oletus)  [2] prod: " CHOICE
if [ "$CHOICE" = "2" ]; then
  ISSUER=letsencrypt-prod
  read -p "VAROITUS: prod on rate-limitattu. Ajoitko stagingin jo onnistuneesti? [y/N]: " OK
  [ "$OK" = "y" ] || { echo "Keskeytetty — aja staging ensin."; exit 1; }
else
  ISSUER=letsencrypt-staging
fi
export EMAIL DOMAIN

echo "==> Gateway + redirect"
kubectl apply -f "$DIR/gateway/kubeflow-gateway-tls.yaml"
kubectl apply -f "$DIR/gateway/virtualservice-redirect.yaml"

echo "==> Issuer: $ISSUER"
envsubst < "$DIR/issuers/clusterissuer-$ISSUER.yaml" | kubectl apply -f -

echo "==> Certificate (domain: $DOMAIN)"
sed "s/letsencrypt-staging/$ISSUER/" "$DIR/certificates/certificate-letsencrypt.yaml" | envsubst | kubectl apply -f -

echo "==> Odotetaan serttiä..."
kubectl wait --for=condition=Ready certificate/mlops-tls -n istio-system --timeout=300s
echo "Valmis: mlops-tls Ready (issuer: $ISSUER, domain: $DOMAIN)."