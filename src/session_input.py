from dataclasses import dataclass, asdict, field
from typing import Dict, Optional

from .utils import read_file

@dataclass
class SessionInput:
    rtl_files: Dict[str, str]
    libre_config: Optional[str] = None
    timing_constraints: Optional[str] = None
    testbench_scripts: Dict[str, str] = field(default_factory=dict)
    system_config: Optional[str] = None
    extra_info: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def create_input(data_path):
    return SessionInput(
        rtl_files={"rtl.v": read_file(f"{data_path}/rtl.v")},
        libre_config=read_file(f"{data_path}/libre_config.mk"),
        timing_constraints=read_file(f"{data_path}/timing_constraints.sdc"),
        testbench_scripts={"tb.v": read_file(f"{data_path}/tb.v")},
        system_config=read_file(f"{data_path}/optimization_config.yaml"),
        extra_info={"objective": "Improve the power performance"}
    )