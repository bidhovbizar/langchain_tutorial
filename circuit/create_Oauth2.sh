client_id=0oasijtht0KJw99dW5d7
client_secret=T3Pe7CWYpM2DSadIfVOYhQykxGG-Mz-fR_EKTGzTwBwFB1Fy0u_HaknaSudq9E5D
curl -X POST "https://id.cisco.com/oauth2/default/v1/token" \
-d "grant_type=client_credentials" \
-u "$client_id:$client_secret" \
-H "Content-Type: application/x-www-form-urlencoded" \
-H "Accept: */*"
