# CallingJournal

AI-powered calling journal system for conversation logging, summarization, and local domain knowledge extraction.


## Environment Setup
python version required: 3.12

Install dependencies in your virtual environment:
   ```bash
   pip install -r requirements.txt
   ```


```call

curl -X POST "http://localhost:8000/calls" \
     -H "Content-Type: application/json" \
     -d '{
           "phone_number": "+14085023851",
           "callback_url": "https://sku-risks-computers-discussions.trycloudflare.com/webhooks/twilio/voice"
         }'

```