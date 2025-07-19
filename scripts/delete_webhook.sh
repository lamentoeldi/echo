curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" \
     -H "Content-Type: application/json" \
     -d '{"drop_pending_updates": true}'