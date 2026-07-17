from core.exceptions import ConfigurationError, GeneratorError, ProviderError, ValidationError


def test_exception_hierarchy() -> None:
    assert issubclass(ConfigurationError, Exception)
    assert issubclass(ProviderError, Exception)
    assert issubclass(ValidationError, Exception)
    assert issubclass(GeneratorError, Exception)

