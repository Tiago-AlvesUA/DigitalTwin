#include <assert.h>
#include <glib.h>
#include <stdint.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <argp.h>
#include <syslog.h>
#include <libqmi-glib.h>
#include <mosquitto.h>
#include "it2s-data-reader.h"
#include "qmi.h"
#include <json-c/json.h>

extern "C" {
	#include <it2s-gnss.h>
}

using namespace std;

static GMainLoop *m_main_loop;

extern gint8 ratmode, lte_rssi, lte_rsrq;
extern guint8 cid;
extern gint16 lte_rsrp, nr_rsrp, lte_snr, nr_snr, nr_rsrq;
extern guint16 mcc, mnc, lte_pci, nr_pci; 

static void on_user_abort() {
	g_main_loop_quit(m_main_loop);
}

unsigned long timestamp_to_its(unsigned long unix_timestamp){
	if (unix_timestamp == 0)
		return 0;
	// ITS timestamp = (seconds since 1970 - seconds before 2004) + leap seconds since 2004
	return (unix_timestamp - 1072915200) + 5;
}

// TODO: Ainda não implementado o uso do GNSS
void com_config(void* com_struct){
	communications_manager_t *com = (communications_manager_t*) com_struct;
	com->mqtt_manager = (mqtt_manager_t*) calloc(sizeof(mqtt_manager_t), 1);
	com->gps_data = (GNSSData*) calloc(sizeof(it2s_gnss_data_t), 1);
	com->gnss_ctx = it2s_gnss_setup();
}

void* mqtt_config(void* mqtt_struct){
	int rv; 
	char client_id[16];
	mqtt_manager_t *mqtt = (mqtt_manager_t*) mqtt_struct;
    
	mqtt->station_id = MQTT_STATION_ID;
	mqtt->msg_sn = 0;

	mosquitto_lib_init();
	sprintf(client_id, MQTT_CLIENT_ID);
	mqtt->mosq = mosquitto_new(client_id, true, 0);
	mosquitto_username_pw_set(mqtt->mosq, MQTT_USERNAME, MQTT_PASSWORD);

    rv = mosquitto_tls_set(mqtt->mosq, MQTT_CAFILE, NULL, NULL, NULL, NULL);
	rv = mosquitto_tls_insecure_set(mqtt->mosq, true);

	syslog_debug("[it2s-data-collection] MQTT - connecting to broker...\n");
	rv = mosquitto_connect(mqtt->mosq, MQTT_HOST, MQTT_PORT, 60);
	if (rv){
		printf("Error connecting to broker: %s\n", mosquitto_strerror(rv));
		syslog_err("[it2s-data-collection] MQTT - error connecting: %s\n", mosquitto_strerror(rv));
		return NULL;
	}else{
		printf("Connected to broker\n");
		syslog_debug("[it2s-data-collection] MQTT - connection complete.\n");
	}

	mosquitto_loop_forever(mqtt->mosq, 1000, 1);
	return NULL;
}

void it2s_loop(communications_manager_t* communications_manager, int period){
	m_main_loop = g_main_loop_new(NULL, 0);
	g_timeout_add_seconds(period, it2s_read, communications_manager);
	g_main_loop_run(m_main_loop);
}

int it2s_read(void* user_data){
	communications_manager_t* communications_manager = (communications_manager_t*) user_data;
	it2s_gnss_read(communications_manager->gnss_ctx, communications_manager->gps_data);
	it2s_send_values(communications_manager);
	return 1;
}

void it2s_send_values(communications_manager_t* communications_manager){
	mqtt_manager_t* mqtt_manager = communications_manager->mqtt_manager;
	int rv;
	char* buffer = (char*) calloc(8192, 1);

	if(it2s_make_message(communications_manager, buffer))
		return;
	
	char* topic = "telemetry";
	mqtt_manager->topic = (char*) calloc(strlen(topic)+1, 1);
	memcpy(mqtt_manager->topic, topic, strlen(topic)+1);

	rv = mosquitto_publish(mqtt_manager->mosq, NULL, mqtt_manager->topic, strlen(buffer), buffer, 0, 0);
	if (rv != MOSQ_ERR_SUCCESS){
		syslog_err("[it2s-data-collection] MQTT - error publishing: %s\n", mosquitto_strerror(rv));
		printf("Error publishing: %s\n", mosquitto_strerror(rv));
	}

	syslog_debug("[it2s-data-collection] MQTT - invalid gps\n");

	free(buffer);
}


