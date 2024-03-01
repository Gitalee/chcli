#!/usr/bin/python3
import json
import os
import time
 
import config
import expected
import helper
import paramiko
 
env_id = None
image_tag = None

def test_user_login():
   """Verifying if a user can login to the site or not"""
   response_login = os.popen(
       './chctl login --username ' + config.web_login_username + ' --password ' + config.web_login_password + ' --server ' + config.web_url).read()
   print('./chctl login --username ' + config.web_login_username + ' --password ' + config.web_login_password + ' --server ' + config.web_url)
   assert (
           expected.login_response in response_login), "Expected: " + expected.login_response + " should be in Actual: " + response_login
 
def test_vault_ssh_create():
   """Verifying if a user can create ssh vault"""
   response_vault_ssh_create = os.popen(
       './chctl vault create ssh --vaultname=' + config.ssh_vault_name + ' --sshkey=' + config.sshkey_path + '').read()
   print('./chctl vault create ssh --vaultname=' + config.ssh_vault_name + ' --sshkey=' + config.sshkey_path + '')
   print(response_vault_ssh_create)
   assert ("success" in response_vault_ssh_create), "Expected: success should be present in the Actual response: " + response_vault_ssh_create
 
def test_vault_dockerhub_create():
   """Verifying if a user can create DockerHub vault"""
   time.sleep(5)
   response_vault_dockerhub_create = os.popen(
       './chctl vault create password --vaultname ' + config.dockerhub_vault_name + ' --username ' + config.dockerhub_vault_username + ' --password ' + config.dockerhub_vault_passwd).read()
   print('./chctl vault create password --vaultname ' + config.dockerhub_vault_name + ' --username ' + config.dockerhub_vault_username + ' --password ' + config.dockerhub_vault_passwd)
   assert ("success" in response_vault_dockerhub_create), "Expected: success should be present in the Actual response: " + response_vault_dockerhub_create
 
def test_vault_buildbox_create():
   """Verifying if a user can create buildbox vault"""
   time.sleep(5)
   ssh_vault_id = helper.get_vault_id(config.ssh_vault_name)
   response_vault_buildbox_create = os.popen(
       './chctl vault create buildbox --v ' + config.buildbox_vault_name + ' -p 22 --host ' + config.buildbox_ip + ' --vaultId ' + ssh_vault_id + ' --username ' + config.buildbox_username + ' --osType linux').read()
   print('./chctl vault create buildbox --v ' + config.buildbox_vault_name + ' -p 22 --host ' + config.buildbox_ip + ' --vaultId ' + ssh_vault_id + ' --username ' + config.buildbox_username + ' --osType linux')
   print(response_vault_buildbox_create)
   assert ("success" in response_vault_buildbox_create), "Expected: success should be present in the Actual response: " + response_vault_buildbox_create
 
def test_node_add():
   """Verifying if a user can add a node"""
   time.sleep(5)
   response_node_add = os.popen(
       './chctl node addNode --nodename=' + config.node_name + ' --osType=' + config.os_type + ' --host=' + config.host_ip + ' --alias=' + config.alias_name + ' --username=' + config.host_user + ' --connectionType=' + config.connection_type + ' --vaultType=' + config.node_vault_type + ' --vaultId=' + helper.get_vault_id(
           config.ssh_vault_name)).read()
   print('./chctl node addNode --nodename=' + config.node_name + ' --osType=' + config.os_type + ' --host=' + config.host_ip + ' --alias=' + config.alias_name + ' --username=' + config.host_user + ' --connectionType=' + config.connection_type + ' --vaultType=' + config.node_vault_type + ' --vaultId=' + helper.get_vault_id(
           config.ssh_vault_name))
   status = json.loads(response_node_add)
   assert (
       status['status']), "Expected: " + expected.node_create_response + ' but Actual response is : ' + response_node_add
 
 
