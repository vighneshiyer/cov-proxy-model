from typing import Tuple, Dict, Union
from pydantic import BaseModel
import random


def int_value(value: int) -> Tuple[range, int]:
    return range(value, value+1), value


def bool_knob(default: int) -> Tuple[range, int]:
    return range(0, 2), default


def disabled_bool_knob() -> Tuple[range, int]:
    return range(0, 1), 0


def enabled_bool_knob() -> Tuple[range, int]:
    return range(1, 2), 1


# Map from knob name to tuple of (allowable range, default value)
riscv_dv_opts: Dict[str, Union[Tuple[range, int], str]] = {
    "num_of_tests": int_value(1),
    # this is an 'int', but I think it should be a bool (enables random PTEs to set exception bits)
    "enable_page_table_exception": bool_knob(0),
    # no interrupts for now
    "enable_interrupt": disabled_bool_knob(),
    "enable_nested_interrupt": disabled_bool_knob(),
    "enable_timer_irq": disabled_bool_knob(),
    # it might be better if this was fixed
    "num_of_sub_program": (range(1, 10), 5),
    # ditto, larger inst cnt can unfairly favor longer programs (NeurIPS paper has instances of instr_cnt above 10k)
    "instr_cnt": (range(100, 20000), 200),
    "no_ebreak": bool_knob(1),
    # can't have arbitrary ecalls
    "no_ecall": enabled_bool_knob(),
    "no_dret": bool_knob(1),
    # wfi will cause problems since we don't produce interrupts in the testharness
    "no_wfi": enabled_bool_knob(),
    "no_branch_jump": bool_knob(1),
    "no_load_store": bool_knob(1),
    # csr R/W could cause problems, check again later
    "no_csr_instr": bool_knob(1),
    # only use canonical sp as stack pointer (this shouldn't matter for functionality)
    "fix_sp": bool_knob(1),
    "use_push_data_section": bool_knob(0),
    "enable_illegal_csr_instruction": bool_knob(0),
    "enable_access_invalid_csr_level": bool_knob(0),
    "enable_misaligned_instr": bool_knob(0),
    "enable_dummy_csr_write": bool_knob(0),
    # no supervisor mode for us
    "allow_sfence_exception": disabled_bool_knob(),
    # never generate a data segment
    "no_data_page": enabled_bool_knob(),
    # enable directed instruction sequences, but we aren't using them anyways
    "no_directed_instr": disabled_bool_knob(),
    "no_fence": bool_knob(1),
    "no_delegation": enabled_bool_knob(),
    # we probably want to weight this towards the lower end (1000 is the actual max)
    "illegal_instr_ratio": (range(0, 100), 0),
    # ditto
    "hint_instr_ratio": (range(0, 100), 0),
    "gen_all_csrs_by_default": bool_knob(0),
    "gen_csr_ro_write": bool_knob(0),
    # "add_csr_write=" # these are only used to exercise custom CSRs
    # "remove_csr_write="
    # hard code to 1 HART
    "num_of_harts": int_value(1),
    "enable_unaligned_load_store": bool_knob(0),
    "force_m_delegation": disabled_bool_knob(),
    "force_s_delegation": disabled_bool_knob(),
    "require_signature_addr": disabled_bool_knob(),
    # "signature_addr" # doesn't need to be set if signature isn't being used
    "disable_compressed_instr": bool_knob(0),
    "randomize_csr": bool_knob(0),
    # TODO: this may be modified, but I will fix it to the default of 2
    "tvec_alignment": int_value(2),
    "gen_debug_section": disabled_bool_knob(),
    "bare_program_mode": disabled_bool_knob(),
    "num_debug_sub_program": int_value(0),
    "enable_ebreak_in_debug_rom": disabled_bool_knob(),
    "set_dcsr_ebreak": disabled_bool_knob(),
    "enable_debug_single_step": disabled_bool_knob(),
    # this only makes sense with supervisor mode enabled
    "set_mstatus_tw": disabled_bool_knob(),
    # unsure about this one
    "set_mstatus_mprv": bool_knob(0),
    # no FP, we're only using rv32imc
    "enable_floating_point": disabled_bool_knob(),
    "enable_vector_extension": disabled_bool_knob(),
    "enable_b_extension": disabled_bool_knob(),
    "enable_zba_extension": disabled_bool_knob(),
    "enable_zbb_extension": disabled_bool_knob(),
    "enable_zbc_extension": disabled_bool_knob(),
    "enable_zbs_extension": disabled_bool_knob(),
    # "+enable_bitmanip_groups=" # no bitmanip ext available on Rocket
    # fix machine mode for now
    "boot_mode": "m",
    # "march": # no need to define this as long as the target directory is included
}


class RiscvDvConfig(BaseModel):
    plusarg_config: Dict[str, str]
    seed: int


def gen_config(default_prob: float, seed: int) -> RiscvDvConfig:
    assert 0.0 <= default_prob <= 1.0
    plusarg_config: Dict[str, str] = {}
    for knob, distr in riscv_dv_opts.items():
        if isinstance(distr, str):
            plusarg_config[knob] = distr
        else:
            allowed_range = distr[0]
            default_value = distr[1]
            # Pick the default value with 'default_prob' likelihood
            if random.uniform(0, 1) < default_prob:
                plusarg_config[knob] = str(default_value)
            else:  # pick from allowed range
                plusarg_config[knob] = str(random.sample(allowed_range, 1)[0])
    return RiscvDvConfig(plusarg_config=plusarg_config, seed=seed)
