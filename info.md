# Home Assistant Electrolux Care Integration V2 (Not Official)

[![Validate with HACS](https://github.com/albaintor/homeassistant_electrolux_status/actions/workflows/hacs.yml/badge.svg)](https://github.com/albaintor/homeassistant_electrolux_status/actions/workflows/hacs.yml)
[![Validate with hassfest](https://github.com/albaintor/homeassistant_electrolux_status/actions/workflows/hassfest.yml/badge.svg)](https://github.com/albaintor/homeassistant_electrolux_status/actions/workflows/hassfest.yml)
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/albaintor)

## This new integration is based on new APIs and may be unstable 
As the former project has been deleted, you will need to delete the existing HACS integration and :
- Searech for "Electrolux Care Integration V2 (Not Official)" in HACS
- Or add a new repository in HACS : https://github.com/albaintor/homeassistant_electrolux_status

If you are interested in contributing to the project and assisting with the integration of the new APIs, your contributions are more than welcome! Feel free to fork the repository, make changes, and submit a pull request.

Thank you for your understanding and support.

## Details
This is an integration to Home Assistant to communicate with the Electrolux OCP Platform (probably for One Connectivity Platform), Electrolux owned brands, like: Electrolux, AEG, Frigidaire, Husqvarna.

Tested with Electrolux and AEG washer-dryer, but probably could be used with some internet connected ovens, diswashers, fridges, airconditioners.

**Last changes :**
- Added support for temperatures
- Added Wifi link quality sensor
- Renamed connection state to connectivity status (old entity should be deleted if exists)

**Known issues :**
- Some commands don't work (to be investigated) : several dropdown lists like setting analog temperature...

### Supported and tested devices

This list is not exhaustive as your appliance may work even if not present here
- ELECTROLUX EDH803BEWA - UltimateCare 800
- ELECTROLUX EW9H283BY - PerfectCare 900
- ELECTROLUX EWF1041ZDWA - UltimateCare 900 AutoDose
- ELECTROLUX EEM69410W - MaxiFlex 700
- ELECTROLUX EOD6P77WZ - SteamBake 600
- ELECTROLUX KODDP77WX - SteamBake 600
- ELECTROLUX EHE6799SA - 609L UltimateTaste 900
- ELECTROLUX EW9H869E9 - PerfectCare 900 Dryer
- ELECTROLUX EW9H188SPC - PerfectCare 900 Dryer
- ELECTROLUX EW8F8669Q8 - PerfectCare 800 Washer
- ELECTROLUX EW9F149SP - PerfectCare 900 Washer
- ELECTROLUX EW9W161BC - PerfectCare 900 Washer & Dryer
- ELECTROLUX KEGB9300W - Dishwasher
- ELECTROLUX EEG69410W - Dishwasher
- ELECTROLUX YH7W979P9  - Airdryer
- AEG L6FBG841CA - 6000 Series Autodose
- AEG L7FENQ96 - 7000 Series ProSteam Autodose
- AEG L7FBE941Q - 7000 Series Prosense Autodose
- AEG L8FEC96QS - 8000 Series Ökomix Autodose
- AEG L9WBA61BC - 9000 Series ÖKOKombi DualSense SensiDry
- AEG BPE558370M - SteamBake 6000
- AEG FSE76738P - 7000 GlassCare

## Prerequisites
All devices need configured and Alias set (otherwise the home assistant integration raises the authentication error) into following applications (depends on device type and region):
- My Electrolux Care/My AEG Care (EMEA region)
- Electrolux Kitchen/AEG Kitchen (EMEA region)
- Electrolux Life (APAC region)
- Electrolux Home+ (LATAM region)
- Electrolux Oven/Frigidaire 2.0 (NA region)

## Installation
1. Click install.
2. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Electrolux status". If you can't find it, add a personalized depot in HACS > Integrations > 3 dots button on the right and type in https://github.com/albaintor/homeassistant_electrolux_status
3. Insert the Electrolux Care Application credentials

## Disclaimer
This Home Assistant integration was not made by Electrolux. It is not official, not developed, and not supported by Electrolux.

