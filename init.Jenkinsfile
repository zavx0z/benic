def remote = [:]
remote.name = "root"
remote.host = params.ip_address
remote.allowAnyHosts = true
remote.user = "root"

pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '4', artifactNumToKeepStr: '4'))
        disableConcurrentBuilds(abortPrevious: true)
    }
    parameters {
        string( name: 'ip_address', defaultValue: "95.163.235.179", description: 'IP-адрес сервера')
        booleanParam(name: 'clear', defaultValue: false, description: 'Перезаписать')
    }
    environment {
        ROOT_APP_DIR='/app'
    }
    stages {
        stage ('Настройка SSH соединения') {
            steps {
                build job: 'known_host', wait: false, parameters: [string(name: 'ip_address', value: '95.163.235.179')]
            }
        }
        stage('Копирование проекта') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                        remote.identityFile = sshKey
                        sshPut remote: remote, from: "${WORKSPACE}", into: "${ROOT_APP_DIR}"
                    }
                }
            }
        }
        stage('Запуск приложения с базой') {
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
        stage ('Открытие порта 443') {
            steps {
                build job: 'openHTTPS', wait: false, parameters: [string(name: 'ip_address', value: '95.163.235.179')]
            }
        }
    }
}
