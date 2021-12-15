# ecmwf-opendata

A package to download ECMWF open data

```python    

from ecmwf.opendata import Client

client = Client("https://....")

client.retrieve(
   date=-1,
   time=6,
   step=144,
   stream="waef",
   type="ef",
   target="data.grib",
   param='mwd',
)

```

### License
[Apache License 2.0](LICENSE) In applying this licence, ECMWF does not waive the privileges and immunities
granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.
