
# Configuration file for everything EC2/Autoscale related.

AUTOSCALE_ON = 0 # change this to 0 if in a non-elastic environment

# EC2 Control endpoints and credentials

EC2_URL = "http://nova.narfindustries.com:8773/services/Cloud"
EC2_ACCESS = "bd3007783bce4c0da4309e9449743492"
EC2_SECRET = "6cf3dea6191e454bb892d40a006b5176"

BASE_IMAGE = 'scanworker'

# Autoscale metric information

MINIMUM_WORKERS = 2
MINIMUM_WORKERS_TO_PENDING_RATIO = 8
MAXIMUM_WORKERS_TO_PENDING_RATIO = 2
