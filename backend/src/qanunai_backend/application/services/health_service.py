from qanunai_backend.domain.entities.legal_question import LegalQuestion


class HealthService:
    def ping(self) -> dict[str, str]:
        sample = LegalQuestion(text="health")
        return {"status": "ok", "sample": sample.text}