int it2s_make_message(communications_manager_t* communications_manager, char* buffer){
	it2s_gnss_data_t* gps_data = communications_manager->gps_data;

    json_object *jobj = json_object_new_object();
    
	// Topic with command to modify the twin
	json_object_object_add(jobj, "topic", json_object_new_string("org.acme/my-device-2/things/twin/commands/modify"));
	
	// Empty headers
	json_object *headers = json_object_new_object();
	json_object_object_add(jobj, "headers", headers);

	json_object_object_add(jobj, "path", json_object_new_string("/features"));

    json_object *value = json_object_new_object();
    
	// Create reference position JSON object
	json_object *referencePosition = json_object_new_object();
	json_object *referencePositionProperties = json_object_new_object();
	json_object_object_add(referencePositionProperties, "latitude", json_object_new_double(gps_data->latitude.value));
	json_object_object_add(referencePositionProperties, "longitude", json_object_new_double(gps_data->longitude.value));
	json_object_object_add(referencePositionProperties, "altitude", json_object_new_double(gps_data->altitude.value));
	json_object_object_add(referencePosition, "properties", referencePositionProperties);

	// Create modem status JSON object
    json_object *modemStatus = json_object_new_object();
	json_object *modemStatusProperties = json_object_new_object();
	json_object_object_add(modemStatusProperties, "mcc", json_object_new_int(mcc));
	json_object_object_add(modemStatusProperties, "mnc", json_object_new_int(mnc));
	json_object_object_add(modemStatus, "properties", modemStatusProperties);

    // Create NR modem status
    json_object *nrStatus = json_object_new_object();
	json_object *nrStatusProperties = json_object_new_object();
	json_object_object_add(nrStatusProperties, "rsrp", json_object_new_int(nr_rsrp));
	json_object_object_add(nrStatusProperties, "rsrq", json_object_new_int(nr_rsrq));
	json_object_object_add(nrStatusProperties, "snr", json_object_new_int(nr_snr));
	json_object_object_add(nrStatusProperties, "pci", json_object_new_int(nr_pci));
	json_object_object_add(nrStatus, "properties", nrStatusProperties);

    // Create LTE modem status
    json_object *lteStatus = json_object_new_object();
	json_object *lteStatusProperties = json_object_new_object();
	json_object_object_add(lteStatusProperties, "rsrp", json_object_new_int(lte_rsrp));
	json_object_object_add(lteStatusProperties, "rsrq", json_object_new_int(lte_rsrq));
	json_object_object_add(lteStatusProperties, "snr", json_object_new_int(lte_snr));
	json_object_object_add(lteStatusProperties, "pci", json_object_new_int(lte_pci));
	json_object_object_add(lteStatusProperties, "rssi", json_object_new_int(lte_rssi));
	json_object_object_add(lteStatus, "properties", lteStatusProperties);

	// Timestamp and sequence number
	json_object *body = json_object_new_object();
	json_object *bodyProperties = json_object_new_object();
	json_object_object_add(bodyProperties, "generationDeltaTime", json_object_new_int(gps_data->timestamp % 65536));
	json_object_object_add(bodyProperties, "sequenceNumber", json_object_new_int(communications_manager->mqtt_manager->msg_sn++));
	json_object_object_add(body, "properties", bodyProperties);

    // Add all the twin features to the value object
    json_object_object_add(value, "reference_position", referencePosition);
	json_object_object_add(value, "modem_status", modemStatus);
	json_object_object_add(value, "nr_modem_status", nrStatus);
	json_object_object_add(value, "lte_modem_status", lteStatus);
	json_object_object_add(value, "body", body);

    // Add the value object to the main jobj
    json_object_object_add(jobj, "value", value);

	// console log the JSON object
	printf ("The json object created: %s\n", json_object_to_json_string(jobj));

    // Convert the JSON object to a string and store it in buffer
    const char *jsonString = json_object_to_json_string(jobj);
    snprintf(buffer, 8192, "%s", jsonString);
    
    // Free the JSON object
    json_object_put(jobj);

    return 0; 

}


void it2s_clean(communications_manager_t* communications_manager){
	mqtt_manager_t* mqtt_manager = communications_manager->mqtt_manager;
	
	mosquitto_disconnect(mqtt_manager->mosq);
	mosquitto_loop_stop(mqtt_manager->mosq, 0);
	pthread_join(mqtt_manager->mqtt_thread, NULL);
	mosquitto_lib_cleanup();

	free(mqtt_manager->mosq);
	free(mqtt_manager);

	free(communications_manager);
	qmi_clean_up();
	sleep(2);
}

int main(int argc, char *argv[]) {
	communications_manager_t* communications_manager = (communications_manager_t*) malloc(sizeof(communications_manager_t));
	com_config(communications_manager);
	
	GFile* device = g_file_new_for_path("/dev/cdc-wdm0");
	qmi_device_new(device, NULL, device_new_callback, NULL);

	pthread_create(&communications_manager->mqtt_manager->mqtt_thread, NULL, mqtt_config, communications_manager->mqtt_manager);
	syslog_debug("[it2s-data-collection] MQTT thread initialized\n");

	signal(SIGINT, (__sighandler_t) on_user_abort);
	it2s_loop(communications_manager, 1);
	it2s_clean(communications_manager);
	return 0;
}

