#!/bin/sh
HOSTNAME=`/etc/webhook/ssh.sh hostname | tail -n +2`
DATE=`/etc/webhook/ssh.sh date | tail -n +2`

cat << EOF
<html>
	<head>
		<title>$HOSTNAME</title>
        <style type="text/css">
            * {
                font-size: 16pt;
            }
            h1 {
                font-size: 36pt;
            }
            li {
                margin: 15px;
            }
        </style>
        <script type="text/javascript">
            function callAsync(url) {
                var req = new XMLHttpRequest();
                req.onreadystatechange=function() {
                    if (req.readyState==4 && req.status==200) {
                        window.location.reload();
                    }
                }
                req.open("GET", url);
                req.send();
            }
            function refreshDate() {
                var date = new Date();
                callAsync("/set-date?date=" + "" + ('00'+(date.getMonth() + 1)).slice(-2) + ('00'+date.getDate()).slice(-2) + ('00'+date.getHours()).slice(-2) + ('00'+date.getMinutes()).slice(-2) + date.getFullYear());
            }
        </script>
	</head>
	<body>
		<h1>$HOSTNAME</h1>
        <h2>Information</h2>
        <table>
            <tr>
                <th>date</th>
                <td>$DATE <a href="#" onclick="refreshDate()">Refresh Date</a></td>
            </tr>
        </table>
        <h2>Menu</h2>
        <ul>
            <li><a href="#motioneye" onClick="window.location = new window.URL(window.location.href).origin + ':8765'">MotionEye</a></li>
            <li><a href="/list-data">Print USB-Data</a></li>
            <li><a href="/start-motioneye">Start motioneye</a></li>
            <li><a href="/reboot" onclick="if(confirm('Are you sure you want to reboot the beecam?')) callAsync('/reboot'); return false;">Reboot</a></li>
            <li><a href="/shutdown" onclick="if(confirm('Are you sure you want to shutdown the beecam?')) callAsync('/shutdown'); return false;">Shutdown</a></li>
            <li><a href="/save-config">Save MotionEye configurations (available only if online)</a></li>
        </ul>
        <h2>Technical Links</h2>
        <ul>
            <li><a href="/status">Status</a></li>
            <li><a href="/power-monitoring">Power-Monitoring</a></li>
            <li><a href="/update" onclick="if(confirm('Are you sure you want to update the beecam?')) callAsync('/update'); return false;">Update</a></li>
            <li><a href="/logs-analyzer">Logs: Analyzer</a></li>
            <li><a href="/logs-motioneye">Logs: MotionEye</a></li>
            <li><a href="/logs-webhook">Logs: Webhook</a></li>
            <li><a href="/logs-update">Logs: Update</a></li>
        </ul>
	</body>
</html>
EOF
