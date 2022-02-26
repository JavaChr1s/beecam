# Install

* Install `docker` and `docker-compose`
* Add the `update.sh` to init.d to run on every boot. There is a `beecam.sh.example-init.d` example file. Adjust it to your needs and move it to `/etc/init.d/`: `mv ~/repo/beecam.sh.example-init.d /etc/init.d/beecam.sh`
* Adjust the `crontab.txt` to your needs, f.e. if you want to capture movies only between 7am and 6pm
* Configure your usb-stick to be automounted using `/etc/fstab` to `/media/usbstick`
* Copy `object_detection/config.json.example` to your usbstick, rename it to `config.json` and configure it to your needs
* If you are using the default-configuration from `config.json.example` create the following folders on your usbstick:
  * analyzed
  * data
  * error
  * raw
* Rename `object_detection/.env.example` to `object_detection/.env` and configure it to your needs
* Add your public-key to git, otherwise the auto-update won't work

# Update
Just push some changes to your git-fork. If you have configured the `update.sh` to run on boot as described in the `Install`-section everything is updated automatically on reboot (while you are connected to the internet).

If you want to update manually, you can do that using `sudo ./update.sh`. It's important to always call it as root!

The update-logs are saved on your usbstick `/media/usbstick/update.log`, so you can easily check if the update-went well.

# Create a new model
Your training- and test-data should be labeled using the PASCAL-VOC XML format. We expect one XML-file per image.

1. Add your training-data to `training/images/train`
1. Add your test-data to `training/images/test`
1. Run `docker-compose up` within `training`
1. Copy the new model (`labels.txt` and `model.tflite`) from `training/output` to `object_detection/models`
1. Push your new model to your git-fork
