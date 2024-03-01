$url = "https://ch-cli.s3.ap-south-1.amazonaws.com/ch-rel-1.4.1/chctl.exe"
$web_login_username = "gjadhav@cloudhedge.io"
$web_login_password = "Password12345%"
$web_url = "https://app.cloudhedge.io"

$dockerhub_vault_username = "gjadhav"
$dockerhub_vault_passwd = "gitalee12"
$dockerhub_vault_name = "test_dockerhub_vault_automation"
$vault_type_registry = "password"
$registry_type = "dockerhub"

$password_host_vault_password = "Elephant11!"
$password_host_vault_name = "test_password_host_vault_automation"

$password_buildbox_vault_name = "test_cred_buildbox"
$buildbox_vault_password = "Elephant111!"
$buildbox_username = "cloudhedge"
$buildbox_ip = "probuildwin2019.eastus2.cloudapp.azure.com"
$buildbox_vault_name = "test_buildbox_vault_automation"
$buildbox_os_type = "Windows"

$os_type = "windows"
$host_ip = "3.22.43.138"
$host_user = "Administrator"
$connection_type = "Basic"
$node_vault_type = "password"
$node_name = "test"
$alias_name = "test_windows-host"
$discover_os_type = "windows"
$process_name = "hrs-new"

$port = "5986"

$docker_image_name = "gjadhav/test-hrs"
$image_tag = "18june"
$application_name = "test_sample-application-automation"
$application_type = "non-prod"
$application_version = "v1"
$application_port = "8082"
$env_name = $process_name
$IPType = "LB"

$cluster_name = "rhocp"
$cluster_type = "non-prod"
$cluster_distro = "eks"
$cluster_kubeconfig_file = "eks.txt"


function get-vaultId($vault_name){
	$vault_list = .\chctl vault list |  ConvertFrom-Json
	$vault_id = ($vault_list.vaults | . where {$_.name -eq $vault_name})._id
	return $vault_id
	
}
function get-nodeId($node_name){
	$node_list = .\chctl node listNodes |  ConvertFrom-Json
	$nodeId = ($node_list.($node_name))._id
	#$vault_id = ($vault_list.vaults | . where {$_.name -eq $password_vault_name})._id
	return $nodeId
	
}
function get-profileId($node_name, $process_name) {
	$profile_list = .\chctl profile list --node-name=$node_name | ConvertFrom-Json
	#$profile_list
	$profileId = ($profile_list | . where {$_.name -eq $process_name}).rootProfileId
	return $profileId
}

function get-appId($application_name){
	$app_list= .\chctl cluster listApp | ConvertFrom-Json
	$app_id = ($app_list.apps | . where {$_.name -eq $application_name})._id
	return $app_id
}

function get-app-versionId($application_version){
	$app_version_list= .\chctl cluster listApp | ConvertFrom-Json
	#$app_version_id = ($app_version_list.apps.versions | . where {$_.name -eq $application_version})._id
	$app_version_id1 = (($app_version_list.apps | . where {$_.name -eq $application_name}).versions )
	$app_version_id2 = ($app_version_id1 | . where {$_.name -eq $application_version})._id
	return $app_version_id2

}
function get-clusterId($cluster_name){
	$cluster_list = .\chctl cluster listCluster | ConvertFrom-Json
	$cluster_id = ($cluster_list.clusters | . where {$_.name -eq $cluster_name})._id
	return $cluster_id
}
function get_chct($url){
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Donwloding chctl...")
	$response = wget $url -OutFile chctl.exe
	if (Test-Path chctl.exe){
		write-host("chctl downloaded !!")
	}else{
		write-host($response)
	}
}
function login ($web_login_username, $web_login_password, $web_url) {
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Logging in to the portal...")
    	$response_login = .\chctl login --username=$web_login_username --password=$web_login_password --server=$web_url
    	if ($response_login -contains '  "success": true,'){
		write-host("Logged in successfully !")
	}else
	{
		write-host($response_login)
	}
}

