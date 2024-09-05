from dcim.models import ConsolePort, Device, PowerPort, Site
from ipam.models import VLAN, Prefix, Role
from rest_framework import permissions, status
from rest_framework.response import Response
from virtualization.models import VirtualMachine


def fetchDataByName(site_name, device_name, device_setup_type, remote_config=''):
    try:
        site = Site.objects.get(name=site_name) # Throws a Site.DoesNotExist if it does not exist
        device_info = Device.objects.get(name=device_name, site=site.id)
        return fetch_data(site.id, device_info.id, device_setup_type, remote_config)
    except Site.DoesNotExist:
        return Response([{"error": f"Site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)

def fetch_data(site_id, device_id, device_setup_type, remote_config=''):
    # Build the default response.
    # Doing this so that the output has every field no matter what data is found.
    nb_data = {
        "remote_config" : "",
        "device_ip": "",
        "device_cidr" : "",
        "device_console_port_count" : 0,
        "device_power_port_count" : 0,
        "device_setup_type" : "",
        "device_type": "",
        "ts_ip" : "",
        "ts_name" : "",
        "ts_port": "",
        "ts_telnet_port" : "",
        "outlets" : [],
        "pdu_name" : "",
        "pdu_ip" : "",
        "pdu_pyats_os" : "",
        "pdu_type" : "",
        "backdoor_prefix" : ""
    }

    nb_data["device_setup_type"] = device_setup_type
    nb_data["remote_config"] = remote_config

    try:        
        device_info = Device.objects.filter(id=device_id, site=site_id)
        if len(device_info) == 1: # A device name is unique per site so it should only return 1 if found.
            nb_data["device_type"] = "hardware"
            
            nb_data["device_console_port_count"] = device_info[0].console_port_count
            if device_info[0].console_port_count > 0:
                # grab the info from console_cable
                console = ConsolePort.objects.filter(device=device_info[0].id)
                # print(f"console peer {console[0].link_peers[0].device}")
                
                if len(console) > 0: # TODO: There can be more than one console so why does it only use console[0]. Shouldn't it do a for loop?
                    if len(console[0].link_peers) > 0:
                        nb_data["ts_name"] = console[0].link_peers[0].device.name

                        # now get the IP of the term server
                        ts_device_info = Device.objects.filter(name=console[0].link_peers[0].device)
                        if len(ts_device_info) > 0:
                            nb_data["ts_ip"] = str(ts_device_info[0].primary_ip).split("/")[0]
                        
                    if console[0].cable:
                        nb_data["ts_telnet_port"] = console[0].cable.label
                        nb_data["ts_port"] = console[0].cable.label[2:]

            nb_data["device_power_port_count"] = device_info[0].power_port_count
            if device_info[0].power_port_count > 0:
                for pdu in PowerPort.objects.filter(device=device_info[0].id):
                    nb_data["pdu_name"] = pdu.link_peers[0].device.name if len(pdu.link_peers) > 0 else ""
                    if pdu.cable and pdu.cable.label:
                        nb_data["outlets"].append(int(pdu.cable.label))
                
                # Get some more info on the PDU itself.
                pdu_device_info = Device.objects.filter(name=nb_data["pdu_name"])
                if len(pdu_device_info) > 0:
                    if pdu_device_info[0].primary_ip:
                        nb_data["pdu_ip"] = str(pdu_device_info[0].primary_ip.address).split("/")[0]
                    
                    if "pyats_os" in pdu_device_info[0].custom_fields:
                        nb_data["pdu_pyats_os"] = pdu_device_info[0].custom_fields["pyats_os"]
                    else :
                        nb_data["pdu_pyats_os"] = "linux"
                    
                    if "pdu_type" in pdu_device_info[0].custom_fields:
                        nb_data["pdu_type"]= pdu_device_info[0].custom_fields["pdu_type"]
                    else:
                        nb_data["pdu_type"]= "generic_cli"
        else:
                ## See if it's a VM
            device_info = VirtualMachine.objects.filter(name=device_info[0].name)
            if len(device_info) == 1:
                nb_data["device_type"] = "virtual"
            else:
                return Response([{"error": f"{device_info[0].name} @ site id {site_id} does not exist."}], status=status.HTTP_404_NOT_FOUND)

        nb_data["device_cidr"] = str(device_info[0].primary_ip)
        nb_data["device_ip"] = nb_data["device_cidr"].split("/")[0]
        
        for a,b in device_info[0].custom_field_data.items():
            # print(f"{a} ==>  {b}")
            if b:
                nb_data[f'device_{a}'] = b
            else:
                nb_data[f'device_{a}'] = ""

        # '''
        # backdoor prefix is pulled via backdoor vlan
        # We can use the name of this by splitting the tenant slug of the device and adding backdoor to the front
        # e.g.
        # "slug": "usw1-pod10hw"
        # vlan = backdoor-pod10hw
        # '''    
        # # print(f"(6)Tenant Slug :: {device_info[0].tenant.slug}")
        # # need to get the role id because of the stupid api needs id not name
        roles = Role.objects.filter(slug="pod-backdoor")
        if len(roles) == 1 and device_info[0].tenant:
            backdoor_vlan = VLAN.objects.filter(role=roles[0].id, name=f"backdoor-{device_info[0].tenant.slug.split('-')[1]}")
            if len(backdoor_vlan) == 1:
                # print(f"(7) backdoor_valn.vid --> {backdoor_vlan[0].vid}")
                backdoor_prefix = Prefix.objects.filter(vlan_id=backdoor_vlan[0].id, site=site_id)
                if len(backdoor_prefix) == 1:
                    nb_data["backdoor_prefix"] = str(backdoor_prefix[0].prefix)
    except Exception as e:
        return Response([{"error": f"Got an error: {e}"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(nb_data, status=status.HTTP_200_OK)