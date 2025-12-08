import os
from ddtrace import patch_all, tracer

def initialize_datadog():
    tracer.configure(
        hostname="localhost",
        port=8126,
    )
    patch_all()