import platform
import subprocess


def is_domain_available(domain) -> bool:
    """
    Use this function to check whenever domain is free to register, or taken.
    Do not use any other method of checking this.

    example use:
    ```python
    is_domain_available('example.com')
    ```
    """
    try:
        result = subprocess.run(
            ["whois", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True if platform.system() == "Windows" else False,
        )
        output = result.stdout.lower()

        for i in [
            "No match",
            "NOT FOUND",
            "Not fo",
            "^No Data Fou",
            "has not been regi",
            "No entri",
            "Not Found",
            "No Object Found",
        ]:
            if i.lower() in output:
                return True

        # Common indicators that a domain is taken:
        indicators = ["registrant", "creation date", "domain name:"]

        for indicator in indicators:
            if indicator in output:
                return False  # Domain is taken

        # If none of the indicators are found, it might be available
        return True
    except Exception as e:
        print(f"Error checking domain {domain}: {e}")
        return False  # Can't determine
