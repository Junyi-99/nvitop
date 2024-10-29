import atexit as _atexit
import amdsmi as _asmi
from amdsmi import AmdSmiInitFlags
from amdsmi import AmdSmiException
from typing import TYPE_CHECKING as _TYPE_CHECKING
from typing import TypeAlias as _TypeAlias
import ctypes as _ctypes
ASMIError: type[_asmi.AmdSmiException] = _asmi.AmdSmiException
ASMIDeviceHandle: _TypeAlias = _ctypes.c_void_p
"""
cp -r /opt/rocm/share/amd_smi ~/amd_smi
python3 -m pip install --user ~/amd_smi

"""


def _lazy_init() -> None:
    """Lazily initialize the NVML context.

    Raises:
        ASMIError_LibraryException


    """
    # export ROCM_PATH = /opt/rocm
    # with __lock:
    #     if __initialized:
    #         return
    try:
        _asmi.amdsmi_init(AmdSmiInitFlags.INIT_AMD_GPUS)
        _atexit.register(_asmi.amdsmi_shut_down)
    except AmdSmiException as e:
        print(e)


def asmi_available() -> bool:
    _lazy_init()
    return device_count() > 0


def device_count() -> int:
    _lazy_init()

    devices: list[ASMIDeviceHandle] = _asmi.amdsmi_get_processor_handles()
    return len(devices)


def device_handle(index: int) -> ASMIDeviceHandle:
    devices = _asmi.amdsmi_get_processor_handles()
    if index > len(devices):
        raise ASMIError("index out of range")
    return devices[index]


def get_uuid(handle: ASMIDeviceHandle) -> str:
    return _asmi.amdsmi_get_gpu_device_uuid(handle)


def get_driver_version() -> str:
    try:
        handle = device_handle(0)
        driver_info = _asmi.amdsmi_get_gpu_driver_info(handle)
        return driver_info['driver_version'] # driver_version, driver_date, driver_name
    except AmdSmiException as e:
        print(e)


def get_device_name(handle: ASMIDeviceHandle) -> str | None:
    try:
        asic_info = _asmi.amdsmi_get_gpu_asic_info(handle)
        print(asic_info['market_name'])
        print(hex(asic_info['vendor_id']))
        print(hex(asic_info['device_id']))
        print(hex(asic_info['rev_id']))
        print(asic_info['asic_serial'])
        return asic_info['market_name']
    except AmdSmiException as e:
        print(e)
        return None


def get_bdf(handle: ASMIDeviceHandle) -> str | None:
    try:
        bdf: str = _asmi.amdsmi_get_gpu_device_bdf(handle)
        return bdf
    except AmdSmiException as e:
        print(e)
        return None


def get_memory_info(handle: ASMIDeviceHandle) -> (int, int):  # type: ignore
    try:
        used = _asmi.amdsmi_get_gpu_memory_usage(handle, _asmi.AmdSmiMemoryType.VRAM)
        total = _asmi.amdsmi_get_gpu_memory_total(handle, _asmi.AmdSmiMemoryType.VRAM)
        return used, total
    except AmdSmiException as e:
        print(e)
        return 0, 0


def get_utilization_rates(handle: ASMIDeviceHandle) -> (int, int):  # type: ignore
    """

    """

    try:
        gfx = _asmi.amdsmi_get_utilization_count(handle, _asmi.AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY)
        mem = _asmi.amdsmi_get_utilization_count(handle, _asmi.AmdSmiUtilizationCounterType.COARSE_GRAIN_MEM_ACTIVITY)
        return gfx, mem
    except AmdSmiException as e:
        print("get_utilization_rates", e)
        return 0, 0


def get_fan_speed(handle: ASMIDeviceHandle) -> int | None:
    try:
        cur_speed = _asmi.amdsmi_get_gpu_fan_speed(handle, 0)
        max_speed = _asmi.amdsmi_get_gpu_fan_speed_max(handle, 0)
        print("cur fan speed:", cur_speed, "max fan speed:", max_speed)
        return cur_speed
    except AmdSmiException as e:
        # print("get_fan_speed", e)
        return None


def get_temperature(handle: ASMIDeviceHandle) -> int | None:
    """
    return temp in millidegrees Celcius
    """
    try:
        temp_metric = _asmi.amdsmi_get_temp_metric(handle, _asmi.AmdSmiTemperatureType.EDGE,
                                                   _asmi.AmdSmiTemperatureMetric.CURRENT)
        return temp_metric
    except AmdSmiException as e:
        print("get_temperature", e)
        return None

def get_power_usage(handle: ASMIDeviceHandle) -> int | None:
    try:
        power_info = _asmi.amdsmi_get_power_info(handle)
        return power_info['average_socket_power']
    except AmdSmiException as e:
        return None

def get_power_cap(handle: ASMIDeviceHandle) -> int | None:
    """
    Return Power Capability in Watts
    """
    try:
        power_info = _asmi.amdsmi_get_power_cap_info(handle)
        return power_info['power_cap']
    except AmdSmiException as e:
        return None