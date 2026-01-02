from kantan_agents.tracing import add_trace_processor, set_trace_processors


class DummyProcessor:
    def on_trace_start(self, trace):
        return None

    def on_trace_end(self, trace):
        return None

    def on_span_start(self, span):
        return None

    def on_span_end(self, span):
        return None

    def shutdown(self) -> None:
        return None

    def force_flush(self) -> None:
        return None


def test_tracing_reexport_accepts_processor():
    processor = DummyProcessor()
    add_trace_processor(processor)
    set_trace_processors([processor])
