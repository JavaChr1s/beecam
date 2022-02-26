#!/bin/sh
### BEGIN INIT INFO
# Provides:          Beecam
# Required-Start:    
# Required-Stop:     
# Default-Start:     3 4 5
# Default-Stop:       
# Short-Description:  
# Description:        
### END INIT INFO

# Actions
case "$1" in
    start)
        cd /home/pi/repo
        ./update.sh
        ;;
    stop)
        # STOP
        ;;
    restart)
        # RESTART
        ;;
esac

exit 0
