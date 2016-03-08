import datetime


def fix_date(datetime_string):
    """
    This function can be used to fix a datetime string where leading zeros of day and month have been left out.
    It can NOT however be used to explain why anyone would do this in the first place.
    Note: Ambiguous dates will be fixed to the date that comes FIRST in a year (e.g. 112 will be Feb 11 not Dec 1)
    """
    ds, ts = datetime_string[:-6], datetime_string[-6:]  # datestring and timestring
    d = datetime.datetime.strptime(ds, "%d%m%Y")  # Parse to datetime object
    return "%0.2d%0.2d%0.4d" % (d.day, d.month, d.year) + ts  # Print datetime object and concat with timestring


def convert_to_datetime(string):
    return datetime.datetime.strptime(string, "%d%m%Y%H%M%S")


def sort_filenames(image_list):
    date_dict = {
        image_name: convert_to_datetime(fix_date(image_name.split("/")[-1].split(".")[0])) for image_name in image_list
    }
    sorted_image_list = sorted(image_list, key=date_dict.get)
    time_list = [
        round((date_dict[name] - date_dict[sorted_image_list[0]]).total_seconds() / 60) for name in sorted_image_list
    ]
    return time_list, sorted_image_list
