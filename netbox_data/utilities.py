from dcim.models import ConsolePort, Device, PowerPort, Site
from ipam.models import VLAN, Prefix, Role
from rest_framework import status
from rest_framework.response import Response
from virtualization.models import VirtualMachine


def fetchDeviceInfoByName(site_name, device_name, device_setup_type, remote_config=''):
    try:
        site = Site.objects.get(name=site_name)
        device_info = Device.objects.get(name=device_name, site=site.id)
        return fetchDeviceInfo(site.id, device_info.id, device_setup_type, remote_config)
    except Site.DoesNotExist:
        return Response([{"error": f"Site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)
    except Device.DoesNotExist:
        return Response([{"error": f"Device {device_name} with site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)

def fetchDeviceInfo(site_id, device_id, device_setup_type, remote_config=''):
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
        # need to get the role id because of the stupid api needs id not name
        roles = Role.objects.filter(slug="pod-backdoor")
        if len(roles) == 1 and device_info[0].tenant:
            backdoor_vlan = VLAN.objects.filter(role=roles[0].id, name=f"backdoor-{device_info[0].tenant.slug.split('-')[1]}")
            if len(backdoor_vlan) == 1:
                backdoor_prefix = Prefix.objects.filter(vlan_id=backdoor_vlan[0].id, site=site_id)
                if len(backdoor_prefix) == 1:
                    nb_data["backdoor_prefix"] = str(backdoor_prefix[0].prefix)
    except Exception as e:
        return Response([{"error": f"Got an error: {e}"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(nb_data, status=status.HTTP_200_OK)

def fetchVlanInfoByNameVid(site_name, vlan_vid):
    try:
        site = Site.objects.get(name=site_name)
        vlan_info = VLAN.objects.get(vid=vlan_vid, site=site.id)
        return fetchVlanInfo(site.id, vlan_info.id)
    except Site.DoesNotExist:
        return Response([{"error": f"Site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)
    except VLAN.DoesNotExist:
        return Response([{"error": f"VLAN {vlan_vid} with site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)


def fetchVlanInfo(site_id, vlan_id):
    try:
        '''
        this is what the data should look like
        http://netbox-lookup-api-tanzu.usw1.production.devnetsandbox.local/api/v1/podinfo?vlan=1411&site=usw1

        {
            backdoor: {
                prefix: "10.21.11.0/24",
                vlan_description: "3311 (backdoor-pod11hw)",
                vlan_id: "3311",
                vlan_name: "backdoor-pod11hw",
                vlan_number: "2",
                vlan_uuid: "3211"
            },
            backend: {
                prefix: "10.10.20.0/24",
                vlan_description: "1411 (pod11hw-backend)",
                vlan_id: "1411",
                vlan_name: "pod11hw-backend",
                vlan_number: "1",
                vlan_uuid: "3210"
            },
            devices: [
                {
                    device_model: "UCS C220M4",
                    device_name: "usw1-sbx-ucsc-1",
                    device_number: "1",
                    primary_ip: "10.10.20.60/24"
                }
            ],
            firewall_ip: "10.17.233.20/21",
            firewall_name: "usw1-pod11hw-fw",
            pod_description: "",
            pod_name: "Pod11hw",
            vpn_address: "devnetsandbox-usw1-reservation.cisco.com",
            vpn_port: 21411
        }        
        '''

        vlan = VLAN.objects.get(id=vlan_id, site=site_id)

        # Build the default response.
        nb_data = {
            "backdoor" : {}, 
            "backend": {}, 
            "devices": [],
            "firewall_ip" : "",
            "firewall_name" : "",
            "pod_name" : "",
            "vpn_address": f"devnetsandbox-usw1-reservation.cisco.com:{20000+vlan.vid}",
            "vpn_port" :  20000+vlan.vid
        }

        ## Now get the VLAN (backend info)
        if vlan.tenant == None:
            return Response({"error": f"VLAN Tenant is not configured for VLAN {vlan.vid}"}, status=status.HTTP_400_BAD_REQUEST)

        nb_data["backend"] = {
            "prefix"    :  "10.10.20.0/24",
            "vlan_id"   : vlan.vid,
            "vlan_name" : vlan.tenant.name,
            "vlan_uuid" : vlan.tenant.id
        }
        
        ## Grab backdoor vlan info
        role = Role.objects.get(slug="pod-backdoor")
        vlan_tenant_slug_split = str(vlan.tenant.slug).split('-')
        if len(vlan_tenant_slug_split) < 2:
            return Response({"error": f"The vlan tenant slug {vlan.tenant.slug} is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        backdoor_vlan = VLAN.objects.get(role=role.id, name=f"backdoor-{vlan_tenant_slug_split[1]}", site=site_id)
        backdoor_prefix = Prefix.objects.get(vlan=backdoor_vlan, site=site_id)
        backdoor_vlan_name = backdoor_prefix.vlan.name

        nb_data["backdoor"] = {
            "prefix": str(backdoor_prefix.prefix),
            "vlan_description": "" if backdoor_prefix.vrf is None else backdoor_prefix.vrf.name,
            "vlan_id": backdoor_prefix.vlan.vid,
            "vlan_name": backdoor_vlan_name
        }

        # get the firewall info
        backdoor_vlan_name_split = backdoor_vlan_name.split("-")
        if len(backdoor_vlan_name) < 2:
            return Response({"error": f"The backdoor vlan name {backdoor_vlan_name} is invalid."}, status=status.HTTP_400_BAD_REQUEST)
            
        firewall_name = f'usw1-{backdoor_vlan_name_split[1]}-fw'
        firewall_device_info = VirtualMachine.objects.get(name=firewall_name, site=site_id)
        
        firewall_cidr = "" if firewall_device_info.primary_ip is None else str(firewall_device_info.primary_ip.address)
        nb_data["firewall_cidr"] = firewall_cidr
        nb_data["firewall_ip"] = firewall_cidr.split("/")[0] if firewall_cidr else "" # Don't need to check on the length of the split because the inforcement of the / is mandatory during creation
        nb_data["firewall_name"] = firewall_name
        nb_data["pod_name"] = vlan.name
        nb_data["nat_ip_address"] = str(firewall_device_info.cf['vpnless_nat_ip'].address) if 'vpnless_nat_ip' in firewall_device_info.cf else ""

        if firewall_device_info.tenant:
            devices = Device.objects.filter(site=site_id, tenant=firewall_device_info.tenant.id)
            for device in devices:
                ip = "" if device.primary_ip is None else str(device.primary_ip.address)
                device = {
                        "device_name" : device.name,
                        "device_ip" : ip
                      }
                nb_data["devices"].append(device)
    except VLAN.DoesNotExist as e:
        return Response({"error": f"Unable to find the Vlan: {e}."}, status=status.HTTP_400_BAD_REQUEST)
    except Role.DoesNotExist:
        return Response({"error": f"Unable to find the Role with slug 'pod-backdoor'."}, status=status.HTTP_400_BAD_REQUEST)
    except Prefix.DoesNotExist:
        return Response({"error": f"Unable to find the backdoor prefix"}, status=status.HTTP_400_BAD_REQUEST)
    except VirtualMachine.DoesNotExist:
        return Response({"error": f"Unable to find the virtual machine"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Got an error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(nb_data, status=status.HTTP_200_OK)