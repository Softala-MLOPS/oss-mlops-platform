#!/bin/bash

# Navigate to the directory containing the script

# Install the requirements
pip install -r oss-mlops-platform/tools/CLI-tool/requirements.txt

read -p "Enter the organization name: " org_name

read -p "Enter the name of the config repo: " repo_name

while true; do
    echo "Select an option:"
    echo "Which script(s) would you like to run?"
    echo "1) Configure Github (GH) for the tool (configure_gh.py)"
    echo "2) Create configuration repo for one or more ML project working repos (setup_cli.py)"
    echo "3) Create one ML project working repo based on a configuration repo (fork_repo.py)"
    echo "4) Both (step 3 is based on config repo created in step 2)"
    echo "5) Exit"
    read -p "Enter your choice: " choice

    case $choice in
        1)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            ;;
        2)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            python3 oss-mlops-platform/tools/CLI-tool/setup_cli.py "$repo_name" "$org_name"
            ;;
        3)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            python3 oss-mlops-platform/tools/CLI-tool/fork_repo.py "$repo_name" "$org_name"
            ;;
        4)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            python3 oss-mlops-platform/tools/CLI-tool/setup_cli.py "$repo_name" "$org_name"
            python3 oss-mlops-platform/tools/CLI-tool/fork_repo.py "$repo_name" "$org_name"
            exit 0
            ;;
        5)
            echo "Exiting. Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done
