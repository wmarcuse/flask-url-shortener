curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com", "shortcode": "aqwert"}' http://127.0.0.1:5000/shorten
Okay

curl -X POST -H "Content-Type: application/json" -d '{"shortcode": "aqwert"}' http://127.0.0.1:5000/shorten
url not present

curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.covm", "shortcode": "aqwer"}' http://127.0.0.1:5000/shorten
Invalid shortcode

curl -i -X GET http://127.0.0.1:5000/aqwer_
redirect

als url exist other shortcode wanted, retuns nu already existing shortcode