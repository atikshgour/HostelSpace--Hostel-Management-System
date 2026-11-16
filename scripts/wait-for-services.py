"""Owner: Atiksh Gour | US-20: fail if either isolated test service is unavailable."""
import time
from urllib.error import URLError
from urllib.request import urlopen

for url in ['http://127.0.0.1:8000/api/health/', 'http://127.0.0.1:3000/login']:
    for attempt in range(60):
        try:
            with urlopen(url, timeout=2) as response:  # nosec B310 -- fixed local test endpoints
                if response.status == 200:
                    break
        except (URLError, TimeoutError):
            pass
        time.sleep(1)
    else:
        raise SystemExit('Test service failed readiness: ' + url)
