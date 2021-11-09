# Ops Manager Alert Scraper utility
GPI - Oct 2021

## Versions
- v1.0 : Opening Demo

## Brief
### Description
- Sample utility script that periodically GET alerts objects out from Ops Manager
- A single project is targeted and it only scraps open alerts
- Collected alerts are indexed and flush to an output file

### Objectif
- Adapting file output format to third party utilities
- Sample : nimsoft/ netcool (legacy utilities at BNPP)

## Capacity
- version 1.0: 
  - scrap alerts for 1 project - 1 cluster 
  - default output file gathering json objects
  
## Usage
### Inline 
- pubKey=xxxx
- privKey=xxxx
- mmsBaseURL= https://vip.ops.manager.com:8443/

```shell
 $ python f_omAlertScraper.py --cfg f_omAlertScraper.yaml --url ${mmsBaseURL} --pubKey ${pubKey} --privKey ${privKey}
```

### Config file
```shell
 $ python f_omAlertScraper.py --cfg f_omAlertScraper.yaml
```

## Requirements
Note: utility targeted for python 2.7
- certifi
- chardet
- idna
- PyYAML 
- requests
- timeloop
- urllib3