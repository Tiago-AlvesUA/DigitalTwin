#include <libqmi-glib.h>
#include <stdio.h>
#include "qmi.h"

QmiDevice* qmidev;
QmiClient* qmiclient;

gint8 ratmode, lte_rssi, lte_rsrq;
guint8 cid;
gint16 lte_rsrp, nr_rsrp, lte_snr, nr_snr, nr_rsrq;
guint16 mcc, mnc, lte_pci, nr_pci; 

void qmi_clean_up(){
	qmi_device_release_client(qmidev, qmiclient, QMI_DEVICE_RELEASE_CLIENT_FLAGS_NONE, 10, NULL, (GAsyncReadyCallback) device_release_client_callback, NULL);
}

void device_release_client_callback(GObject* sourceObject, GAsyncResult* res) {
	qmiclient = (QmiClient*) sourceObject;
	GError* error = NULL;
	gboolean output = qmi_device_release_client_finish(qmidev, res, &error);
	if (!output) {
		g_error("[it2s-data-collection] Failed to release qmi client: %s", error->message);
		g_error_free(error);
		exit(1);
	}
	exit(0);
}

void nas_cell_location_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	qmiclient = (QmiClient*) sourceObject;
	GError* error = NULL;

	try {
		QmiMessageNasGetCellLocationInfoOutput*	output = qmi_client_nas_get_cell_location_info_finish((QmiClientNas*) qmiclient, res, &error);
		if (!output) {
			g_error("[it2s-data-collection] Failed to query cell location: %s", error->message);
			g_error_free(error);
			qmi_clean_up();

		}
		if (!qmi_message_nas_get_cell_location_info_output_get_result(output, &error)) {
			g_error("[it2s-data-collection] Failed to get result of cell location: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}

		if (ratmode == QMI_NAS_RADIO_INTERFACE_LTE) {
			GArray* list_placeholder = g_array_new (FALSE, FALSE, sizeof (QmiMessageNasGetCellLocationInfoOutputIntrafrequencyLteInfoV2CellElement));	
			qmi_message_nas_get_cell_location_info_output_get_intrafrequency_lte_info_v2(output, NULL, NULL, NULL, NULL, NULL, &lte_pci, NULL, NULL, NULL, NULL, &list_placeholder, &error);
			if (error != NULL) {
				g_error("[it2s-data-collection] Failed to get lte cell location: %s", error->message);
				g_error_free(error);
				qmi_clean_up();
			}
		}

		if (ratmode == QMI_NAS_RADIO_INTERFACE_5GNR) {
			qmi_message_nas_get_cell_location_info_output_get_nr5g_cell_information(output, NULL, NULL, NULL, &nr_pci, NULL, NULL, NULL, &error);
			if (error != NULL) {
				g_error("[it2s-data-collection] Failed to get 5g cell location: %s", error->message);
				g_error_free(error);
				qmi_clean_up();
			}
		}

		qmi_message_nas_get_cell_location_info_output_unref(output);
		qmi_client_nas_get_home_network((QmiClientNas*) qmiclient, NULL, 10, NULL, nas_get_home_network_callback, NULL);
	}
	catch (...) {
		// TODO: instantiate ref and catch specific exceptions
		syslog_debug("[it2s-data-collection] unexpected error\n");
		qmi_clean_up();
	}
}

void nas_signal_info_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	qmiclient = (QmiClient*) sourceObject;
	GError* error = NULL;

	try {
		QmiMessageNasGetSignalInfoOutput* output = qmi_client_nas_get_signal_info_finish((QmiClientNas*)qmiclient, res, &error);

		if (!output) {
			g_error("[it2s-data-collection] Failed to query signal info: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}

		if (!qmi_message_nas_get_signal_info_output_get_result(output, &error)) {
			g_error("[it2s-data-collection] Failed to get result of lte signal info: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}

		if (ratmode == QMI_NAS_RADIO_INTERFACE_LTE) {
			qmi_message_nas_get_signal_info_output_get_lte_signal_strength(output, &lte_rssi, &lte_rsrq, &lte_rsrp, &lte_snr, &error);
			if (error != NULL) {
				g_error("[it2s-data-collection] Failed to get lte signal strength: %s", error->message);
				g_error_free(error);
				qmi_clean_up();
			}
		}

		qmi_message_nas_get_signal_info_output_get_5g_signal_strength(output, &nr_rsrp, &nr_snr, &error);
		if (error != NULL) {
			g_error("[it2s-data-collection] Failed to get 5g signal strength: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}

		qmi_message_nas_get_signal_info_output_get_5g_signal_strength_extended(output, &nr_rsrq, &error);
		if (error != NULL) {
			g_error("[it2s-data-collection] Failed to get 5g signal strength extended: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}

		qmi_message_nas_get_signal_info_output_unref(output);
		qmi_client_nas_get_cell_location_info((QmiClientNas*) qmiclient, NULL, 10, NULL, nas_cell_location_callback, NULL);
	}
	catch (...) {
		// TODO: instantiate ref and catch specific exceptions
		syslog_debug("[it2s-data-collection] unexpected error\n");
		qmi_clean_up();
	}
}

void nas_rf_band_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	qmiclient = (QmiClient*) sourceObject;
	GError* error = NULL;

	try {
		QmiMessageNasGetRfBandInformationOutput* output = qmi_client_nas_get_rf_band_information_finish((QmiClientNas*) qmiclient, res, &error);
		if (!output) {
			g_error("[it2s-data-collection] Failed to query RF band: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}
		if (!qmi_message_nas_get_rf_band_information_output_get_result(output, &error)) {
			g_error("[it2s-data-collection] Failed to get result of RF band: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}
		GArray* list_placeholder = g_array_new (FALSE, FALSE, sizeof (QmiMessageNasGetRfBandInformationOutputListElement));	
		if (!qmi_message_nas_get_rf_band_information_output_get_list(output, &list_placeholder, &error)) {
			g_error("[it2s-data-collection] Failed to get output list of RF band: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}
		for (int i = 0; i < list_placeholder->len; i++){
			QmiMessageNasGetRfBandInformationOutputListElement output_list = g_array_index(list_placeholder, QmiMessageNasGetRfBandInformationOutputListElement, i);
			ratmode = output_list.radio_interface;
		}
		qmi_message_nas_get_rf_band_information_output_unref(output);
		qmi_client_nas_get_signal_info((QmiClientNas*) qmiclient, NULL, 10, NULL, nas_signal_info_callback, NULL);
	}
	catch (...) {
		// TODO: instantiate ref and catch specific exceptions
		syslog_debug("[it2s-data-collection] unexpected error\n");
		qmi_clean_up();
	}
}

void nas_get_home_network_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	qmiclient = (QmiClient*) sourceObject;
	GError* error = NULL;

	try {
		QmiMessageNasGetHomeNetworkOutput* output = qmi_client_nas_get_home_network_finish((QmiClientNas*) qmiclient, res, &error);
		if (!output) {
			g_error("[it2s-data-collection] Failed to query home network: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}
		if (!qmi_message_nas_get_home_network_output_get_result(output, &error)) {
			g_error("[it2s-data-collection] Failed to get result of home network: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}
		if (!qmi_message_nas_get_home_network_output_get_home_network(output, &mnc, &mcc, NULL, &error)) {
			g_error("[it2s-data-collection] Failed to get home network: %s", error->message);
			g_error_free(error);
			qmi_clean_up();
		}

		qmi_message_nas_get_home_network_output_unref(output);
		qmi_client_nas_get_rf_band_information((QmiClientNas*) qmiclient, NULL, 10, NULL, nas_rf_band_callback, NULL);
	}
	catch (...) {
		// TODO: instantiate ref and catch specific exceptions
		syslog_debug("[it2s-data-collection] unexpected error\n");
		qmi_clean_up();
	}
}

void client_alloc_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	qmidev = (QmiDevice*) sourceObject;
	GError* error = NULL;
	qmiclient = (QmiClient*) qmi_device_allocate_client_finish(qmidev, res, &error);
	cid = qmi_client_get_cid((QmiClient*) qmiclient);
	syslog_debug("[it2s-data-collection] allocated client with cid: %d", cid);

	if (!qmiclient) {
		g_error("[it2s-data-collection] Failed to create QMI client: %s", error->message);
		g_error_free(error);
		exit(1);
	}
	qmi_client_nas_get_home_network((QmiClientNas*) qmiclient, NULL, 10, NULL, nas_get_home_network_callback, NULL);
}

void device_open_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	qmidev = (QmiDevice*) sourceObject;
	GError* error = NULL;
	if (!qmi_device_open_finish(qmidev, res, &error)){
		g_error("[it2s-data-collection] Failed to open QMI device: %s", error->message);
		g_error_free(error);
		exit(1);
	}
	qmi_device_allocate_client(qmidev, QMI_SERVICE_NAS, QMI_CID_NONE, 10, NULL, client_alloc_callback, NULL);
}

void device_new_callback(GObject* sourceObject, GAsyncResult* res, void* userData) {
	GError* error = NULL;
	qmidev = qmi_device_new_finish(res, &error);
	if (!qmidev) {
		g_error("[it2s-data-collection] Failed to create QMI device: %s", error->message);
		g_error_free(error);
		exit(1);
	}
	qmi_device_open(qmidev, QMI_DEVICE_OPEN_FLAGS_PROXY, 10, NULL, device_open_callback, NULL);
}
