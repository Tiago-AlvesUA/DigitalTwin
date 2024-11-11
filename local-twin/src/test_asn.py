import asn1tools
import json

asn1_files = ['ditto_message_test.asn1', 'cd_dictionary_ts_102_894_2_v2.2.1.asn1', 'modem_status_2.0.asn1']
dtm = asn1tools.compile_files(asn1_files, 'jer')

def main():

    ditto_msg = {
        "topic": f"org.acme/my-device/things/twin/commands/modify",
        "referencePosition": {
            "properties": {
                "latitude": 340800,
                "longitude": -802001,
                "positionConfidenceEllipse": {
                    "semiMajorConfidence": 4095,
                    "semiMinorConfidence": 4095,
                    "semiMajorOrientation": 900
                },
                "altitude": {
                    "altitudeValue": 200,
                    "altitudeConfidence": "unavailable"
                }
            }
        }   
    }
        

    encoded_data = dtm.encode('DITTO-STRUCT', ditto_msg)

if __name__ == '__main__':
    main()
