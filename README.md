# ecmwf-opendata

A package to download ECMWF open data.

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

- `beta` is a boolean that indicates whether to access the beta or the prodcution version of the dataset. Current only `beta=True` is supported.

- `preserve_request_order`. If this flag is set to `True`, the library will attempt to return to write the retrieved data into the target file following the order specified by the request. For example, if the request specifies `param=[2t,msl]` the libary will ensure that the field `2t` is first in the target file, while with `param=[msl,2t]`, the field `msl` will be first. This also works accross different keywords: `...,levelist=[500,100],param=[z,t],...` will produce a different output than `...,param=[z,t],levelist=[500,100],...`
If it is set to `False`, the library will sort the request to minimise the number of HTTP requests made to the server, leading to faster download speeds. **It is not recommanded to use that flag when dowloading a large number of fields.** Default is `False`.

- `infer_stream_keyword`. The `stream` keyword represents the ECMWF forecasting system that creates the data. Setting it properly requires knowledge on how ECMWF runs its operations. If this boolean is set to `True`, the library will try to infer the rigth value for the `stream` keyword based on the rest of the request. Default is `True`.

## Request syntax

 This package uses a request syntax similar to the one used by [ecmwf-api-client](https://github.com/ecmwf/ecmwf-api-client).

### Date and time

The date and time parameters refer to the starting time of the forecast. All date and time are expressed in UTC.


There are several way to specify the date and time in a request.

```python
...
    date='20220125',
    time=12,
...
```

The keyword `time` can be given as a string or an integer. All values of time below are equivalent:

```python
...
    time=12,
    time=1200,
    time='12',
    time='1200'
...```

If `time` is not specified, the time is extracted from the date.

```python
...
   date='2022-01-25 12:00:00',
...
```

If the `time` keyword is specified, it overrides any time given in the request.

### Stream and type

ECMWF runs several foreacsting systems that are refered to using the keywords
`stream` and `type`.

### Time steps

...

### Parameters and levels

For a complete list of parameters, refer to this [page](https://www.ecmwf.int/en/forecasts/datasets/open-data)

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

- For HRES Atmospheric model products at time=06 or time=12, use `stream = "scda",`

### Download the Tropical Cyclone tracks from ECMWF's 00UTC HRES forecast (Set I-iii)

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

- To download a single ensemble member, use the **number** keyword:  `number = [1,]`.
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

The ensemble probability products are identified by the keyword `type
= "ep"`.  The probability products are available only for time=00
and time=12.

Two different productsa are available.

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
