import importlib
from unittest.mock import Mock


def test_generate_ai_market_summaries_all_returns_per_provider(monkeypatch):
    mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')
    ai_mod = importlib.import_module('ai_model_config')

    # Make two providers available
    monkeypatch.setattr(ai_mod, 'get_available_providers', lambda: [ai_mod.AIProvider.GEMINI, ai_mod.AIProvider.OPENAI])

    # Return a single dummy model for each provider
    def fake_get_models(provider):
        return [ai_mod.AIModelInfo(
            provider=provider,
            model_id=f"{provider.name}-test",
            display_name="TestModel",
            description="",
            tier="lite",
            input_token_limit=1,
            output_token_limit=1
        )]

    monkeypatch.setattr(ai_mod, 'get_models_by_provider', fake_get_models)

    # call_ai_model should return a provider-specific string
    # accept session_key and other kwargs to match production call signature
    def fake_call_ai(model_info, prompt, max_tokens=0, temperature=0, session_key=None, **kwargs):
        return f"response-from-{model_info.provider.name}"

    monkeypatch.setattr(ai_mod, 'call_ai_model', fake_call_ai)

    result = mod.generate_ai_market_summaries_all({}, {}, {}, {}, {}, {}, {})

    assert isinstance(result, dict)
    assert ai_mod.AIProvider.GEMINI.value in result
    assert ai_mod.AIProvider.OPENAI.value in result
    assert result[ai_mod.AIProvider.GEMINI.value]['response'] == 'response-from-GEMINI'


def test_render_ai_market_intelligence_shows_each_provider(monkeypatch):
    mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')

    # Prepare a fake multi-provider response
    fake_responses = {
        'Google Gemini': {'model': 'gem-1', 'response': 'Gemini summary text'},
        'OpenAI': {'model': 'gpt-4', 'response': 'OpenAI summary text'}
    }

    # Patch the generator to return our fake responses
    monkeypatch.setattr(mod, 'generate_ai_market_summaries_all', lambda *args, **kwargs: fake_responses)

    # Create a dummy Streamlit-like API that records expanders and writes
    class DummyST:
        def __init__(self):
            self.session_state = {'enable_ai_features': True, 'ai_market_prompt': 'short prompt'}
            self.writes = []
            self.expanders = []

        def markdown(self, *args, **kwargs):
            return None

        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def caption(self, *args, **kwargs):
            return None

        def text_area(self, *args, **kwargs):
            # simulate writing to session_state
            return self.session_state.get('ai_market_prompt')

        def expander(self, label, expanded=False):
            self.expanders.append(label)

            class _Ctx:
                def __enter__(inner_self):
                    # set a marker so writes know the active expander
                    self._active = label
                    return inner_self

                def __exit__(inner_self, exc_type, exc, tb):
                    self._active = None
                    return False

            return _Ctx()

        def write(self, txt):
            active = getattr(self, '_active', None)
            self.writes.append((active, txt))

        def columns(self, *args, **kwargs):
            # used elsewhere in the page — return simple context managers
            class Ctx:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            return (Ctx(), Ctx())

        def button(self, *args, **kwargs):
            return False

        def spinner(self, *args, **kwargs):
            class _Spin:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            return _Spin()

    dummy = DummyST()

    # Patch the module's st and app_utils.st to avoid touching real Streamlit
    monkeypatch.setattr(mod, 'st', dummy)
    monkeypatch.setattr('app_utils.st', dummy)

    # Call the renderer — it should populate expanders and writes
    mod.render_ai_market_intelligence({}, {}, {}, {}, {}, {}, {})

    # Make sure we saw expanders for each provider and their responses were written
    assert any('Google Gemini' in e for e in dummy.expanders)
    assert any('OpenAI' in e for e in dummy.expanders)

    # Check writes were produced for the provider responses
    written_texts = [w[1] for w in dummy.writes]
    assert 'Gemini summary text' in written_texts
    assert 'OpenAI summary text' in written_texts
