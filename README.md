# <img src='icon.png' card_color='#F66716' width='50' height='50' style='vertical-align:bottom'/> Auto volume
Sets the volume depending on background noise level

## About
This skill lets Mycroft decide when to use high, normal, or low volume. Mycrofts keeps monitoring the background sound levels using the microphone, using which it decides what volume level is the right one to use.

As it is not easy to know what is high and what is low noise level, the skill will adapt over time. The skill notices the highest and lowest measured levels over time and adjusts its settings according to those measurements.

The skill stops adjusting the volume if another skill is using the speaker or if Mycroft himself is talking.

The skill can be activated or deactivated using the command "Hey Mycroft, set auto volume off" or "Hey Mycroft, set auto volume on".


## Examples
* "Set auto volume on"
* "Set auto volume off"
* "Clear auto volume measurements"

## Credits
Andreas Lorensen (@andlo)

## Supported Devices
platform_mark1 platform_picroft

## Category
Daily
**Configuration**

## Tags
#volume

