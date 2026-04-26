# In-Cluster Setup

The current setup for the in-cluster is done through the script located in the same folder.

## Limitations
- It doesn't have user input validation.
- Relies on GitHub API to generate the token.
- Requires `jq` to be installed for it to work.
- Requires the script to be run again every time the platform shuts down and restarts, as the YAML config does not save the old configuration like the manual runner installation.
- A new config is required every 24 hours after the last script run if the system is shut down.
- The script manages various tasks in the setup process.

## Possible Further Development Paths
- Implement user input validation and a logging mechanism.
- Consider rewriting the script in Python instead of Bash to make bug detection easier.
- Explore ways to make the token infinite or use a Personal Access Token instead of the one generated solely for this purpose.
