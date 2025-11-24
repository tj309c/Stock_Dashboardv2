import importlib


def test_call_ai_model_returns_failed_when_openai_missing(monkeypatch):
    ai = importlib.import_module('ai_model_config')

    # Simulate missing openai SDK
    monkeypatch.setattr(ai, 'OpenAI', None)

    # Use a real model id from the catalog so create_model_client reaches the SDK-check path
    model_info = ai.AIModelInfo(
        provider=ai.AIProvider.OPENAI,
        model_id='gpt-3.5-turbo',
        display_name='Test',
        description='',
        tier='lite',
        input_token_limit=1,
        output_token_limit=1
    )

    res = ai.call_ai_model(model_info, 'hello')
    assert isinstance(res, str)
    assert res.startswith('failed:')
    assert 'openai SDK is not available' in res


def test_call_ai_model_returns_failed_when_anthropic_missing(monkeypatch):
    ai = importlib.import_module('ai_model_config')

    # Simulate missing anthropic SDK
    monkeypatch.setattr(ai, 'anthropic', None)

    # Use a real Claude model id from the catalog
    model_info = ai.AIModelInfo(
        provider=ai.AIProvider.CLAUDE,
        model_id='claude-3-5-haiku-20241022',
        display_name='Test',
        description='',
        tier='lite',
        input_token_limit=1,
        output_token_limit=1
    )

    res = ai.call_ai_model(model_info, 'hello')
    assert isinstance(res, str)
    assert res.startswith('failed:')
    assert 'anthropic SDK is not available' in res


def test_call_ai_model_returns_failed_when_openai_missing_for_grok(monkeypatch):
    ai = importlib.import_module('ai_model_config')

    # Simulate missing OpenAI SDK (used for GROK)
    monkeypatch.setattr(ai, 'OpenAI', None)

    # Use a real Grok model id from the catalog
    model_info = ai.AIModelInfo(
        provider=ai.AIProvider.GROK,
        model_id='grok-beta',
        display_name='Test',
        description='',
        tier='lite',
        input_token_limit=1,
        output_token_limit=1
    )

    res = ai.call_ai_model(model_info, 'hello')
    assert isinstance(res, str)
    assert res.startswith('failed:')
    assert 'openai SDK is not available for GROK' in res
