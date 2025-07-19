curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "'"${WEBHOOK_URL}"'",
           "secret_token": "'"${WEBHOOK_SECRET}"'",
           "drop_pending_updates": true
         }'