def test_check_connection():
   """Node Connection Test"""
   time.sleep(10)
   response_node_connection = os.popen(
       './chctl check-connection --node_id ' + helper.get_node_id(config.node_name)).read()
   print('./chctl check-connection --node_id ' + helper.get_node_id(config.node_name))
   time.sleep(60)
   assert (
           expected.pre_discover_reponse in response_node_connection), "Expected: " + expected.pre_discover_reponse + ' but Actual response is : ' + response_node_connection
 
def test_prerequisite():
   """Node Connection Test"""
   time.sleep(10)
   response_node_prerequisite = os.popen(
       './chctl check-prerequisite --node_id ' + helper.get_node_id(config.node_name)).read()
   print('./chctl check-prerequisite --node_id ' + helper.get_node_id(config.node_name))
   time.sleep(60)
   assert (
           expected.pre_discover_reponse in response_node_prerequisite), "Expected: " + expected.pre_discover_reponse + ' but Actual response is : ' + response_node_prerequisite
 
def test_start_discover_node():
   """If a user can start discovering a node"""
   time.sleep(10)
   response_node_discovery = os.popen(
       './chctl discover --os ' + config.os_type + ' --nodeId=' + helper.get_node_id(config.node_name)).read()
   print('./chctl discover --os ' + config.os_type + ' --nodeId=' + helper.get_node_id(config.node_name))
   time.sleep(100)
   assert (
           expected.node_discovery_response in response_node_discovery), "Expected: " + expected.node_discovery_response + ' but Actual response is : ' + response_node_discovery
 
def test_attach_prob():
   """If a prob can be attached to a process"""
   response_prob_attach = os.popen('./chctl probe attach --processname=' +
       config.process_name + ' --processid=' + str(
           helper.get_process_id(helper.get_node_id(config.node_name))) + ' --nodeid=' + helper.get_node_id(
           config.node_name)).read()
   print('./chctl probe attach --processname=' + str(
       config.process_name + ' --processid=' + str(
           helper.get_process_id(helper.get_node_id(config.node_name))) + ' --nodeid=' + helper.get_node_id(
           config.node_name)))
   assert expected.prob_attach_response in response_prob_attach, "Expected: " + expected.prob_attach_response + ' but Actual response is : ' + response_prob_attach
 
def test_detach_prob():
   """If a prob can be detached successfully"""
   time.sleep(80)
   os.popen('curl http://'+config.host_ip+' >> /dev/null')
   response_prob_detach = os.popen('./chctl probe detach --nodeid=' + helper.get_node_id(config.node_name) + " --processname="+config.process_name+ " --processid="+str(
           helper.get_process_id(helper.get_node_id(config.node_name))) + " -t true").read()
 
   print('./chctl probe detach --nodeid=' + helper.get_node_id(config.node_name) + " --processname="+config.process_name+ " --processid="+str(
           helper.get_process_id(helper.get_node_id(config.node_name))) + " -t true")
   assert expected.prob_detach_response in response_prob_detach, "Expected: " + expected.prob_detach_response + ' but Actual response is : ' + response_prob_detach
 
def test_transform():
   """If the process can be transformed"""
   time.sleep(100)
  
   profile_id = (helper.get_profile_id(config.node_name))
 
   global image_tag
   image_tag = helper.get_tag()
 
   response_transform = os.popen('./chctl transform linux --profileId ' + profile_id + ' --buildBoxVaultId ' + helper.get_vault_id(config.buildbox_vault_name) + ' --uploadToRegistry --registryType dockerhub --registryServer=hub.docker.com --repository ' + config.docker_image_name + ' --tag ' + image_tag + ' --registryVaultId '+ helper.get_vault_id(config.dockerhub_vault_name) +' --clean').read()
   print ('./chctl transform linux --profileId ' + profile_id + ' --buildBoxVaultId ' + helper.get_vault_id(config.buildbox_vault_name) + ' --uploadToRegistry --registryType dockerhub --registryServer=hub.docker.com --repository ' + config.docker_image_name + ' --tag ' + image_tag + ' --registryVaultId '+ helper.get_vault_id(config.dockerhub_vault_name) +' --clean')
   assert "Auto Containerisation started" in response_transform, "Expected: " + expected.transform_response + " but Actual response : " + response_transform
 
 
