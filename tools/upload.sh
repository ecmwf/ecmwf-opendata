#!/usr/bin/env bash
# https://get.ecmwf.int/#browse/browse:ecmwf-opendata
set -eau

DATE1=20220119
DATE2=20220120
touch done

for time in 00 06 12 18
do
    DATE=$DATE2
    if [[ $time -gt 12 ]]
    then
        DATE=$DATE1
    fi
    for stream in oper wave scda scwv enfo waef
    do
        for type in fc ef ep # tf
        do
            ext=grib2
            if [[ $type == "tf" ]]
            then
                ext=bufr
            fi
            for step in $(seq 0 3 144) $(seq 150 6 360)
            do

                grep url done && continue

                url=$URL/$DATE/${time}z/0p4-beta/${stream}/${DATE}${time}0000-${step}h-$stream-$type.$ext
                code=$(curl --silent --head $url | head -1 | awk '{print $2;}')
                if [[ $code -eq 404 ]]
                then
                    continue
                fi
                if [[ $code -ne 200 ]]
                then
                    echo "Code $code"
                    exit 1
                fi
                echo $url
                base=$(basename $url .grib2)
                data=$base.grib2
                index=$base.index
                curl --fail $url -o $data.raw
                ~/build/mir/bin/mir --grid=20/20 $data.raw $data
                ~/build/pgen/bin/pgen-create-index-file -i $data -o $index
                yes | ./upload.py $data /testing/$DATE/${time}z/0p4-beta/${stream}/
                yes | ./upload.py $index /testing/$DATE/${time}z/0p4-beta/${stream}/
                rm -f $data $index $data.raw
                echo $url >> done
            done
        done
    done
done
