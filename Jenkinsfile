import java.time.*;
result = 'Result';
startTime = new Date().format("dd-MM-yyyy HH:mm:ss", TimeZone.getTimeZone('IST'));

node('master'){
    try{
        stage('Get Parameters'){
            List props = []
            List params = [
                string(name: 'targetURL',           description: 'URL of Appliance',            defaultValue: 'https://app.cloudhedge.io'),
                credentials(
                    credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl',
                    defaultValue: 'chappUser',
                    description: 'The credentials needed to deploy.',
                    name: 'applianceCreds',
                    required: true
                ),
                credentials(
                    credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl',
                    defaultValue: 'dockerhubCreds',
                    description: 'The credentials needed to deploy.',
                    name: 'dockerCreds',
                    required: true
                ),
                credentials(
                    credentialType: 'com.cloudbees.plugins.credentials.impl.AWSCredentialsImpl',
                    defaultValue: 'gitalee-aws-cred',
                    description: 'The credentials needed to deploy.',
                    name: 'awsCreds',
                    required: true
                ),
                string(name: 'IMAGE_NAME',          description: 'IMAGE_NAME',                  defaultValue: 'gjadhav/demo')
            ]
            props << parameters(params)
            properties(props)
        }
        stage('Git Pull'){
            git branch: 'main', credentialsId: 'gitalee_git_cred', url: 'https://gitlab.com/gjadhav-chg/chcli.git'
        }
        stage('Get CHCLI'){
                withCredentials([[ $class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'gitalee-aws-cred', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY' ]]){
                withAWS(region:'ap-south-1', credentialsId: 'gitalee-aws-cred'){
                    
                    exists = s3DoesObjectExist(bucket:'ch-cli', path:'latest/chctl_linux');
                        if(exists){
                            s3Download(file:'chctl', bucket:'ch-cli', path:'latest/chctl_linux', force:true);
                            sh('chmod +x chctl')
                        }
                    }
                }
            }
            stage('Create AWS Instances'){
                withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                credentialsId: 'gitalee-aws-cred',
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'],
                usernamePassword(credentialsId: applianceCreds, usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD'),
                usernamePassword(credentialsId: dockerCreds, usernameVariable: 'DOCKERHUBUSERNAME', passwordVariable: 'DOCKERHUBPASSWORD')
            ])
            {
                sh'''
                echo "--===========================================--"
                echo "Creating EC2 Instances using Terraform"
                ./terraform init
                echo "Terraform Init is Done"
                echo "--===========================================--"
                ./terraform plan
                echo "Terraform Plan is Done"
                echo "--===========================================--"
                ./terraform apply --auto-approve
                sleep 10
                echo "Machines are created on AWS using Terraform"
                echo "--===========================================--"
                sed -i "s,BUILD_BOX_IP,$(./terraform output buildbox_public_ip),g" config.py
                sed -i "s,HOST_IP,$(./terraform output host_public_ip),g" config.py
                sed -i "s,DOCKERHUBUSERNAME,$DOCKERHUBUSERNAME,g" config.py
                sed -i "s,DOCKERHUBPASSWORD,$DOCKERHUBPASSWORD,g" config.py
                sed -i "s,TARGET_URL,$targetURL,g" config.py
                sed -i "s,CHUSERNAME,$USERNAME,g" config.py
                sed -i "s,CHPASSWORD,$PASSWORD,g" config.py
                sed -i "s,AWSACCESSKEY,$AWS_ACCESS_KEY_ID,g" config.py
                sed -i "s,AWSSECRETKEY,$AWS_SECRET_ACCESS_KEY,g" config.py
                sed -i "s,IMAGE_NAME,$IMAGE_NAME,g" config.py
                sed -i "s,DOCKER_IMAGE_TAG,$BUILD_NUMBER,g" config.py
                '''
                }
            withCredentials([sshUserPrivateKey(credentialsId: '8bac1c33-5372-4e13-9275-1142a4fb3028', keyFileVariable: 'identity', passphraseVariable: '', usernameVariable: 'userName')]) {
                    def remote = [:]
                    remote.name = "node-1"
                    env.cluster_public_IP = sh (
                    script: "./terraform output cluster_public_ip",
                    returnStdout: true
                    ).trim()
                    echo "Build full flag: ${cluster_public_IP}"
                    env.cluster_private_IP = sh (
                    script: "./terraform output cluster_private_ip",
                    returnStdout: true
                    ).trim()
                    sh 'sed -i "s,CLUSTER_PUBLIC_IP,$cluster_public_IP,g" config.py'
                    remote.host = cluster_public_IP
                    echo "$remote.host"
                    remote.allowAnyHosts = true
                    remote.user = userName
                    remote.identityFile = identity
                    stage("Create cluster") {
                            sshCommand remote: remote, command: 'kubeadm  reset -f', sudo: true
                            sshCommand remote: remote, command: "kubeadm init --pod-network-cidr=10.244.0.0/16  --apiserver-advertise-address=0.0.0.0 --apiserver-cert-extra-sans=$cluster_public_IP", sudo: true
                            sshCommand remote: remote, command: "mkdir -p $HOME/.kube", sudo: true
                            sshCommand remote: remote, command: "cp -r /etc/kubernetes/admin.conf $HOME/.kube/config", sudo: true
                            sshCommand remote: remote, command: "chown \$(id -u):\$(id -g) $HOME/.kube/config", sudo: true
                            sshCommand remote: remote, command: 'export KUBECONFIG=/etc/kubernetes/admin.conf'
                            env.taint = sshCommand remote: remote, command: "kubectl get nodes | grep ip | awk '{ print \$1 }'", sudo: true
                            sshCommand remote: remote, command: "kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml", sudo: true
                            sshCommand remote: remote, command: "kubectl taint nodes $taint node-role.kubernetes.io/master:NoSchedule-", sudo: true
                            sshGet remote: remote, from: "$HOME/.kube/config", into: 'cluster.yaml', override: true
                            sh'''
                            sed -i "s,$cluster_private_IP,$cluster_public_IP,g" cluster.yaml
                            cat cluster.yaml
                            '''
                                

                        }
                    }    
                
        }
        
        stage('Tests'){
            def customImage = docker.build("chcli-test:$BUILD_NUMBER", "-f Dockerfile .")
            sh('docker run --name chcli-test chcli-test:$BUILD_NUMBER')
            result = "Passed";
        }
        
    }
    catch(e){
        result = "Failed";
        throw e
    }
    finally {
        
        stage('Delete AWS Instances'){
                withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                credentialsId: 'gitalee-aws-cred',
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
            ]]){
                sh'''
                if [ -f terraform.tfstate ]; then
                    [ -s terraform.tfstate ] && ./terraform destroy --auto-approve || echo 'file is empty'
                  
                else
                    echo "AWS instances were not created"
                fi
                '''
                sh('docker cp chcli-test:/test/nosetests.html nosetests.html')
                sh('docker rm chcli-test && docker rmi chcli-test:$BUILD_NUMBER')
                }
        }
        
        stage('Email Notification'){
            endTime = new Date().format("dd-MM-yyyy HH:mm:ss", TimeZone.getTimeZone('IST'));
            executionTime = endTime - startTime;
            emailext attachmentsPattern: 'chcli-automation/nosetests.html', 
            body: "Hi Team,<br><br>Following are the details for test execution of chcli:<br><br><table border='1' style='table-layout: fixed; border: 1px solid black;'><tbody><tr style='border: 1px solid black;'><td style='border: 1px solid black;'>Target URL</td><td style='border: 1px solid black;'>${targetURL}</td></tr><tr style='border: 1px solid black;'><td style='border: 1px solid black;'>Start Time</td><td style='border: 1px solid black;'>${startTime} IST</td></tr><tr style='border: 1px solid black;'><td style='border: 1px solid black;'>End Time</td><td style='border: 1px solid black;'>${endTime} IST</td></tr></tbody></table><br><br>The report is in the attachment.", 
            subject: "${env.JOB_NAME} tested ${env.targetURL} and it ${result}", 
            mimeType: 'text/html',to: "uupadhyay@cloudhedge.io,ppanditrao@cloudhedge.io,kingale@cloudhedge.io"
        }
        stage('Delete Workspace'){
            deleteDir()
        }
    }
}
