#!/bin/bash

# Define variables
HOST="http://127.0.0.1:8000"
TOKEN="yourtoken"

# Function to send curl requests with timeout
send_curl_request() {
    local url=$1
    local timeout=$2

    echo "Sending request to $url with a timeout of $timeout seconds..."
    curl --max-time $timeout "$url"
}

# Check if a parameter is passed
if [ $# -eq 0 ]; then
    echo "Error: No parameter provided"
    exit 1
fi

# Handle different parameters
case "$1" in
    morning)
        send_curl_request "$HOST/api/tickets/morning?token=$TOKEN" 60
        ;;
    evening)
        send_curl_request "$HOST/api/tickets/evening?token=$TOKEN" 60
        ;;
    resend)
        send_curl_request "$HOST/api/tickets/resend?token=$TOKEN" 1800  # 30 minutes in seconds
        ;;
    check)
        send_curl_request "$HOST/api/google-sheet/responses?token=$TOKEN" 900  # 15 minutes in seconds
        ;;
    *)
        echo "Error: Invalid parameter. Use one of the following: morning, evening, resend, check"
        exit 1
        ;;
esac
