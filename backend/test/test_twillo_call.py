import requests

if __name__ == "__main__":
    response = requests.post(
        "http://localhost:8000/api/calls/outbound",
        json={"to_number": "+12166003962"}  # 你的手机号
    )
    print(response.json())
