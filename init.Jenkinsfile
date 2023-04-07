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
        string( name: 'SUPERUSER_PASSWORD', defaultValue: "", description: 'Пароль суперпользователя')
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
        booleanParam(name: 'Refresh', defaultValue: false, description: 'Перезагрузка параметров')
        booleanParam(name: 'Staging', defaultValue: false)
    }
    environment {
        ROOT_APP_DIR='/app'

        POSTGRES_DIR="${STORE_DIR}/db"
        CERTBOT_DIR="${STORE_DIR}/certbot"
        NGINX_DIR="${STORE_DIR}/nginx"

        APP_NETWORK='app_net'
        APP_HOST='app'
        BACKUP_DIR='/media/hdd/backUp'
    }
    stages {
        stage('Перезагрузка параметров') {
            when { expression { return params.Refresh == true } }
            steps { echo("Ended pipeline early.") }
        }
        stage ('Настройка SSH соединения') {
            when { expression { return params.Refresh == false } }
            steps {
                build job: 'known_host', wait: true, parameters: [string(name: 'ip_address', value: params.IP)]
            }
        }
        stage ('Открытие порта 443') {
            when { expression { return params.Refresh == false } }
            steps {
                build job: 'openHTTPS', wait: true, parameters: [string(name: 'ip_address', value: params.IP)]
            }
        }
        stage ('Получение сертификата') {
            when { expression { return params.Refresh == false } }
            steps {
                build job: 'cert', wait: true, parameters: [
                    string( name: 'IP', value: params.IP),
                    string( name: 'CERTBOT_DIR', value: env.CERTBOT_DIR),
                    string( name: 'DOMAIN', value: params.DOMAIN),
                    string( name: 'EMAIL', value: params.EMAIL),
                    booleanParam(name: 'Staging', value: params.Staging)
                ]
            }
        }
        stage ('Резервирование сертификата') {
            when { expression { return params.Refresh == false } }
            steps {
                build job: 'backUpCertificate', wait: true, parameters: [
                    string(name: 'IP', value: params.IP),
                    string(name: 'FROM', value: "${env.CERTBOT_DIR}/conf"),
                    string(name: 'TO', value: env.BACKUP_DIR)
                ]
            }

        }
        stage('Приложение с базой данных') {
            when { expression { return params.Refresh == false } }
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                        remote.identityFile = sshKey
                        sh script: 'scp -i ${sshKey} -rp ${WORKSPACE} root@${IP}:${ROOT_APP_DIR}', returnStdout: true
                        sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml build"
                        sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml up -d --force-recreate"
                    }
                }
            }
        }
        stage ('Сертифицированный прокси-сервер') {
            when { expression { return params.Refresh == false } }
            steps {
                build job: 'certProxy', wait: true, parameters: [
                    string( name: 'IP', value: params.IP),
                    string( name: 'CERTBOT_DIR', value: env.CERTBOT_DIR),
                    string( name: 'NGINX_DIR', value: env.NGINX_DIR),
                    string( name: 'DOMAIN', value: params.DOMAIN),
                    string( name: 'EMAIL', value: params.EMAIL),
                    string( name: 'APP_NETWORK', value: env.APP_NETWORK),
                    string( name: 'APP_HOST', value: env.APP_HOST),
                    booleanParam(name: 'Staging', value: params.Staging)
                ]
            }
        }
    }
}
