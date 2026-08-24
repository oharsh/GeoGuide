/*
 * Copy this file to secrets.h and fill in your own values before flashing.
 * secrets.h is gitignored so credentials never end up in version control.
 */

#ifndef SECRETS_H
#define SECRETS_H

// Hotspot the robot and the host machine both join.
const char *ssid = "your-wifi-ssid";
const char *pass = "your-wifi-password";

// Address of the machine running control_center.py. Must match HOST_IP and
// HOST_PORT in control_center/config.py.
const char *host = "192.168.137.181";
const uint16_t port = 8002;

#endif
