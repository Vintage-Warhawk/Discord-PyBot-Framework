#!/bin/bash

# Function to prompt for Discord token
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

# Function to continue with Docker compose
continue_action() {
    echo "Creating Discord bot..."
    # Pass the token as an environment variable
    DISCORD_TOKEN="$DISCORD_TOKEN" docker compose up -d --build
    if [ $? -ne 0 ]; then
        echo "An error occurred while building or starting the container."
        exit_action
    fi
    echo "Done. Press Enter to exit."
    read
    exit 0
}

# Function to exit
exit_action() {
    echo "Exiting."
    exit 0
}

# Start the script
prompt_token
