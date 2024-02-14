"""
Reasonably helpful functions that can be often used.

"""

import csv
import datetime as dt
import numpy as np
import warnings
import json
import yaml
import xml.etree.ElementTree as ET


def _map_data_type(data_type):
    types_dict = {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "bool": bool,
    }
    return types_dict[data_type]


def check_int(value):
    """
    Returns True if value is an integer, otherwise returns False.

    Args:
        value (str): string to test

    Returns:
        bool: True if value is an integer
    """
    try:
        int(value)
        return True
    except ValueError:
        return False
    except:
        raise


def check_float(value):
    """
    Returns True if value is a float, otherwise returns False.

    Args:
        value (str): string to test

    Returns:
        bool: True if value is a float
    """
    try:
        float(value)
        return True
    except ValueError:
        return False
    except:
        raise


def check_type_convert(value, dtype):
    """
    Returns True if value is of type dtype, otherwise returns False.

    Args:
        value (str): string to test
        dtype (type): type to test

    Returns:
        bool: True if value can be of type dtype
    """
    try:
        dtype(value)
        return True
    except ValueError:
        return False
    except:
        raise


def read_csv_metadata(metafile):
    """
    Returns a dict from a csv with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): csv file with metadata, one attribute per line

    Returns:
        dict: metadata from csv as dictionary
    """
    with open(metafile, "rt") as meta:
        raw_metadata = {}  # empty dict
        metaread = csv.reader(meta)
        for row in metaread:
            if len(row) >= 2:
                raw_metadata[row[0]] = {"value": "", "append": "False", "type": "str"}
                n = None
                if row[-1].startswith("type=") or row[-1].startswith("append="):
                    raw_metadata[row[0]][row[-1].split("=")[0]] = row[-1].split("=")[1]
                    if row[-2].startswith("type=") or row[-2].startswith("append="):
                        n = -2
                        raw_metadata[row[0]][row[-2].split("=")[0]] = row[-2].split(
                            "="
                        )[1]
                    else:
                        n = -1
                raw_metadata[row[0]]["value"] = ",".join(row[1:n]).strip()
                raw_metadata[row[0]]["type"] = _map_data_type(
                    raw_metadata[row[0]]["type"]
                )
                raw_metadata[row[0]]["append"] = (
                    True if raw_metadata[row[0]]["append"].lower() == "true" else False
                )
    return raw_metadata


def read_json_metadata(metafile):
    """
    Returns a dict from a JSON with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): JSON file with metadata

    Returns:
        dict: metadata from JSON as dictionary
    """
    with open(metafile, "rt") as meta:
        raw_metadata = json.load(meta)
    for key, value in raw_metadata.items():
        # Convert all values to strings for now, type will convert later
        if not isinstance(value, dict):
            raw_metadata[key] = {"value": str(value), "type": "str", "append": "False"}
        elif not isinstance(value["value"], str):
            raw_metadata[key]["value"] = str(value["value"])
        # Set defaults if not present, convert where needed
        if "type" not in raw_metadata[key]:
            raw_metadata[key]["type"] = "str"
        raw_metadata[key]["type"] = _map_data_type(raw_metadata[key]["type"])
        if "append" not in raw_metadata[key]:
            raw_metadata[key]["append"] = False
        else:
            raw_metadata[key]["append"] = (
                True if raw_metadata[key]["append"].lower() == "true" else False
            )
    return raw_metadata


def read_yaml_metadata(metafile):
    """
    Returns a dict from a YAML with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): YAML file with metadata

    Returns:
        dict: metadata from YAML as dictionary
    """
    with open(metafile, "rt") as meta:
        raw_metadata = yaml.safe_load(meta)
    for key, value in raw_metadata.items():
        # Convert all values to strings for now, type will convert later
        if not isinstance(value, dict):
            raw_metadata[key] = {"value": str(value), "type": "str", "append": "False"}
        elif not isinstance(value["value"], str):
            raw_metadata[key]["value"] = str(value["value"])
        # Set defaults if not present, convert where needed
        if "type" not in raw_metadata[key]:
            raw_metadata[key]["type"] = "str"
        raw_metadata[key]["type"] = _map_data_type(raw_metadata[key]["type"])
        if "append" not in raw_metadata[key]:
            raw_metadata[key]["append"] = False
        else:
            raw_metadata[key]["append"] = (
                True if raw_metadata[key]["append"].lower() == "true" else False
            )
    return raw_metadata


def read_xml_metadata(metafile):
    """
    Returns a dict from a XML with metadata.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): XML file with metadata

    Returns:
        dict: metadata from XML as dictionary
    """
    raw_metadata = {}
    tree = ET.parse(metafile)
    root = tree.getroot()
    for child in root:
        raw_metadata[child.tag] = {"value": "", "append": False, "type": str}
        for subchild in child:
            if subchild.tag == "type":
                raw_metadata[child.tag]["type"] = _map_data_type(subchild.text)
            elif subchild.tag == "append":
                raw_metadata[child.tag]["append"] = (
                    True if subchild.text.lower() == "true" else False
                )
            elif subchild.tag == "value":
                raw_metadata[child.tag]["value"] = subchild.text
    return raw_metadata


