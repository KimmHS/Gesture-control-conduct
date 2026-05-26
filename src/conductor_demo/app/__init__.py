__all__ = ["AppRunner"]


def __getattr__(name: str):
    if name == "AppRunner":
        from .runner import AppRunner

        return AppRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
