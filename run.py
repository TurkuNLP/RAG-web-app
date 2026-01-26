import os
from importlib import import_module


APP_REGISTRY = {
    "local": {"module": "local_app", "app": "local_app", "init": "init_app", "port": 5000},
    "seus": {"module": "seus_app", "app": "seus_app", "init": "init_app", "port": 6666},
    "arch-ru": {"module": "arch_ru_app", "app": "arch_ru_app", "init": "init_app", "port": 6667},
    "arch-en": {"module": "arch_en_app", "app": "arch_en_app", "init": "init_app", "port": 6668},
    "news": {"module": "news_app", "app": "news_app", "init": "init_app", "port": 6669},
    "law": {"module": "law_app", "app": "law_app", "init": "init_app", "port": 6670},
}


def load_app(app_name):
    if app_name not in APP_REGISTRY:
        available = ", ".join(sorted(APP_REGISTRY.keys()))
        raise SystemExit(
            f"Unknown APP_NAME '{app_name}'. Available: {available}"
        )

    config = APP_REGISTRY[app_name]
    module = import_module(config["module"])
    app = getattr(module, config["app"])
    init_fn = getattr(module, config["init"], None)
    if callable(init_fn):
        init_fn()
    return app, config["port"]


def strtobool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def main():
    app_name = os.environ.get("APP_NAME", "local")
    host = os.environ.get("HOST", "0.0.0.0")
    app, default_port = load_app(app_name)
    port = int(os.environ.get("PORT", default_port))
    debug = strtobool(os.environ.get("DEBUG"), default=False)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
