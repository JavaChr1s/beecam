# Install

* Install `docker` and `docker-compose`
* Enable the auto-update by typing:
```
sudo systemctl --force --full edit beecam-update.service
```
Paste the content of `beecam-update.service.example` into the opened editor.
Type the following to enable it:
```
sudo systemctl enable beecam-update.service
```
* Adjust the `crontab.txt` to your needs, f.e. if you want to capture movies only between 7am and 6pm and copy it to your usb-stick
* Add your public-key to git, otherwise the auto-update won't work
* Change settings in your rpi-eeprom-config using `sudo -E rpi-eeprom-config --edit` and change the following values:
```
BOOT_UART=0
WAKE_ON_GPIO=0
POWER_OFF_ON_HALT=1
```
* Add those two lines to `/etc/crontab`:
```
#BEECAM-START
#BEECAM-END
```
* Reboot. The reboot will install your `/etc/crontab` automatically

# Create a new model
Your training- and test-data should be labeled using the PASCAL-VOC XML format. We expect one XML-file per image.

1. Add your training-data to `training/images/train`
1. Add your test-data to `training/images/test`
1. Run `docker-compose up` within `training`
1. Copy the new model (`labels.txt` and `model.tflite`) from `training/output` to `object_detection/models`
1. Push your new model to your git-fork
