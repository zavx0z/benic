def remote = [:]
remote.name = "root"
remote.host = params.IP
remote.allowAnyHosts = true
remote.user = "root"

pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '4', artifactNumToKeepStr: '4'))
        disableConcurrentBuilds(abortPrevious: true)
    }
    parameters {
        string( name: 'IP', defaultValue: "95.163.235.179", description: 'IP-адрес сервера')
        string( name: 'STORE_DIR', defaultValue: "/store")
        string( name: 'DOMAIN', defaultValue: "zavx0z.com")
        string( name: 'EMAIL', defaultValue: "metaversebdfl@gmail.com")
        string( name: 'POSTGRES_DB', defaultValue: "benif")
        string( name: 'POSTGRES_HOST', defaultValue: "db")
        string( name: 'POSTGRES_PORT', defaultValue: "5432")
        string( name: 'POSTGRES_USER', defaultValue: "zavx0zBenif")
        string( name: 'POSTGRES_PASSWORD', defaultValue: "12112022")
        string( name: 'JWT_SECRET_KEY', defaultValue: "adkngdfFDGSDFqhnlakjflorqirefOJ;SJDG")
    }
    environment {
        ROOT_APP_DIR='/app'
        CERTBOT_DIR="${STORE_DIR}/certbot"
        NGINX_DIR="${STORE_DIR}/nginx/conf.d"
    }
    stages {
        stage ('Настройка SSH соединения') {
            steps {
                build job: 'known_host', wait: true, parameters: [string(name: 'ip_address', value: params.IP)]
            }
        }
        stage ('Открытие порта 443') {
            steps {
                build job: 'openHTTPS', wait: true, parameters: [string(name: 'ip_address', value: params.IP)]
            }
        }
        stage ('Получение сертификата') {
            steps {
                build job: 'cert', wait: true, parameters: [
                    string( name: 'IP', value: params.IP),
                    string( name: 'CERTBOT_DIR', value: params.STORE_DIR),
                    string( name: 'DOMAIN', value: params.DOMAIN),
                    string( name: 'EMAIL', value: params.EMAIL),
                ]
            }
        }
        stage('Копирование проекта') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                        sh script: 'scp -i ${sshKey} -rp ${WORKSPACE} root@${IP}:${ROOT_APP_DIR}', returnStdout: true
                    }
                }
            }
        }
        stage('Настройка Nginx') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                        remote.identityFile = sshKey
                        sshCommand remote: remote, command: "sed -i \"s/\\\${DOMAIN}/${DOMAIN}/g\" ${NGINX_DIR}/nginx.conf"
                        sshCommand remote: remote, command: "sed -i \"s/\\\${APP_HOST}/${APP_HOST}/g\" ${NGINX_DIR}/nginx.conf"
                        sshCommand remote: remote, command: "sed -i \"s/\\\${CERTBOT_DIR}/${CERTBOT_DIR}/g\" ${NGINX_DIR}/nginx.conf"
                    }
                }
            }
        }
        stage('Запуск') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                        remote.identityFile = sshKey
                        sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml build"
                        sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml up -d"
                    }
                }
            }
        }
    }
}