def test_addbyoccluster():
   """Verifying if a user is able to create aws cluster"""
   time.sleep(100)
   response_addbyoccluster_status = os.popen('./chctl cluster addbyoccluster --clustername=' + config.cluster_name + ' --type=' + config.cluster_type +  ' --distro=' + config.cloud_distro + ' --kubeConfig cluster.yaml').read()
   time.sleep(60)
   response_addbyoccluster_status = os.popen('./chctl cluster listCluster').read()
   print('./chctl cluster listCluster')
   assert config.cluster_name in response_addbyoccluster_status, "Expected: "+config.cluster_name+" should be present in the Actual response: "+response_addbyoccluster_status
 
def test_app_blue_print_create():
   """Application blue print should get created."""
   response_app_creation = os.popen(
       './chctl cluster addApp --bluePrintName=' + config.application_name + ' --type=' + config.application_type).read()
   print('./chctl cluster addApp --bluePrintName=' + config.application_name + ' --type=' + config.application_type)
   assert (config.application_name in response_app_creation), "Expected application : " + config.application_name + \
                                                              " but Actual response: " + response_app_creation
 
     
def test_app_version_deploy():
   """A new version should get added"""
   time.sleep(5)
   app_id = helper.get_app_id(config.application_name)
   response_app_version = os.popen(
       './chctl cluster addVersion --versionName=' + config.application_version + ' --secret="" '
       + ' --blueprintId=' + app_id).read()
   print('./chctl cluster addVersion --versionName=' + config.application_version + ' --secret="" --blueprintId=' + app_id)
   assert config.application_version in response_app_version, "Expected App Version: " + config.application_version + \
       "should be in actual response : " + response_app_version
 
 
def test_add_service():
   """Service should get added"""
   time.sleep(5)
   image_tag = helper.get_tag()
   print('./chctl cluster addService --name='+config.process_name+' --appVersion="'+helper.get_app_version_id(config.application_version)+'" --image="'+config.docker_image_name+'" --imageTag='+image_tag+' --port='+config.application_port + ' --IPType LB')
   response_add_service = os.popen('./chctl cluster addService --name='+config.process_name+' --appVersion="'+helper.get_app_version_id(config.application_version)+'" --image="'+config.docker_image_name+'" --imageTag='+image_tag+' --port='+config.application_port+ ' --IPType LB').read()
   assert (expected.add_service_response in response_add_service), "Expected: " + expected.add_service_response + \
       " should be present in actual response : " + response_add_service
 
def test_deploy_application():
   """Application should get deployed successfully"""
   time.sleep(5)
   cluster_id = helper.get_cluster_info(config.cluster_name)['_id']
   application_id = helper.get_app_id(config.application_name)
   application_version_id = helper.get_app_version_id(config.application_version)
   env_name = config.env_name
   response_deploy_application = os.popen('./chctl deploy container --appId='+application_id+' --appVersionId='+application_version_id+' --clusterId='+cluster_id+' --name='+env_name).read()
   time.sleep(100)
   print('./chctl deploy container --appId='+application_id+' --appVersionId='+application_version_id+' --clusterId='+cluster_id+' --name='+env_name)
   deployment_detail = json.loads(response_deploy_application)
   global env_id
   env_id = deployment_detail['envId']
   status = deployment_detail['status']
   assert (status is True), "Expected status: true but actual response is: " + response_deploy_application
 
 
