import geni.portal as portal
import geni.rspec.pg as rspec

request = portal.context.makeRequestRSpec()

prefixForIP = "192.168.1."
link = request.LAN("lan")

# === Create webserver node ===
webserver = request.XenVM("webserver")
webserver.routable_control_ip = "true"
webserver.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU20-64-STD"

web_iface = webserver.addInterface("if0")
web_iface.component_id = "eth1"
web_iface.addAddress(rspec.IPv4Address(prefixForIP + "1", "255.255.255.0"))
link.addInterface(web_iface)

# Apache + NFS mount setup for webserver
webserver.addService(rspec.Execute(shell="sh", command="""
sudo apt update && sudo apt install -y apache2 nfs-common
sudo mkdir -p /var/webserver_log
sudo mount -t nfs 192.168.1.2:/var/webserver_monitor /var/webserver_log
"""))

# === Create observer node ===
observer = request.XenVM("observer")
observer.routable_control_ip = "false"
observer.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU20-64-STD"

obs_iface = observer.addInterface("if1")
obs_iface.component_id = "eth1"
obs_iface.addAddress(rspec.IPv4Address(prefixForIP + "2", "255.255.255.0"))
link.addInterface(obs_iface)

# NFS setup for observer
observer.addService(rspec.Execute(shell="sh", command="""
sudo apt update && sudo apt install -y nfs-kernel-server
sudo mkdir -p /var/webserver_monitor
echo "/var/webserver_monitor 192.168.1.1(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
sudo systemctl restart nfs-server
"""))

# Print RSpec
portal.context.printRequestRSpec()

