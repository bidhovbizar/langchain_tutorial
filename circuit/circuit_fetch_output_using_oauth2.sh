access_token=eyJraWQiOiI5NGU4cmxzTzUyUmhoc1RfWDNVMkRvb1lFS2xRTzZlaFRaM3NVajBVUXpnIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULkdHamNoVDBPWUFBWGZVYl9PLUhHdDIweFV0eC1wOWZmTmNtUTlaSWR3V28iLCJpc3MiOiJodHRwczovL2lkLmNpc2NvLmNvbS9vYXV0aDIvZGVmYXVsdCIsImF1ZCI6ImFwaTovL2RlZmF1bHQiLCJpYXQiOjE3Njg5OTI2NTMsImV4cCI6MTc2ODk5NjI1MywiY2lkIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJzY3AiOlsiY3VzdG9tc2NvcGUiXSwic3ViIjoiMG9hc2lqdGh0MEtKdzk5ZFc1ZDciLCJhenAiOiIwb2FzaWp0aHQwS0p3OTlkVzVkNyJ9.ihG-fYi1ec5g-DVNge8zeNThvB2IIGExaKl2NEMuMAbfTAwkXSeQF8_oFoyJ21aTQR4awEu_08iSEQ8hjDrL4H4GdKcinM3lHBNW4C2eNGYRXVl2rccVl9SaG1F_CDcLcGnp-2nnF-Or3CMNhBmHDDtpWW1vPE9w8JLHwyzVNLJcgmiJrbETKtvrveeqYZGWfZWJ6tJmAuYgTjK7O2FghZPO2jTXPoQE4sdZ9AMrrbaUS6NWn72zLZCz297cJ3-RMIiH9IBqdiLTyJlS-q3re4IIJuIqPwmTpODGVjzlhtNHnupogJ5ETA2OAoAlpKTbRzyyVEIieYuWMVcIn_fA3g
appkey=egai-prd-networking-123120833-summarize-1768589443863
model=gpt-4.1
curl --location "https://chat-ai.cisco.com/openai/deployments/$model/chat/completions" \
--request POST \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "api-key: $access_token" \
--data "{
  \"messages\": [
    {
      \"role\": \"system\",
      \"content\": \"You are a chatbot\"
    },
    {
      \"role\": \"user\",
      \"content\": \"what is the capital of France?\"
    }
  ],
  \"user\": \"{\\\"appkey\\\":\\\"$appkey\\\"}\",
  \"stop\": [\"<|im_end|>\"]
}"
