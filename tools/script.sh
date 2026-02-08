curl -s -v http://www.nwu.ac.za
dig A www.nwu.ac.za +short
python3 -c "import requests; for i in range(1000); requests.get('http://www.nwu.ac.za')"
