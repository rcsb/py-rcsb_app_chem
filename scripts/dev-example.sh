#!/bin/sh
# File: chemsearch/option/dev.sh
#
INSTALL_ROOT_PATH=/opt/services
APP_DIR=py-rcsb-app_chem
SERVICE_PATH=${INSTALL_ROOT_PATH}/${APP_DIR}
export CHEM_SEARCH_CLOUD_INSTANCE=`/SysAdmin/instance-setup/routes/common/what_coast.sh`
export CHEM_SEARCH_UPDATE_CHANNEL=`hostname | cut -d '-' -f 4`
#
#
echo "### Running $0 Starting install in ${INSTALL_ROOT_PATH} ${CHEM_SEARCH_CLOUD_INSTANCE} ${CHEM_SEARCH_UPDATE_CHANNEL}"
#
apt-get -yqq install cmake flex bison
#
mkdir ${INSTALL_ROOT_PATH}
cd ${INSTALL_ROOT_PATH}
git clone https://github.com/rcsb/${APP_DIR}.git
#
cd ${SERVICE_PATH}
#
git checkout render-image-20200510
#
/usr/local/bin/pip3.8 install -r requirements.txt
#
export CHEM_SEARCH_DATA_HOSTNAME="bl-${CHEM_SEARCH_CLOUD_INSTANCE}.rcsb.org"
export CHEM_SEARCH_DATA_PATH="4-coastal"
wget http://${CHEM_SEARCH_DATA_HOSTNAME}/${CHEM_SEARCH_DATA_PATH}/OE/oe_license.txt
#
chown -R ubuntu.ubuntu ${INSTALL_ROOT_PATH}
#
export OE_LICENSE=${SERVICE_PATH}/oe_license.txt
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${SERVICE_PATH}
export CHEM_DEPICT_CACHE_PATH=${SERVICE_PATH}

systemctl import-environment CHEM_SEARCH_DATA_PATH CHEM_SEARCH_CLOUD_INSTANCE CHEM_SEARCH_UPDATE_CHANNEL  CHEM_SEARCH_DATA_HOSTNAME
#
cat > /etc/systemd/system/chemsearch.service <<EOF
# Chemical search service  **GENERATED DO NOT EDIT **
[Unit]
Description=Chemical search web service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=${SERVICE_PATH}
PassEnvironment=CHEM_SEARCH_DATA_PATH CHEM_SEARCH_CLOUD_INSTANCE CHEM_SEARCH_UPDATE_CHANNEL  CHEM_SEARCH_DATA_HOSTNAME CHEM_SEARCH CHEM_SEARCH_CC_PREFIX CHEM_SEARCH_CA
CHE_PATH CHEM_DEPICT_CACHE_PATH OE_LICENSE
##
ExecStart=/usr/local/bin/gunicorn rcsb.app.chem.main:app \
    --timeout 300 \
    --workers 2 \
    --chdir ${SERVICE_PATH} \
    --bind 0.0.0.0:80 \
    --reload \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile -
    # --access-logformat '%(t)s %(p)s %(h)s %(m)s %(U)s %(s)s - %(L)ss' \
Restart=always

[Install]
WantedBy=multi-user.target
EOF

#service chemsearch start

echo "# $0 Complete"

