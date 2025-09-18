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
// #include <mosquitto.h>
#include "it2s-data-reader.h"
#include "qmi.h"
#include <json-c/json.h>
// new library for D-Bus
#include <gio/gio.h>


extern "C" {
	#include <it2s-gnss.h>
}

using namespace std;

static GMainLoop *m_main_loop;
static GVariant *params_variant;
static GDBusConnection *connection;

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
	return ((unix_timestamp * 1000) + 5000) - 1072915200000; 
	//return (unix_timestamp - 1072915200) + 5;
}

void com_config(void* com_struct){
	communications_manager_t *com = (communications_manager_t*) com_struct;
	com->gps_data = (GNSSData*) calloc(sizeof(it2s_gnss_data_t), 1);
	com->gnss_ctx = it2s_gnss_setup();
	com->msg_sn = 0;
}

void init_dbus_connection(){
	GError *error = NULL;
	connection = g_bus_get_sync(G_BUS_TYPE_SYSTEM, NULL, &error);
	if (error != NULL) {
		g_printerr("Error getting D-Bus connection: %s\n", error->message);
		g_error_free(error);
		exit(1);
	}
}

void send_dbus_signal(){
	GError *error = NULL;

	g_dbus_connection_emit_signal(
		connection, // Connection to the D-Bus
		NULL, // Sender
		"/org/example/DataReader", // Object path
		"org.example.DataReader", // Interface name
		"NewDataAvailable", // Signal name
		params_variant, 
		&error
	);

	if (error != NULL) {
		g_printerr("Error emitting signal: %s\n", error->message);
		g_error_free(error);
	}else{
		g_print("Signal emitted\n\n");
	}
}

void it2s_loop(communications_manager_t* communications_manager, int period){
	m_main_loop = g_main_loop_new(NULL, 0);
	g_timeout_add_seconds(period, it2s_read, communications_manager);
	g_main_loop_run(m_main_loop);
}

int it2s_read(void* user_data){
	communications_manager_t* communications_manager = (communications_manager_t*) user_data;
	it2s_gnss_read(communications_manager->gnss_ctx, communications_manager->gps_data);
	it2s_make_message(communications_manager);
	send_dbus_signal();
	return 1;
}


void it2s_make_message(communications_manager_t* communications_manager){
	it2s_gnss_data_t* gps_data = communications_manager->gps_data;
	
	int32_t gps_lat = gps_data->latitude.value;
	int32_t gps_lon = gps_data->longitude.value;
	int32_t gps_alt = gps_data->altitude.value;
	//printf("GPS TIMESTAMP: %lu\n", gps_data->timestamp);
	ulong gps_timestamp = gps_data->timestamp;
	//ulong timestamp = timestamp_to_its(gps_data->timestamp);// % 65536);
	// TODO: 65536 module only after

	printf("GPS: %d, %d, %d\n", gps_lat, gps_lon, gps_alt);
	printf("Timestamp: %lu\n", gps_timestamp);//timestamp);
	printf("RAT: %d, lte_rssi: %d, lte_rsrq: %d\n", ratmode, lte_rssi, lte_rsrq);
	printf("CID: %d\n", cid);
	printf("lte_rsrp: %d, nr_rsrp: %d, lte_snr: %d, nr_snr: %d, nr_rsrq: %d\n", lte_rsrp, nr_rsrp, lte_snr, nr_snr, nr_rsrq);	
	printf("Message Seq Number: %d\n", communications_manager->msg_sn);


	params_variant = g_variant_new("(iiiiiiuiiiiiuuuuti)",
		gps_lat, gps_lon, gps_alt, 
		ratmode, lte_rssi, lte_rsrq,
		cid,
		lte_rsrp, nr_rsrp, lte_snr, nr_snr, nr_rsrq,
		mcc, mnc, lte_pci, nr_pci,
		gps_timestamp, communications_manager->msg_sn++
	);
}


void it2s_clean(communications_manager_t* communications_manager){
	free(communications_manager);
	qmi_clean_up();
	sleep(2);
}

int main(int argc, char *argv[]) {
	communications_manager_t* communications_manager = (communications_manager_t*) malloc(sizeof(communications_manager_t));
	com_config(communications_manager);
	
	GFile* device = g_file_new_for_path("/dev/cdc-wdm0");
	qmi_device_new(device, NULL, device_new_callback, NULL);
	init_dbus_connection();

	signal(SIGINT, (__sighandler_t) on_user_abort);
	it2s_loop(communications_manager, 1);
	it2s_clean(communications_manager);

	// Clean up
	g_object_unref(connection);
	return 0;
}

