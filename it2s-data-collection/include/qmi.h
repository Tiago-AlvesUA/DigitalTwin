#include <glib.h>
#include <syslog.h>

#define syslog_debug(msg, ...) syslog(LOG_DEBUG, msg "", ##__VA_ARGS__)
#define syslog_err(msg, ...) syslog(LOG_ERR, msg "", ##__VA_ARGS__)

void device_new_callback(GObject* sourceObject, GAsyncResult* res, void* userData);
void device_open_callback(GObject* sourceObject, GAsyncResult* res, void* userData);
void device_release_client_callback(GObject* sourceObject, GAsyncResult* res);
void client_alloc_callback(GObject* sourceObject, GAsyncResult* res, void* userData);
void nas_rf_band_callback(GObject* sourceObject, GAsyncResult* res, void* userData);
void nas_signal_info_callback(GObject* sourceObject, GAsyncResult* res, void* userData);
void nas_get_home_network_callback(GObject* sourceObject, GAsyncResult* res, void* userData);
void qmi_clean_up();
