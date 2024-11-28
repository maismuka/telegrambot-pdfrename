# telegrambot-pdfrename
This telegram bot is to fetch any PDF in a group chat, download, then rename with custom format, and resend back. Every day at 23:50 it will compile all PDF in a day and send to a dedicated group


To rebuild everything, ensuring no old file or cache
sudo docker build --no-cache -t telegrambot-audit .


To run docker with mount to /volume1/audit_temp
docker run -d -v /volume1/audit_temp:/volume1/audit_temp --name telegrambot-audit telegrambot-audit