function create_password_vault($vault_name , $vault_username , $vault_password) {
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Password vault creating ...")
	$response_host_password_vault = .\chctl vault create password --vaultname=$vault_name --username=$vault_username --password=$vault_password
	if ($response_password_vault -contains '  "status": "success",'){
		write-host("Password vault created successfully!")
	}
	elseif($response_password_vault -contains '  "message": "Vault name already exists"') {
		write-host("Vault name already exists ,please use different vault name")
	}
	else{
		write-host($response_host_password_vault)
	}
}


function create_buildbox_vault($buildbox_vault_name, $port, $buildbox_ip, $buildbox_username , $buildbox_os_type, $connection_type) {
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Buildbox vault creating ...")
	$buildbox_vaultId = get-vaultId($password_buildbox_vault_name)
	$response_buildbox_vault = .\chctl vault create buildbox --vaultname=$buildbox_vault_name --port=$port --host=$buildbox_ip --vaultId=$buildbox_vaultId --username=$buildbox_username  --osType=$buildbox_os_type --connectionType=$connection_type
	if ($response_password_vault -contains '  "status": "success",'){
		write-host("Buildbox vault created successfully!")
	}
	elseif($response_password_vault -contains '  "message": "Vault name already exists"') {
		write-host("Vault name already exists , please use different vault name")
	}
	else{
		write-host($response_buildbox_vault)
	}
}	
function create_wave ($node_name, $os_type, $host_ip, $alias_name , $host_user, $connection_type, $node_vault_type, $port) {
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Wave creation started...")
	$vault_name = $password_host_vault_name
	$vault_id = get-vaultId($vault_name)
	$response_create_wave = .\chctl node addNode --nodename=$node_name --osType=$os_type --host=$host_ip --alias=$alias_name --username=$host_user --connectionType=$connection_type --vaultType=$node_vault_type --vaultId=$vault_id --port=$port
	if ($response_password_vault -contains '  "status": "true",'){
		write-host("Wave  created successfully!")
	}
	else{
		write-host($response_create_wave)
	}
}


function discovery($node_name) {
	Start-Sleep -s 10
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Discovery starting ...")
	$nodeId = get-nodeId($node_name)
	$response_discovery = .\chctl discover --os=$os_type --nodeId=$nodeId | ConvertFrom-Json
	if ($response_discovery.status -eq "true"){
		write-host("Discovery started !!!")
		write-host("Please check the status of discovery from cloudhedge portal")
	}else{
		write-host($response_discovery)
	}

}
function transform($node_name ,$process_name, $buildbox_vault_name, $dockerhub_vault_name, $docker_image_name, $image_tag){
	write-host("Waiting for process to get ready to transform")
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	Start-Sleep -s 80
	write-host("Transform starting ...")
	$profile_id = get-profileId $node_name $process_name
	$buildboxVaultId = get-vaultId($buildbox_vault_name)
	$registry_vaultId = get-vaultId($dockerhub_vault_name)
	$response_transform = .\chctl transform windows --profileId=$profile_id --buildBoxVaultId=$buildboxVaultId --deleteArtifacts=true --uploadToRegistry=true  --registryType=dockerhub  --registryServer=hub.docker.com  --repository=$docker_image_name --tag=$image_tag  --registryVaultId=$registry_vaultId --clean=true | ConvertFrom-Json
	if ($response_transfrom.status -eq "true"){
		write-host("Transform started !!!")
		write-host("Please check the status of transform from cloudhedge portal")
	}
	else{
		write-host($response_transform)
	}

}
function addbyoc_cluster($cluster_name, $cluster_type, $cluster_distro, $cluster_kubeconfig_file){
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Adding BYOC Cluster ...")
	$response_add_cluster = .\chctl cluster addbyoccluster --clustername=$cluster_name --type=$cluster_type --distro=$cluster_distro --kubeConfig=$cluster_kubeconfig_file
	write-host($response_add_cluster)
}

