#!/bin/bash
# File: build.sh
# Maintainer: Vintage Warhawk
# Last Edit: 2025-11-17
#
# Description:
# This shell script builds and starts the Discord bot Docker container on Linux/macOS.
# It prompts the user for their Discord bot token, sets it as an environment variable,
# and runs docker-compose to build and launch the container. Includes basic error handling.

# -----------------------------
# Function to prompt for Discord token
# -----------------------------
prompt_token() {
    read -p "Please enter your Discord Token: " DISCORD_TOKEN
    echo "Using token: $DISCORD_TOKEN"

    while true; do
        echo "Do you want to continue (Y), exit (N), or change token (E)?"
        read -n1 -r choice
        echo
        case "$choice" in
            [Yy])
                continue_action
                break
                ;;
            [Nn])
                exit_action
                break
                ;;
            [Ee])
                prompt_token
                break
                ;;
            *)
                echo "Invalid choice. Please enter Y, N, or E."
                ;;
        esac
    done
}

# -----------------------------
# Function to continue with Docker compose
# -----------------------------
continue_action() {
    echo "Creating Discord bot..."
    # Pass the token as an environment variable to Docker Compose
    DISCORD_TOKEN="$DISCORD_TOKEN" docker compose up -d --build
    if [ $? -ne 0 ]; then
        echo "An error occurred while building or starting the container."
        exit_action
    fi
    echo "Done. Press Enter to exit."
    read
    exit 0
}

# -----------------------------
# Function to exit the script
# -----------------------------
exit_action() {
    echo "Exiting."
    exit 0
}

# -----------------------------
# Start the script
# -----------------------------
prompt_token
