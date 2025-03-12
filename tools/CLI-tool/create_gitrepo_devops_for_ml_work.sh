#!/bin/bash
set -e
# Navigate to the directory containing the script

# Install the requirements
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r oss-mlops-platform/tools/CLI-tool/requirements.txt

read -p "Enter the organization name: " org_name

read -p "Enter the name of the config repo: " repo_name

while true; do
    echo "Select an option:"
    echo "Which script(s) would you like to run?"
    echo "1) Configure Github (GH) for the tool (configure_gh.py)"
    echo "2) Create configuration repo for one or more ML project working repos (create_config_repo.py)"
    echo "3) Create one ML project working repo based on a configuration repo (create_working_repo.py)"
    echo "4) Both (step 3 is based on config repo created in step 2) 🟢 RECOMMENDED 🟢"
    echo "5) Exit"
    read -p "Enter your choice: " choice

    case $choice in
        1)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            ;;
        2)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            python3 oss-mlops-platform/tools/CLI-tool/create_config_repo.py "$repo_name" "$org_name"
            ;;
        3)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            python3 oss-mlops-platform/tools/CLI-tool/create_working_repo.py "$repo_name" "$org_name"
            exit 0
            ;;
        4)
            python3 oss-mlops-platform/tools/CLI-tool/configure_gh.py
            python3 oss-mlops-platform/tools/CLI-tool/create_config_repo.py "$repo_name" "$org_name"
            python3 oss-mlops-platform/tools/CLI-tool/create_working_repo.py "$repo_name" "$org_name"
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
