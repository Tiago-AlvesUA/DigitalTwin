#include <syslog.h>
#include <mosquitto.h>
#include <it2s-gnss.h>

#define syslog_debug(msg, ...) syslog(LOG_DEBUG,  msg "", ##__VA_ARGS__)
#define syslog_err(msg, ...) syslog(LOG_ERR, msg "", ##__VA_ARGS__)
#define MQTT_HOST "10.255.41.221"
#define MQTT_PORT 8883
#define MQTT_USERNAME "my-auth-id-2@my-tenant"
#define MQTT_PASSWORD "my-password"
#define MQTT_STATION_ID 123
#define MQTT_CLIENT_ID "dev123"
#define MQTT_CAFILE "../certificates/c2e_hono_truststore.pem"


typedef struct mqtt_manager {
	struct mosquitto* mosq;
	int station_id;
	char* topic;	

	pthread_t mqtt_thread;
	int msg_sn;
} mqtt_manager_t;

typedef struct communications_manager {
	mqtt_manager_t* mqtt_manager;
	// SPVSMBody_t* spvsm_body;
	// SNVSMBody_t* snvsm_body;
	// SBVSMBody_t* sbvsm_body;
	// OVSMBody_t* ovsm_body;
	it2s_gnss_data_t* gps_data;
	void* gnss_ctx;
} communications_manager_t;

void com_config(void* com_struct);
void* mqtt_config(void *mqtt_struct);

int it2s_read(void* user_data);
void it2s_send_values(communications_manager_t* com_manager);
int it2s_make_message(communications_manager_t* com_manager, char* buffer);
void it2s_clean(communications_manager_t* com_manager);
