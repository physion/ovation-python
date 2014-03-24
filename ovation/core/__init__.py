from ovation import autoclass

NumericDataElements = autoclass("us.physion.ovation.domain.NumericDataElements")
NumericData = autoclass("us.physion.ovation.values.NumericData")

Logging = autoclass("us.physion.ovation.logging.Logging")

### Common references outside the us.physion.ovation namespace

# java.
Integer = autoclass("java.lang.Integer")
Double = autoclass("java.lang.Double")
Map = autoclass("java.util.Map")
URL = autoclass("java.net.URL")
URI = autoclass("java.net.URI")
File = autoclass("java.io.File")
TimeUnit = autoclass("java.util.concurrent.TimeUnit")

# org.joda
DateTime = autoclass("org.joda.time.DateTime")
DateTimeZone = autoclass("org.joda.time.DateTimeZone")
DateTimeFormat = autoclass("org.joda.time.format.DateTimeFormat")

# com.google.common
Sets = autoclass("com.google.common.collect.Sets")
Maps = autoclass("com.google.common.collect.Maps")
Optional = autoclass("com.google.common.base.Optional")


def date_time(year, month, day, hour=0, minute=0, second=0, millis=0, zone=None):
    if zone is None:
        zone = DateTimeZone.getDefault()
    else:
        zone = DateTimeZone.forID(zone)
    
    return DateTime(year, month, day, hour, minute, second, millis, zone)