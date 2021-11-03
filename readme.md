# Ops Manager Alert Scraper utility
GPI - Oct 2021

## Versions
- v1.0 : Opening Demo

## Capacity
- version 1.0: 
  - scrap alerts for 1 project - 1 cluster 
  - default output file gather json objects
  
## Usage
- pubKey=xxxx
- privKey=xxxx
- mmsBaseURL= https://ec2-3-9-206-23.eu-west-2.compute.amazonaws.com:8443/

```shell
 $ python f_omAlertScraper.py --cfg f_omAlertScraper.yaml --url ${mmsBaseURL} --pubKey ${pubKey} --privKey ${privKey}
```

## Requirements
