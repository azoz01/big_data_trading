from typing import Any, Type


class ProcessRegistry:

    def __init__(self):
        self.processess_mapping = dict()

    def __call__(self, process_name: str) -> Type[Any]:
        def decorator(process_class_: Type[Any]):
            assert hasattr(process_class_, "execute"), "Process class should have execute method"
            self.processess_mapping[process_name] = process_class_

        return decorator

    def execute(self, process_name: str) -> None:
        return self.processess_mapping[process_name].execute()


process_registry = ProcessRegistry()
