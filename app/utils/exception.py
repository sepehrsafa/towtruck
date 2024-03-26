class TowTruckException(Exception):
    def __init__(self, code: str, http_status_code: int = 400):
        self.code = code
        self.message = exception_codes.get(code, "Unknown error")
        self.http_status_code = http_status_code

    def __str__(self):
        return f"TowTruckException: {self.code}"


exception_codes = {
    "E1000": "General error",
    "E1001": "Validation error",
    "E1002": "Incorrect identifier or password",
    "E1003": "Invalid phone number",
    "E1004": "Invalid email",
    "E1005": "Invalid password",
    "E1007": "Invalid token",
    "E1008": "Invalid refresh token",
    "E1009": "Invalid user",
    "E1012": "Invalid identifier. Must be an email or phone number in E.164 format",
    "E1016": "Token expired",
    "E1017": "Refresh token expired or invalid",
    "E1018": "Invalid Access Token",
    "E1019": "Invalid Refresh Token",
    "E1023": "Not found",
}
