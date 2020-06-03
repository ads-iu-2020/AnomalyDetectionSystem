from dataclasses import dataclass, field


@dataclass
class MetricsResponse:
    average_cpu: float
    max_cpu: float
    average_memory: float
    max_memory: float

    lines_added: int
    lines_deleted: int
    changed_files: int