def test_deployment():
   ssh = paramiko.SSHClient()
   key = paramiko.RSAKey.from_private_key_file('cb-demo.pem')
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
   ssh.connect(hostname = config.cluster_public_ip, username = 'centos', key_filename = 'cb-demo.pem')  
   stdin, stdout, stderr = ssh.exec_command("export KUBECONFIG=/etc/kubernetes/admin.conf | sudo curl -o -I -L -s -w '%{http_code}' http://$(sudo kubectl get svc -n sample-application-automation1-nginx | awk 'NR==2 {print $3}')")
   stdout=stdout.readlines()
 
   ssh.close()
   output =""
   for line in stdout:
        output=output+line
   if output!="":
       print output
   assert  '200' in output, "Expected output: 200 in response data " + output 
 
def test_delete_cluster():
   time.sleep(60)
   """Verifying if a cluster can be deleted successfully."""
   cluster_id = helper.get_cluster_info(config.cluster_name)['_id']
   os.popen('./chctl cluster deleteCluster --clusterId ' + cluster_id + ' --deleteForce "' + config.force_delete + '"')
   print('./chctl cluster deleteCluster --clusterId ' + cluster_id + ' --deleteForce "' + config.force_delete + '"')
   time.sleep(30)
   cluster_status = helper.get_cluster_info(config.cluster_name)['status']
   print('./chctl cluster listCluster')
   time.sleep(60)
   assert (expected.delete_cluster_status == cluster_status), "Expected cluster status: " + \
                                                              expected.delete_cluster_status + " But actual status " \
 
def test_app_blue_print_delete():
   """Application blue print get deleted"""
   time.sleep(5)
   print('./chctl cluster deleteApp --appId ' + helper.get_app_id(config.application_name))
   response_app_deletion = os.popen('./chctl cluster deleteApp --appId ' +
                                    helper.get_app_id(config.application_name)).read()
   print('./chctl cluster listApp')
   assert config.application_name in response_app_deletion, "Expected: success in response data " + response_app_deletion
 
 
def test_node_delete():
   """Verifying if a user can delete a node"""
   time.sleep(10)
   print('./chctl node deleteNode --nodeId=' + helper.get_node_id(config.node_name))
   response_node_delete = os.popen('./chctl node deleteNode --nodeId=' + helper.get_node_id(config.node_name)).read()
   time.sleep(60)
   assert ("Node removal started" in response_node_delete), "Expected: success in response data " + response_node_delete
 
def test_vault_buildbox_delete():
   """Verifying if a user can delete ssh vault"""
   time.sleep(5)
   vault_id = helper.get_vault_id(config.buildbox_vault_name)
   print('./chctl vault delete --vaultId=' + vault_id + '')
   response_vault_buildbox_delete = os.popen('./chctl vault delete --vaultId=' + vault_id + '').read()
   assert (
           "success" in response_vault_buildbox_delete), "Expected: success should be present in the Actual response: " + response_vault_ssh_delete + " and vault_id is " + vault_id
 
def test_vault_ssh_delete():
   """Verifying if a user can delete ssh vault"""
   time.sleep(5)
   vault_id = helper.get_vault_id(config.ssh_vault_name)
   response_vault_ssh_delete = os.popen('./chctl vault delete --vaultId=' + vault_id + '').read()
   print('./chctl vault delete --vaultId=' + vault_id + '')
   assert (
           "success" in response_vault_ssh_delete), "Expected: success should be present in the Actual response: " + response_vault_ssh_delete + " and vault_id is " + vault_id
 
 
def test_vault_dockerhub_delete():
   """Verifying if a user can delete AWS vault"""
   time.sleep(5)
   vault_id = helper.get_vault_id(config.dockerhub_vault_name)
   response_vault_dockerhub_delete = os.popen('./chctl vault delete --vaultId=' + vault_id + '').read()
   print('./chctl vault delete --vaultId=' + vault_id + '')
   assert (
           "success" in response_vault_dockerhub_delete), "Expected: success should be present in the Actual response: " + response_vault_dockerhub_delete + " and vault_id is " + vault_id
 
 
 
 
 
 
 
               

