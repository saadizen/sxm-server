import sys
import requests
import uuid as uuid_module
from flask import Flask, request, render_template


api = Flask(__name__)
SESSION = requests.session()
RESPONSES = {
    'activated': {
        'crm': {'resultCode': 'SUCCESS', 'opstatus': 0, 'httpStatusCode': 200},
        'create': {'resultData': [{'resultCode': 'SUCCESS'}], 'opstatus': 0, 'httpStatusCode': 200},
        'refresh': {'opstatus': 0, 'errors': [{'resultCode': 'SUCCESS'}], 'httpStatusCode': 200},
    },
    'already_activated': {
        'crm': {'resultCode': 'SUCCESS', 'opstatus': 0, 'httpStatusCode': 200},
        'create': {'resultData': [{'resultCode': 'FAILURE'}, {'code': '11-03-ACCT-1073'},
                                  {'message': 'Device ID is already active'}], 'opstatus': 0, 'httpStatusCode': 200},
        'refresh': {'opstatus': 0, 'errors': [{'resultCode': 'SUCCESS'}], 'httpStatusCode': 200},
    }
}


def appconfig():
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/authService/100000002/appconfig",
        headers={
            "X-Voltmx-Integrity": "GWSUSEVMJK;FEC9AA232EC59BE8A39F0FAE1B71300216E906B85F40CA2B1C5C7A59F85B17A4",
            "X-HTTP-Method-Override": "GET",
            "Accept": "*/*",
            "X-Voltmx-App-Secret": "c086fca8646a72cf391f8ae9f15e5331",
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "X-Voltmx-App-Key": "67cfe0220c41a54cb4e768723ad56b41",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
        },
    )

    return response.json()


def login():
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/authService/100000002/login",
        headers={
            "X-Voltmx-Platform-Type": "ios",
            "Accept": "application/json",
            "X-Voltmx-App-Secret": "c086fca8646a72cf391f8ae9f15e5331",
            "Accept-Language": "en-us",
            "X-Voltmx-SDK-Type": "js",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-SDK-Version": "9.5.36",
            "X-Voltmx-App-Key": "67cfe0220c41a54cb4e768723ad56b41",
        },
    )

    return response.json().get('claims_token').get('value')


def version_control(token: str, uuid: str):
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/DealerAppService7/VersionControl",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "deviceCategory": "iPhone",
            "appver": "3.1.0",
            "deviceLocale": "en_US",
            "deviceModel": "iPhone 6 Plus",
            "deviceVersion": "12.5.7",
            "deviceType": "",
        },
    )

    return response.json()


def get_properties(token: str, uuid: str):
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/DealerAppService7/getProperties",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
    )

    return response.json()


def update_device_sat_refresh_with_priority(device_id: str, token: str, uuid: str) -> int:
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/USUpdateDeviceSATRefresh/updateDeviceSATRefreshWithPriority",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "deviceId": device_id,
            "appVersion": "3.1.0",
            "lng": "-86.210313195",
            "deviceID": uuid,
            "provisionPriority": "2",
            "provisionType": "activate",
            "lat": "32.37436705",
        },
    )

    return response.json().get('seqValue', -1)


def get_crm_account_plan_information(device_id: str, token: str, seq_value: int, uuid: str):
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/DemoConsumptionRules/GetCRMAccountPlanInformation",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "seqVal": seq_value,
            "deviceId": device_id,
        },
    )

    return response.json()


def db_update_for_google(device_id: str, token: str, seq_value: int, uuid: str):
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/DBSuccessUpdate/DBUpdateForGoogle",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "OM_ELIGIBILITY_STATUS": "Eligible",
            "appVersion": "3.1.0",
            "flag": "failure",
            "Radio_ID": device_id,
            "deviceID": uuid,
            "G_PLACES_REQUEST": "",
            "OS_Version": "iPhone 12.5.7",
            "G_PLACES_RESPONSE": "",
            "Confirmation_Status": "SUCCESS",
            "seqVal": seq_value,
        },
    )

    return response.json()


def block_list_device(token: str, uuid: str):
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/USBlockListDevice/BlockListDevice",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "deviceId": uuid,
        },
    )

    return response.json()


def create_account(device_id: str, token: str, seq_value: int, uuid: str):

    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/DealerAppService3/CreateAccount",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "seqVal": seq_value,
            "deviceId": device_id,
            "oracleCXFailed": "1",
            "appVersion": "3.1.0",
        },
    )

    return response.json()


def update_device_sat_refresh_with_priority_cc(device_id: str, token: str, uuid: str):
    response = SESSION.post(
        url="https://dealerapp.siriusxm.com/services/USUpdateDeviceRefreshForCC/updateDeviceSATRefreshWithPriority",
        headers={
            "Accept": "*/*",
            "X-Voltmx-API-Version": "1.0",
            "X-Voltmx-DeviceId": uuid,
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SiriusXM Dealer/3.1.0 CFNetwork/1568.200.51 Darwin/24.1.0",
            "X-Voltmx-Authorization": token,
        },
        data={
            "deviceId": device_id,
            "provisionPriority": "2",
            "appVersion": "3.1.0",
            "device_Type": "iPhone iPhone 6 Plus",
            "deviceID": uuid,
            "os_Version": "iPhone 12.5.7",
            "provisionType": "activate",
        },
    )

    return response.json()


def process(device_id: str):

    results = {}

    uuid = str(uuid_module.uuid4())

    appconfig()
    auth_token = login()
    version_control(auth_token, uuid)
    get_properties(auth_token, uuid)
    seq = int(update_device_sat_refresh_with_priority(device_id, auth_token, uuid))
    results['crm'] = get_crm_account_plan_information(device_id, auth_token, seq, uuid)
    db_update_for_google(device_id, auth_token, seq, uuid)
    block_list_device(auth_token, uuid)
    results['create'] = create_account(device_id, auth_token, seq, uuid)
    results['refresh'] = update_device_sat_refresh_with_priority_cc(device_id, auth_token, uuid)

    return results


@api.route("/", methods=['GET', 'POST'])
def index() -> str:
    test = 'test' in request.args.keys()

    if test:
        result = {
            'success': True,
            'responses': RESPONSES.get('activated'),
        }
        return render_template('index.html', result=result)

    if request.method == 'POST':

        radio_id = request.form.get('radio_id').upper().strip()
        result = {
            'success': False,
            'responses': process(radio_id),
        }

        responses = {k: result.get('responses')[k] for k in result.get('responses').keys()}
        if responses.get('crm', {}).get('deviceId'):
            responses['crm'].pop('deviceId')

        result['success'] = responses == RESPONSES.get('activated') or responses == RESPONSES.get('already_activated')

        return render_template('index.html', result=result)

    else:
        return render_template('index.html')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        radio_id_input = sys.argv[1].upper().strip()
        print(f'Processing for Radio ID "{radio_id_input}"...')
        for key, value in process(radio_id_input).items():
            print(f"\n{key}:\n{value}")
    else:
        api.run()
