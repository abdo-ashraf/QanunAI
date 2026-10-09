class AssistantUnavailableError(Exception):
    """The assistant could not produce an answer.

    Raised when an external provider the assistant depends on (LLM or
    embedding API) fails or responds unexpectedly, e.g. an empty response
    caused by exhausted provider credits.

    The underlying cause is logged by the infrastructure adapter. The
    presentation layer maps this error to an HTTP 503 response.
    """
