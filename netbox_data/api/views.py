import json
import requests
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from dcim.models import Device, Site, ConsolePort, PowerPort
from ipam.models import Prefix, VLAN, Role
from virtualization.models import VirtualMachine

from .serializers import NetboxDataSerializer

class NetboxDataDeviceViewSet(APIView):

    queryset = Site.objects.all()
    serializer_class = NetboxDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Get the request body
            request_body = request.body.decode("utf-8")
            if not request_body:
                return Response([{"error": "Missing request body."}], status=status.HTTP_400_BAD_REQUEST)
            data = json.loads(request_body)

            # Get the values from the request body
            site_name = data.get("site_name")
            device_name = data.get("device_name")
            device_setup_type = data.get("device_setup_type")
            remote_config = data.get("remote_config")

            if not(site_name and device_name and device_setup_type):
                return Response([{"error": "Missing one or more of the required parameters (site_name, device_name, and/or device_setup_type)."}], status=status.HTTP_400_BAD_REQUEST)

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

            if remote_config:
                nb_data["remote_config"] = remote_config
            
            nb_data["device_setup_type"] = device_setup_type

            site = Site.objects.get(name=site_name) # Throws a Site.DoesNotExist if it does not exist
            # print(f"Site exists: {site_name}, site id: {site.id}")
            
            device_info = Device.objects.filter(name=device_name, site=site.id)
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
                device_info = VirtualMachine.objects.filter(name=device_name)
                if len(device_info) == 1:
                    nb_data["device_type"] = "virtual"
                else:
                    return Response([{"error": f"{device_name} @ {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)

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
                    backdoor_prefix = Prefix.objects.filter(vlan_id=backdoor_vlan[0].id, site=site.id)
                    if len(backdoor_prefix) == 1:
                        nb_data["backdoor_prefix"] = str(backdoor_prefix[0].prefix)
        except Site.DoesNotExist:
            return Response([{"error": f"Site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response([{"error": f"Got an error: {e}"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(nb_data, status=status.HTTP_200_OK)
    
class NetboxDataVlanViewSet(APIView):

    queryset = Site.objects.all()
    serializer_class = NetboxDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Get the request body
            request_body = request.body.decode("utf-8")
            if not request_body:
                return Response([{"error": "Missing request body."}], status=status.HTTP_400_BAD_REQUEST)
            data = json.loads(request_body)

            # Get the values from the request body
            site_name = data.get("site_name")
            vlan = data.get("vlan")

            if not(site_name and vlan):
                return Response([{"error": "Missing one or more of the required parameters (site_name, vlan)."}], status=status.HTTP_400_BAD_REQUEST)

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
            # Build the default response.
            nb_data = {
                "backdoor" : {}, 
                "backend": {}, 
                "devices": [],
                "firewall_ip" : "",
                "firewall_name" : "",
                "pod_description" : "",
                "pod_name" : "",
                "vpn_address" : f"devnetsandbox-usw1-reservation.cisco.com:{20000+vlan}",
                "vpn_port" : 20000+vlan
            }
            
            ## Check site 
            # print(f"data= {data}")
            site = Site.objects.get(name=site_name)
            # print(len(site))

            ## Now get the VLAN (backend info)
            _vlan = VLAN.objects.filter(vid=vlan, site=site.id)
            # print(f"VLAN = {vlan}, found {_vlan[0].vid}")
            if len(_vlan) != 1:
                return Response([{"error": f"Expect to find 1 VLAN, but found {len(_vlan)}."}], status=status.HTTP_400_BAD_REQUEST)

            if _vlan[0].tenant == None:
                return Response([{"error": f"VLAN Tenant is not configured for VLAN {vlan}"}], status=status.HTTP_400_BAD_REQUEST)

            # print(f"1- VLANID = {_vlan[0].tenant.name}")
            nb_data["backend"] = {
                "prefix"    :  "10.10.20.0/24",
                "vlan_id"   : vlan,
                "vlan_name" : _vlan[0].tenant.name,
                "vlan_uuid" : _vlan[0].tenant.id
            }
            
            ## Grab backdoor vlan info
            roles = Role.objects.filter(slug="pod-backdoor")
            if len(roles) != 1:
                return Response([{"error": f"pod-backdoor is not configured."}], status=status.HTTP_400_BAD_REQUEST)

            # print(f"2 - rolid = {roles[0].id}")
            # print(f"3 - backdoor = {_vlan[0].tenant.slug}")
            
            backdoor_vlan = VLAN.objects.filter(role=roles[0].id, name=f"backdoor-{str(_vlan[0].tenant.slug).split('-')[1]}", site=site.id)
            if len(backdoor_vlan) == 1:
                # print(f"4 - {backdoor_vlan[0].vid}")
                backdoor_prefix = Prefix.objects.filter(vlan_id=backdoor_vlan[0].id, site=site.id)
                if len(backdoor_prefix) != 1:
                    return Response([{"error": f"Unable to find the backdoor prefix"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                nb_data["backdoor"] = {
                    "prefix": str(backdoor_prefix[0].prefix),
                    "vlan_description": backdoor_prefix[0].vrf.name,
                    "vlan_id": backdoor_prefix[0].vlan.vid,
                    "vlan_name": backdoor_prefix[0].vlan.name
                }

                # get the firewall info
                fw_name = f'usw1-{nb_data["backdoor"]["vlan_name"].split("-")[1]}-fw'
                # print(f"5 - {type(fw_name)}")

                fw_device_info = VirtualMachine.objects.filter(name=fw_name, site=site.id)
                if len(fw_device_info) == 1:
                    # print(f"6 - {fw_device_info[0].primary_ip.address}")
                    nb_data["firewall_cidr"] = str(fw_device_info[0].primary_ip.address)
                    nb_data["firewall_ip"] = str(fw_device_info[0].primary_ip.address).split("/")[0]
                    nb_data["firewall_name"] = fw_name
                    nb_data["pod_name"] = _vlan[0].name

                    if fw_device_info[0].tenant:
                        devices = Device.objects.filter(site=site.id, tenant=fw_device_info[0].tenant.id)
                        for device in devices:
                            # print(device.name)
                            
                            ip = "" if device.primary_ip is None else str(device.primary_ip.address)
                            dev = {"device_name" : device.name,
                                "device_ip" : ip
                            }
                            nb_data["devices"].append(dev)
        except Site.DoesNotExist:
            return Response([{"error": f"Site {site_name} does not exist."}], status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response([{"error": f"Got an error: {e}"}], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(nb_data, status=status.HTTP_200_OK)