def get_metadata(metafile):
    """
    Returns a dict from of metadata from file. Metadata can be in a CSV, JSON, YAML, or XML file.
    Can also include latitude and longitude variables if
    they are single values (e.g. point deployment).

    Args:
        metafile (file): file with metadata

    Returns:
        dict: metadata as dictionary
    """
    if metafile.endswith(".csv"):
        return read_csv_metadata(metafile)
    elif metafile.endswith(".json"):
        return read_json_metadata(metafile)
    elif metafile.endswith(".yaml") or metafile.endswith(".yml"):
        return read_yaml_metadata(metafile)
    elif metafile.endswith(".xml"):
        return read_xml_metadata(metafile)
    else:
        warnings.warn(
            "Unknown metadata file type, trying csv...", UserWarning, stacklevel=2
        )
        return read_csv_metadata(metafile)


def add_metadata_to_netcdf(ncfile, metadata_file=None):
    """
    Reads metadata from csv file using get_metadata, adds values to
    global attributes in netCDF file.
    Numbers in metadata file are converted to integers or floats unless
    they are strings in the format 'number' (e.g. '123').
    Can also include latitude and longitude variables if they are
    single values (e.g. point deployment), using update_variable function.

    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        metadata_file (file): csv file with metadata, one attribute per line
    """
    if metadata_file is not None:
        raw_metadata = get_metadata(metadata_file)
        for attr, attr_info in raw_metadata.items():
            value = attr_info["value"]
            append = attr_info["append"]
            valuetype = attr_info["type"]
            # if value can be converted to valuetype, do so, otherwise keep as string
            if check_type_convert(value, valuetype):
                value = valuetype(value)
            else:
                warnings.warn(
                    f"Value '{value}' for attribute '{attr}' could not be converted to type '{valuetype}'",
                    UserWarning,
                    stacklevel=2,
                )
            if attr in ncfile.ncattrs():
                ncfile.setncattr(attr, value)
            elif attr == "latitude" or attr == "longitude":
                update_variable(ncfile, attr, value)


def get_times(dt_times):
    """
    Returns all time units for AMOF netCDF files from series of datetime objects.

    Args:
        dt_times (list-like object): object with datetime objects for times

    Returns:
        lists: unix_times, day-of-year, years, months, days, hours, minutes, seconds
        floats: unix time of first and last times (time_coverage_start and
                 time_coverage_end)
        str: date in YYYYmmdd format of first time, (file_date)
    """
    unix_times = [i.replace(tzinfo=dt.timezone.utc).timestamp() for i in dt_times]
    doy = [i.timetuple().tm_yday for i in dt_times]
    years = [i.year for i in dt_times]
    months = [i.month for i in dt_times]
    days = [i.day for i in dt_times]
    hours = [i.hour for i in dt_times]
    minutes = [i.minute for i in dt_times]
    seconds = [i.second + i.microsecond / 1000000 for i in dt_times]
    time_coverage_start_dt = unix_times[0]
    time_coverage_end_dt = unix_times[-1]
    doy = list(
        np.array(doy)
        + np.array([i / 24 for i in hours])
        + np.array([i / (24 * 60) for i in minutes])
        + np.array([i / (24 * 60 * 60) for i in seconds])
    )
    file_date = ""
    if years[0] == years[-1]:
        file_date += str(years[0])
        if months[0] == months[-1]:
            file_date += str(zero_pad_number(months[0]))
            if days[0] == days[-1]:
                file_date += str(zero_pad_number(days[0]))
                if hours[0] == hours[-1]:
                    file_date += f"-{zero_pad_number(hours[0])}"
                    if minutes[0] == minutes[-1]:
                        file_date += str(zero_pad_number(minutes[0]))
                        if int(seconds[0]) == int(seconds[-1]):
                            file_date += str(zero_pad_number(int(seconds[0])))
    else:
        raise ValueError("Incompatible dates - data from over 2 years")
    return (
        unix_times,
        doy,
        years,
        months,
        days,
        hours,
        minutes,
        seconds,
        time_coverage_start_dt,
        time_coverage_end_dt,
        file_date,
    )


def update_variable(ncfile, ncfile_varname, data, qc_data_error=True):
    """
    Adds data to variable, and updates valid_min and valid_max
     variable attrs if they exist.

    Args:
        ncfile (netCDF Dataset): Dataset object of netCDF file.
        ncfile_varname (str): Name of variable in netCDF file.
        data (array or list): Data to be added to netCDF variable.
        qc_data_error (bool): Raise error if trying to add values to QC flag
                               variables that are not in the flag_values attribute.
                               Otherwise, just a warning is printed. Default True.
    """
    if "valid_min" in ncfile.variables[ncfile_varname].ncattrs():
        ncfile.variables[ncfile_varname].valid_min = np.float64(np.nanmin(data)).astype(
            ncfile.variables[ncfile_varname].datatype
        )
        ncfile.variables[ncfile_varname].valid_max = np.float64(np.nanmax(data)).astype(
            ncfile.variables[ncfile_varname].datatype
        )
    if (
        "qc" in ncfile_varname.lower()
        and "flag_values" in ncfile.variables[ncfile_varname].ncattrs()
    ):
        if not np.in1d(data, ncfile.variables[ncfile_varname].flag_values).all():
            valid_values = list(ncfile.variables[ncfile_varname].flag_values)
            msg = (
                "Invalid data being added to QC variable, "
                f"only {valid_values} are allowed."
            )
            if qc_data_error:
                raise ValueError(msg)
            else:
                print(f"[WARN]: {msg}")
    ncfile.variables[ncfile_varname][:] = data


def zero_pad_number(n):
    """
    Returns single digit number n as '0n'
    Returns multiple digit number n as 'n'
    Used for date or month strings

    Args:
        n (int): Number

    Returns:
        str: Number with zero padding if single digit.

    """
    if len(f"{n}") == 1:
        return f"0{n}"
    else:
        return f"{n}"
