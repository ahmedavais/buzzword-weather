from typing import Generic, TypeVar

Response = TypeVar("Response")


class ConfigurableResponses(Generic[Response]):
    def __init__(self, responses: Response | list[Response], name: str):
        self._repeating = not isinstance(responses, list)
        self._responses = responses if isinstance(responses, list) else [responses]
        self._name = name

    def next(self) -> Response:
        if self._repeating:
            return self._responses[0]
        assert self._responses, f"No more responses configured in {self._name}"
        return self._responses.pop(0)