function add_application ($application_name, $application_type){
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Adding application ...")
	$response_add_app = .\chctl cluster addApp --bluePrintName=$application_name --type=$application_type
	write-host($response_add_app)	
}

function add_version_to_blueprint ($application_name, $application_version){
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Adding version to blueprint...")
	$blueprint_Id = get-appId($application_name)
	$response_add_version = .\chctl cluster addVersion --versionName=$application_version --blueprintId=$blueprint_Id
	write-host($response_add_version)
}
function add_service ($process_name ,$docker_image_name, $image_tag, $application_port, $os_type , $IPType){
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Waiting for image to get avaibale at dockerhub...")
	write-host("Meanwhile you can check transform logs , whether docker image is pushed to dockerhub or not")
	Start-Sleep -s 200
	write-host("Adding service...")
	$app_versionId = get-app-versionId($application_version)
	$response_add_service = .\chctl cluster addService --name=$process_name --appVersion=$app_versionId --image=$docker_image_name --imageTag=$image_tag --port=$application_port --osType=$os_type --IPType=$IPType
	write-host($response_add_service)
} 
function deploy($application_name ,$application_version,$cluster_name, $env_name){
	write-host "`n"
	write-host("----------------------------------------------------------------------")
	write-host("Deployment starting ...")
	$app_Id = get-appId($application_name)
	$appVersion_Id =  get-app-versionId($application_version)
	$cluster_Id = get-clusterId($cluster_name)
	$response_deploy = .\chctl deploy container --appId=$app_Id --appVersionId=$appVersion_Id --clusterId=$cluster_Id --name=$env_name
	if ($response_deploy.status -eq "true"){
		write-host("Deployment started !!!")
		write-host("Please check the status of deployment from cloudhedge portal")
	}
	else{
		write-host($response_deploy)
	}
}	
function dtc_automation{
	write-host("----------------------------------------------------------------------")
	write-host("To run this script , first need to provide inputs.Required varibales are defined above (beginning of script), please provide valid values to them first.")
	Start-Sleep -s 10
	write-host("-----------------------------Script started ------------------------------------------------------")
	get_chct($url)                                                                                                      #Downloads chctl.exe                                     
	login $web_login_username $web_login_password $web_url                                                              #Login to Cloudhedge portal 
	create_password_vault $password_host_vault_name $host_user $password_host_vault_password   			                #Creates password type vault to connect host
	create_wave $node_name $os_type $host_ip $alias_name $host_user $connection_type $node_vault_type $port             #Creates node 
	discovery $node_name												                                                #Perform discovery on given node
	create_password_vault $password_buildbox_vault_name $buildbox_username $buildbox_vault_password                     #Creates password type vault to connect buildbox
	create_buildbox_vault $buildbox_vault_name $port $buildbox_ip $buildbox_username $buildbox_os_type $connection_type #Creates buildbox type vault
	create_password_vault $dockerhub_vault_name $dockerhub_vault_username $dockerhub_vault_passwd                       #Creates password type vautl to connect to dockerhub registry
	transform $node_name $process_name $buildbox_vault_name $dockerhub_vault_name $docker_image_name $image_tag	        #Performs transform for given process of provided node and push image to dockerhub registry
	addbyoc_cluster $cluster_name $cluster_type $cluster_distro $cluster_kubeconfig_file				                #Add BYOC Cluster for deployment
	add_application $application_name $application_type						                                            #Add application with given name and type
	add_version_to_blueprint $application_name $application_version						                                #Add version to blueprint for given application
	add_service $process_name $docker_image_name $image_tag $application_port $os_type $IPType			                #Add service with provided inputs
	deploy $application_name $application_version $cluster_name $env_name                                               #Deploy an application to given cluster
	write-host("")
	write-host("-----------------------------Script ended ----------------------------------------------------------")
}
dtc_automation