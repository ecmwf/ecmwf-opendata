# ecmwf-opendata

A package to download ECMWF [open data](https://www.ecmwf.int/en/forecasts/datasets/open-data).


<!--
https://www.ecmwf.int/en/forecasts/documentation-and-support/medium-range-forecasts
https://www.ecmwf.int/en/forecasts/documentation-and-support/long-range
-->



```python
from ecmwf.opendata import Client

client = Client()

client.retrieve(
    date=-1,
    time=6,
    step=144,
    stream="waef",
    type="cf",
    param="mwd",
    target="data.grib",
)
```

## Options

The constructor of the client object takes the following options:

```python
client = Client(
    source="ecmwf",
    beta=True,
    preserve_request_order=False,
    infer_stream_keyword=True,
)
```

where:

- `source` is either the name of server to contact or a fully qualified URL. Possible values are `ecmwf` to access ECMWF's servers, or `azure` to access data hosted on Microsoft's Azure. Default is `ecmwf`.

- `beta` is a boolean that indicates whether to access the beta or the production version of the dataset. Current only `beta=True` is supported.

- `preserve_request_order`. If this flag is set to `True`, the library will attempt to return to write the retrieved data into the target file following the order specified by the request. For example, if the request specifies `param=[2t,msl]` the library will ensure that the field `2t` is first in the target file, while with `param=[msl,2t]`, the field `msl` will be first. This also works across different keywords: `...,levelist=[500,100],param=[z,t],...` will produce a different output than `...,param=[z,t],levelist=[500,100],...`
If it is set to `False`, the library will sort the request to minimise the number of HTTP requests made to the server, leading to faster download speeds. Default is `False`.

- `infer_stream_keyword`. The `stream` keyword represents the ECMWF forecasting system that creates the data. Setting it properly requires knowledge on how ECMWF runs its operations. If this boolean is set to `True`, the library will try to infer the right value for the `stream` keyword based on the rest of the request. Default is `True`.

 > ⚠️ **NOTE** It is  recommended **not** to set the `preserve_request_order` flag to `True` when downloading a large number of fields as this will add extra load on the servers.

## Methods

The `Client.retrieve()` method takes request as input and will retrieve the corresponding data from the server and write them in the user's target file.

A request is a list of keyword/value pairs use to select the desired data. It is possible to specify a list of values for a given keyword.

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

The `date` and `time` keyword are used to select the date and time of the forecast run (see [Date and time](#date-and-time) below). If `date` or both `date` and `time` are not specified, the library will query the server for the most recent matching data. The `date` and `time` of the downloaded forecast is returned by the `download()` method.


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

may print:

```bash
2022-01-23 00:00:00
```

The `Client.latest()` method takes the same parameters as the `Client.retrieve()` method, and returns the date of the most recent matching forecast without downloading the data.

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

may print:

```bash
2022-01-23 00:00:00
```

> 📌 **NOTE**: The data is available between 7 and 9 hours after the forecast starting date and time, depending on the forecasting system and the time step specified.


## Request syntax

 This package uses a request syntax similar to the one used by [ecmwf-api-client](https://github.com/ecmwf/ecmwf-api-client).

### Date and time

The date and time parameters refer to the starting time of the forecast. All date and time are expressed in UTC.

There are several way to specify the date and time in a request.



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


As stated before, if `date` or both `date` and `time` are not specified, the library will query the server for the most recent matching data. The `date` and `time` of the downloaded forecast is returned by the `download()` method:

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

ECMWF runs several forecasting systems that are referred to using the keywords
`stream` and `type`.

(See [`infer_stream_keyword`](#options))

   <!-- "type": [
        "cf",
        "em",
        "ep",
        "es",
        "fc",
        "pf"
    ],
    "stream": [
        "enfo",
        "oper",
        "scda",
        "scwv",
        "waef",
        "wave"
    ], -->

### Time steps

...

 <!-- "step": [
        "0",
        "0-24",
        "102",
        "105",
        "108",
        "108-132",
        "111",
        "114",
        "117",
        "12",
        "12-36",
        "120",
        "120-144",
        "123",
        "126",
        "129",
        "132",
        "132-156",
        "135",
        "138",
        "141",
        "144",
        "144-168",
        "15",
        "150",
        "156",
        "156-180",
        "162",
        "168",
        "168-192",
        "174",
        "18",
        "180",
        "180-204",
        "186",
        "192",
        "192-216",
        "198",
        "204",
        "204-228",
        "21",
        "210",
        "216",
        "216-240",
        "222",
        "228",
        "228-252",
        "234",
        "24",
        "24-48",
        "240",
        "240-264",
        "246",
        "252",
        "252-276",
        "258",
        "264",
        "264-288",
        "27",
        "270",
        "276",
        "276-300",
        "282",
        "288",
        "288-312",
        "294",
        "3",
        "30",
        "300",
        "300-324",
        "306",
        "312",
        "312-336",
        "318",
        "324",
        "324-348",
        "33",
        "330",
        "336",
        "336-360",
        "342",
        "348",
        "354",
        "36",
        "36-60",
        "360",
        "39",
        "42",
        "45",
        "48",
        "48-72",
        "51",
        "54",
        "57",
        "6",
        "60",
        "60-84",
        "63",
        "66",
        "69",
        "72",
        "72-96",
        "75",
        "78",
        "81",
        "84",
        "84-108",
        "87",
        "9",
        "90",
        "93",
        "96",
        "96-120",
        "99" -->

### Parameters and levels

For a complete list of parameters, refer to this [page](https://www.ecmwf.int/en/forecasts/datasets/open-data)

  <!-- "1000",
        "200",
        "250",
        "300",
        "50",
        "500",
        "700",
        "850",
        "925" -->

<!-- "10fgg10",
        "10fgg15",
        "10fgg25",
        "10u",
        "10v",
        "2t",
        "d",
        "gh",
        "mp2",
        "msl",
        "mwd",
        "mwp",
        "pp1d",
        "ptsa_gt_1p5stdev",
        "ptsa_gt_1stdev",
        "ptsa_gt_2stdev",
        "ptsa_lt_1p5stdev",
        "ptsa_lt_1stdev",
        "ptsa_lt_2stdev",
        "q",
        "r",
        "ro",
        "skt",
        "sp",
        "st",
        "swh",
        "swhg2",
        "swhg4",
        "swhg6",
        "swhg8",
        "t",
        "tcwv",
        "tp",
        "tpg1",
        "tpg10",
        "tpg100",
        "tpg20",
        "tpg25",
        "tpg5",
        "tpg50",
        "u",
        "v",
        "vo",
        "ws" -->

### Ensemble numbers

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

- For HRES Atmospheric model products at time=06 or time=12, use `stream="scda",`

### Download the Tropical Cyclone tracks from ECMWF's 00UTC HRES forecast

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
   stream = "scda",
   step = 90,
...
```

### Download a single surface parameter at a single forecast step for all ensemble members from ECMWF's 12UTC 00UTC ENS forecast

```python
from ecmwf.opendata import Client

client = Client(source = "ecmwf")

client.retrieve(
   time = 0,
   stream = "enfo",
   type = "pf",
   param = "msl",
   target = "data.grib2"
)
```

- To download a single ensemble member, use the `number` keyword:  `number=1`.
- All of the odd numbered ensemble members use `number = [num for num in range(1,51,2)]`.
- To download the control member, use `type = "cf"`.

### Download the Tropical Cyclone tracks from ECMWF's 00UTC ENS forecast

The Tropical Cyclone tracks are identified by the keyword `type = "tf"`.

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
- For the ENS Tropical Cyclone tracks at time=06 and time=18 replace `step = [240,]` with `step = [144,]`.

### Download the ensemble mean and standard deviation for all parameters at a single forecast step from ECMWF's 00UTC ENS forecast

The ensemble mean and standard deviation are identified by the keywords `type = "em"`:

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

and `type = "es"`, respectively:

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

The ensemble probability products are identified by the keyword `type="ep"`.  The probability products are available only for `time=00`
and `time=12`.

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
    levtype="pl",
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

The probabilities of total precipitation and wind gusts exceeding specified thresholds in a 24 hour period are available for step ranges 0-24 to 336-360 by 12​​.  These are specified in the retrieval request using, e.g.: `step = ["0-24", "12-36", "24-48"]`.

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")

steps = [f"{12 * i}-{ 12 * i + 24}" for i in range(29)]

client.retrieve(
    time=0,
    stream="enfo",
    type="ep",
    step=steps,
    levtype="sfc",
    param=["tpg1", "tpg5", "10fgg10"],
    target="data.grib2",
)

```

### ECMWF open data license

By downloading data from the ECMWF open data dataset, you agree to the their terms: Attribution 4.0 International (CC BY 4.0). If you do not agree with such terms, do not download the data. Visit [this page](https://apps.ecmwf.int/datasets/licences/general/) for more information.

### License

[Apache License 2.0](LICENSE) In applying this licence, ECMWF does not waive the privileges and immunities
granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.
