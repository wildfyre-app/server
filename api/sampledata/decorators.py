def register():
    from . import sampledata

    def _register_wrapper(func):
        sampledata.register(func)
        return func
    return _register_wrapper
