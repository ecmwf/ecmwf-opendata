# ecmwf-opendata

`ecmwf-opendata` is a package to simplify the download of ECMWF [open data](https://www.ecmwf.int/en/forecasts/datasets/open-data). It implements a request-based interface to the dataset using ECMWF's MARS language to select meteorological fields, similar to the existing  [ecmwf-api-client](https://github.com/ecmwf/ecmwf-api-client) Python package.

A collection of Jupyter Notebooks that make use of that package is available [here](https://github.com/ecmwf/notebook-examples/tree/master/opencharts).

## Installation

The `ecmwf-opendata` Python package can be installed from PyPI with:

```$ pip install ecmwf-opendata```

## Usage
The example below will download the latest available 10-day forecast for the *mean sea level pressure* (`msl`) into a local file called `data.grib2`:

```python
from ecmwf.opendata import Client

client = Client()

client.retrieve(
    step=240,
    type="fc",
    param="msl",
    target="data.grib2",
)
```

> ❗ **NOTE:** This package is designed for users that want to download a subset of the whole dataset. If you plan to download a large percentage of each data file, it may be more efficient to download whole files and filter out the data you want locally. See the documentation on the [file naming convention](https://confluence.ecmwf.int/display/DAC/ECMWF+open+data%3A+real-time+forecasts+from+IFS+and+AIFS) for more information. Alternatively, you can use this tool to download whole files by only specifying `date`, `time`, `step`, `stream` and `type`. Please be aware that all data for a full day is in the order of 726 GiB.


## Options

The constructor of the client object takes the following options:

```python
client = Client(
    source="ecmwf",
    model="ifs",
    resol="0p25",
    preserve_request_order=False,
    infer_stream_keyword=True,
)
```

where:

- `source` is either the name of server to contact or a fully qualified URL. Possible values are `ecmwf` to access ECMWF's servers, `aws` for data hosted by Amazon Web Services, `google` for data hosted on Google Cloud Platform, or `azure` to access data hosted on Microsoft's Azure. Default is `ecmwf`.

 > ⚠️ **Warning:** `source=ecmwf` To ensure the stability of our systems and to preserve resources for our operational activities (network, compute, etc.), access to the open-data portal is limited to 500 simultaneous connections. This limit helps us guarantee reliable service for our operational users, especially during periods of high demand. For added reliability, the open-data is replicated across AWS, Azure, and Google Cloud. If you experience difficulties accessing the portal directly, you can also retrieve the data from these cloud platforms.

 > ⚠️ **NOTE:** The source `azure` generates an sas token for the user during retrieval. More information about the sas key can be found here [sas tokens](https://confluence.ecmwf.int/display/DAC/ECMWF+open+data%3A+real-time+forecasts+from+IFS+and+AIFS).

- `model` is the name of the model that produced the data. Use `ifs` for the physics-driven model, `aifs-single` for the data-driven model, and `aifs-ens` for the ensemble data-driven model. Default is `ifs`.

- `resol` specifies the default resolution of the data. Possible values are `0p25` for 0.25 degree resolution and `0p1` for 0.1 degree resolution. Default is `0p25`. The resolution can also be set for an individual request with the `resol` keyword, see [Resolution](#resolution).

- `preserve_request_order`. If this flag is set to `True`, the library will attempt to write the retrieved data into the target file in the order specified by the request. For example, if the request specifies `param=[2t,msl]` the library will ensure that the field `2t` is first in the target file, while with `param=[msl,2t]`, the field `msl` will be first. This also works across different keywords: `...,levelist=[500,100],param=[z,t],...` will produce different output to `...,param=[z,t],levelist=[500,100],...`
If the flag is set to `False`, the library will sort the request to minimise the number of HTTP requests made to the server, leading to faster download speeds. Default is `False`.

- `infer_stream_keyword`. The `stream` keyword represents the ECMWF forecasting system that creates the data. Setting it properly requires knowledge of how ECMWF runs its operations. If this boolean is set to `True`, the library will try to infer the correct value for the `stream` keyword based on the rest of the request. Default is `True` if model is `ifs`.

 > ⚠️ **NOTE:** It is recommended **not** to set the `preserve_request_order` flag to `True` when downloading a large number of fields as this will add extra load on the servers.

## Methods

> `Client.retrieve()`

The `Client.retrieve()` method takes request as input and will retrieve the corresponding data from the server and write them in the user's target file.

A request is a list of keyword/value pairs used to select the desired data. It is possible to specify a list of values for a given keyword.

The request can either be specified as a dictionary:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

request = {
    "time": 0,
    "type": "fc",
    "step": 24,
    "param": ["2t", "msl"],
}

client.retrieve(request, "data.grib2")

# or:

client.retrieve(
    request=request,
    target="data.grib2",
)
```

or directly as arguments to the `retrieve()` method:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    type="fc",
    step=24,
    param=["2t", "msl"],
    target="data.grib2",
)
```

The `date` and `time` keyword are used to select the date and time of the forecast run (see [Date and time](#date-and-time) below). If `date` or both `date` and `time` are not specified, the library will query the server for the most recent matching data. The `date` and `time` of the downloaded forecast is returned by the `retrieve()` method.

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

result = client.retrieve(
    type="fc",
    step=24,
    param=["2t", "msl"],
    target="data.grib2",
)

print(result.datetime)
```

may print `2022-01-23 00:00:00`.

> `Client.download()`

The `Client.download()` method takes the same parameters as the `Client.retrieve()` method, but will download the whole data files from the server, ignoring keywords like `param`, `levelist` or `number`.

The example below will download all field from the latest time step 24, ignoring the keyword `param`:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.download(
    param="msl",
    type="fc",
    step=24,
    target="data.grib2",
)

```

> 📌 **NOTE**: At `resol="0p1"` the data is split into a single level file and a pressure level file. `Client.download()` downloads both files into the target unless `levtype` is given, see [Resolution](#resolution).

> `Client.latest()`

The `Client.latest()` method takes the same parameters as the `Client.retrieve()` method, and returns the date of the most recent matching forecast without downloading the data:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

print(client.latest(
    type="fc",
    step=24,
    param=["2t", "msl"],
    target="data.grib2",
))
```

may print `2022-01-23 00:00:00`.

> ⏰ **NOTE**: The data is available between 7 and 9 hours after the forecast starting date and time, depending on the forecasting system and the time step specified.

## Request keywords

The supported keywords are:

- `type`: the type of data (compulsory, defaults to `fc`).
- `stream`: the forecast system (optional if unambiguous, compulsory otherwise). See the `infer_stream_keyword` [above](#options).
- `date`: the date at which the forecast starts.
- `time`: the time at which the forecast starts.
- `step`: the forecast time step in hours, or `fcmonth`, the time step in months for the seasonal forecast (compulsory, default to `0` and `1`, respectively).
- `resol`: the resolution of the data, `0p25` or `0p1` (defaults to the `resol` given to the `Client`, see [Resolution](#resolution)).

and (all optional, with no defaults):

- `param`: the meteorological parameters, such as wind, pressure or humidity.
- `levtype`: select between single level parameters (`sfc`), parameters on pressure levels (`pl`) and soil levels (`sol`). At `resol="0p1"` it is also used to select which file to access.
- `levelist`: the list of pressure levels when relevant.
- `number`: the list of ensemble member numbers when relevant.

The keywords in the first list are used to identify which file to access, while the second list is used to identify which parts of the files need to be actually downloaded. Some HTTP servers are able to return multiple parts of a file, while other can only return a single part from a file. In the latter case, the library may perform many HTTP requests to the server. If you wish to download whole files, only provide keywords from the first list.

### Date and time

The date and time parameters refer to the starting time of the forecast. All date and time are expressed in UTC.

There are several ways to specify the date and time in a request.

Date can be specified using strings, numbers and Python `datetime.datetime` or `datetime.date` objects:

```python
...
    date='20220125',
    time=12,
...
    date='2022-01-25',
    time=12,
...
    date='2022-01-25 12:00:00',
...
    date=20220125,
    time=12,
...
    date=datetime.datetime(2022, 1, 25, 12, 0, 0),
...
    date=datetime.date(2022, 1, 25),
    time=12,
...
```

Dates can also be given as a number less than or equal to zero. In this case, it is equivalent to the current UTC date minus the given number of days:

```python
...
    date=0, # today
    date=-1, # yesterday
    date=-2, # the day before yesterday
...
```

The keyword `time` can be given as a string or an integer, or a Python `datetime.time` object. All values of time below are equivalent:

```python
...
    time=12,
...
    time=1200,
...
    time='12',
...
    time='1200',
...
    time=datetime.time(12),
...
```

| List of valid values for time |
| ----------------------------- |
| 0, 6, 12 and 18 |

If `time` is not specified, the time is extracted from the date.

```python
...
   date='2022-01-25 12:00:00',
...
```

is equivalent to:

```python
...
   date='2022-01-25',
   time=12,
...
```

If the `time` keyword is specified, it overrides any time given in the request.

```python
...
   date='2022-01-25 12:00:00',
   time=18,
...
```

is equivalent to:

```python
...
   date='2022-01-25',
   time=18,
...
```

As stated before, if `date` or both `date` and `time` are not specified, the library will query the server for the most recent matching data. The `date` and `time` of the downloaded forecast is returned by the `retrieve()` method:

Example without the `date` keyword:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

result = client.retrieve(
    time=12,
    type="fc",
    param="2t",
    step="24",
    target="data.grib2",
)

print(result.datetime)

```

will print `2022-01-22 12:00:00` if run in the morning of 2022-01-23.

Example without the `date` and `time` keywords:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

result = client.retrieve(
    type="fc",
    param="2t",
    step="24",
    target="data.grib2",
)

print(result.datetime)

```

will print `2022-01-23 00:00:00` if run in the morning of 2022-01-23.

### Stream and type

ECMWF runs several forecasting systems:

- [HRES](https://confluence.ecmwf.int/display/FUG/HRES+-+High-Resolution+Forecast): High Resolution Forecast.
- [ENS](https://confluence.ecmwf.int/display/FUG/ENS+-+Ensemble+Forecasts): Ensemble Forecasts.
- [SEAS](https://confluence.ecmwf.int/display/FUG/Long-Range+%28Seasonal%29+Forecast): Long-Range (Seasonal) Forecast.

Each of these forecasts also produces several types of products, that are referred to using the keywords
`stream` and `type`.

> Valid values for `type` are:

HRES:

- `fc`: Forecast.

ENS:

- `cf`: Control forecast.
- `pf`: Perturbed forecast.
- `em`: Ensemble mean.
- `es`: Ensemble standard deviation.
- `ep`: Probabilities.

> Valid values for `stream` are:

- `oper`: Atmospheric fields from HRES - 00 UTC and 12 UTC.
- `wave`: Ocean wave fields from HRES - 00 UTC and 12 UTC.
- `enfo`: Atmospheric fields from ENS.
- `waef`: Ocean wave fields from ENS.
- `scda`: Atmospheric fields from HRES - 06 UTC and 18 UTC.
- `scwv`: Ocean wave fields from HRES - 06 UTC and 18 UTC.

> 📌 **NOTE**: if the client's flag [`infer_stream_keyword`](#options) is set to `True`, the library will infer the stream from the `type` and `time`. In that case, you just need to specify `stream=wave` to access ocean wave products, and don't provide a value for `stream` in other cases.

### Time steps

To select a time step, use the `step` keyword:

```python
...
   step=24,
...
   step=[24, 48],
...
```

| Forecasting system | Time | List of time steps |
| -------- | ---- | ------------------ |
| HRES | 00 and 12 | 0 to 144 by 3, 144 to 240 by 6 |
| ENS | 00 and 12 | 0 to 144 by 3, 144 to 360 by 6 |
| HRES | 06 and 18 | 0 to 90 by 3 |
| ENS | 06 and 18 | 0 to 144 by 3 |
| Probabilities - Instantaneous weather events | 00 and 12 | 0 to 360 by 12 |
| Probabilities - Daily weather events | 00 and 12 | 0-24 to 336-360 by 12 |

> 📌 **NOTE**: Not specifying `step` will return all available time steps.

### Resolution

The data is available at two resolutions, selected with the `resol` keyword:

| `resol` | Grid | Models |
| ------- | ---- | ------ |
| `0p25` (default) | 0.25° x 0.25° | `ifs`, `aifs-single`, `aifs-ens` |
| `0p1` | 0.1° x 0.1° | `ifs` |

The `0p1` resolution is only available for the `ifs` model. Requesting it with `model="aifs-single"` or `model="aifs-ens"` raises an error.

The resolution can be set when creating the client, or for an individual request. A value given in the request takes precedence over the client value:

```python
client = Client(source="ecmwf")  # resol="0p25" by default

client.retrieve(
   resol="0p1",
   param="2t",
   step=24,
   target="data.grib2",
)
```

At `0p25`, all the fields of a forecast step are in a single file. At `0p1`, they are split into two files: one for single level fields (`sfc`) and one for pressure level fields (`pl`). The library handles this for you:

- if `levtype` is not given, both files are used, so a request returns the same fields at `0p1` as it would at `0p25`;
- if `levtype="sfc"` or `levtype="pl"` is given, only the matching file is used, which reduces the number of HTTP requests. The soil level fields (`levtype="sol"`) are in the `sfc` file;
- the ocean wave streams (`wave` and `waef`) only have single level fields, so only the `sfc` file is used.

> 📌 **NOTE**: The tropical cyclone tracks (`type="tf"`) do not depend on resolution, and are always retrieved from the `0p25` files.

### Parameters and levels

To select a parameter, use the `param` keyword:

```python
...
   param="msl",
...
   param=["2t", "msl"]
...
```

for pressure level parameters, use the `levelist` keyword:

```python
...
   param="t",
   levelist=850,
...
   param=["u", "v"],
   levelist=[1000, 850, 500],
...
```

> 📌 **NOTE**: Not specifying `levelist` will return all available levels, and not specifying `param` will return all available parameters.

| List of pressure levels (hPa) |
| ----------------------------- |
|   1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50 and 10 |


Below is the list of all parameters. The parameters marked with ¹ are only available in the HRES forecast (`stream="oper"`), the others are available in both the HRES and ENS forecasts. Some parameters, such as the 6-hourly maximum and minimum temperatures, are only available at some time steps.

> Atmospheric fields on pressure levels

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| d | Divergence | s<sup>-1</sup> |
| gh | Geopotential height | gpm |
| q | Specific humidity | kg kg<sup>-1</sup> |
| r | Relative humidity | % |
| t | Temperature | K |
| u | U component of wind | m s<sup>-1</sup> |
| v | V component of wind | m s<sup>-1</sup> |
| vo | Vorticity (relative) | s<sup>-1</sup> |
| w | Vertical velocity | Pa s<sup>-1</sup> |
| z ¹ | Geopotential | m<sup>2</sup> s<sup>-2</sup> |

> Atmospheric fields on a single level

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| 100u | 100 metre U wind component | m s<sup>-1</sup> |
| 100v | 100 metre V wind component | m s<sup>-1</sup> |
| 10fg | Maximum 10 metre wind gust since previous post-processing | m s<sup>-1</sup> |
| 10fg3 | Maximum 10 metre wind gust in the last 3 hours | m s<sup>-1</sup> |
| 10u | 10 metre U wind component | m s<sup>-1</sup> |
| 10v | 10 metre V wind component | m s<sup>-1</sup> |
| 2d | 2 metre dewpoint temperature | K |
| 2t | 2 metre temperature | K |
| asn | Snow albedo | (0 - 1) |
| ewss | Time-integrated eastward turbulent surface stress | N m<sup>-2</sup> s |
| lsm | Land-sea mask | (0 - 1) |
| mn2t3 | Minimum temperature at 2 metres in the last 3 hours | K |
| mn2t6 | Minimum temperature at 2 metres in the last 6 hours | K |
| msl | Mean sea level pressure | Pa |
| mucape | Most-unstable CAPE | J kg<sup>-1</sup> |
| mx2t3 | Maximum temperature at 2 metres in the last 3 hours | K |
| mx2t6 | Maximum temperature at 2 metres in the last 6 hours | K |
| nsss | Time-integrated northward turbulent surface stress | N m<sup>-2</sup> s |
| ptype | Precipitation type | (Code table 4.201) |
| ro | Runoff | m |
| rsn | Snow density | kg m<sup>-3</sup> |
| sd | Snow depth | m of water equivalent |
| sdor ¹ | Standard deviation of sub-gridscale orography | m |
| sf | Snowfall | m of water equivalent |
| sithick | Sea ice thickness | m |
| skt | Skin temperature | K |
| slor ¹ | Slope of sub-gridscale orography | Numeric |
| sp | Surface pressure | Pa |
| ssr | Surface net short-wave (solar) radiation | J m<sup>-2</sup> |
| ssrd | Surface short-wave (solar) radiation downwards | J m<sup>-2</sup> |
| str | Surface net long-wave (thermal) radiation | J m<sup>-2</sup> |
| strd | Surface long-wave (thermal) radiation downwards | J m<sup>-2</sup> |
| sve | Eastward surface sea water velocity | m s<sup>-1</sup> |
| svn | Northward surface sea water velocity | m s<sup>-1</sup> |
| tcc | Total cloud cover | (0 - 1) |
| tcw | Total column water | kg m<sup>-2</sup> |
| tcwv | Total column vertically-integrated water vapour | kg m<sup>-2</sup> |
| tp | Total precipitation | m |
| tprate | Total precipitation rate | kg m<sup>-2</sup> s<sup>-1</sup> |
| ttr | Top net long-wave (thermal) radiation | J m<sup>-2</sup> |
| z ¹ | Geopotential | m<sup>2</sup> s<sup>-2</sup> |
| zos | Sea surface height | m |

> Soil fields (`levtype="sol"`, `levelist` 1 to 4)

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| sot | Soil temperature | K |
| vsw | Volumetric soil moisture | m<sup>3</sup> m<sup>-3</sup> |

> Ocean waves fields

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| cdww | Coefficient of drag with waves | dimensionless |
| h1012 | Significant wave height of all waves with periods within the inclusive range from 10 to 12 seconds | m |
| h1214 | Significant wave height of all waves with periods within the inclusive range from 12 to 14 seconds | m |
| h1417 | Significant wave height of all waves with periods within the inclusive range from 14 to 17 seconds | m |
| h1721 | Significant wave height of all waves with periods within the inclusive range from 17 to 21 seconds | m |
| h2125 | Significant wave height of all waves with periods within the inclusive range from 21 to 25 seconds | m |
| h2530 | Significant wave height of all waves with periods within the inclusive range from 25 to 30 seconds | m |
| mp2 | Mean zero-crossing wave period | s |
| mwd | Mean wave direction | Degree true |
| mwp | Mean wave period | s |
| pp1d | Peak wave period | s |
| swh | Significant height of combined wind waves and swell | m |
| wmb | Model bathymetry | m |

> Ensemble mean and standard deviation - pressure levels

| Parameter | Description | Units | Levels |
| --------- | ----------- | ----- | ------ |
| gh | Geopotential height | gpm | 300, 500, 1000 |
| t | Temperature | K | 250, 500, 850 |
| ws | Wind speed | m s<sup>-1</sup> | 250, 850 |

> Ensemble mean and standard deviation - single level

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| msl | Mean sea level pressure | Pa |

> Instantaneous weather events - atmospheric fields - 850 hPa

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| ptsa_gt_1p5stdev | Probability of temperature standardized anomaly greater than 1.5 standard deviation | % |
| ptsa_gt_1stdev | Probability of temperature standardized anomaly greater than 1 standard deviation | % |
| ptsa_gt_2stdev | Probability of temperature standardized anomaly greater than 2 standard deviation | % |
| ptsa_lt_1p5stdev | Probability of temperature standardized anomaly less than -1.5 standard deviation | % |
| ptsa_lt_1stdev | Probability of temperature standardized anomaly less than -1 standard deviation | % |
| ptsa_lt_2stdev | Probability of temperature standardized anomaly less than -2 standard deviation | % |

> Daily weather events - atmospheric fields - single level

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| 10fgg10 | 10 metre wind gust of at least 10 m/s | % |
| 10fgg15 | 10 metre wind gust of at least 15 m/s | % |
| 10fgg25 | 10 metre wind gust of at least 25 m/s | % |
| tpg1 | Total precipitation of at least 1 mm | % |
| tpg10 | Total precipitation of at least 10 mm | % |
| tpg100 | Total precipitation of at least 100 mm | % |
| tpg20 | Total precipitation of at least 20 mm | % |
| tpg25 | Total precipitation of at least 25 mm | % |
| tpg5 | Total precipitation of at least 5 mm | % |
| tpg50 | Total precipitation of at least 50 mm | % |

> Instantaneous weather events - ocean waves fields

| Parameter | Description | Units |
| --------- | ----------- | ----- |
| swhg2 | Significant wave height of at least 2 m | % |
| swhg4 | Significant wave height of at least 4 m | % |
| swhg6 | Significant wave height of at least 6 m | % |
| swhg8 | Significant wave height of at least 8 m | % |

### Ensemble numbers

You can select individual members of the ensemble forecast use the keyword `number`.

```python
...
   stream="enfo",
   step=24,
   param="msl",
   number=1,
...
   stream="enfo",
   step=24,
   param="msl",
   number=[1, 10, 20],
...
```

| List of ensemble numbers |
| ----------------------------- |
|   1 to 50 |

> 📌 **NOTE**: Not specifying `number` will return all ensemble forecast members.

## Examples

### Download a single surface parameter at a single forecast step from ECMWF's 00UTC HRES forecast

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="oper",
    type="fc",
    step=24,
    param="2t",
    target="data.grib2",
)
```

### Download single level and pressure level parameters at 0.1 degree resolution from ECMWF's 00UTC HRES forecast

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf", resol="0p1")

client.retrieve(
    time=0,
    stream="oper",
    type="fc",
    step=24,
    param=["2t", "msl", "t"],
    target="data.grib2",
)
```

As `levtype` is not given, both the single level and pressure level files are accessed. To only access the pressure level file, add `levtype="pl"`.

### Download the tropical cyclone tracks from ECMWF's 00UTC HRES forecast

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="oper",
    type="tf",
    step=240,
    target="data.bufr",
)
```

- The downloaded data are encoded in BUFR edition 4
- For the HRES Tropical Cyclone tracks at time=06 and time=18 use:

```python
...
   step = 90,
...
```

> ❗ **NOTE:** Tropical cyclone tracks products are only available when there are tropical cyclones observed or forecast.

### Download a single surface parameter at a single forecast step for all ensemble members from ECMWF's 12UTC 00UTC ENS forecast

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="enfo",
    type="pf",
    param="msl",
    target="data.grib2",
)
```

- To download a single ensemble member, use the `number` keyword:  `number=1`.
- All of the odd numbered ensemble members use `number=[num for num in range(1,51,2)]`.
- To download the control member, use `type="cf"`.


### Download a single surface parameter at a single forecast step for all ensemble members from ECMWF's 12UTC 00UTC AIFS-ENS forecast

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf", model="aifs-ens")

client.retrieve(
    time=0,
    stream="enfo",
    type="pf",
    param="msl",
    target="data.grib2",
)
```

- To download a single ensemble member, use the `number` keyword:  `number=1`.
- All of the odd numbered ensemble members use `number=[num for num in range(1,51,2)]`.
- To download the control member, use `type="cf"`.

### Download the Tropical Cyclone tracks from ECMWF's 00UTC ENS forecast

The Tropical Cyclone tracks are identified by the keyword `type="tf"`.

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="enfo",
    type="tf",
    step=240,
    target="data.bufr",
)
```

- The downloaded data are encoded in BUFR edition 4
- For the ENS Tropical Cyclone tracks at time=06 and time=18 replace `step=240` with `step=144`.

### Download the ensemble mean and standard deviation for all parameters at a single forecast step from ECMWF's 00UTC ENS forecast

The ensemble mean and standard deviation are identified by the keywords `type="em"`:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="enfo",
    type="em",
    step=24,
    target="data.grib2",
)
```

and `type="es"`, respectively:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="enfo",
    type="es",
    step=24,
    target="data.grib2",
)

```

### Download the ensemble probability products

The ensemble probability products are identified by the keyword `type="ep"`.  The probability products are available only for `time=00` and `time=12`.

Two different products are available.

#### Probabilities - Instantaneous weather events - Pressure levels

The probability of temperature standardized anomalies at a constant
pressure level of 850hPa are available at 12 hourly forecast steps.

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

client.retrieve(
    time=0,
    stream="enfo",
    type="ep",
    step=[i for i in range(12, 361, 12)],
    levelist=850,
    param=[
        "ptsa_gt_1stdev",
        "ptsa_gt_1p5stdev",
        "ptsa_gt_2stdev",
        "ptsa_lt_1stdev",
        "ptsa_lt_1p5stdev",
        "ptsa_lt_2stdev",
    ],
    target="data.grib2",
)
```

#### Probabilities - Daily weather events - Single level

The probabilities of total precipitation and wind gusts exceeding specified thresholds in a 24 hour period are available for step ranges 0-24 to 336-360 by 12​​.  These are specified in the retrieval request using, e.g.: `step=["0-24", "12-36", "24-48"]`.

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

steps = [f"{12 * i}-{ 12 * i + 24}" for i in range(29)]

client.retrieve(
    time=0,
    stream="enfo",
    type="ep",
    step=steps,
    param=["tpg1", "tpg5", "10fgg10"],
    target="data.grib2",
)
```

### ECMWF open data license

By downloading data from the ECMWF open data dataset, you agree to the terms: Attribution 4.0 International (CC BY 4.0). If you do not agree with such terms, do not download the data. Visit [this page](https://apps.ecmwf.int/datasets/licences/general/) for more information.

## Retry policy

The client automatically retries failed requests on transient HTTP errors (429, 500, 502, 503, 504, 408) and connection errors. You can configure the retry behaviour:

```python
from ecmwf.opendata import Client

client = Client(
    source="ecmwf",
    maximum_retries=500,          # Maximum number of retry attempts (default: 500)
    retry_after=120,              # Seconds to wait between retries (default: 120)
    use_server_retry_after=True,  # Honour the server's Retry-After header (default: True)
)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `maximum_retries` | 500 | Maximum number of retry attempts before giving up |
| `retry_after` | 120 | Fallback wait time in seconds between retries |
| `use_server_retry_after` | True | If the server responds with a `Retry-After` header (e.g. on HTTP 429), use that value instead of `retry_after` |

When `use_server_retry_after=True` (the default), the client respects rate-limiting signals from the server. If the server does not provide a `Retry-After` header, the `retry_after` value is used as a fallback.

The `retry_after` parameter also accepts a tuple `(min, max, ratio)` for incremental backoff:

```python
client = Client(
    source="ecmwf",
    retry_after=(10, 300, 2),  # Start at 10s, double each time, cap at 300s
)
```

### License

[Apache License 2.0](LICENSE) In applying this licence, ECMWF does not waive the privileges and immunities
granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.
