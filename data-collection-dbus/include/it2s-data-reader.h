#include <syslog.h>
// #include <mosquitto.h>
#include <it2s-gnss.h>

#define syslog_debug(msg, ...) syslog(LOG_DEBUG,  msg "", ##__VA_ARGS__)
#define syslog_err(msg, ...) syslog(LOG_ERR, msg "", ##__VA_ARGS__)

typedef struct communications_manager {
	//mqtt_manager_t* mqtt_manager;
	it2s_gnss_data_t* gps_data;
	void* gnss_ctx;
	int msg_sn;
} communications_manager_t;

void com_config(void* com_struct);
void* mqtt_config(void *mqtt_struct);
// void mqtt_set_tile_topic(mqtt_manager_t* mqtt_manager, double latitude, double longitude);
int it2s_read(void* user_data);
void it2s_make_message(communications_manager_t* com_manager);
void send_dbus_signal();
void it2s_clean(communications_manager_t* com_manager);
