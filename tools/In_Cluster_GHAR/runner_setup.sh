#!/bin/bash
set -eoa pipefail

if ! [[ $(which jq) ]]; then
	echo "please install jq"
	exit 1
fi

#TODO please add auth
#read -p "please type in your organization: " org
#read -p "please type in your repository's name: " repo
org=ecremotedemo
repo=ecdemowork

token=$(gh api --method POST repos/$org/$repo/actions/runners/registration-token | jq -r '.token')
echo $token
deploy_runner()
{
	if ! [[ $(kubectl get namespace actions-runner) ]]; then
		kubectl create namespace actions-runner
	fi
	echo "Creating kubernetes secret"
	kubectl create secret generic github-runner-secrets --from-literal=GITHUB_TOKEN=$token --from-literal=GITHUB_URL="https://github.com/$org/$repo" -n actions-runner
 	kubectl apply -f github-runner-deployment.yaml

}

if kubectl delete deployment github-runner --namespace=actions-runner; then
	if kubectl delete secret github-runner-secrets --namespace actions-runner; then
			echo "Reinstalling the github-runner"
			deploy_runner
	else
		echo "Reinstalling the github-runner"
		deploy_runner
	fi
else
	if kubectl delete secret github-runner-secrets --namespace actions-runner; then
		echo "No in cluster runner was found..."
		echo "Creating new in cluster runner"
		deploy_runner
	else
		echo "No in cluster runner was found..."
		echo "Creating new in cluster runner"
		deploy_runner
	fi
fi


