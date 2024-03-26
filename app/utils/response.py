from app.schemas.general import ErrorResponse, ValidationErrorResponse

responses = {
    400: {
        "model": ErrorResponse,
        "description": "An error occurred. Check the error code and message.",
    },
    422: {
        "model": ValidationErrorResponse,
        "description": "Validation error. The input doesn't match the schema. Check the error code and message.",
    },
}
