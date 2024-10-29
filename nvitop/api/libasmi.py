import atexit as _atexit
import amdsmi as _asmi
from amdsmi import AmdSmiInitFlags
from amdsmi import AmdSmiException
from typing import TYPE_CHECKING as _TYPE_CHECKING
from typing import TypeAlias as _TypeAlias
import ctypes as _ctypes
import logging

ASMIError: type[_asmi.AmdSmiException] = _asmi.AmdSmiException
ASMIDeviceHandle: _TypeAlias = _ctypes.c_void_p
"""
cp -r /opt/rocm/share/amd_smi ~/amd_smi
python3 -m pip install --user ~/amd_smi

"""

# The 'handle' of the devices may change frequently, so we need to get the handle every time we want to get the data

# def _lazy_init() -> None:
#     """Lazily initialize the NVML context.

#     Raises:
#         ASMIError_LibraryException


#     """
#     # export ROCM_PATH = /opt/rocm
#     # with __lock:
#     #     if __initialized:
#     #         return
#     try:
#         _asmi.amdsmi_init(AmdSmiInitFlags.INIT_AMD_GPUS)
#         # _atexit.register(_asmi.amdsmi_shut_down)
#     except AmdSmiException as e:
#         print(e)


def asmi_available() -> bool:
    return device_count() > 0


def device_count() -> int:
    _asmi.amdsmi_init()
    devices: list[ASMIDeviceHandle] = _asmi.amdsmi_get_processor_handles()
    _asmi.amdsmi_shut_down()
    return len(devices)


def get_uuid(index: int) -> str | None:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        uuid = _asmi.amdsmi_get_gpu_device_uuid(handle)
        _asmi.amdsmi_shut_down()
        return uuid
    except IndexError:
        return None
    except AmdSmiException as e:
        logging.error(f"get_uuid {e=}")
        return None
    

def get_driver_version() -> str:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[0]
        driver_info = _asmi.amdsmi_get_gpu_driver_info(handle)
        _asmi.amdsmi_shut_down()
        return driver_info['driver_version'] # driver_version, driver_date, driver_name
    except IndexError:
        return "No AMD GPU Found"
    except AmdSmiException as e:
        logging.error(f"get_driver_version {e=}")
        return "ERROR"


def get_device_name(index: int) -> str | None:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        asic_info = _asmi.amdsmi_get_gpu_asic_info(handle)
        _asmi.amdsmi_shut_down()
        # print(asic_info['market_name'])
        # print(hex(asic_info['vendor_id']))
        # print(hex(asic_info['device_id']))
        # print(hex(asic_info['rev_id']))
        # print(asic_info['asic_serial'])
        return asic_info['market_name']
    except AmdSmiException as e:
        logging.error(f"get_device_name {e=}")
        return None


def get_bdf(index: int) -> str | None:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        bdf: str = _asmi.amdsmi_get_gpu_device_bdf(handle)
        _asmi.amdsmi_shut_down()
        return bdf
    except AmdSmiException as e:
        logging.error(f"get_bdf {e=}")
        return None


def get_memory_info(index: int) -> (int, int):  # type: ignore
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        used = _asmi.amdsmi_get_gpu_memory_usage(handle, _asmi.AmdSmiMemoryType.VRAM)
        total = _asmi.amdsmi_get_gpu_memory_total(handle, _asmi.AmdSmiMemoryType.VRAM)
        _asmi.amdsmi_shut_down()
        return used, total
    except AmdSmiException as e:
        logging.error(f"get_memory_info {e=}")
        return 0, 0


def get_utilization_rates(index: int) -> (int, int):  # type: ignore
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        engine_usage = _asmi.amdsmi_get_gpu_activity(handle)
        _asmi.amdsmi_shut_down()
        return int(engine_usage['gfx_activity']), int(engine_usage['umc_activity'])
    except AmdSmiException as e:
        logging.error(f"get_utilization_rates {e=}")
        return -1, -1


def get_fan_speed(index: int) -> int | None:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        cur_speed = _asmi.amdsmi_get_gpu_fan_speed(handle, 0)
        max_speed = _asmi.amdsmi_get_gpu_fan_speed_max(handle, 0)
        _asmi.amdsmi_shut_down()
        print("cur fan speed:", cur_speed, "max fan speed:", max_speed)
        return cur_speed
    except AmdSmiException as e:
        logging.error(f"get_fan_speed {e=}")
        return None


def get_temperature(index: int) -> int | None:
    """
    return temp in millidegrees Celcius
    """
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        temp_metric = _asmi.amdsmi_get_temp_metric(handle, _asmi.AmdSmiTemperatureType.EDGE,
                                                   _asmi.AmdSmiTemperatureMetric.CURRENT)
        _asmi.amdsmi_shut_down()
        return temp_metric
    except AmdSmiException as e:
        logging.error(f"get_temperature {e=}")
        return None

def get_power_usage(index: int) -> int | None:
    """
    Watts
    """
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        power_info = _asmi.amdsmi_get_power_info(handle)
        logging.error(f"get power usage {handle=} {devices=} {power_info=}")
        _asmi.amdsmi_shut_down()
        return power_info['average_socket_power'] * 1000
    except AmdSmiException as e:
        logging.error(f"get_power_usage {e=}")
        return None

def get_power_cap(index: int) -> int | None:
    """
    Return Power Capability in Watts
    """
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        power_info = _asmi.amdsmi_get_power_cap_info(handle)
        _asmi.amdsmi_shut_down()
        return power_info['power_cap']
    except AmdSmiException as e:
        logging.error(f"get_power_cap {e=}")
        return None

def get_perf_level(index: int) -> str | None:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        perf_level = _asmi.amdsmi_get_gpu_perf_level(handle)
        _asmi.amdsmi_shut_down()
        return str(perf_level).replace("AMDSMI_DEV_PERF_LEVEL_", "").upper()[:3]
    except AmdSmiException as e:
        logging.error(f"get_perf_level {e=}")
        return None

def get_uncorrectable_ecc(index: int) -> int | None:
    try:
        _asmi.amdsmi_init()
        devices = _asmi.amdsmi_get_processor_handles()
        handle = devices[index]
        ecc_count = _asmi.amdsmi_get_gpu_total_ecc_count(handle)
        _asmi.amdsmi_shut_down()
        return ecc_count['uncorrectable_count']
    except AmdSmiException as e:
        logging.error(f"get_uncorrectable_ecc {e=}")
        return None